"""Git-based storage for bill analyses with version control."""

import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from config import Config

logger = logging.getLogger(__name__)


class GitStoreError(Exception):
    """Custom exception for git storage errors."""
    pass


def save_analysis(bill_number: str, data: Dict, auto_commit: bool = Config.GIT_AUTO_COMMIT) -> Path:
    """
    Save bill analysis to JSON file with optional git commit.

    Args:
        bill_number: Bill identifier (e.g., "H.R. 1234")
        data: Analysis data to save
        auto_commit: Whether to automatically commit to git

    Returns:
        Path to saved file

    Raises:
        GitStoreError: If save or commit fails
    """
    logger.info(f"Saving analysis for {bill_number}")

    try:
        # Ensure directories exist
        Config.setup_directories()

        # Sanitize bill number for filename
        safe_bill_number = _sanitize_filename(bill_number)
        filepath = Config.BILLS_DIR / f"{safe_bill_number}.json"

        # Add metadata
        data["_metadata"] = {
            "bill_number": bill_number,
            "saved_at": datetime.utcnow().isoformat(),
            "version": data.get("_metadata", {}).get("version", 1) + 1 if filepath.exists() else 1,
        }

        # Save to JSON
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved analysis to {filepath}")

        # Update metadata index
        update_metadata(bill_number, {
            "file": str(filepath.relative_to(Config.DATA_DIR)),
            "last_updated": datetime.utcnow().isoformat(),
        })

        # Commit to git if enabled
        if auto_commit:
            _git_commit(filepath, bill_number)

        return filepath

    except Exception as e:
        logger.error(f"Failed to save analysis: {e}")
        raise GitStoreError(f"Failed to save analysis: {e}") from e


def load_analysis(bill_number: str) -> Optional[Dict]:
    """
    Load bill analysis from JSON file.

    Args:
        bill_number: Bill identifier

    Returns:
        Analysis data dictionary, or None if not found

    Raises:
        GitStoreError: If load fails
    """
    logger.info(f"Loading analysis for {bill_number}")

    try:
        safe_bill_number = _sanitize_filename(bill_number)
        filepath = Config.BILLS_DIR / f"{safe_bill_number}.json"

        if not filepath.exists():
            logger.warning(f"Analysis not found for {bill_number}")
            return None

        with open(filepath, "r") as f:
            data = json.load(f)

        logger.info(f"Loaded analysis from {filepath}")
        return data

    except Exception as e:
        logger.error(f"Failed to load analysis: {e}")
        raise GitStoreError(f"Failed to load analysis: {e}") from e


def update_metadata(bill_number: str, info: Dict) -> None:
    """
    Update the metadata index with bill information.

    Args:
        bill_number: Bill identifier
        info: Metadata to store

    Raises:
        GitStoreError: If update fails
    """
    logger.debug(f"Updating metadata for {bill_number}")

    try:
        Config.setup_directories()

        # Load existing metadata
        metadata = {}
        if Config.METADATA_FILE.exists():
            with open(Config.METADATA_FILE, "r") as f:
                metadata = json.load(f)

        # Update bill entry
        if "bills" not in metadata:
            metadata["bills"] = {}

        metadata["bills"][bill_number] = {
            **metadata["bills"].get(bill_number, {}),
            **info,
        }

        metadata["last_updated"] = datetime.utcnow().isoformat()
        metadata["total_bills"] = len(metadata["bills"])

        # Save metadata
        with open(Config.METADATA_FILE, "w") as f:
            json.dump(metadata, f, indent=2)

        logger.debug(f"Updated metadata for {bill_number}")

    except Exception as e:
        logger.error(f"Failed to update metadata: {e}")
        raise GitStoreError(f"Failed to update metadata: {e}") from e


def _sanitize_filename(bill_number: str) -> str:
    """
    Sanitize bill number for use in filenames.

    Args:
        bill_number: Bill identifier

    Returns:
        Sanitized filename
    """
    # Replace problematic characters
    safe_name = bill_number.replace(" ", "_").replace(".", "")
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in "_-")
    return safe_name


def _git_commit(filepath: Path, bill_number: str) -> None:
    """
    Commit file changes to git.

    Args:
        filepath: Path to file to commit
        bill_number: Bill identifier for commit message

    Raises:
        GitStoreError: If git commit fails
    """
    try:
        # Check if git repo exists
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=filepath.parent,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            logger.warning("Not a git repository - skipping commit")
            return

        # Add file
        subprocess.run(
            ["git", "add", str(filepath), str(Config.METADATA_FILE)],
            cwd=Config.DATA_DIR,
            check=True,
            capture_output=True,
            text=True,
        )

        # Commit
        commit_message = f"Update analysis for {bill_number}\n\nAutomated commit from OpenUSPolitics.org pipeline"

        subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=Config.DATA_DIR,
            check=True,
            capture_output=True,
            text=True,
        )

        logger.info(f"Committed changes for {bill_number} to git")

    except subprocess.CalledProcessError as e:
        # Don't fail if nothing to commit
        if "nothing to commit" in e.stderr.lower():
            logger.debug("No changes to commit")
        else:
            logger.warning(f"Git commit failed: {e.stderr}")
            # Don't raise - we don't want to fail the entire save if git fails
    except Exception as e:
        logger.warning(f"Git commit failed: {e}")
        # Don't raise - we don't want to fail the entire save if git fails


