"""Provenance tracking for bill analysis pipeline."""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class ProvenanceTracker:
    """
    Track data provenance and lineage throughout the pipeline.

    Records:
    - Source data (where bills came from)
    - Processing steps (when and how data was processed)
    - Analysis metadata (model versions, tokens, etc.)
    - Version history (changes over time)
    """

    def __init__(self):
        """Initialize the provenance tracker."""
        self.events: List[Dict] = []
        logger.info("Initialized provenance tracker")

    def record_fetch(
        self,
        bill_number: str,
        source: str,
        url: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> None:
        """
        Record a bill fetch event.

        Args:
            bill_number: Bill identifier
            source: Data source (e.g., "congress.gov API")
            url: Source URL
            metadata: Additional metadata
        """
        event = {
            "event_type": "fetch",
            "timestamp": datetime.utcnow().isoformat(),
            "bill_number": bill_number,
            "source": source,
            "url": url,
            "metadata": metadata or {},
        }

        self.events.append(event)
        logger.debug(f"Recorded fetch event for {bill_number}")

    def record_processing(
        self,
        bill_number: str,
        step: str,
        details: Optional[Dict] = None,
    ) -> None:
        """
        Record a processing step.

        Args:
            bill_number: Bill identifier
            step: Processing step name (e.g., "parsing", "chunking", "embedding")
            details: Step details (e.g., chunk count, parameters)
        """
        event = {
            "event_type": "processing",
            "timestamp": datetime.utcnow().isoformat(),
            "bill_number": bill_number,
            "step": step,
            "details": details or {},
        }

        self.events.append(event)
        logger.debug(f"Recorded {step} step for {bill_number}")

    def record_analysis(
        self,
        bill_number: str,
        analysis_type: str,
        model: str,
        tokens: Dict[str, int],
        chunks_used: List[str],
        metadata: Optional[Dict] = None,
    ) -> None:
        """
        Record an analysis event.

        Args:
            bill_number: Bill identifier
            analysis_type: Type of analysis (e.g., "summary", "qa", "full_analysis")
            model: Model used for analysis
            tokens: Token usage (input/output)
            chunks_used: List of chunk IDs used
            metadata: Additional metadata
        """
        event = {
            "event_type": "analysis",
            "timestamp": datetime.utcnow().isoformat(),
            "bill_number": bill_number,
            "analysis_type": analysis_type,
            "model": model,
            "tokens": tokens,
            "chunks_used": chunks_used,
            "metadata": metadata or {},
        }

        self.events.append(event)
        logger.debug(f"Recorded {analysis_type} analysis for {bill_number}")

    def record_storage(
        self,
        bill_number: str,
        storage_type: str,
        location: str,
        metadata: Optional[Dict] = None,
    ) -> None:
        """
        Record a storage event.

        Args:
            bill_number: Bill identifier
            storage_type: Type of storage (e.g., "json", "git", "database")
            location: Storage location
            metadata: Additional metadata
        """
        event = {
            "event_type": "storage",
            "timestamp": datetime.utcnow().isoformat(),
            "bill_number": bill_number,
            "storage_type": storage_type,
            "location": location,
            "metadata": metadata or {},
        }

        self.events.append(event)
        logger.debug(f"Recorded storage event for {bill_number}")

    def get_lineage(self, bill_number: str) -> List[Dict]:
        """
        Get complete lineage for a bill.

        Args:
            bill_number: Bill identifier

        Returns:
            List of events for this bill in chronological order
        """
        bill_events = [
            event for event in self.events if event.get("bill_number") == bill_number
        ]

        # Sort by timestamp
        bill_events.sort(key=lambda e: e["timestamp"])

        logger.info(f"Retrieved {len(bill_events)} events for {bill_number}")
        return bill_events

    def get_provenance_summary(self, bill_number: str) -> Dict:
        """
        Get a summary of provenance for a bill.

        Args:
            bill_number: Bill identifier

        Returns:
            Dictionary with provenance summary
        """
        lineage = self.get_lineage(bill_number)

        if not lineage:
            return {"bill_number": bill_number, "status": "not_found"}

        # Extract key information
        fetch_events = [e for e in lineage if e["event_type"] == "fetch"]
        processing_events = [e for e in lineage if e["event_type"] == "processing"]
        analysis_events = [e for e in lineage if e["event_type"] == "analysis"]
        storage_events = [e for e in lineage if e["event_type"] == "storage"]

        summary = {
            "bill_number": bill_number,
            "first_fetched": fetch_events[0]["timestamp"] if fetch_events else None,
            "source": fetch_events[0]["source"] if fetch_events else None,
            "processing_steps": [e["step"] for e in processing_events],
            "analyses_performed": [
                {
                    "type": e["analysis_type"],
                    "model": e["model"],
                    "timestamp": e["timestamp"],
                    "tokens": e["tokens"],
                }
                for e in analysis_events
            ],
            "storage_locations": [
                {"type": e["storage_type"], "location": e["location"]}
                for e in storage_events
            ],
            "total_events": len(lineage),
        }

        return summary

    def export_to_json(self, filepath: Path) -> None:
        """
        Export all provenance data to JSON.

        Args:
            filepath: Path to save JSON file
        """
        data = {
            "export_timestamp": datetime.utcnow().isoformat(),
            "total_events": len(self.events),
            "events": self.events,
        }

        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Exported {len(self.events)} events to {filepath}")

    def load_from_json(self, filepath: Path) -> None:
        """
        Load provenance data from JSON.

        Args:
            filepath: Path to JSON file
        """
        with open(filepath, "r") as f:
            data = json.load(f)

        self.events = data.get("events", [])

        logger.info(f"Loaded {len(self.events)} events from {filepath}")

    def clear(self) -> None:
        """Clear all recorded events."""
        count = len(self.events)
        self.events = []
        logger.info(f"Cleared {count} events")


if __name__ == "__main__":
    # Test the provenance tracker
    logging.basicConfig(level=logging.INFO)

    tracker = ProvenanceTracker()

    # Record some test events
    tracker.record_fetch(
        bill_number="H.R. 1234",
        source="congress.gov API",
        url="https://api.congress.gov/v3/bill/118/hr/1234",
        metadata={"congress": 118, "type": "hr"},
    )

    tracker.record_processing(
        bill_number="H.R. 1234",
        step="parsing",
        details={"format": "HTML", "size_chars": 50000},
    )

    tracker.record_processing(
        bill_number="H.R. 1234",
        step="chunking",
        details={"chunk_count": 25, "chunk_size": 1500},
    )

    tracker.record_analysis(
        bill_number="H.R. 1234",
        analysis_type="summary",
        model="claude-3-5-sonnet-20241022",
        tokens={"input": 5000, "output": 500},
        chunks_used=["H.R. 1234_chunk_0", "H.R. 1234_chunk_1"],
    )

    # Get lineage
    lineage = tracker.get_lineage("H.R. 1234")
    print(f"\nLineage for H.R. 1234: {len(lineage)} events")

    # Get summary
    summary = tracker.get_provenance_summary("H.R. 1234")
    print(f"\nProvenance Summary:")
    print(json.dumps(summary, indent=2))

    # Export
    test_path = Path("/tmp/provenance_test.json")
    tracker.export_to_json(test_path)
    print(f"\nExported to {test_path}")
