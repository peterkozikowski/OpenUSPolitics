#!/usr/bin/env python3
"""
Main ETL pipeline orchestrator for OpenUSPolitics.org bill analysis.

Complete pipeline flow:
1. Fetch bills from Congress.gov API
2. Parse bill text (PDF/HTML)
3. Chunk documents with token awareness
4. Generate embeddings and store in vector DB
5. Retrieve context via hybrid RAG search
6. Analyze with Claude (summary, provisions, impact, fiscal)
7. Save to git-based storage with version control

Usage:
    python main.py --bills 10 --verbose
    python main.py --bill-numbers "H.R. 1234" "S. 5678"
    python main.py --validate
    python main.py --dry-run --bills 5
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from config import Config
from fetchers.congress_api import CongressAPIClient, CongressAPIError
from processors.parser import parse_bill_text, ParserError
from processors.chunker import chunk_document, ChunkerError
from processors.embedder import generate_embeddings, setup_vector_store, EmbedderError
from analyzers.rag_engine import RAGEngine, RAGError
from analyzers.claude_client import ClaudeAnalyzer, ClaudeAPIError
from storage.git_store import (
    save_analysis,
    load_analysis,
    bill_needs_update,
    get_all_bills,
    GitStoreError,
)

# ============================================================================
# Logging Configuration
# ============================================================================


def setup_logging(verbose: bool = False) -> None:
    """
    Configure logging for the pipeline.

    Args:
        verbose: Enable verbose (DEBUG) logging
    """
    Config.setup_directories()

    level = logging.DEBUG if verbose else logging.INFO

    # Create log filename with timestamp
    log_filename = (
        Config.LOGS_DIR / f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )

    # Configure root logger
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout),
        ],
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Logging to: {log_filename}")


logger = logging.getLogger(__name__)


# ============================================================================
# Utility Functions
# ============================================================================


def is_post_office_bill(title: str) -> bool:
    """
    Check if a bill is a trivial post office naming bill.

    These bills are filtered out to save analysis costs and keep
    the database focused on substantive legislation.

    Args:
        title: The bill title

    Returns:
        True if the bill is a post office naming bill

    Examples:
        >>> is_post_office_bill("To designate the United States Postal Service facility...")
        True
        >>> is_post_office_bill("Infrastructure Investment and Jobs Act")
        False
    """
    title_lower = title.lower()
    return ('united states postal service' in title_lower or
            ('post office' in title_lower and 'designate' in title_lower))


# ============================================================================
# Pipeline Statistics
# ============================================================================


class PipelineStats:
    """Track pipeline execution statistics."""

    def __init__(self):
        self.start_time = time.time()
        self.bills_processed = 0
        self.bills_failed = 0
        self.bills_skipped = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.errors = []

    def add_success(self, bill_number: str, tokens: int = 0, cost: float = 0.0):
        """Record successful bill processing."""
        self.bills_processed += 1
        self.total_tokens += tokens
        self.total_cost += cost

    def add_failure(self, bill_number: str, error: str):
        """Record failed bill processing."""
        self.bills_failed += 1
        self.errors.append({"bill_number": bill_number, "error": str(error)})

    def add_skip(self, bill_number: str, reason: str):
        """Record skipped bill."""
        self.bills_skipped += 1

    def get_summary(self) -> Dict:
        """Get statistics summary."""
        elapsed = time.time() - self.start_time
        return {
            "elapsed_seconds": round(elapsed, 2),
            "bills_processed": self.bills_processed,
            "bills_failed": self.bills_failed,
            "bills_skipped": self.bills_skipped,
            "total_tokens": self.total_tokens,
            "total_cost_usd": round(self.total_cost, 4),
            "avg_time_per_bill": round(elapsed / max(self.bills_processed, 1), 2),
            "errors": self.errors,
        }

    def save_metrics(self):
        """Save metrics to JSON file."""
        metrics_file = (
            Config.LOGS_DIR / f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(metrics_file, "w") as f:
            json.dump(self.get_summary(), f, indent=2)
        logger.info(f"Saved metrics to: {metrics_file}")


# ============================================================================
# Main Pipeline Functions
# ============================================================================


def validate_pipeline() -> bool:
    """
    Run validation checks on the pipeline.

    Returns:
        True if all validations pass, False otherwise
    """
    logger.info("=" * 80)
    logger.info("PIPELINE VALIDATION")
    logger.info("=" * 80)

    all_passed = True

    # Validate configuration
    try:
        Config.validate()
        logger.info("✓ Configuration validation passed")
    except ValueError as e:
        logger.error(f"✗ Configuration validation failed: {e}")
        all_passed = False

    # Check API keys
    if not Config.ANTHROPIC_API_KEY:
        logger.error("✗ ANTHROPIC_API_KEY not set")
        all_passed = False
    else:
        logger.info("✓ ANTHROPIC_API_KEY is set")

    if not Config.CONGRESS_GOV_API_KEY:
        logger.error("✗ CONGRESS_GOV_API_KEY not set")
        all_passed = False
    else:
        logger.info("✓ CONGRESS_GOV_API_KEY is set")

    # Check directories
    required_dirs = [
        Config.DATA_DIR,
        Config.BILLS_DIR,
        Config.VECTOR_DB_DIR,
        Config.LOGS_DIR,
    ]
    for directory in required_dirs:
        if directory.exists():
            logger.info(f"✓ Directory exists: {directory}")
        else:
            logger.warning(f"⚠ Directory missing (will be created): {directory}")

    # Test API clients
    try:
        congress_client = CongressAPIClient()
        logger.info("✓ Congress API client initialized")
    except Exception as e:
        logger.error(f"✗ Congress API client failed: {e}")
        all_passed = False

    try:
        claude_client = ClaudeAnalyzer()
        logger.info("✓ Claude API client initialized")
    except Exception as e:
        logger.error(f"✗ Claude API client failed: {e}")
        all_passed = False

    # Test vector store
    try:
        test_chunks = [
            {"id": "test_0", "text": "This is a test chunk.", "bill_number": "TEST"}
        ]
        # Generate embeddings for test chunk
        from processors.embedder import generate_embeddings

        test_chunks_with_embeddings = generate_embeddings(test_chunks)
        collection = setup_vector_store(
            test_chunks_with_embeddings, collection_name="validation_test"
        )
        logger.info("✓ Vector store test passed")
    except Exception as e:
        logger.error(f"✗ Vector store test failed: {e}")
        all_passed = False

    logger.info("=" * 80)
    if all_passed:
        logger.info("✅ All validation checks passed")
    else:
        logger.error("❌ Some validation checks failed")
    logger.info("=" * 80)

    return all_passed


def analyze_single_bill(
    bill_number: str,
    force_update: bool = False,
    dry_run: bool = False,
) -> Optional[Dict]:
    """
    Analyze a single bill through the complete pipeline.

    Args:
        bill_number: Bill identifier (e.g., "H.R. 1234")
        force_update: Force re-analysis even if bill exists
        dry_run: Only fetch and parse, don't run AI analysis

    Returns:
        Analysis dictionary if successful, None otherwise
    """
    logger.info("=" * 80)
    logger.info(f"Analyzing bill: {bill_number}")
    logger.info("=" * 80)

    try:
        # Check if update needed
        if not force_update and not bill_needs_update(bill_number):
            logger.info(f"Bill {bill_number} is up to date, loading existing analysis")
            return load_analysis(bill_number)

        # Initialize clients
        congress_client = CongressAPIClient()
        claude_client = ClaudeAnalyzer()

        # Step 1: Fetch bill details
        logger.info("Step 1/7: Fetching bill details from Congress.gov...")
        bill_details = congress_client.get_bill_details(bill_number)

        if not bill_details:
            logger.error(f"Could not fetch details for {bill_number}")
            return None

        title = bill_details.get('title', '')
        logger.info(f"  Title: {title[:100]}...")

        # Skip post office naming bills
        if is_post_office_bill(title):
            logger.info(f"  → Skipping post office naming bill: {bill_number}")
            logger.info(f"     (Post office bills are filtered to save analysis costs)")
            return None

        # Step 2: Get bill text
        logger.info("Step 2/7: Fetching bill text...")
        bill_text_data = congress_client.get_bill_text(bill_number)

        if not bill_text_data or not bill_text_data.get("url"):
            logger.error(f"No text URL available for {bill_number}")
            return None

        text_url = bill_text_data["url"]
        logger.info(f"  Text URL: {text_url}")

        # Step 3: Parse bill text
        logger.info("Step 3/7: Parsing bill text (PDF/HTML)...")
        parsed_bill = parse_bill_text(text_url)
        logger.info(f"  Parsed {len(parsed_bill['raw_text'])} characters")
        logger.info(f"  Found {len(parsed_bill.get('sections', []))} sections")

        # Step 4: Chunk document
        logger.info("Step 4/7: Chunking document with token awareness...")
        chunks = chunk_document(
            parsed_bill,
            chunk_size=Config.CHUNK_SIZE,
            overlap=Config.CHUNK_OVERLAP,
        )
        logger.info(f"  Created {len(chunks)} chunks")

        # Add bill_number to each chunk
        for chunk in chunks:
            chunk["bill_number"] = bill_number

        if dry_run:
            logger.info("DRY RUN: Stopping before embeddings/analysis")
            return {
                "bill_number": bill_number,
                "title": bill_details.get("title"),
                "chunks_count": len(chunks),
                "dry_run": True,
            }

        # Step 5: Generate embeddings
        logger.info("Step 5/7: Generating embeddings with sentence-transformers...")
        chunks_with_embeddings = generate_embeddings(chunks)
        logger.info(f"  Generated {len(chunks_with_embeddings)} embeddings")

        # Setup vector store
        collection_name = f"bill_{bill_number.replace('.', '_').replace(' ', '_')}"
        collection = setup_vector_store(
            chunks_with_embeddings, collection_name=collection_name
        )
        logger.info(f"  Stored in collection: {collection_name}")

        # Step 6: Retrieve context via RAG
        logger.info("Step 6/7: Retrieving context via hybrid RAG search...")
        rag_engine = RAGEngine(collection=collection)

        # Get comprehensive context for analysis
        context = rag_engine.get_full_bill_context(
            bill_number=bill_number,
            max_tokens=8000,  # Leave room for prompts
        )
        logger.info(f"  Retrieved context: {len(context)} characters")

        # Step 7: Analyze with Claude
        logger.info(
            "Step 7/7: Analyzing with Claude (summary, provisions, impact, fiscal)..."
        )

        bill_data = {
            "bill_number": bill_number,
            "title": bill_details.get("title", ""),
            "sponsor": bill_details.get("sponsor", {}).get("name", "Unknown"),
            "introduced_date": bill_details.get("introduced_date", "Unknown"),
            "text_url": text_url,
        }

        analysis = claude_client.analyze_bill(bill_data, chunks_with_embeddings)

        logger.info(
            f"  Analysis complete - Cost: ${analysis.get('estimated_cost', 0):.4f}"
        )
        logger.info(f"  Tokens used: {analysis.get('total_tokens', 0)}")

        # Prepare final data
        analysis_data = {
            **bill_data,
            "bill_version": bill_text_data.get("version", "Unknown"),
            "status": bill_details.get("status", "Unknown"),
            "chunks_count": len(chunks),
            "chunks": chunks,  # Include actual chunks for frontend
            "analysis": {
                "plain_english_summary": analysis.get("plain_english_summary", ""),
                "key_provisions": analysis.get("key_provisions", []),
                "practical_impact": analysis.get("practical_impact", {}),
                "fiscal_impact": analysis.get("fiscal_impact"),
                "generated_at": analysis.get("generated_at", ""),
                "model_used": analysis.get("model_used", Config.CLAUDE_MODEL),
            },
            "model": analysis.get("model_used", Config.CLAUDE_MODEL),
            "total_tokens": analysis.get("total_tokens", 0),
            "cost": analysis.get("estimated_cost", 0.0),
        }

        # Save analysis
        logger.info("Saving analysis to git storage...")
        filepath = save_analysis(
            bill_number, analysis_data, auto_commit=Config.GIT_AUTO_COMMIT
        )
        logger.info(f"✓ Saved to: {filepath}")

        logger.info("=" * 80)
        logger.info(f"✅ Successfully analyzed {bill_number}")
        logger.info("=" * 80)

        return analysis_data

    except CongressAPIError as e:
        logger.error(f"Congress API error for {bill_number}: {e}")
        return None
    except ParserError as e:
        logger.error(f"Parser error for {bill_number}: {e}")
        return None
    except ChunkerError as e:
        logger.error(f"Chunker error for {bill_number}: {e}")
        return None
    except EmbedderError as e:
        logger.error(f"Embedder error for {bill_number}: {e}")
        return None
    except RAGError as e:
        logger.error(f"RAG error for {bill_number}: {e}")
        return None
    except ClaudeAPIError as e:
        logger.error(f"Claude API error for {bill_number}: {e}")
        return None
    except GitStoreError as e:
        logger.error(f"Storage error for {bill_number}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error for {bill_number}: {e}", exc_info=True)
        return None


def main(
    num_bills: Optional[int] = None,
    bill_numbers: Optional[List[str]] = None,
    force_update: bool = False,
    verbose: bool = False,
    dry_run: bool = False,
) -> None:
    """
    Main ETL pipeline orchestrator.

    Args:
        num_bills: Number of recent bills to fetch and analyze
        bill_numbers: Specific bill numbers to analyze
        force_update: Force re-analysis even if bills exist
        verbose: Enable verbose logging
        dry_run: Only fetch and parse, don't run AI analysis
    """
    setup_logging(verbose)

    logger.info("=" * 80)
    logger.info("OpenUSPolitics.org ETL Pipeline")
    logger.info("=" * 80)

    # Validate configuration
    try:
        Config.validate()
        Config.setup_directories()
        logger.info("✓ Configuration validated")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    # Initialize statistics
    stats = PipelineStats()

    try:
        # Determine which bills to process
        bills_to_process = []

        if bill_numbers:
            # Process specific bills
            logger.info(f"Processing {len(bill_numbers)} specific bills")
            bills_to_process = bill_numbers

        elif num_bills:
            # Fetch recent bills
            logger.info(f"Fetching {num_bills} recent bills from Congress.gov...")
            congress_client = CongressAPIClient()

            try:
                bills_data = congress_client.fetch_recent_bills(limit=num_bills)
                bills_to_process = [bill["bill_number"] for bill in bills_data]
                logger.info(f"Fetched {len(bills_to_process)} bills")
            except CongressAPIError as e:
                logger.error(f"Failed to fetch bills: {e}")
                sys.exit(1)

        else:
            logger.error("Must specify either --bills N or --bill-numbers")
            sys.exit(1)

        # Process each bill
        logger.info("=" * 80)
        logger.info(f"Processing {len(bills_to_process)} bills")
        logger.info("=" * 80)

        for i, bill_number in enumerate(bills_to_process, 1):
            logger.info(f"\n[{i}/{len(bills_to_process)}] Processing: {bill_number}")

            try:
                # Check if update needed (unless forced)
                if not force_update and not bill_needs_update(bill_number):
                    logger.info(f"  → Skipping {bill_number} (already up to date)")
                    stats.add_skip(bill_number, "up to date")
                    continue

                # Quick check: fetch bill title to filter post office bills early
                congress_client = CongressAPIClient()
                try:
                    bill_details = congress_client.get_bill_details(bill_number)
                    if bill_details:
                        title = bill_details.get('title', '')
                        if is_post_office_bill(title):
                            logger.info(f"  → Skipping post office naming bill")
                            logger.info(f"     Title: {title[:80]}...")
                            stats.add_skip(bill_number, "post office naming bill")
                            continue
                except Exception as e:
                    logger.warning(f"  Could not pre-check bill title: {e}")
                    # Continue anyway and let analyze_single_bill handle it

                # Analyze bill
                result = analyze_single_bill(
                    bill_number,
                    force_update=force_update,
                    dry_run=dry_run,
                )

                if result:
                    stats.add_success(
                        bill_number,
                        tokens=result.get("total_tokens", 0),
                        cost=result.get("cost", 0.0),
                    )
                else:
                    stats.add_failure(bill_number, "Analysis returned None")

            except KeyboardInterrupt:
                logger.info("\n⚠️  Pipeline interrupted by user")
                raise
            except Exception as e:
                logger.error(f"Failed to process {bill_number}: {e}")
                stats.add_failure(bill_number, str(e))
                # Continue with next bill

        # Print final statistics
        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE COMPLETE")
        logger.info("=" * 80)

        summary = stats.get_summary()
        logger.info(f"Elapsed time: {summary['elapsed_seconds']}s")
        logger.info(f"Bills processed: {summary['bills_processed']}")
        logger.info(f"Bills failed: {summary['bills_failed']}")
        logger.info(f"Bills skipped: {summary['bills_skipped']}")
        logger.info(f"Total tokens: {summary['total_tokens']:,}")
        logger.info(f"Total cost: ${summary['total_cost_usd']:.4f}")
        logger.info(f"Avg time per bill: {summary['avg_time_per_bill']}s")

        if summary["errors"]:
            logger.info(f"\nErrors encountered ({len(summary['errors'])}):")
            for error in summary["errors"]:
                logger.info(f"  - {error['bill_number']}: {error['error']}")

        # Save metrics
        stats.save_metrics()

        logger.info("=" * 80)

    except KeyboardInterrupt:
        logger.info("\n⚠️  Pipeline interrupted by user")
        stats.save_metrics()
        sys.exit(1)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        stats.save_metrics()
        sys.exit(1)


# ============================================================================
# CLI Entry Point
# ============================================================================


def cli():
    """Command-line interface for the pipeline."""
    parser = argparse.ArgumentParser(
        description="OpenUSPolitics.org ETL Pipeline - Bill Analysis System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process 10 recent bills
  python main.py --bills 10

  # Process specific bills
  python main.py --bill-numbers "H.R. 1234" "S. 5678"

  # Force re-analysis of bills
  python main.py --bills 5 --force-update

  # Validate pipeline configuration
  python main.py --validate

  # Dry run (fetch and parse only, no AI)
  python main.py --dry-run --bills 3

  # Verbose logging
  python main.py --bills 10 --verbose
        """,
    )

    parser.add_argument(
        "--bills",
        "-b",
        type=int,
        metavar="N",
        help="Number of recent bills to fetch and analyze",
    )

    parser.add_argument(
        "--bill-numbers",
        "-n",
        nargs="+",
        metavar="BILL",
        help='Specific bill numbers to analyze (e.g., "H.R. 1234" "S. 5678")',
    )

    parser.add_argument(
        "--force-update",
        "-f",
        action="store_true",
        help="Force re-analysis even if bills exist",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose (DEBUG) logging",
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run validation checks and exit",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and parse only, skip embeddings and AI analysis",
    )

    args = parser.parse_args()

    # Validate mode
    if args.validate:
        setup_logging(args.verbose)
        success = validate_pipeline()
        sys.exit(0 if success else 1)

    # Normal processing mode
    if not args.bills and not args.bill_numbers:
        parser.error("Must specify either --bills N or --bill-numbers")

    main(
        num_bills=args.bills,
        bill_numbers=args.bill_numbers,
        force_update=args.force_update,
        verbose=args.verbose,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    cli()
