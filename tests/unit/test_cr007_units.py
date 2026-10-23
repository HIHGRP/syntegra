"""CR-007 pure pieces: access levels, address lines, file sniffing and text, the Word copy."""

from __future__ import annotations

import io
import xml.etree.ElementTree as ET
import zipfile

from syntegra.core import access
from syntegra.records import docx, text


def test_five_access_levels_cover_lower_classifications() -> None:
    assert [lv.number for lv in access.LEVELS] == [1, 2, 3, 4, 5]
    assert access.level("restricted").label == "Level 4 · Restricted"
    assert access.covers("confidential", "internal") and not access.covers("internal", "confidential")
    assert access.level(None).classification == "internal"
    assert [lv.number for lv in access.lower_or_equal("confidential")] == [1, 2, 3]


def test_address_line() -> None:
    from syntegra.iam.services import format_address

    assert format_address({"town": "Ohambele", "lga": "Ukwa East", "state": "Abia", "demo": True}) == (
        "Ohambele, Ukwa East LGA, Abia State"
    )
    assert format_address({"office": "X", "street": "Bende Road", "town": "Umuahia", "state": "Abia"}) == (
        "Bende Road, Umuahia, Abia State"
    )
    assert format_address(None) == ""


def test_uploads_are_identified_by_their_bytes() -> None:
    assert text.sniff(b"%PDF-1.7\n...") == text.PDF
    assert text.sniff(b"\x89PNG\r\n\x1a\n....") == "image/png"
    assert text.sniff(b"\xff\xd8\xff\xe0") == "image/jpeg"
    assert text.sniff(b"II*\x00....") == "image/tiff"
    assert text.sniff(b"Minutes of the PTA meeting\nPresent: 64 parents") == text.TEXT
    assert text.sniff(b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00") is None


def test_text_comes_from_the_pdf_layer_and_the_transcription() -> None:
    from syntegra.platform.demo.abia import _pdf

    pdf = _pdf("ADMISSION REGISTER", ["1001 Chidi Okafor born 1986 parent Okafor family", "1002 Ada Nwosu"] * 3)
    got = text.extract(pdf, text.PDF, transcription="Volume 3 shelf B")
    assert "Chidi Okafor" in got.text and "Volume 3 shelf B" in got.text
    assert got.source == "pdf_text_layer_and_transcription" and got.pages == 1
    only = text.extract(b"\x89PNG\r\n\x1a\n", "image/png", transcription="handwritten register")
    assert only.text.endswith("handwritten register") and only.source in ("transcription", "ocr")


def test_word_copy_is_a_valid_docx() -> None:
    data = docx.build(
        "Admission register", [("Reference", "INS-NG-000129/ADM/1998/00001")], "line one\fpage two\x07", "note"
    )
    z = zipfile.ZipFile(io.BytesIO(data))
    assert {"[Content_Types].xml", "word/document.xml", "word/styles.xml", "_rels/.rels"} <= set(z.namelist())
    root = ET.fromstring(z.read("word/document.xml"))  # noqa: S314 — our own output
    body = "".join(t.text or "" for t in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"))
    assert "INS-NG-000129/ADM/1998/00001" in body and "page two" in body and "\x07" not in body
    for name in z.namelist():
        if name.endswith(".xml") or name.endswith(".rels"):
            ET.fromstring(z.read(name))  # noqa: S314 — every part is well-formed XML


def _scan(lines: list[str]) -> bytes:
    """A flatbed-scanner style page: the demo PDF rendered to a PNG at 200 dpi — an image, no text layer."""
    import pypdfium2 as pdfium

    from syntegra.platform.demo.abia import _pdf

    pdf = pdfium.PdfDocument(_pdf("ADMISSION REGISTER", lines))
    buf = io.BytesIO()
    pdf[0].render(scale=200 / 72).to_pil().save(buf, "PNG")
    return buf.getvalue()


def test_scanned_pages_are_read_by_ocr() -> None:
    import pytest
    from PIL import Image

    if not text.ocr_available():
        pytest.skip("No English Tesseract data (eng.traineddata) on this machine")
    scan = _scan(["Admission number 1001 Chidi Okafor", "Admission number 1002 Ada Nwosu"])
    got = text.extract(scan, "image/png")
    assert got.source == "ocr" and "Okafor" in got.text and "Nwosu" in got.text
    # a scanned PDF (pages are images) and a two-page TIFF are read page by page
    page = Image.open(io.BytesIO(scan))
    for fmt, mime in (("PDF", "application/pdf"), ("TIFF", "image/tiff")):
        buf = io.BytesIO()
        page.save(buf, fmt, save_all=True, append_images=[page.copy()])
        got = text.extract(buf.getvalue(), mime)
        assert got.source == "ocr" and got.text.count("Okafor") == 2, (fmt, got)
    assert text.extract(b"%PDF-1.4 not really a pdf", "application/pdf").source == "none"
    assert text.extract(b"\x89PNG\r\n\x1a\n broken", "image/png").source == "none"
