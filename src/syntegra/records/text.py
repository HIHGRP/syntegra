"""Text of a stored document for the search index (CR-007, FR-DOC-203).

Sources, best first: the PDF's own text layer (searchable PDFs from scanners or word processors); plain text files;
OCR of page images with Tesseract; and the transcription typed at upload. The scan itself stays the record — the text
only makes it findable and exportable.

OCR runs in-process with Python wheels that carry their own native libraries, so it needs no system packages (the
RHEL UBI image has none for it): ``tesserocr`` (Tesseract 5 and Leptonica), ``pypdfium2`` to render scanned PDF pages
and Pillow to read JPEG, PNG and multi-page TIFF. Only the English language data (``eng.traineddata``) is needed on
disk: ``SYNTEGRA_TESSDATA_DIR`` (set in the production image) or the usual system locations.
"""

from __future__ import annotations

import io
import os
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PDF = "application/pdf"
IMAGES = {"image/jpeg", "image/png", "image/tiff"}
TEXT = "text/plain"
ALLOWED = {PDF, TEXT, *IMAGES}
EXTENSIONS = {PDF: "pdf", TEXT: "txt", "image/jpeg": "jpg", "image/png": "png", "image/tiff": "tif"}
MAX_OCR_PAGES = 40
MIN_LAYER_CHARS = 40  # a PDF with less text than this per page is treated as a scan


@dataclass(frozen=True)
class OcrWord:
    text: str
    box: tuple[int, int, int, int]  # left, top, right, bottom in page pixels


@dataclass(frozen=True)
class OcrPage:
    """One page as OCR saw it: the greyscale image, its resolution and the words with their positions — enough to
    lay the text invisibly over the image in a searchable PDF (CR-008)."""

    image: Any  # PIL.Image.Image, greyscale
    dpi: float
    words: tuple[OcrWord, ...]
    text: str


@dataclass(frozen=True)
class Extracted:
    text: str
    source: str  # text_source enum: none, pdf_text_layer, text_file, transcription, …, ocr
    pages: int
    ocr: tuple[OcrPage, ...] = ()  # the OCR'd pages, when the text came from OCR


def sniff(data: bytes) -> str | None:
    """The real type of an upload from its first bytes (the browser's content type is not trusted)."""
    head = data[:16]
    if head.startswith(b"%PDF-"):
        return PDF
    if head.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if head[:4] in (b"II*\x00", b"MM\x00*"):
        return "image/tiff"
    try:
        sample = data[:4096].decode("utf-8")
    except UnicodeDecodeError:
        return None
    printable = sum(ch.isprintable() or ch in "\r\n\t" for ch in sample)
    return TEXT if sample and printable / len(sample) > 0.97 else None


TESSDATA_DIRS = (
    "/usr/share/tesseract-ocr/5/tessdata",
    "/usr/share/tesseract-ocr/4.00/tessdata",
    "/usr/share/tesseract/tessdata",
    "/usr/share/tessdata",
    "/usr/local/share/tessdata",
)
OCR_DPI = 200
MAX_OCR_PIXELS = 40_000_000  # larger pages are scaled down first: OCR time grows with the area


def tessdata_dir() -> str | None:
    """The directory holding ``eng.traineddata``, or None."""
    for d in (os.environ.get("SYNTEGRA_TESSDATA_DIR"), os.environ.get("TESSDATA_PREFIX"), *TESSDATA_DIRS):
        if d and (Path(d) / "eng.traineddata").is_file():
            return d
    return None


def ocr_available() -> bool:
    if tessdata_dir() is None:
        return False
    try:
        import tesserocr  # noqa: F401
    except ImportError:
        return False
    return True


