#!/usr/bin/env python3
"""
Lightweight bill fetcher for OpenUSPolitics.org

This script fetches bill metadata from Congress.gov API without running
expensive AI analysis. It's designed to quickly update the website with
new bills while keeping costs low.

Usage:
    python fetch_bills.py --bills 50
    python fetch_bills.py --bill-numbers "H.R. 1234" "S. 5678"
    python fetch_bills.py --update-existing
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
from storage.git_store import get_all_bills

# ============================================================================
# Logging Setup
# ============================================================================


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the fetcher."""
    Config.setup_directories()

    level = logging.DEBUG if verbose else logging.INFO
    log_filename = (
        Config.LOGS_DIR / f"fetch_bills_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )

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
# Post Office Bill Filter
# ============================================================================


def is_post_office_bill(title: str) -> bool:
    """
    Check if a bill is a trivial post office naming bill.

    Args:
        title: The bill title

    Returns:
        True if the bill is a post office naming bill
    """
    title_lower = title.lower()
    return ('united states postal service' in title_lower or
            ('post office' in title_lower and 'designate' in title_lower))


# ============================================================================
# Bill Metadata Fetching
# ============================================================================


def fetch_bill_metadata(bill_number: str, client: CongressAPIClient) -> Optional[Dict]:
    """
    Fetch basic metadata for a single bill (no AI analysis).

    Args:
        bill_number: Bill identifier (e.g., "H.R. 1234")
        client: Congress API client

    Returns:
        Bill metadata dictionary or None if failed/skipped
    """
    try:
        logger.info(f"Fetching metadata for {bill_number}...")

        # Get bill details
        bill_details = client.get_bill_details(bill_number)
        if not bill_details:
            logger.error(f"  Could not fetch details for {bill_number}")
            return None

        title = bill_details.get('title', '')
        sponsor = bill_details.get('sponsor', 'Unknown')
        introduced_date = bill_details.get('introducedDate', '')
        status = bill_details.get('latestAction', {}).get('text', 'Unknown')

        logger.info(f"  Title: {title[:80]}...")

        # Filter out post office bills
        if is_post_office_bill(title):
            logger.info(f"  ✗ Skipping post office naming bill")
            return None

        # Get bill text URL (but don't download/parse it)
        try:
            bill_text_data = client.get_bill_text(bill_number)
            text_url = bill_text_data.get('url', '') if bill_text_data else ''
            bill_version = bill_text_data.get('version', 'Unknown') if bill_text_data else 'Unknown'
        except Exception as e:
            logger.warning(f"  Could not fetch text URL: {e}")
            text_url = ''
            bill_version = 'Unknown'

        # Create minimal metadata structure
        metadata = {
            "bill_number": bill_number,
            "title": title,
            "sponsor": sponsor,
            "introduced_date": introduced_date,
            "text_url": text_url,
            "bill_version": bill_version,
            "status": status,
            "_metadata": {
                "fetched_at": datetime.now().isoformat(),
                "source": "Congress.gov API",
                "has_analysis": False
            }
        }

        logger.info(f"  ✓ Fetched metadata for {bill_number}")
        return metadata

    except CongressAPIError as e:
        logger.error(f"  API error for {bill_number}: {e}")
        return None
    except Exception as e:
        logger.error(f"  Unexpected error for {bill_number}: {e}", exc_info=True)
        return None


def save_bill_metadata(bill_data: Dict) -> bool:
    """
    Save bill metadata to JSON file.

    Args:
        bill_data: Bill metadata dictionary

    Returns:
        True if saved successfully
    """
    try:
        bill_number = bill_data['bill_number']

        # Create filename (e.g., "H.R. 1234" -> "HR_1234.json")
        filename = bill_number.replace('.', '').replace(' ', '_') + '.json'
        filepath = Config.BILLS_DIR / filename

        # Load existing file if it exists (to preserve AI analysis if present)
        if filepath.exists():
            with open(filepath, 'r') as f:
                existing_data = json.load(f)

                # If existing file has analysis, preserve it
                if 'analysis' in existing_data:
                    bill_data['analysis'] = existing_data['analysis']
                    bill_data['_metadata']['has_analysis'] = True

                # Preserve chunks and embeddings if they exist
                if 'chunks' in existing_data:
                    bill_data['chunks'] = existing_data['chunks']
                    bill_data['chunks_count'] = existing_data.get('chunks_count', len(existing_data['chunks']))

        # Save updated metadata
        with open(filepath, 'w') as f:
            json.dump(bill_data, f, indent=2, ensure_ascii=False)

        logger.debug(f"  Saved to {filepath}")
        return True

    except Exception as e:
        logger.error(f"  Failed to save {bill_data.get('bill_number', 'unknown')}: {e}")
        return False


def update_metadata_index(bills: List[str]) -> bool:
    """
    Update the metadata.json index file.

    Args:
        bills: List of bill numbers

    Returns:
        True if updated successfully
    """
    try:
        metadata_path = Config.BILLS_DIR / 'metadata.json'

        # Read existing metadata or create new
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        else:
            metadata = {"bills": {}, "last_updated": "", "total_bills": 0}

        # Update bill entries
        for bill_number in bills:
            filename = bill_number.replace('.', '').replace(' ', '_') + '.json'
            filepath = Config.BILLS_DIR / filename

            if filepath.exists():
                with open(filepath, 'r') as f:
                    bill_data = json.load(f)

                metadata["bills"][bill_number] = {
                    "file": filename,
                    "last_updated": bill_data.get('_metadata', {}).get('fetched_at', datetime.now().isoformat())
                }

        # Update counts and timestamp
        metadata["total_bills"] = len([k for k in metadata["bills"].keys() if not k.startswith('TEST')])
        metadata["last_updated"] = datetime.now().isoformat()

        # Save updated metadata
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        logger.info(f"✓ Updated metadata index: {metadata['total_bills']} bills")
        return True

    except Exception as e:
        logger.error(f"Failed to update metadata index: {e}")
        return False


# ============================================================================
# Main Execution
# ============================================================================


def main(
    num_bills: Optional[int] = None,
    bill_numbers: Optional[List[str]] = None,
    update_existing: bool = False,
    verbose: bool = False,
) -> None:
    """
    Main bill fetcher orchestrator.

    Args:
        num_bills: Number of recent bills to fetch
        bill_numbers: Specific bill numbers to fetch
        update_existing: Update metadata for all existing bills
        verbose: Enable verbose logging
    """
    setup_logging(verbose)

    logger.info("=" * 80)
    logger.info("OpenUSPolitics.org Bill Metadata Fetcher")
    logger.info("=" * 80)

    # Validate configuration
    try:
        Config.validate()
        Config.setup_directories()
        logger.info("✓ Configuration validated")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    # Initialize API client
    client = CongressAPIClient()

    # Determine which bills to process
    bills_to_fetch = []

    if bill_numbers:
        logger.info(f"Fetching {len(bill_numbers)} specific bills")
        bills_to_fetch = bill_numbers

    elif update_existing:
        logger.info("Updating metadata for all existing bills")
        bills_to_fetch = get_all_bills()
        logger.info(f"Found {len(bills_to_fetch)} existing bills")

    elif num_bills:
        logger.info(f"Fetching {num_bills} recent bills from Congress.gov...")
        try:
            bills_data = client.fetch_recent_bills(limit=num_bills)
            bills_to_fetch = [bill["bill_number"] for bill in bills_data]
            logger.info(f"✓ Fetched {len(bills_to_fetch)} bill identifiers")
        except CongressAPIError as e:
            logger.error(f"Failed to fetch bills: {e}")
            sys.exit(1)

    else:
        logger.error("Must specify --bills N, --bill-numbers, or --update-existing")
        sys.exit(1)

    # Fetch and save bill metadata
    logger.info("=" * 80)
    logger.info(f"Processing {len(bills_to_fetch)} bills")
    logger.info("=" * 80)

    successful_bills = []
    skipped_bills = []
    failed_bills = []

    for i, bill_number in enumerate(bills_to_fetch, 1):
        logger.info(f"\n[{i}/{len(bills_to_fetch)}] {bill_number}")

        metadata = fetch_bill_metadata(bill_number, client)

        if metadata:
            if save_bill_metadata(metadata):
                successful_bills.append(bill_number)
            else:
                failed_bills.append(bill_number)
        else:
            skipped_bills.append(bill_number)

        # Rate limiting
        time.sleep(0.5)

    # Update metadata index
    if successful_bills:
        update_metadata_index(successful_bills)

    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("FETCH COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Successful: {len(successful_bills)}")
    logger.info(f"Skipped:    {len(skipped_bills)} (post office bills)")
    logger.info(f"Failed:     {len(failed_bills)}")
    logger.info(f"Total:      {len(bills_to_fetch)}")
    logger.info("=" * 80)

    # Save summary report
    summary = {
        "timestamp": datetime.now().isoformat(),
        "bills_requested": len(bills_to_fetch),
        "successful": len(successful_bills),
        "skipped": len(skipped_bills),
        "failed": len(failed_bills),
        "successful_bills": successful_bills,
        "skipped_bills": skipped_bills,
        "failed_bills": failed_bills,
    }

    summary_path = Config.LOGS_DIR / f"fetch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    logger.info(f"Summary saved to {summary_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch bill metadata from Congress.gov (no AI analysis)"
    )

    parser.add_argument(
        "--bills",
        type=int,
        help="Number of recent bills to fetch",
    )

    parser.add_argument(
        "--bill-numbers",
        nargs="+",
        help="Specific bill numbers to fetch (e.g., 'H.R. 1234' 'S. 5678')",
    )

    parser.add_argument(
        "--update-existing",
        action="store_true",
        help="Update metadata for all existing bills",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose (DEBUG) logging",
    )

    args = parser.parse_args()

    main(
        num_bills=args.bills,
        bill_numbers=args.bill_numbers,
        update_existing=args.update_existing,
        verbose=args.verbose,
    )
