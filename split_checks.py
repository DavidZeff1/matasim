#!/usr/bin/env python3
"""Split a multi-page Hebrew check PDF into one PDF per check (page).

The recipient name is extracted from the line ``תשלום זה ניתן עבור: <name>``
on each page via Tesseract OCR (Hebrew). Each page becomes its own PDF named
after the recipient; duplicates get a numeric suffix (e.g. ``פלוני (2).pdf``).
"""

from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path

import fitz  # PyMuPDF
import pytesseract
from PIL import Image


def _configure_tesseract() -> None:
    """Point pytesseract at the right binary when it isn't on PATH.

    Needed on Windows (default installer doesn't add to PATH) and on macOS
    when launched via Finder (.command files inherit a minimal PATH that
    excludes /opt/homebrew/bin and /usr/local/bin)."""
    import os, shutil, sys
    if shutil.which("tesseract"):
        return
    if sys.platform.startswith("win"):
        candidates = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
        ]
    elif sys.platform == "darwin":
        candidates = [
            "/opt/homebrew/bin/tesseract",   # Apple Silicon Homebrew
            "/usr/local/bin/tesseract",      # Intel Homebrew
            "/opt/local/bin/tesseract",      # MacPorts
        ]
    else:
        candidates = []
    for path in candidates:
        if os.path.isfile(path):
            pytesseract.pytesseract.tesseract_cmd = path
            return


_configure_tesseract()

RECIPIENT_LABEL = "תשלום זה ניתן עבור"
# Common OCR fragments that bleed in from the next label ("שם המוטב",
# "כתובת המוטב") when the name line wraps. Trimmed from the tail of the name.
TRAILING_NOISE = ("מו", "כת", "שם", "המ")
ILLEGAL_FS_CHARS = re.compile(r'[\\/:*?"<>|\x00-\x1f]')


def ocr_page(page: fitz.Page, dpi: int) -> str:
    pix = page.get_pixmap(dpi=dpi)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    return pytesseract.image_to_string(img, lang="heb")


def extract_recipient(ocr_text: str) -> str | None:
    for raw_line in ocr_page_lines(ocr_text):
        if RECIPIENT_LABEL in raw_line:
            _, _, after = raw_line.partition(":")
            return clean_name(after)
    return None


def ocr_page_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def clean_name(raw: str) -> str:
    name = raw.strip().replace("|", " ")
    name = re.sub(r"\s+", " ", name).strip()
    # Drop a short trailing token if it matches a known label fragment.
    tokens = name.split(" ")
    while len(tokens) > 1 and tokens[-1] in TRAILING_NOISE:
        tokens.pop()
    return " ".join(tokens)


def safe_filename(name: str) -> str:
    cleaned = ILLEGAL_FS_CHARS.sub("", name).strip().rstrip(".")
    return cleaned or "unknown"


def split_pdf(src: Path, out_dir: Path, dpi: int) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(src)

    written: list[Path] = []
    used: dict[str, int] = {}
    for i, page in enumerate(doc):
        text = ocr_page(page, dpi=dpi)
        name = extract_recipient(text) or f"unknown_page_{i + 1}"
        print(f"page {i + 1}: {name}")

        base = safe_filename(name)
        count = used.get(base, 0)
        used[base] = count + 1
        filename = f"{base}.pdf" if count == 0 else f"{base} ({count + 1}).pdf"
        out_path = out_dir / filename

        sub = fitz.open()
        sub.insert_pdf(doc, from_page=i, to_page=i)
        sub.save(out_path)
        sub.close()
        written.append(out_path)

    doc.close()
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path, help="Path to source PDF")
    parser.add_argument(
        "-o", "--out-dir", type=Path, default=Path("split"),
        help="Directory for output PDFs (default: ./split)",
    )
    parser.add_argument(
        "--dpi", type=int, default=300, help="Render DPI for OCR (default: 300)",
    )
    args = parser.parse_args()

    if not args.pdf.is_file():
        print(f"error: {args.pdf} not found", file=sys.stderr)
        return 1

    written = split_pdf(args.pdf, args.out_dir, args.dpi)
    print(f"\nWrote {len(written)} file(s) to {args.out_dir}:")
    for p in written:
        print(f"  {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