def ocr_pages(images: Iterable[tuple[Any, float]]) -> list[OcrPage]:
    """OCR each (Pillow image, dpi): its text and the position of every word."""
    import tesserocr
    from PIL import Image

    out: list[OcrPage] = []
    with tesserocr.PyTessBaseAPI(path=tessdata_dir(), lang="eng", psm=tesserocr.PSM.AUTO) as api:
        for img, dpi in images:
            page = img.convert("L")
            if page.width * page.height > MAX_OCR_PIXELS:
                scale = (MAX_OCR_PIXELS / (page.width * page.height)) ** 0.5
                page = page.resize((int(page.width * scale), int(page.height * scale)), Image.Resampling.LANCZOS)
                dpi *= scale
            api.SetImage(page)
            api.Recognize()
            words: list[OcrWord] = []
            level = tesserocr.RIL.WORD
            for r in tesserocr.iterate_level(api.GetIterator(), level):
                word = (r.GetUTF8Text(level) or "").strip()
                box = r.BoundingBox(level)
                if word and box:
                    words.append(OcrWord(word, tuple(int(v) for v in box)))  # type: ignore[arg-type]
            out.append(OcrPage(page, dpi, tuple(words), api.GetUTF8Text() or ""))
    return out


def page_images(data: bytes, mime: str) -> list[tuple[Any, float]]:
    """The pages of a scan as (Pillow image, dpi): PDF pages rendered at 200 dpi; image frames as they are."""
    from PIL import Image, ImageSequence, UnidentifiedImageError

    if mime == PDF:
        import pypdfium2 as pdfium

        try:
            pdf = pdfium.PdfDocument(data)
        except pdfium.PdfiumError:
            return []
        try:
            return [
                (pdf[i].render(scale=OCR_DPI / 72, grayscale=True).to_pil(), float(OCR_DPI))
                for i in range(min(len(pdf), MAX_OCR_PAGES))
            ]
        finally:
            pdf.close()
    try:
        with Image.open(io.BytesIO(data)) as img:
            out = []
            for _, f in zip(range(MAX_OCR_PAGES), ImageSequence.Iterator(img), strict=False):
                dpi = f.info.get("dpi", (OCR_DPI, OCR_DPI))[0] or OCR_DPI
                out.append((f.copy(), float(dpi if 50 <= dpi <= 1200 else OCR_DPI)))
            return out
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        return []


def _ocr(data: bytes, mime: str) -> list[OcrPage]:
    if not ocr_available():
        return []
    images = page_images(data, mime)
    return ocr_pages(images) if images else []


def extract(data: bytes, mime: str, transcription: str = "") -> Extracted:
    text, source, pages = "", "none", 1
    ocr: list[OcrPage] = []
    if mime == PDF:
        from pypdf import PdfReader

        try:
            reader = PdfReader(io.BytesIO(data))
            pages = len(reader.pages)
            text = "\n\f".join((page.extract_text() or "") for page in reader.pages)
        except Exception:
            text = ""
        if len(text.strip()) >= MIN_LAYER_CHARS * max(1, pages) // 2:
            source = "pdf_text_layer"
        else:
            ocr = _ocr(data, mime)
            text = "\n\f".join(p.text for p in ocr)
            source = "ocr" if text.strip() else "none"
    elif mime == TEXT:
        text, source = data.decode("utf-8", "replace"), "text_file"
    elif mime in IMAGES:
        ocr = _ocr(data, mime)
        text = "\n\f".join(p.text for p in ocr)
        source = "ocr" if text.strip() else "none"
    transcription = (transcription or "").strip()
    if transcription:
        if source == "none":
            text, source = transcription, "transcription"
        else:
            text = f"{text}\n\n{transcription}"
            source = "pdf_text_layer_and_transcription" if source == "pdf_text_layer" else source
    if ocr and mime in IMAGES:
        pages = len(ocr)
    return Extracted(text=_clean(text), source=source, pages=pages, ocr=tuple(ocr) if source == "ocr" else ())


def _clean(text: str) -> str:
    lines = [" ".join(line.split()) for line in text.replace("\r", "").split("\n")]
    out: list[str] = []
    for line in lines:
        if line or (out and out[-1]):
            out.append(line)
    return "\n".join(out).strip()[:4_000_000]
