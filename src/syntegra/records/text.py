"""Text of a stored document for the search index (CR-007, FR-DOC-203).

Sources, best first: the PDF's own text layer (searchable PDFs from scanners or word processors); plain text files;
OCR of page images with Tesseract when it is installed (scanned PDFs are rasterised with ``pdftoppm``); and the
transcription typed at upload. The scan itself stays the record — the text only makes it findable and exportable.
"""

from __future__ import annotations

import io
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

PDF = "application/pdf"
IMAGES = {"image/jpeg", "image/png", "image/tiff"}
TEXT = "text/plain"
ALLOWED = {PDF, TEXT, *IMAGES}
EXTENSIONS = {PDF: "pdf", TEXT: "txt", "image/jpeg": "jpg", "image/png": "png", "image/tiff": "tif"}
MAX_OCR_PAGES = 40
MIN_LAYER_CHARS = 40  # a PDF with less text than this per page is treated as a scan


@dataclass(frozen=True)
class Extracted:
    text: str
    source: str  # text_source enum: none, pdf_text_layer, text_file, transcription, …, ocr
    pages: int


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


def ocr_available() -> bool:
    return shutil.which("tesseract") is not None


def _ocr_image(path: Path) -> str:
    exe = shutil.which("tesseract")
    if not exe:
        return ""
    out = subprocess.run(  # noqa: S603
        [exe, str(path), "stdout", "-l", "eng", "--psm", "3"], capture_output=True, timeout=120, check=False
    )
    return out.stdout.decode("utf-8", "replace") if out.returncode == 0 else ""


def _ocr_pdf(data: bytes, pages: int) -> str:
    exe = shutil.which("pdftoppm")
    if not exe or not ocr_available():
        return ""
    with tempfile.TemporaryDirectory(prefix="syn-ocr-") as tmp:
        src = Path(tmp) / "in.pdf"
        src.write_bytes(data)
        subprocess.run(  # noqa: S603
            [exe, "-r", "200", "-gray", "-png", "-l", str(min(pages, MAX_OCR_PAGES)), str(src), str(Path(tmp) / "p")],
            capture_output=True,
            timeout=300,
            check=False,
        )
        return "\n\f".join(_ocr_image(p) for p in sorted(Path(tmp).glob("p*.png")))


def extract(data: bytes, mime: str, transcription: str = "") -> Extracted:
    text, source, pages = "", "none", 1
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
            text = _ocr_pdf(data, pages)
            source = "ocr" if text.strip() else "none"
    elif mime == TEXT:
        text, source = data.decode("utf-8", "replace"), "text_file"
    elif mime in IMAGES:
        with tempfile.TemporaryDirectory(prefix="syn-ocr-") as tmp:
            p = Path(tmp) / f"in.{EXTENSIONS[mime]}"
            p.write_bytes(data)
            text = _ocr_image(p)
        source = "ocr" if text.strip() else "none"
    transcription = (transcription or "").strip()
    if transcription:
        if source == "none":
            text, source = transcription, "transcription"
        else:
            text = f"{text}\n\n{transcription}"
            source = "pdf_text_layer_and_transcription" if source == "pdf_text_layer" else source
    return Extracted(text=_clean(text), source=source, pages=pages)


def _clean(text: str) -> str:
    lines = [" ".join(line.split()) for line in text.replace("\r", "").split("\n")]
    out: list[str] = []
    for line in lines:
        if line or (out and out[-1]):
            out.append(line)
    return "\n".join(out).strip()[:4_000_000]
