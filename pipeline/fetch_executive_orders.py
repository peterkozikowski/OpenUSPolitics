#!/usr/bin/env python3
"""
Executive Orders fetching pipeline for OpenUSPolitics.org.

This script fetches executive orders from the Federal Register API and stores them
as JSON files for the frontend to consume.

Usage:
    python fetch_executive_orders.py --limit 50
    python fetch_executive_orders.py --president "joe-biden"
    python fetch_executive_orders.py --start-date "2024-01-01"
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from fetchers.federal_register import FederalRegisterClient, FederalRegisterAPIError

# ============================================================================
# Configuration
# ============================================================================

# Paths
PIPELINE_DIR = Path(__file__).parent
DATA_DIR = PIPELINE_DIR / "data" / "executive-orders"
METADATA_FILE = DATA_DIR / "metadata.json"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            PIPELINE_DIR
            / "logs"
            / f"eo_pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        ),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


# ============================================================================
# Helper Functions
# ============================================================================


def sanitize_eo_number(eo_number: str) -> str:
    """
    Sanitize executive order number for use as filename.

    Args:
        eo_number: Executive order number (e.g., "14110")

    Returns:
        Sanitized filename (e.g., "EO_14110")
    """
    return f"EO_{eo_number.replace(' ', '_')}"


def save_executive_order(order: Dict) -> None:
    """
    Save executive order data to JSON file.

    Args:
        order: Executive order dictionary
    """
    eo_number = order.get("executive_order_number", "unknown")
    filename = sanitize_eo_number(eo_number) + ".json"
    filepath = DATA_DIR / filename

    # Add metadata
    order["last_updated"] = datetime.now().isoformat()

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(order, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved executive order: {eo_number} to {filename}")


def update_metadata(orders: List[Dict]) -> None:
    """
    Update metadata.json index file.

    Args:
        orders: List of executive order dictionaries
    """
    metadata = {
        "executive_orders": {},
        "total_orders": len(orders),
        "last_updated": datetime.now().isoformat(),
    }

    for order in orders:
        eo_number = order.get("executive_order_number")
        if not eo_number:
            continue

        eo_id = f"EO {eo_number}"
        filename = sanitize_eo_number(eo_number) + ".json"

        metadata["executive_orders"][eo_id] = {
            "file": filename,
            "title": order.get("title", ""),
            "president": order.get("president", ""),
            "signing_date": order.get("signing_date", ""),
            "last_updated": order.get("last_updated", datetime.now().isoformat()),
        }

    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    logger.info(f"Updated metadata file with {len(orders)} executive orders")


def load_existing_orders() -> Dict[str, Dict]:
    """
    Load existing executive orders from metadata file.

    Returns:
        Dictionary of existing orders keyed by EO number
    """
    if not METADATA_FILE.exists():
        return {}

    try:
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            metadata = json.load(f)
            return metadata.get("executive_orders", {})
    except Exception as e:
        logger.warning(f"Could not load existing metadata: {e}")
        return {}


def filter_significant_orders(orders: List[Dict]) -> List[Dict]:
    """
    Filter out minor administrative executive orders.

    Similar to filtering post office bills, we want to exclude:
    - Orders that are just administrative housekeeping
    - Orders that simply extend other orders

    Args:
        orders: List of executive order dictionaries

    Returns:
        Filtered list of significant orders
    """
    significant = []

    for order in orders:
        title = order.get("title", "").lower()

        # Skip simple extensions/amendments unless they're significant
        skip_phrases = [
            "continuation of the national emergency",
            "continuation of emergency",
        ]

        # Keep if it doesn't match skip phrases
        if not any(phrase in title for phrase in skip_phrases):
            significant.append(order)
        # Or if it has substantial content (long title usually means important)
        elif len(title) > 100:
            significant.append(order)

    logger.info(
        f"Filtered {len(orders)} orders down to {len(significant)} significant orders"
    )
    return significant


# ============================================================================
# Main Pipeline
# ============================================================================


def fetch_executive_orders(
    limit: int = 50,
    president: str = None,
    start_date: str = None,
    end_date: str = None,
    skip_existing: bool = True,
) -> List[Dict]:
    """
    Fetch executive orders from Federal Register API.

    Args:
        limit: Maximum number of orders to fetch
        president: Filter by president name (e.g., "joe-biden")
        start_date: Start date in ISO format (YYYY-MM-DD)
        end_date: End date in ISO format (YYYY-MM-DD)
        skip_existing: Skip orders that already exist

    Returns:
        List of fetched executive order dictionaries
    """
    logger.info("=" * 80)
    logger.info("Starting Executive Orders Pipeline")
    logger.info("=" * 80)

    # Initialize API client
    client = FederalRegisterClient()

    # Fetch orders
    logger.info(f"Fetching up to {limit} executive orders...")
    if president:
        logger.info(f"Filtering by president: {president}")
    if start_date or end_date:
        logger.info(f"Date range: {start_date or 'any'} to {end_date or 'any'}")

    try:
        orders = client.fetch_recent_executive_orders(
            limit=limit, president=president, start_date=start_date, end_date=end_date
        )

        logger.info(f"Fetched {len(orders)} executive orders from API")

        # Filter significant orders
        orders = filter_significant_orders(orders)

        # Load existing orders
        if skip_existing:
            existing = load_existing_orders()
            new_orders = []

            for order in orders:
                eo_id = f"EO {order.get('executive_order_number')}"
                if eo_id not in existing:
                    new_orders.append(order)

            logger.info(
                f"Found {len(new_orders)} new orders (skipping {len(orders) - len(new_orders)} existing)"
            )
            orders = new_orders

        # Save each order
        for order in orders:
            save_executive_order(order)

        # Update metadata (reload all orders from disk to get complete list)
        all_orders = []
        for filepath in DATA_DIR.glob("EO_*.json"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    all_orders.append(json.load(f))
            except Exception as e:
                logger.warning(f"Could not load {filepath}: {e}")

        update_metadata(all_orders)

        logger.info("=" * 80)
        logger.info(
            f"Pipeline completed successfully! Processed {len(orders)} executive orders"
        )
        logger.info("=" * 80)

        return orders

    except FederalRegisterAPIError as e:
        logger.error(f"API error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise


# ============================================================================
# CLI
# ============================================================================


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Fetch executive orders from Federal Register API"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum number of executive orders to fetch (default: 50)",
    )

    parser.add_argument(
        "--president",
        type=str,
        help="Filter by president name (e.g., 'joe-biden', 'donald-trump')",
    )

    parser.add_argument(
        "--start-date", type=str, help="Start date in YYYY-MM-DD format"
    )

    parser.add_argument("--end-date", type=str, help="End date in YYYY-MM-DD format")

    parser.add_argument(
        "--no-skip-existing",
        action="store_true",
        help="Re-fetch existing executive orders",
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        fetch_executive_orders(
            limit=args.limit,
            president=args.president,
            start_date=args.start_date,
            end_date=args.end_date,
            skip_existing=not args.no_skip_existing,
        )
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