def get_metadata() -> Dict:
    """
    Load metadata.json index.

    Returns:
        Complete metadata dictionary with bills index and summary stats

    Raises:
        GitStoreError: If read fails
    """
    logger.info("Loading metadata index")

    try:
        if not Config.METADATA_FILE.exists():
            logger.warning("Metadata file not found, returning empty")
            return {
                "bills": {},
                "total_bills": 0,
                "last_updated": None
            }

        with open(Config.METADATA_FILE, "r") as f:
            metadata = json.load(f)

        logger.info(f"Loaded metadata: {metadata.get('total_bills', 0)} bills")
        return metadata

    except Exception as e:
        logger.error(f"Failed to load metadata: {e}")
        raise GitStoreError(f"Failed to load metadata: {e}") from e


def get_all_bills() -> Dict[str, Dict]:
    """
    Get metadata for all stored bills.

    Returns:
        Dictionary mapping bill numbers to metadata

    Raises:
        GitStoreError: If read fails
    """
    metadata = get_metadata()
    return metadata.get("bills", {})


def bill_needs_update(bill_number: str, current_version: Optional[str] = None) -> bool:
    """
    Check if a bill analysis needs updating.

    Args:
        bill_number: Bill identifier
        current_version: Current version from Congress API (if available)

    Returns:
        True if bill should be re-analyzed, False otherwise
    """
    try:
        safe_bill_number = _sanitize_filename(bill_number)
        filepath = Config.BILLS_DIR / f"{safe_bill_number}.json"

        if not filepath.exists():
            return True  # New bill, needs analysis

        # Load existing analysis
        with open(filepath, "r") as f:
            existing_data = json.load(f)

        # Check if version has changed (if provided)
        if current_version:
            stored_version = existing_data.get("bill_version")
            if stored_version != current_version:
                logger.info(f"Bill {bill_number} version changed: {stored_version} -> {current_version}")
                return True

        # Check age of analysis (re-analyze if older than 30 days)
        metadata = existing_data.get("_metadata", {})
        saved_at_str = metadata.get("saved_at")
        if saved_at_str:
            saved_at = datetime.fromisoformat(saved_at_str)
            age_days = (datetime.utcnow() - saved_at).days
            if age_days > 30:
                logger.info(f"Bill {bill_number} analysis is {age_days} days old, needs refresh")
                return True

        logger.debug(f"Bill {bill_number} analysis is current")
        return False

    except Exception as e:
        logger.warning(f"Error checking if bill needs update: {e}")
        return True  # When in doubt, update


def delete_analysis(bill_number: str, auto_commit: bool = Config.GIT_AUTO_COMMIT) -> None:
    """
    Delete bill analysis and update metadata.

    Args:
        bill_number: Bill identifier
        auto_commit: Whether to automatically commit to git

    Raises:
        GitStoreError: If deletion fails
    """
    logger.info(f"Deleting analysis for {bill_number}")

    try:
        safe_bill_number = _sanitize_filename(bill_number)
        filepath = Config.BILLS_DIR / f"{safe_bill_number}.json"

        if not filepath.exists():
            logger.warning(f"Analysis not found for {bill_number}")
            return

        # Delete file
        filepath.unlink()

        # Update metadata
        if Config.METADATA_FILE.exists():
            with open(Config.METADATA_FILE, "r") as f:
                metadata = json.load(f)

            if "bills" in metadata and bill_number in metadata["bills"]:
                del metadata["bills"][bill_number]
                metadata["total_bills"] = len(metadata["bills"])
                metadata["last_updated"] = datetime.utcnow().isoformat()

                with open(Config.METADATA_FILE, "w") as f:
                    json.dump(metadata, f, indent=2)

        logger.info(f"Deleted analysis for {bill_number}")

        # Commit deletion if enabled
        if auto_commit:
            try:
                subprocess.run(
                    ["git", "rm", str(filepath)],
                    cwd=Config.DATA_DIR,
                    check=True,
                    capture_output=True,
                    text=True,
                )

                subprocess.run(
                    ["git", "commit", "-m", f"Delete analysis for {bill_number}"],
                    cwd=Config.DATA_DIR,
                    check=True,
                    capture_output=True,
                    text=True,
                )

                logger.info(f"Committed deletion of {bill_number} to git")
            except subprocess.CalledProcessError:
                logger.warning("Git commit of deletion failed")

    except Exception as e:
        logger.error(f"Failed to delete analysis: {e}")
        raise GitStoreError(f"Failed to delete analysis: {e}") from e


if __name__ == "__main__":
    # Test the git store
    logging.basicConfig(level=logging.INFO)

    # Test data
    test_data = {
        "bill_number": "H.R. TEST",
        "title": "Test Bill Act",
        "analysis": "This is a test analysis.",
        "summary": "Test summary",
    }

    try:
        # Save
        filepath = save_analysis("H.R. TEST", test_data, auto_commit=False)
        print(f"Saved to: {filepath}")

        # Load
        loaded_data = load_analysis("H.R. TEST")
        print(f"Loaded: {loaded_data.get('title')}")

        # Get all
        all_bills = get_all_bills()
        print(f"Total bills: {len(all_bills)}")

        # Delete
        delete_analysis("H.R. TEST", auto_commit=False)
        print("Deleted test bill")

    except GitStoreError as e:
        print(f"Error: {e}")
