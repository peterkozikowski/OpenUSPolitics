"""Analyzers module for RAG-based bill analysis using Claude."""

from .claude_client import ClaudeAnalyzer

try:
    from .rag_engine import RAGEngine

    __all__ = ["ClaudeAnalyzer", "RAGEngine"]
except ImportError as e:
    # RAGEngine requires sentence-transformers (large dependency)
    __all__ = ["ClaudeAnalyzer"]
    import warnings

    warnings.warn(f"RAGEngine not available: {e}")
    RAGEngine = None
