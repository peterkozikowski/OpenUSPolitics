"""
Comprehensive tests for RAG engine with hybrid search.

Tests cover:
- Vector search
- BM25 keyword search
- Hybrid fusion
- Context retrieval with token limits
- Specific provision finding
- Various query types
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import numpy as np

from analyzers.rag_engine import (
    RAGEngine,
    RAGEngineError,
    setup_bm25_index,
    tokenize_query,
    count_tokens,
    normalize_scores,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_collection():
    """Create a mock ChromaDB collection."""
    collection = Mock()
    collection.count.return_value = 5

    # Mock query results
    collection.query.return_value = {
        "ids": [["chunk_0", "chunk_1", "chunk_2"]],
        "documents": [["Healthcare text", "Education text", "Budget text"]],
        "metadatas": [[
            {"section": "1", "section_title": "Healthcare", "bill_number": "H.R. 1"},
            {"section": "2", "section_title": "Education", "bill_number": "H.R. 1"},
            {"section": "3", "section_title": "Budget", "bill_number": "H.R. 1"}
        ]],
        "distances": [[0.2, 0.3, 0.4]]
    }

    # Mock get results
    collection.get.return_value = {
        "ids": ["chunk_0", "chunk_1", "chunk_2"],
        "documents": ["Healthcare text", "Education text", "Budget text"],
        "metadatas": [
            {"section": "1", "section_title": "Healthcare", "bill_number": "H.R. 1", "start_char": 0},
            {"section": "2", "section_title": "Education", "bill_number": "H.R. 1", "start_char": 100},
            {"section": "3", "section_title": "Budget", "bill_number": "H.R. 1", "start_char": 200}
        ]
    }

    return collection


@pytest.fixture
def test_chunks():
    """Create test chunks for BM25 indexing."""
    return [
        {
            "id": "chunk_0",
            "text": "This bill provides healthcare funding for rural areas",
            "metadata": {"section": "1", "bill_number": "H.R. 1"}
        },
        {
            "id": "chunk_1",
            "text": "The Secretary shall allocate education funds to schools",
            "metadata": {"section": "2", "bill_number": "H.R. 1"}
        },
        {
            "id": "chunk_2",
            "text": "Appropriations of $50 million for healthcare programs",
            "metadata": {"section": "3", "bill_number": "H.R. 1"}
        }
    ]


# ============================================================================
# Helper Function Tests
# ============================================================================

class TestHelperFunctions:
    """Tests for helper functions."""

    def test_setup_bm25_index(self, test_chunks):
        """Test BM25 index creation."""
        bm25, indexed_chunks = setup_bm25_index(test_chunks)

        assert bm25 is not None
        assert len(indexed_chunks) == 3
        assert indexed_chunks == test_chunks

    def test_setup_bm25_index_empty_chunks(self):
        """Test BM25 index with empty chunks raises error."""
        with pytest.raises(ValueError, match="Cannot create BM25 index"):
            setup_bm25_index([])

    def test_tokenize_query(self):
        """Test query tokenization."""
        query = "Healthcare Funding Programs"
        tokens = tokenize_query(query)

        assert tokens == ["healthcare", "funding", "programs"]
        assert isinstance(tokens, list)

    def test_count_tokens(self):
        """Test token counting."""
        text = "This is a test sentence with some words."
        count = count_tokens(text)

        assert count > 0
        assert isinstance(count, int)

    def test_normalize_scores_normal(self):
        """Test score normalization."""
        scores = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        normalized = normalize_scores(scores)

        assert normalized.min() == 0.0
        assert normalized.max() == 1.0
        assert len(normalized) == len(scores)

    def test_normalize_scores_all_same(self):
        """Test normalization when all scores are the same."""
        scores = np.array([5.0, 5.0, 5.0])
        normalized = normalize_scores(scores)

        assert np.all(normalized == 1.0)

    def test_normalize_scores_empty(self):
        """Test normalization with empty array."""
        scores = np.array([])
        normalized = normalize_scores(scores)

        assert len(normalized) == 0


# ============================================================================
# RAG Engine Tests
# ============================================================================

class TestRAGEngine:
    """Tests for RAGEngine class."""

    @patch('analyzers.rag_engine.SentenceTransformer')
    def test_init(self, mock_transformer, mock_collection):
        """Test RAG engine initialization."""
        engine = RAGEngine(mock_collection)

        assert engine.collection == mock_collection
        assert engine.embedder is not None
        assert engine.bm25 is None  # Lazy initialization
        assert engine.use_reranker is False
        mock_transformer.assert_called_once()

    @patch('analyzers.rag_engine.SentenceTransformer')
    @patch('analyzers.rag_engine.CrossEncoder')
    def test_init_with_reranker(self, mock_cross_encoder, mock_transformer, mock_collection):
        """Test initialization with reranker enabled."""
        engine = RAGEngine(mock_collection, use_reranker=True)

        assert engine.use_reranker is True
        assert engine.reranker is not None
        mock_cross_encoder.assert_called_once()

    @patch('analyzers.rag_engine.SentenceTransformer')
    def test_get_all_chunks(self, mock_transformer, mock_collection):
        """Test getting all chunks from collection."""
        engine = RAGEngine(mock_collection)
        chunks = engine._get_all_chunks()

        assert len(chunks) == 3
        assert all("id" in chunk for chunk in chunks)
        assert all("text" in chunk for chunk in chunks)
        mock_collection.get.assert_called_once()


class TestVectorSearch:
    """Tests for vector search functionality."""

    @patch('analyzers.rag_engine.SentenceTransformer')
    def test_vector_search(self, mock_transformer, mock_collection):
        """Test vector similarity search."""
        # Mock embedder
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_transformer.return_value = mock_model

        engine = RAGEngine(mock_collection)
        results = engine._vector_search("healthcare", top_k=3)

        assert len(results) == 3
        assert all("vector_score" in r for r in results)
        assert all("text" in r for r in results)
        mock_collection.query.assert_called_once()

    @patch('analyzers.rag_engine.SentenceTransformer')
    def test_vector_search_with_filter(self, mock_transformer, mock_collection):
        """Test vector search with bill number filter."""
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_transformer.return_value = mock_model

        engine = RAGEngine(mock_collection)
        results = engine._vector_search("healthcare", top_k=3, bill_number="H.R. 1")

        mock_collection.query.assert_called_once()
        call_args = mock_collection.query.call_args
        assert call_args[1]["where"] == {"bill_number": "H.R. 1"}


class TestBM25Search:
    """Tests for BM25 keyword search."""

    @patch('analyzers.rag_engine.SentenceTransformer')
    def test_bm25_search(self, mock_transformer, mock_collection, test_chunks):
        """Test BM25 keyword search."""
        engine = RAGEngine(mock_collection)

        # Manually set BM25 index for testing
        engine.bm25, engine.bm25_chunks = setup_bm25_index(test_chunks)

        results = engine._bm25_search("healthcare funding", top_k=3)

        assert len(results) > 0
        assert all("bm25_score" in r for r in results)
        assert all(r["bm25_score"] > 0 for r in results)

    @patch('analyzers.rag_engine.SentenceTransformer')
    def test_bm25_search_with_filter(self, mock_transformer, mock_collection, test_chunks):
        """Test BM25 search with bill number filter."""
        engine = RAGEngine(mock_collection)
        engine.bm25, engine.bm25_chunks = setup_bm25_index(test_chunks)

        results = engine._bm25_search("healthcare", top_k=3, bill_number="H.R. 1")

        assert len(results) > 0


class TestHybridSearch:
    """Tests for hybrid search combining vector and BM25."""

    @patch('analyzers.rag_engine.SentenceTransformer')
    def test_hybrid_search_balanced(self, mock_transformer, mock_collection, test_chunks):
        """Test hybrid search with balanced weights."""
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_transformer.return_value = mock_model

        engine = RAGEngine(mock_collection)
        engine.bm25, engine.bm25_chunks = setup_bm25_index(test_chunks)

        results = engine.hybrid_search("healthcare funding", top_k=3, alpha=0.5)

        assert len(results) <= 3
        assert all("final_score" in r for r in results)
        # Results should be sorted by final_score
        scores = [r["final_score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    @patch('analyzers.rag_engine.SentenceTransformer')
    def test_hybrid_search_pure_vector(self, mock_transformer, mock_collection, test_chunks):
        """Test hybrid search with pure vector (alpha=1.0)."""
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_transformer.return_value = mock_model

        engine = RAGEngine(mock_collection)
        engine.bm25, engine.bm25_chunks = setup_bm25_index(test_chunks)

        results = engine.hybrid_search("healthcare", top_k=2, alpha=1.0)

        # With alpha=1.0, should be pure vector search
        assert len(results) <= 2

    @patch('analyzers.rag_engine.SentenceTransformer')
    def test_hybrid_search_pure_bm25(self, mock_transformer, mock_collection, test_chunks):
        """Test hybrid search with pure BM25 (alpha=0.0)."""
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_transformer.return_value = mock_model

        engine = RAGEngine(mock_collection)
        engine.bm25, engine.bm25_chunks = setup_bm25_index(test_chunks)

        results = engine.hybrid_search("healthcare", top_k=2, alpha=0.0)

        # With alpha=0.0, should be pure BM25 search
        assert len(results) <= 2

    @patch('analyzers.rag_engine.SentenceTransformer')
    def test_hybrid_search_caching(self, mock_transformer, mock_collection, test_chunks):
        """Test that hybrid search results are cached."""
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_transformer.return_value = mock_model

        engine = RAGEngine(mock_collection)
        engine.bm25, engine.bm25_chunks = setup_bm25_index(test_chunks)

        # First call
        results1 = engine.hybrid_search("healthcare", top_k=2, alpha=0.5)

        # Second call (should use cache)
        results2 = engine.hybrid_search("healthcare", top_k=2, alpha=0.5)

        assert results1 == results2
        # Verify embedder was only called once
        assert mock_model.encode.call_count == 1


class TestContextRetrieval:
    """Tests for context retrieval with token limits."""

    @patch('analyzers.rag_engine.SentenceTransformer')
    def test_retrieve_context(self, mock_transformer, mock_collection, test_chunks):
        """Test context retrieval within token limit."""
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_transformer.return_value = mock_model

        engine = RAGEngine(mock_collection)
        engine.bm25, engine.bm25_chunks = setup_bm25_index(test_chunks)

        context = engine.retrieve_context(
            bill_number="H.R. 1",
            query="healthcare",
            max_tokens=1000
        )

        assert isinstance(context, str)
        assert len(context) > 0
        # Check token count
        token_count = count_tokens(context)
        assert token_count <= 1000

    @patch('analyzers.rag_engine.SentenceTransformer')
    def test_retrieve_context_formatted(self, mock_transformer, mock_collection, test_chunks):
        """Test that context is properly formatted with section headers."""
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_transformer.return_value = mock_model

        engine = RAGEngine(mock_collection)
        engine.bm25, engine.bm25_chunks = setup_bm25_index(test_chunks)

        context = engine.retrieve_context(
            bill_number="H.R. 1",
            query="healthcare",
            max_tokens=2000
        )

        # Should contain section headers
        assert "Section" in context


class TestFullBillContext:
    """Tests for retrieving full bill context."""

    @patch('analyzers.rag_engine.SentenceTransformer')
    def test_get_full_bill_context(self, mock_transformer, mock_collection):
        """Test getting full bill context in order."""
        engine = RAGEngine(mock_collection)
        chunks = engine.get_full_bill_context("H.R. 1")

        assert len(chunks) == 3
        # Verify sorted by start_char
        start_chars = [c["metadata"]["start_char"] for c in chunks]
        assert start_chars == sorted(start_chars)


class TestSpecificProvisions:
    """Tests for finding specific provisions."""

    @patch('analyzers.rag_engine.SentenceTransformer')
    def test_find_provisions_any_keyword(self, mock_transformer, mock_collection, test_chunks):
        """Test finding provisions with ANY keyword match."""
        engine = RAGEngine(mock_collection)

        # Mock get_full_bill_context
        with patch.object(engine, 'get_full_bill_context', return_value=test_chunks):
            provisions = engine.find_specific_provisions(
                bill_number="H.R. 1",
                keywords=["healthcare", "education"],
                match_all=False
            )

        assert len(provisions) > 0
        # Should find chunks with either keyword
        assert all("keyword_matches" in p for p in provisions)

    @patch('analyzers.rag_engine.SentenceTransformer')
    def test_find_provisions_all_keywords(self, mock_transformer, mock_collection, test_chunks):
        """Test finding provisions with ALL keywords required."""
        engine = RAGEngine(mock_collection)

        # Modify test chunk to have both keywords
        test_chunks_modified = test_chunks.copy()
        test_chunks_modified[0]["text"] = "Healthcare and education funding bill"

        with patch.object(engine, 'get_full_bill_context', return_value=test_chunks_modified):
            provisions = engine.find_specific_provisions(
                bill_number="H.R. 1",
                keywords=["healthcare", "education"],
                match_all=True
            )

        # Only chunks with ALL keywords should be returned
        for prov in provisions:
            text_lower = prov["text"].lower()
            assert "healthcare" in text_lower
            assert "education" in text_lower

    @patch('analyzers.rag_engine.SentenceTransformer')
    def test_find_provisions_sorted_by_matches(self, mock_transformer, mock_collection, test_chunks):
        """Test that provisions are sorted by number of keyword matches."""
        engine = RAGEngine(mock_collection)

        with patch.object(engine, 'get_full_bill_context', return_value=test_chunks):
            provisions = engine.find_specific_provisions(
                bill_number="H.R. 1",
                keywords=["healthcare", "funding"],
                match_all=False
            )

        # Verify sorted by match count
        if len(provisions) > 1:
            match_counts = [p["keyword_matches"] for p in provisions]
            assert match_counts == sorted(match_counts, reverse=True)


# ============================================================================
# Query Type Tests
# ============================================================================

class TestQueryTypes:
    """Tests for various query types."""

    @patch('analyzers.rag_engine.SentenceTransformer')
    def test_broad_query(self, mock_transformer, mock_collection, test_chunks):
        """Test broad query like 'What does this bill do?'"""
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_transformer.return_value = mock_model

        engine = RAGEngine(mock_collection)
        engine.bm25, engine.bm25_chunks = setup_bm25_index(test_chunks)

        results = engine.hybrid_search(
            "What does this bill do?",
            top_k=5,
            alpha=0.6  # Slightly favor vector for broad queries
        )

        assert len(results) > 0

    @patch('analyzers.rag_engine.SentenceTransformer')
    def test_specific_query(self, mock_transformer, mock_collection, test_chunks):
        """Test specific query like 'How much money is allocated?'"""
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_transformer.return_value = mock_model

        engine = RAGEngine(mock_collection)
        engine.bm25, engine.bm25_chunks = setup_bm25_index(test_chunks)

        results = engine.hybrid_search(
            "How much money is allocated?",
            top_k=3,
            alpha=0.4  # Slightly favor BM25 for specific queries
        )

        assert len(results) > 0

    @patch('analyzers.rag_engine.SentenceTransformer')
    def test_impact_query(self, mock_transformer, mock_collection, test_chunks):
        """Test impact-focused query like 'Who is affected?'"""
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_transformer.return_value = mock_model

        engine = RAGEngine(mock_collection)
        engine.bm25, engine.bm25_chunks = setup_bm25_index(test_chunks)

        results = engine.hybrid_search(
            "Who is affected by this bill?",
            top_k=5,
            alpha=0.5
        )

        assert len(results) > 0


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.skip(reason="Requires vector store and embeddings to be set up")
def test_rag_engine_integration():
    """Integration test with real vector store."""
    from processors.embedder import load_vector_store

    collection = load_vector_store("test_bills", db_path="data/test_vector_db")
    engine = RAGEngine(collection)

    # Test hybrid search
    results = engine.hybrid_search("healthcare", top_k=3, alpha=0.5)
    assert len(results) > 0

    # Test context retrieval
    context = engine.retrieve_context("H.R. TEST", "healthcare", max_tokens=1000)
    assert isinstance(context, str)
    assert count_tokens(context) <= 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
