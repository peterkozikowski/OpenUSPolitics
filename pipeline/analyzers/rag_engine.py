"""
RAG (Retrieval-Augmented Generation) engine with hybrid search.

Combines vector similarity search and BM25 keyword matching for optimal retrieval.
"""

import logging
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
import tiktoken
import numpy as np
from tqdm import tqdm

logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEFAULT_RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
TOKEN_ENCODING = "cl100k_base"
MAX_CONTEXT_TOKENS = 4000


# ============================================================================
# Custom Exceptions
# ============================================================================

class RAGEngineError(Exception):
    """Custom exception for RAG engine errors."""
    pass


# Alias for backward compatibility
RAGError = RAGEngineError


# ============================================================================
# Helper Functions
# ============================================================================

def setup_bm25_index(chunks: List[Dict]) -> Tuple[BM25Okapi, List[Dict]]:
    """
    Create BM25 index for keyword search.

    Args:
        chunks: List of chunk dictionaries

    Returns:
        Tuple of (BM25Okapi index, list of chunks)

    Example:
        >>> bm25, indexed_chunks = setup_bm25_index(chunks)
        >>> scores = bm25.get_scores(["healthcare", "reform"])
    """
    if not chunks:
        raise ValueError("Cannot create BM25 index from empty chunks")

    # Tokenize all chunk texts (simple whitespace tokenization)
    tokenized_corpus = [chunk["text"].lower().split() for chunk in chunks]

    # Create BM25 index
    bm25 = BM25Okapi(tokenized_corpus)

    logger.info(f"Created BM25 index with {len(chunks)} documents")
    return bm25, chunks


def tokenize_query(query: str) -> List[str]:
    """
    Tokenize query for BM25 search.

    Args:
        query: Search query

    Returns:
        List of tokens
    """
    return query.lower().split()


def count_tokens(text: str) -> int:
    """
    Count tokens in text using tiktoken.

    Args:
        text: Text to count

    Returns:
        Number of tokens
    """
    tokenizer = tiktoken.get_encoding(TOKEN_ENCODING)
    return len(tokenizer.encode(text))


def normalize_scores(scores: np.ndarray) -> np.ndarray:
    """
    Normalize scores to [0, 1] range.

    Args:
        scores: Array of scores

    Returns:
        Normalized scores
    """
    if len(scores) == 0:
        return scores

    min_score = np.min(scores)
    max_score = np.max(scores)

    if max_score == min_score:
        return np.ones_like(scores)

    return (scores - min_score) / (max_score - min_score)


# ============================================================================
# RAG Engine
# ============================================================================

