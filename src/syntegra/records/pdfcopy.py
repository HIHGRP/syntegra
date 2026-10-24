"""Searchable access copies and stamped releases of documents (CR-008, FR-DOC-302/303).

Searchable copy: each page of the scan as an image, with the words OCR found laid over it in invisible text (PDF
text render mode 3) at the place they were read. A PDF reader shows the scan exactly as captured, and lets the
reader search, select and copy the words. The master is never touched; the copy is a new PDF written here without
extra libraries.

Stamped release: every copy that leaves the system carries, on every page, who received it, when, for what
purpose and a release code that the release register resolves. PDFs are stamped with an overlay merged by pypdf;
images are first placed on PDF pages.
"""

# ruff: noqa: E501 — PDF operators are kept on one line each

from __future__ import annotations

import io
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any

from syntegra.records.text import OcrPage

HELVETICA_AVG = 0.52  # average advance of Helvetica glyphs, in em — enough to fit an invisible word to its box


# --------------------------------------------------------------------------- a small PDF writer
class _Pdf:
    def __init__(self) -> None:
        self.objects: list[bytes] = []

    def add(self, body: bytes) -> int:
        self.objects.append(body)
        return len(self.objects)

    def reserve(self) -> int:
        self.objects.append(b"")
        return len(self.objects)

    def set(self, num: int, body: bytes) -> None:
        self.objects[num - 1] = body

    def stream(self, dictionary: str, data: bytes) -> int:
        return self.add(f"<< {dictionary} /Length {len(data)} >>\nstream\n".encode() + data + b"\nendstream")

    def output(self, root: int, info: int) -> bytes:
        out = io.BytesIO()
        out.write(b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n")
        offsets = []
        for i, body in enumerate(self.objects, start=1):
            offsets.append(out.tell())
            out.write(f"{i} 0 obj\n".encode() + body + b"\nendobj\n")
        xref = out.tell()
        out.write(f"xref\n0 {len(self.objects) + 1}\n0000000000 65535 f \n".encode())
        for off in offsets:
            out.write(f"{off:010d} 00000 n \n".encode())
        out.write(
            f"trailer\n<< /Size {len(self.objects) + 1} /Root {root} 0 R /Info {info} 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
        )
        return out.getvalue()


def _text(s: str) -> str:
    """A PDF literal string in WinAnsi: characters outside it become '?'."""
    raw = s.encode("cp1252", errors="replace").decode("latin-1")
    return "(" + raw.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)") + ")"


def _info(pdf: _Pdf, title: str, producer: str) -> int:
    return pdf.add(f"<< /Title {_text(title)} /Producer {_text(producer)} /Creator (Syntegra records) >>".encode())


@dataclass(frozen=True)
class Page:
    image: Any  # PIL image
    dpi: float
    words: Sequence[Any] = ()  # OcrWord


def searchable_pdf(pages: Iterable[OcrPage | Page], *, title: str, producer: str, quality: int = 70) -> bytes:
    """A PDF of the page images with each OCR word laid invisibly over the place it was read."""
    pdf = _Pdf()
    catalog, tree = pdf.reserve(), pdf.reserve()
    font = pdf.add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    kids: list[int] = []
    for n, page in enumerate(pages, start=1):
        img = page.image.convert("L") if page.image.mode not in ("L", "RGB") else page.image
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=quality, optimize=True)
        colour = "/DeviceGray" if img.mode == "L" else "/DeviceRGB"
        xobj = pdf.stream(
            f"/Type /XObject /Subtype /Image /Width {img.width} /Height {img.height} /ColorSpace {colour} /BitsPerComponent 8 /Filter /DCTDecode",
            buf.getvalue(),
        )
        scale = 72.0 / (page.dpi or 200.0)
        w, h = img.width * scale, img.height * scale
        ops = [f"q {w:.2f} 0 0 {h:.2f} 0 0 cm /Im{n} Do Q", "BT 3 Tr"]
        for word in page.words:
            x0, y0, x1, y1 = word.box
            size = max(2.0, (y1 - y0) * scale * 0.88)
            natural = HELVETICA_AVG * size * max(1, len(word.text))
            stretch = max(10.0, min(400.0, 100.0 * (x1 - x0) * scale / natural))
            ops.append(
                f"/F1 {size:.2f} Tf {stretch:.1f} Tz 1 0 0 1 {x0 * scale:.2f} {h - y1 * scale + size * 0.12:.2f} Tm {_text(word.text)} Tj"
            )
        ops.append("ET")
        content = pdf.stream("", "\n".join(ops).encode("latin-1"))
        kids.append(
            pdf.add(
                f"<< /Type /Page /Parent {tree} 0 R /MediaBox [0 0 {w:.2f} {h:.2f}] /Resources << /XObject << /Im{n} {xobj} 0 R >> /Font << /F1 {font} 0 R >> >> /Contents {content} 0 R >>".encode()
            )
        )
    if not kids:
        raise ValueError("no pages")
    pdf.set(tree, f"<< /Type /Pages /Kids [{' '.join(f'{k} 0 R' for k in kids)}] /Count {len(kids)} >>".encode())
    pdf.set(catalog, f"<< /Type /Catalog /Pages {tree} 0 R >>".encode())
    return pdf.output(catalog, _info(pdf, title, producer))


