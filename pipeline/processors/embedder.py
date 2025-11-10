"""
Embedder for creating vector embeddings from text chunks using sentence-transformers.

Supports batch processing, progress bars, and persistent ChromaDB storage.
"""

import logging
from typing import List, Dict, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np
from tqdm import tqdm

logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

DEFAULT_MODEL = "all-MiniLM-L6-v2"  # Fast, good quality, 384 dimensions
DEFAULT_BATCH_SIZE = 32
DEFAULT_DB_PATH = "data/vector_db"


# ============================================================================
# Custom Exceptions
# ============================================================================


class EmbedderError(Exception):
    """Custom exception for embedder errors."""

    pass


# ============================================================================
# Embedding Generation
# ============================================================================


def generate_embeddings(
    chunks: List[Dict],
    model_name: str = DEFAULT_MODEL,
    batch_size: int = DEFAULT_BATCH_SIZE,
    normalize: bool = True,
) -> List[Dict]:
    """
    Generate vector embeddings for each chunk using sentence-transformers.

    Args:
        chunks: Output from chunk_document()
        model_name: Sentence-transformers model name
        batch_size: Batch size for processing (default 32)
        normalize: Normalize embeddings to unit length (default True)

    Returns:
        Same chunks with added 'embedding' field (list of floats)

    Example:
        >>> chunks = chunk_document(parsed_bill)
        >>> chunks_with_embeddings = generate_embeddings(chunks)
        >>> print(f"Embedding dimension: {len(chunks_with_embeddings[0]['embedding'])}")
        384
    """
    if not chunks:
        logger.warning("No chunks to embed")
        return []

    logger.info(f"Generating embeddings for {len(chunks)} chunks using {model_name}")

    try:
        # Load model
        model = SentenceTransformer(model_name)
        logger.info(
            f"Loaded model: {model_name} (dimension: {model.get_sentence_embedding_dimension()})"
        )

        # Extract texts
        texts = [chunk["text"] for chunk in chunks]

        # Generate embeddings in batches with progress bar
        all_embeddings = []

        for i in tqdm(range(0, len(texts), batch_size), desc="Embedding batches"):
            batch_texts = texts[i : i + batch_size]
            batch_embeddings = model.encode(
                batch_texts,
                batch_size=batch_size,
                show_progress_bar=False,
                normalize_embeddings=normalize,
            )
            all_embeddings.extend(batch_embeddings)

        # Add embeddings to chunks
        for i, chunk in enumerate(chunks):
            # Convert numpy array to list for JSON serialization
            embedding = (
                all_embeddings[i].tolist()
                if hasattr(all_embeddings[i], "tolist")
                else list(all_embeddings[i])
            )
            chunk["embedding"] = embedding
            chunk["embedding_model"] = model_name
            chunk["embedding_dimension"] = len(embedding)

        logger.info(f"Successfully generated {len(all_embeddings)} embeddings")
        return chunks

    except Exception as e:
        logger.error(f"Failed to generate embeddings: {e}")
        raise EmbedderError(f"Failed to generate embeddings: {e}") from e


# ============================================================================
# Vector Store Setup
# ============================================================================


