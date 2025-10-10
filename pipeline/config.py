"""
Configuration management for OpenUSPolitics.org ETL pipeline.

Loads settings from environment variables and .env file.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Configuration class for pipeline settings.

    All settings are loaded from environment variables with sensible defaults.
    """

    # ========================================================================
    # API Keys (Required)
    # ========================================================================

    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    CONGRESS_GOV_API_KEY: str = os.getenv("CONGRESS_GOV_API_KEY", "")

    # Alias for backward compatibility
    CONGRESS_API_KEY: str = os.getenv("CONGRESS_GOV_API_KEY", "")

    # ========================================================================
    # Storage Paths
    # ========================================================================

    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "data/vector_db")
    DATA_PATH: str = os.getenv("DATA_PATH", "data/bills")
    LOGS_PATH: str = os.getenv("LOGS_PATH", "logs")

    # Derived paths
    DATA_DIR: Path = Path(DATA_PATH)
    BILLS_DIR: Path = DATA_DIR
    VECTOR_DB_DIR: Path = Path(VECTOR_DB_PATH)
    LOGS_DIR: Path = Path(LOGS_PATH)
    METADATA_FILE: Path = DATA_DIR / "metadata.json"

    # ========================================================================
    # Pipeline Configuration
    # ========================================================================

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    MAX_BILLS_PER_RUN: int = int(os.getenv("MAX_BILLS_PER_RUN", "20"))

    # ========================================================================
    # Document Processing
    # ========================================================================

    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1500"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "300"))

    # ========================================================================
    # RAG Configuration
    # ========================================================================

    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "5"))
    RAG_ALPHA: float = float(os.getenv("RAG_ALPHA", "0.5"))  # Hybrid search weight

    # ========================================================================
    # Claude Configuration
    # ========================================================================

    CLAUDE_MODEL: str = "claude-sonnet-4-5-20250929"
    CLAUDE_MAX_TOKENS: int = 4096
    CLAUDE_RATE_LIMIT_RPM: int = int(os.getenv("CLAUDE_RATE_LIMIT_RPM", "50"))

    # ========================================================================
    # Congress.gov API
    # ========================================================================

    CONGRESS_API_BASE_URL: str = "https://api.congress.gov/v3"
    CONGRESS_API_RATE_LIMIT: float = float(os.getenv("CONGRESS_API_RATE_LIMIT", "0.28"))  # ~1000/hour

    # ========================================================================
    # Optional Features
    # ========================================================================

    ENABLE_BIAS_AUDIT: bool = os.getenv("ENABLE_BIAS_AUDIT", "false").lower() == "true"
    ENABLE_TRACEABILITY: bool = os.getenv("ENABLE_TRACEABILITY", "true").lower() == "true"

    # ========================================================================
    # Git Configuration
    # ========================================================================

    GIT_AUTO_COMMIT: bool = os.getenv("GIT_AUTO_COMMIT", "true").lower() == "true"
    GIT_AUTO_PUSH: bool = os.getenv("GIT_AUTO_PUSH", "false").lower() == "true"

    # ========================================================================
    # Retry Configuration
    # ========================================================================

    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_BACKOFF_FACTOR: int = int(os.getenv("RETRY_BACKOFF_FACTOR", "2"))

    # ========================================================================
    # Methods
    # ========================================================================

    @classmethod
    def validate(cls) -> None:
        """
        Validate that required configuration is present.

        Raises:
            ValueError: If required configuration is missing
        """
        errors = []

        # Check required API keys
        if not cls.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY is not set")

        if not cls.CONGRESS_GOV_API_KEY:
            errors.append("CONGRESS_GOV_API_KEY is not set")

        # Check value ranges
        if cls.CHUNK_SIZE < 100:
            errors.append(f"CHUNK_SIZE ({cls.CHUNK_SIZE}) must be at least 100")

        if cls.CHUNK_OVERLAP >= cls.CHUNK_SIZE:
            errors.append("CHUNK_OVERLAP must be less than CHUNK_SIZE")

        if cls.RAG_TOP_K < 1:
            errors.append("RAG_TOP_K must be at least 1")

        if not 0 <= cls.RAG_ALPHA <= 1:
            errors.append("RAG_ALPHA must be between 0 and 1")

        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            raise ValueError(error_msg)

    @classmethod
    def setup_directories(cls) -> None:
        """Create necessary directories if they don't exist."""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.BILLS_DIR.mkdir(parents=True, exist_ok=True)
        cls.VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def __str__(cls) -> str:
        """
        Pretty print configuration (hiding sensitive API keys).

        Returns:
            Formatted configuration string
        """
        def mask_key(key: str) -> str:
            """Mask API key for display."""
            if not key:
                return "<not set>"
            return f"{key[:8]}...{key[-4:]}" if len(key) > 12 else "***"

        config_str = """
OpenUSPolitics.org Pipeline Configuration
==========================================

API Keys:
  ANTHROPIC_API_KEY: {anthropic_key}
  CONGRESS_GOV_API_KEY: {congress_key}

Storage:
  DATA_PATH: {data_path}
  VECTOR_DB_PATH: {vector_db_path}
  LOGS_PATH: {logs_path}

Pipeline:
  LOG_LEVEL: {log_level}
  MAX_BILLS_PER_RUN: {max_bills}

Document Processing:
  CHUNK_SIZE: {chunk_size}
  CHUNK_OVERLAP: {chunk_overlap}

RAG:
  RAG_TOP_K: {rag_top_k}
  RAG_ALPHA: {rag_alpha}

Claude:
  CLAUDE_MODEL: {claude_model}
  CLAUDE_RATE_LIMIT_RPM: {claude_rpm}

Features:
  ENABLE_BIAS_AUDIT: {bias_audit}
  ENABLE_TRACEABILITY: {traceability}
  GIT_AUTO_COMMIT: {git_commit}
  GIT_AUTO_PUSH: {git_push}
"""
        return config_str.format(
            anthropic_key=mask_key(cls.ANTHROPIC_API_KEY),
            congress_key=mask_key(cls.CONGRESS_GOV_API_KEY),
            data_path=cls.DATA_PATH,
            vector_db_path=cls.VECTOR_DB_PATH,
            logs_path=cls.LOGS_PATH,
            log_level=cls.LOG_LEVEL,
            max_bills=cls.MAX_BILLS_PER_RUN,
            chunk_size=cls.CHUNK_SIZE,
            chunk_overlap=cls.CHUNK_OVERLAP,
            rag_top_k=cls.RAG_TOP_K,
            rag_alpha=cls.RAG_ALPHA,
            claude_model=cls.CLAUDE_MODEL,
            claude_rpm=cls.CLAUDE_RATE_LIMIT_RPM,
            bias_audit=cls.ENABLE_BIAS_AUDIT,
            traceability=cls.ENABLE_TRACEABILITY,
            git_commit=cls.GIT_AUTO_COMMIT,
            git_push=cls.GIT_AUTO_PUSH
        )


# Validate configuration on import (with graceful handling)
if __name__ != "__main__":
    try:
        Config.validate()
    except ValueError as e:
        print(f"⚠️  Configuration Warning: {e}")
        print("\n💡 Please create a .env file with required settings:")
        print("   ANTHROPIC_API_KEY=your_key_here")
        print("   CONGRESS_GOV_API_KEY=your_key_here")


if __name__ == "__main__":
    # Test configuration
    print(Config.__str__(Config))

    try:
        Config.validate()
        print("\n✅ Configuration is valid!")
    except ValueError as e:
        print(f"\n❌ Configuration errors:\n{e}")

    # Setup directories
    Config.setup_directories()
    print(f"\n📁 Directories created:")
    print(f"   - {Config.DATA_DIR}")
    print(f"   - {Config.VECTOR_DB_DIR}")
    print(f"   - {Config.LOGS_DIR}")
