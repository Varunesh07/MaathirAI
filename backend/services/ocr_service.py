import easyocr
import fitz  # PyMuPDF
import os
import tempfile
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from services.embedding_service import embed_chunks
from services.vector_store import add_documents

# Initialize once at import time — avoids reloading weights on every request
# gpu=False is safe for MVP. Set gpu=True if CUDA is available.
reader = easyocr.Reader(["en"], gpu=False)


def extract_text_from_image(image_bytes: bytes) -> str:
    """Extract raw text from an image and immediately store its chunks in ChromaDB.
    The function returns the concatenated raw text for backward compatibility.
    """
    # mag_ratio=2.5 upscales image for tiny text. paragraph=True merges disconnected words.
    results = reader.readtext(image_bytes, detail=0, paragraph=True, mag_ratio=2.5)
    raw_text = " ".join(results)
    chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_text(raw_text)
    embeddings = embed_chunks(chunks)
    add_documents(collection_name="medical_reports", documents=chunks, embeddings=embeddings)
    return raw_text

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract raw text from a PDF, chunk, embed, and store in ChromaDB.
    Returns the concatenated raw text for downstream use.
    """
    all_text = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    # 1. Try to extract native embedded text first
    for page in doc:
        all_text.append(page.get_text())
    
    combined_text = " ".join(all_text).strip()
    
    # If we got meaningful text out of it, it's a digital PDF
    if len(combined_text) > 50:
        # Chunk, embed and store
        chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_text(combined_text)
        embeddings = embed_chunks(chunks)
        add_documents(collection_name="medical_reports", documents=chunks, embeddings=embeddings)
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