class RAGEngine:
    """
    Hybrid RAG engine combining vector similarity and keyword (BM25) search.

    Features:
    - Vector search using sentence-transformers
    - BM25 keyword search
    - Hybrid fusion with configurable weights
    - Optional cross-encoder reranking
    - Context retrieval with token limits
    - Provision-specific search
    """

    def __init__(
        self,
        collection: chromadb.Collection,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
        use_reranker: bool = False,
        reranker_model: str = DEFAULT_RERANKER_MODEL
    ):
        """
        Initialize RAG engine with ChromaDB collection.

        Args:
            collection: ChromaDB collection from embedder
            embedding_model: Sentence-transformer model name
            use_reranker: Whether to use cross-encoder for reranking
            reranker_model: Cross-encoder model for reranking

        Example:
            >>> from processors.embedder import load_vector_store
            >>> collection = load_vector_store("bill_chunks")
            >>> engine = RAGEngine(collection)
        """
        self.collection = collection
        self.embedder = SentenceTransformer(embedding_model)
        self.use_reranker = use_reranker

        if use_reranker:
            self.reranker = CrossEncoder(reranker_model)
            logger.info(f"Loaded reranker: {reranker_model}")
        else:
            self.reranker = None

        # BM25 index (lazy initialization)
        self.bm25 = None
        self.bm25_chunks = None

        # Query cache for performance
        self.query_cache = {}

        logger.info(f"Initialized RAG engine with {collection.count()} chunks")

    def _ensure_bm25_index(self):
        """Ensure BM25 index is initialized (lazy loading)."""
        if self.bm25 is None:
            logger.info("Building BM25 index...")
            all_chunks = self._get_all_chunks()
            self.bm25, self.bm25_chunks = setup_bm25_index(all_chunks)

    def _get_all_chunks(self) -> List[Dict]:
        """Get all chunks from collection."""
        # Get all documents from collection
        results = self.collection.get()

        chunks = []
        for i in range(len(results["ids"])):
            chunks.append({
                "id": results["ids"][i],
                "text": results["documents"][i],
                "metadata": results["metadatas"][i] if results["metadatas"] else {}
            })

        return chunks

    def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        alpha: float = 0.5,
        bill_number: Optional[str] = None
    ) -> List[Dict]:
        """
        Perform hybrid search combining vector similarity and BM25 keyword matching.

        Args:
            query: Search query or question
            top_k: Number of chunks to retrieve
            alpha: Weight for vector search (1-alpha for BM25)
                  0.0 = pure BM25, 1.0 = pure vector, 0.5 = balanced
            bill_number: Optional filter for specific bill

        Returns:
            List of most relevant chunks with scores

        Example:
            >>> results = engine.hybrid_search("healthcare funding", top_k=5, alpha=0.7)
            >>> for chunk in results:
            ...     print(f"Score: {chunk['score']:.4f} - {chunk['text'][:100]}")
        """
        # Check cache
        cache_key = f"{query}:{top_k}:{alpha}:{bill_number}"
        if cache_key in self.query_cache:
            logger.debug("Using cached results")
            return self.query_cache[cache_key]

        logger.info(f"Hybrid search: '{query}' (alpha={alpha}, top_k={top_k})")

        # 1. Vector Search
        vector_results = self._vector_search(query, top_k=top_k*2, bill_number=bill_number)

        # 2. BM25 Keyword Search
        bm25_results = self._bm25_search(query, top_k=top_k*2, bill_number=bill_number)

        # 3. Fusion: Combine scores
        combined_results = self._fuse_results(vector_results, bm25_results, alpha=alpha)

        # 4. Deduplicate and take top_k
        final_results = self._deduplicate_results(combined_results, top_k=top_k)

        # 5. Optional: Rerank with cross-encoder
        if self.use_reranker and self.reranker:
            final_results = self._rerank_results(query, final_results)

        # Cache results
        self.query_cache[cache_key] = final_results

        logger.info(f"Retrieved {len(final_results)} chunks")
        return final_results

    def _vector_search(
        self,
        query: str,
        top_k: int,
        bill_number: Optional[str] = None
    ) -> List[Dict]:
        """Perform vector similarity search."""
        # Embed query
        query_embedding = self.embedder.encode([query], normalize_embeddings=True)[0].tolist()

        # Build filter
        where_filter = {"bill_number": bill_number} if bill_number else None

        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter
        )

        # Format results
        chunks = []
        for i in range(len(results["ids"][0])):
            # Distance to similarity: smaller distance = higher similarity
            # ChromaDB returns L2 or cosine distance
            distance = results["distances"][0][i]
            similarity = 1 / (1 + distance)  # Convert distance to similarity score

            chunks.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "vector_score": similarity,
                "distance": distance
            })

        return chunks

    def _bm25_search(
        self,
        query: str,
        top_k: int,
        bill_number: Optional[str] = None
    ) -> List[Dict]:
        """Perform BM25 keyword search."""
        # Ensure BM25 index exists
        self._ensure_bm25_index()

        # Tokenize query
        query_tokens = tokenize_query(query)

        # Get BM25 scores
        scores = self.bm25.get_scores(query_tokens)

        # Filter by bill_number if specified
        if bill_number:
            filtered_indices = [
                i for i, chunk in enumerate(self.bm25_chunks)
                if chunk.get("metadata", {}).get("bill_number") == bill_number
            ]
            scores = np.array([scores[i] if i in filtered_indices else 0 for i in range(len(scores))])

        # Get top_k indices
        top_indices = np.argsort(scores)[::-1][:top_k]

        # Format results
        chunks = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only include non-zero scores
                chunk = self.bm25_chunks[idx]
                chunks.append({
                    "id": chunk["id"],
                    "text": chunk["text"],
                    "metadata": chunk.get("metadata", {}),
                    "bm25_score": float(scores[idx])
                })

        return chunks

    def _fuse_results(
        self,
        vector_results: List[Dict],
        bm25_results: List[Dict],
        alpha: float
    ) -> List[Dict]:
        """
        Fuse vector and BM25 results with weighted scoring.

        Args:
            vector_results: Results from vector search
            bm25_results: Results from BM25 search
            alpha: Weight for vector search

        Returns:
            Combined results with fused scores
        """
        # Normalize scores
        if vector_results:
            vector_scores = np.array([r.get("vector_score", 0) for r in vector_results])
            vector_scores = normalize_scores(vector_scores)
            for i, result in enumerate(vector_results):
                result["vector_score_norm"] = float(vector_scores[i])

        if bm25_results:
            bm25_scores = np.array([r.get("bm25_score", 0) for r in bm25_results])
            bm25_scores = normalize_scores(bm25_scores)
            for i, result in enumerate(bm25_results):
                result["bm25_score_norm"] = float(bm25_scores[i])

        # Combine results
        combined = {}

        # Add vector results
        for result in vector_results:
            chunk_id = result["id"]
            combined[chunk_id] = {
                **result,
                "final_score": alpha * result.get("vector_score_norm", 0)
            }

        # Add/update with BM25 results
        for result in bm25_results:
            chunk_id = result["id"]
            if chunk_id in combined:
                # Update score
                combined[chunk_id]["final_score"] += (1 - alpha) * result.get("bm25_score_norm", 0)
                combined[chunk_id]["bm25_score"] = result.get("bm25_score", 0)
                combined[chunk_id]["bm25_score_norm"] = result.get("bm25_score_norm", 0)
            else:
                combined[chunk_id] = {
                    **result,
                    "vector_score": 0,
                    "vector_score_norm": 0,
                    "final_score": (1 - alpha) * result.get("bm25_score_norm", 0)
                }

        return list(combined.values())

    def _deduplicate_results(self, results: List[Dict], top_k: int) -> List[Dict]:
        """Deduplicate and sort results by score."""
        # Sort by final score
        sorted_results = sorted(results, key=lambda x: x.get("final_score", 0), reverse=True)

        # Take top_k
        return sorted_results[:top_k]

    def _rerank_results(self, query: str, results: List[Dict]) -> List[Dict]:
        """Rerank results using cross-encoder."""
        if not results:
            return results

        logger.info("Reranking with cross-encoder...")

        # Prepare pairs for cross-encoder
        pairs = [[query, result["text"]] for result in results]

        # Get reranking scores
        rerank_scores = self.reranker.predict(pairs)

        # Update results with rerank scores
        for i, result in enumerate(results):
            result["rerank_score"] = float(rerank_scores[i])

        # Sort by rerank score
        reranked = sorted(results, key=lambda x: x["rerank_score"], reverse=True)

        return reranked

    def retrieve_context(
        self,
        bill_number: str,
        query: str,
        max_tokens: int = MAX_CONTEXT_TOKENS,
        alpha: float = 0.5
    ) -> str:
        """
        Retrieve relevant context for a specific query with token limit.

        Args:
            bill_number: Filter to specific bill
            query: What to search for
            max_tokens: Maximum context length in tokens
            alpha: Hybrid search weight

        Returns:
            Formatted context string for LLM prompt

        Example:
            >>> context = engine.retrieve_context("H.R. 1234", "funding provisions", max_tokens=2000)
            >>> print(context)
            Section 1 - SHORT TITLE:
            ...
        """
        logger.info(f"Retrieving context for '{query}' from {bill_number}")

        # Perform hybrid search
        results = self.hybrid_search(
            query=query,
            top_k=20,  # Get more, then filter by tokens
            alpha=alpha,
            bill_number=bill_number
        )

        # Build context within token limit
        context_parts = []
        total_tokens = 0

        for result in results:
            # Format chunk with section header
            section = result["metadata"].get("section", "Unknown")
            section_title = result["metadata"].get("section_title", "")

            header = f"Section {section}"
            if section_title:
                header += f" - {section_title}"

            chunk_text = f"{header}:\n{result['text']}\n"

            # Count tokens
            chunk_tokens = count_tokens(chunk_text)

            # Check if adding this chunk exceeds limit
            if total_tokens + chunk_tokens > max_tokens:
                break

            context_parts.append(chunk_text)
            total_tokens += chunk_tokens

        context = "\n".join(context_parts)

        logger.info(f"Retrieved context: {total_tokens} tokens, {len(context_parts)} chunks")
        return context

    def get_full_bill_context(self, bill_number: str, max_tokens: int = 8000) -> str:
        """
        Get all chunks for a bill as concatenated text.

        Args:
            bill_number: Bill identifier
            max_tokens: Maximum tokens to include (applies truncation if needed)

        Returns:
            Full bill text as string

        Example:
            >>> context = engine.get_full_bill_context("H.R. 1234")
            >>> print(context[:100])
        """
        logger.info(f"Retrieving full bill context for {bill_number}")

        # Get all chunks for this bill
        results = self.collection.get(
            where={"bill_number": bill_number}
        )

        # Format and sort by start position
        chunks = []
        for i in range(len(results["ids"])):
            chunks.append({
                "id": results["ids"][i],
                "text": results["documents"][i],
                "metadata": results["metadatas"][i] if results["metadatas"] else {}
            })

        # Sort by start_char to get document order
        chunks_sorted = sorted(chunks, key=lambda x: x["metadata"].get("start_char", 0))

        # Concatenate chunks with section headers
        context_parts = []
        for chunk in chunks_sorted:
            section = chunk["metadata"].get("section", "")
            section_title = chunk["metadata"].get("section_title", "")
            if section and section_title:
                context_parts.append(f"[Section {section}: {section_title}]")
            context_parts.append(chunk["text"])

        full_context = "\n\n".join(context_parts)

        # Apply max_tokens limit if needed
        if max_tokens:
            tokenizer = tiktoken.get_encoding("cl100k_base")
            tokens = tokenizer.encode(full_context)
            if len(tokens) > max_tokens:
                logger.warning(f"Truncating context from {len(tokens)} to {max_tokens} tokens")
                truncated_tokens = tokens[:max_tokens]
                full_context = tokenizer.decode(truncated_tokens)

        logger.info(f"Retrieved {len(chunks_sorted)} chunks in order ({len(full_context)} chars)")
        return full_context

    def find_specific_provisions(
        self,
        bill_number: str,
        keywords: List[str],
        match_all: bool = False
    ) -> List[Dict]:
        """
        Find chunks containing specific terms.

        Args:
            bill_number: Bill to search
            keywords: List of terms to find (e.g., ["appropriations", "$50 million"])
            match_all: If True, require ALL keywords; if False, require ANY keyword

        Returns:
            Chunks containing the keywords, sorted by relevance

        Example:
            >>> provisions = engine.find_specific_provisions(
            ...     "H.R. 1234",
            ...     ["$50 million", "appropriations"],
            ...     match_all=False
            ... )
        """
        logger.info(f"Finding provisions with keywords: {keywords} (match_all={match_all})")

        # Get all chunks for this bill
        all_chunks = self.get_full_bill_context(bill_number)

        # Filter by keywords
        matching_chunks = []

        for chunk in all_chunks:
            text_lower = chunk["text"].lower()

            if match_all:
                # All keywords must be present
                if all(keyword.lower() in text_lower for keyword in keywords):
                    matching_chunks.append(chunk)
            else:
                # Any keyword must be present
                if any(keyword.lower() in text_lower for keyword in keywords):
                    matching_chunks.append(chunk)

        # Score by number of keyword matches
        for chunk in matching_chunks:
            text_lower = chunk["text"].lower()
            match_count = sum(1 for kw in keywords if kw.lower() in text_lower)
            chunk["keyword_matches"] = match_count

        # Sort by match count
        matching_chunks.sort(key=lambda x: x["keyword_matches"], reverse=True)

        logger.info(f"Found {len(matching_chunks)} matching chunks")
        return matching_chunks


