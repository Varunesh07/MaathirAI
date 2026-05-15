import os
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

# Load the model once at import time for efficiency
_MODEL_NAME = "all-MiniLM-L6-v2"
_model = SentenceTransformer(_MODEL_NAME)

def embed_chunks(chunks: List[str]) -> List[np.ndarray]:
    """Convert a list of text chunks into embeddings.

    Args:
        chunks: List of textual chunks (already split).
    Returns:
        List of NumPy arrays representing the embeddings.
    """
    # SentenceTransformer returns a NumPy matrix (N x dim)
    embeddings = _model.encode(chunks, normalize_embeddings=True, show_progress_bar=False)
    # Ensure each embedding is a 1‑D np.ndarray
    return [np.array(vec) for vec in embeddings]
