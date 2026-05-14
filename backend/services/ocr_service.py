import easyocr
import fitz  # PyMuPDF
import os
import tempfile
from pathlib import Path

# Initialize once at import time — avoids reloading weights on every request
# gpu=False is safe for MVP. Set gpu=True if CUDA is available.
reader = easyocr.Reader(["en"], gpu=False)


def extract_text_from_image(image_bytes: bytes) -> str:
    # mag_ratio=2.5 upscales image for tiny text. paragraph=True merges disconnected words.
    results = reader.readtext(image_bytes, detail=0, paragraph=True, mag_ratio=2.5)
    return " ".join(results)

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    all_text = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

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
    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(dpi=150)
        # easyocr can take numpy array directly from pixmap
        import numpy as np
        # Convert pixmap to numpy array
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        # Read text
        results = reader.readtext(img, detail=0, paragraph=True, mag_ratio=2.5)
        all_text.append(" ".join(results))

    doc.close()
    return " ".join(all_text)