def setup_vector_store(
    chunks: List[Dict],
    collection_name: str = "bill_chunks",
    db_path: str = DEFAULT_DB_PATH,
    distance_metric: str = "cosine",
) -> chromadb.Collection:
    """
    Store chunks with embeddings in ChromaDB vector database.

    Args:
        chunks: Chunks with 'embedding' field (from generate_embeddings)
        collection_name: Name of ChromaDB collection
        db_path: Path to persistent database directory
        distance_metric: Distance metric ("cosine", "l2", "ip")

    Returns:
        ChromaDB collection object

    Example:
        >>> chunks_with_embeddings = generate_embeddings(chunks)
        >>> collection = setup_vector_store(chunks_with_embeddings)
        >>> print(f"Stored {collection.count()} chunks")
    """
    if not chunks:
        raise EmbedderError("No chunks to store")

    # Ensure all chunks have embeddings
    if not all("embedding" in chunk for chunk in chunks):
        raise EmbedderError(
            "Not all chunks have embeddings. Run generate_embeddings() first."
        )

    logger.info(f"Setting up vector store at {db_path}")

    try:
        # Create directory if it doesn't exist
        Path(db_path).mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client with persistent storage
        client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False, allow_reset=True),
        )

        # Get or create collection
        # Delete if exists to avoid duplicates (can be changed to get_or_create for append behavior)
        try:
            client.delete_collection(name=collection_name)
            logger.info(f"Deleted existing collection: {collection_name}")
        except:
            pass

        collection = client.create_collection(
            name=collection_name,
            metadata={
                "description": "Bill text chunks with embeddings",
                "hnsw:space": distance_metric,  # cosine, l2, or ip (inner product)
            },
        )

        logger.info(f"Created collection: {collection_name}")

        # Prepare data for ChromaDB
        ids = [chunk["id"] for chunk in chunks]
        documents = [chunk["text"] for chunk in chunks]
        embeddings = [chunk["embedding"] for chunk in chunks]

        metadatas = [
            {
                "bill_number": chunk.get("bill_number", ""),
                "section": chunk.get("section", ""),
                "section_title": chunk.get("section_title", ""),
                "start_char": chunk.get("start_char", 0),
                "end_char": chunk.get("end_char", 0),
                "page": chunk.get("page") if chunk.get("page") is not None else -1,
                "tokens": chunk.get("tokens", 0),
                "embedding_model": chunk.get("embedding_model", ""),
                "embedding_dimension": chunk.get("embedding_dimension", 0),
            }
            for chunk in chunks
        ]

        # Add to collection in batches (ChromaDB has batch size limits)
        batch_size = 5000  # ChromaDB's default max batch size
        total_batches = (len(chunks) + batch_size - 1) // batch_size

        for i in tqdm(
            range(0, len(chunks), batch_size),
            desc="Storing chunks",
            total=total_batches,
        ):
            batch_ids = ids[i : i + batch_size]
            batch_docs = documents[i : i + batch_size]
            batch_embeddings = embeddings[i : i + batch_size]
            batch_metadatas = metadatas[i : i + batch_size]

            collection.add(
                ids=batch_ids,
                documents=batch_docs,
                embeddings=batch_embeddings,
                metadatas=batch_metadatas,
            )

        logger.info(f"Successfully stored {collection.count()} chunks in vector store")
        return collection

    except Exception as e:
        logger.error(f"Failed to setup vector store: {e}")
        raise EmbedderError(f"Failed to setup vector store: {e}") from e


# ============================================================================
# Vector Store Query
# ============================================================================


def query_vector_store(
    query_text: str,
    collection: chromadb.Collection,
    n_results: int = 5,
    model_name: str = DEFAULT_MODEL,
    filter_metadata: Optional[Dict] = None,
) -> Dict:
    """
    Query the vector store for similar chunks.

    Args:
        query_text: Search query
        collection: ChromaDB collection
        n_results: Number of results to return
        model_name: Model used for query embedding (must match stored embeddings)
        filter_metadata: Optional metadata filter (e.g., {"section": "1"})

    Returns:
        Dictionary with:
            - ids: List of chunk IDs
            - documents: List of chunk texts
            - metadatas: List of metadata dicts
            - distances: List of similarity distances

    Example:
        >>> results = query_vector_store("healthcare reform", collection, n_results=3)
        >>> for doc, dist in zip(results['documents'], results['distances']):
        ...     print(f"Distance: {dist:.4f} - {doc[:100]}")
    """
    logger.info(f"Querying vector store: '{query_text}' (top {n_results})")

    try:
        # Generate query embedding
        model = SentenceTransformer(model_name)
        query_embedding = model.encode([query_text], normalize_embeddings=True)[
            0
        ].tolist()

        # Query collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata,
        )

        logger.info(f"Found {len(results['ids'][0])} results")

        return {
            "ids": results["ids"][0],
            "documents": results["documents"][0],
            "metadatas": results["metadatas"][0],
            "distances": results["distances"][0],
        }

    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise EmbedderError(f"Query failed: {e}") from e


# ============================================================================
# Utility Functions
# ============================================================================