# --------------------------------------------------------------------------- stamping released copies
@dataclass(frozen=True)
class Stamp:
    recipient: str
    released_at: str  # as printed, e.g. "23 Oct 2026 15:42 WAT"
    purpose: str
    code: str
    reference: str
    issuer: str  # e.g. "Syntegra · Abia State"

    def lines(self) -> tuple[str, str]:
        return (
            f"Released to {self.recipient} - {self.released_at} - Purpose: {self.purpose or 'not stated'}",
            f"Release code {self.code} - {self.reference} - {self.issuer}. Check the code in the release register.",
        )


def _overlay(width: float, height: float, stamp: Stamp) -> bytes:
    """One transparent page carrying the stamp: a band along the foot of the page and the code faintly across it."""
    pdf = _Pdf()
    catalog, tree = pdf.reserve(), pdf.reserve()
    font = pdf.add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    bold = pdf.add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")
    gs_band = pdf.add(b"<< /Type /ExtGState /ca 0.86 >>")
    gs_faint = pdf.add(b"<< /Type /ExtGState /ca 0.13 >>")
    size = max(6.0, min(9.0, width / 70))
    band = size * 3.4
    one, two = stamp.lines()
    diag = max(18.0, min(54.0, width / 12))
    ops = [
        f"q /GSb gs 1 1 1 rg 0 0 {width:.2f} {band:.2f} re f Q",
        f"q 0.05 0.42 0.31 RG 1 w 0 {band:.2f} m {width:.2f} {band:.2f} l S Q",
        f"BT 0.08 0.11 0.10 rg /F2 {size:.2f} Tf 1 0 0 1 {size * 1.6:.2f} {band - size * 1.45:.2f} Tm {_text(one)} Tj ET",
        f"BT 0.08 0.11 0.10 rg /F1 {size:.2f} Tf 1 0 0 1 {size * 1.6:.2f} {band - size * 2.75:.2f} Tm {_text(two)} Tj ET",
        f"q /GSf gs BT 0.05 0.42 0.31 rg /F2 {diag:.2f} Tf 0.7071 0.7071 -0.7071 0.7071 {width * 0.16:.2f} {height * 0.22:.2f} Tm {_text(stamp.code + ' - ' + stamp.recipient)} Tj ET Q",
    ]
    content = pdf.stream("", "\n".join(ops).encode("latin-1"))
    page = pdf.add(
        f"<< /Type /Page /Parent {tree} 0 R /MediaBox [0 0 {width:.2f} {height:.2f}] /Resources << /Font << /F1 {font} 0 R /F2 {bold} 0 R >> /ExtGState << /GSb {gs_band} 0 R /GSf {gs_faint} 0 R >> >> /Contents {content} 0 R >>".encode()
    )
    pdf.set(tree, f"<< /Type /Pages /Kids [{page} 0 R] /Count 1 >>".encode())
    pdf.set(catalog, f"<< /Type /Catalog /Pages {tree} 0 R >>".encode())
    return pdf.output(catalog, _info(pdf, "stamp", "Syntegra"))


def stamp_pdf(data: bytes, stamp: Stamp) -> bytes:
    """A copy of the PDF with the stamp on every page; the input is not modified."""
    from pypdf import PdfReader, PdfWriter, Transformation

    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted:
            reader.decrypt("")
        writer = PdfWriter()
        for source in reader.pages:
            page = writer.add_page(source)
            box = page.mediabox
            w, h = float(box.width), float(box.height)
            rotate = int(page.get("/Rotate", 0) or 0) % 360
            vw, vh = (h, w) if rotate in (90, 270) else (w, h)
            over = PdfReader(io.BytesIO(_overlay(vw, vh, stamp))).pages[0]
            t = Transformation()
            if rotate == 90:
                t = t.rotate(-90).translate(0, vw)
            elif rotate == 180:
                t = t.rotate(180).translate(vw, vh)
            elif rotate == 270:
                t = t.rotate(90).translate(vh, 0)
            page.merge_transformed_page(over, t.translate(float(box.left), float(box.bottom)))
        writer.add_metadata({"/Producer": "Syntegra stamped release", "/Subject": f"Release {stamp.code}"})
        out = io.BytesIO()
        writer.write(out)
        return out.getvalue()
    except Exception:  # a damaged or unusual PDF: stamp a rendered copy of its pages instead
        from syntegra.records.text import page_images

        pages = page_images(data, "application/pdf")
        if not pages:
            raise
        return stamp_pdf(
            searchable_pdf((Page(i, d) for i, d in pages), title=stamp.reference, producer="Syntegra"), stamp
        )


def images_to_pdf(data: bytes, mime: str, title: str) -> bytes:
    """A JPEG, PNG or TIFF scan placed on PDF pages (one per frame), so that it can be stamped."""
    from syntegra.records.text import page_images

    pages = page_images(data, mime)
    if not pages:
        raise ValueError("not an image")
    return searchable_pdf(
        (Page(i.convert("RGB") if i.mode not in ("L", "RGB") else i, d) for i, d in pages),
        title=title,
        producer="Syntegra",
        quality=82,
    )
