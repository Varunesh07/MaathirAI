import easyocr
import fitz  # PyMuPDF
import os
import tempfile
from pathlib import Path

# Initialize once at import time — avoids reloading weights on every request
# gpu=False is safe for MVP. Set gpu=True if CUDA is available.
reader = easyocr.Reader(["en"], gpu=False)


def extract_text_from_file(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        return _extract_from_pdf(file_path)
    elif ext in [".png", ".jpg", ".jpeg"]:
        return _extract_from_image(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def _extract_from_image(image_path: str) -> str:
    # mag_ratio=2.5 upscales image for tiny text. paragraph=True merges disconnected words.
    results = reader.readtext(image_path, detail=0, paragraph=True, mag_ratio=2.5)
    return " ".join(results)


def _extract_from_pdf(pdf_path: str) -> str:
    all_text = []
    doc = fitz.open(pdf_path)

    # 1. Try to extract native embedded text first
    for page in doc:
        all_text.append(page.get_text())
    
    combined_text = " ".join(all_text).strip()
    
    # If we got meaningful text out of it, it's a digital PDF
    if len(combined_text) > 50:
        doc.close()
        return combined_text

    # 2. Scanned PDF fallback: render pages to images and run OCR
    all_text = []
    with tempfile.TemporaryDirectory() as tmp_dir:
        for page_num in range(len(doc)):
            page = doc[page_num]
            # 150 DPI is a good balance of speed vs accuracy
            pix = page.get_pixmap(dpi=150)
            img_path = os.path.join(tmp_dir, f"page_{page_num}.png")
            pix.save(img_path)
            page_text = _extract_from_image(img_path)
            all_text.append(page_text)

    doc.close()
    return " ".join(all_text)
