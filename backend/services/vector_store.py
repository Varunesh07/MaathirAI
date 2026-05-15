import os
from typing import List
import numpy as np
from chromadb import PersistentClient

# Directory where ChromaDB stores its files
_CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", os.path.join(os.path.dirname(__file__), "..", "chroma_db"))

# Initialise a singleton persistent client (thread‑safe for our simple use‑case)
_client = PersistentClient(path=_CHROMA_DB_PATH)

def get_collection(name: str = "medical_reports"):
    """Retrieve (or create) a collection with the given name.
    
    For this MVP we keep a single global collection; in a multi‑user setup you could
    pass a per‑session identifier instead.
    """
    # Use get_or_create_collection which accepts optional metadata
    return _client.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})

def add_documents(collection_name: str, documents: List[str], embeddings: List[np.ndarray]):
    """Add a batch of documents and their embeddings to the specified collection.
    
    Args:
        collection_name: Name of the Chroma collection (e.g., "medical_reports").
        documents: List of text chunks.
        embeddings: List of NumPy vectors (same length as `documents`).
    """
    collection = get_collection(collection_name)
    # Generate deterministic IDs for each chunk (could be UUIDs; here we use simple index)
    ids = [f"doc_{i}" for i in range(len(documents))]
    # Chroma expects embeddings as list of list/float, not np.ndarray
    emb_list = [vec.tolist() for vec in embeddings]
    collection.add(
        documents=documents,
        embeddings=emb_list,
        ids=ids,
    )

def search(collection_name: str, query: str, top_k: int = 3) -> List[str]:
    """Perform a similarity search in the given collection.
    
    Returns the top‑k matching document texts.
    """
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_emb = model.encode([query], normalize_embeddings=True)[0].tolist()
    collection = get_collection(collection_name)
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=top_k,
        include=['documents']
    )
    # `results['documents']` is a list of list
    return results.get('documents', [[]])[0]

def clear_vector_store(collection_name: str = "medical_reports"):
    """Completely wipe the specified collection from ChromaDB."""
    try:
        _client.delete_collection(name=collection_name)
    except Exception:
        # Collection might not exist yet
        pass