def load_vector_store(
    collection_name: str = "bill_chunks", db_path: str = DEFAULT_DB_PATH
) -> chromadb.Collection:
    """
    Load an existing vector store.

    Args:
        collection_name: Name of collection to load
        db_path: Path to database

    Returns:
        ChromaDB collection

    Raises:
        EmbedderError: If collection doesn't exist
    """
    try:
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_collection(name=collection_name)
        logger.info(
            f"Loaded collection '{collection_name}' with {collection.count()} documents"
        )
        return collection
    except Exception as e:
        logger.error(f"Failed to load collection: {e}")
        raise EmbedderError(
            f"Failed to load collection '{collection_name}': {e}"
        ) from e


def get_collection_stats(collection: chromadb.Collection) -> Dict:
    """
    Get statistics about a collection.

    Args:
        collection: ChromaDB collection

    Returns:
        Dictionary with collection stats
    """
    count = collection.count()

    # Sample metadata to get model info
    sample = collection.peek(limit=1)
    model_info = {}

    if sample["metadatas"]:
        metadata = sample["metadatas"][0]
        model_info = {
            "embedding_model": metadata.get("embedding_model", "unknown"),
            "embedding_dimension": metadata.get("embedding_dimension", 0),
        }

    return {"name": collection.name, "total_chunks": count, **model_info}


# ============================================================================
# Main / Testing
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Test data (simulating chunked bill)
    test_chunks = [
        {
            "id": "chunk_0",
            "text": "SEC. 1. SHORT TITLE. This Act may be cited as the Healthcare Reform Act of 2024.",
            "section": "1",
            "section_title": "SHORT TITLE",
            "start_char": 0,
            "end_char": 80,
            "page": 1,
            "tokens": 18,
        },
        {
            "id": "chunk_1",
            "text": "SEC. 2. DEFINITIONS. In this Act, the term 'healthcare provider' means any licensed medical professional.",
            "section": "2",
            "section_title": "DEFINITIONS",
            "start_char": 80,
            "end_char": 187,
            "page": 1,
            "tokens": 22,
        },
        {
            "id": "chunk_2",
            "text": "SEC. 3. EDUCATION FUNDING. The Secretary shall allocate funds for education programs in underserved areas.",
            "section": "3",
            "section_title": "EDUCATION FUNDING",
            "start_char": 187,
            "end_char": 294,
            "page": 1,
            "tokens": 19,
        },
    ]

    print("=" * 80)
    print("Testing Embedder")
    print("=" * 80)

    try:
        # Step 1: Generate embeddings
        print("\n📊 Step 1: Generating embeddings...")
        chunks_with_embeddings = generate_embeddings(
            test_chunks, model_name=DEFAULT_MODEL, batch_size=32
        )

        print(f"✅ Generated embeddings for {len(chunks_with_embeddings)} chunks")
        print(
            f"   Embedding dimension: {chunks_with_embeddings[0]['embedding_dimension']}"
        )

        # Step 2: Setup vector store
        print("\n💾 Step 2: Setting up vector store...")
        collection = setup_vector_store(
            chunks_with_embeddings,
            collection_name="test_bills",
            db_path="data/test_vector_db",
        )

        print(f"✅ Stored {collection.count()} chunks in vector store")

        # Step 3: Query vector store
        print("\n🔍 Step 3: Querying vector store...")

        queries = [
            "healthcare and medical providers",
            "education and schools",
            "short title of the act",
        ]

        for query in queries:
            print(f"\n  Query: '{query}'")
            results = query_vector_store(
                query, collection, n_results=2, model_name=DEFAULT_MODEL
            )

            for i, (doc, dist, meta) in enumerate(
                zip(results["documents"], results["distances"], results["metadatas"]), 1
            ):
                print(
                    f"    {i}. [Distance: {dist:.4f}] Section {meta['section']}: {doc[:80]}..."
                )

        # Step 4: Collection stats
        print("\n📈 Step 4: Collection statistics...")
        stats = get_collection_stats(collection)
        print(f"   Collection: {stats['name']}")
        print(f"   Total chunks: {stats['total_chunks']}")
        print(f"   Model: {stats.get('embedding_model', 'N/A')}")
        print(f"   Dimension: {stats.get('embedding_dimension', 'N/A')}")

        print("\n" + "=" * 80)
        print("✅ All tests completed successfully!")
        print("=" * 80)

    except EmbedderError as e:
        print(f"\n❌ Error: {e}")