# ============================================================================
# Main / Testing
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 80)
    print("Testing RAG Engine with Hybrid Search")
    print("=" * 80)

    # Note: This requires a vector store to be set up first
    try:
        from processors.embedder import load_vector_store

        # Load collection
        collection = load_vector_store("test_bills", db_path="data/test_vector_db")

        # Initialize RAG engine
        engine = RAGEngine(collection, use_reranker=False)

        # Test 1: Hybrid search
        print("\n📊 Test 1: Hybrid Search")
        results = engine.hybrid_search("healthcare and medical", top_k=3, alpha=0.7)

        for i, result in enumerate(results, 1):
            print(f"\n  Result {i} (Score: {result['final_score']:.4f}):")
            print(f"    Vector: {result.get('vector_score_norm', 0):.4f}, BM25: {result.get('bm25_score_norm', 0):.4f}")
            print(f"    {result['text'][:100]}...")

        # Test 2: Context retrieval
        print("\n\n📝 Test 2: Context Retrieval")
        context = engine.retrieve_context(
            bill_number="H.R. TEST",
            query="healthcare providers",
            max_tokens=500
        )
        print(f"Context ({count_tokens(context)} tokens):")
        print(context[:300] + "...")

        # Test 3: Specific provisions
        print("\n\n🔍 Test 3: Specific Provisions")
        provisions = engine.find_specific_provisions(
            bill_number="H.R. TEST",
            keywords=["education", "Secretary"]
        )
        print(f"Found {len(provisions)} provisions")
        for prov in provisions[:2]:
            print(f"  - Matches: {prov['keyword_matches']}")
            print(f"    {prov['text'][:80]}...")

        print("\n" + "=" * 80)
        print("✅ All tests completed!")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
