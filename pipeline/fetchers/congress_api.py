"""
Production-ready Congress.gov API client for OpenUSPolitics.org.

This module provides a comprehensive client for interacting with the Congress.gov API v3,
including rate limiting, retry logic, caching, and detailed error handling.

API Documentation: https://api.congress.gov/
"""

import logging
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import re

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry as UrlLibRetry
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from cachetools import TTLCache
from tqdm import tqdm

from config import Config

logger = logging.getLogger(__name__)


# ============================================================================
# Custom Exceptions
# ============================================================================


class CongressAPIError(Exception):
    """Base exception for Congress API errors."""

    pass


class BillNotFoundError(CongressAPIError):
    """Raised when a bill cannot be found."""

    pass


class APIRateLimitError(CongressAPIError):
    """Raised when API rate limit is exceeded."""

    pass


class APIConnectionError(CongressAPIError):
    """Raised when there's a connection error to the API."""

    pass


# ============================================================================
# Congress API Client
# ============================================================================


class CongressAPIClient:
    """
    Client for interacting with the Congress.gov API v3.

    Features:
    - Session pooling for efficient connection reuse
    - Rate limiting (1000 requests/hour)
    - Exponential backoff retry logic
    - Response caching with TTL
    - Comprehensive error handling
    - Progress bars for bulk operations

    Example:
        >>> client = CongressAPIClient()
        >>> bills = client.fetch_recent_bills(limit=10, congress=118, bill_type="hr")
        >>> for bill in bills:
        ...     print(bill['bill_number'], bill['title'])
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Congress API client.

        Args:
            api_key: Congress.gov API key. If not provided, uses Config.CONGRESS_API_KEY

        Raises:
            ValueError: If no API key is provided
        """
        self.api_key = api_key or Config.CONGRESS_API_KEY
        if not self.api_key:
            raise ValueError(
                "Congress API key is required. Set CONGRESS_API_KEY in environment."
            )

        self.base_url = Config.CONGRESS_API_BASE_URL
        self.rate_limit = Config.CONGRESS_API_RATE_LIMIT  # requests per second
        self.last_request_time = 0

        # Session pooling for connection reuse
        self.session = requests.Session()

        # Configure retry strategy at the urllib3 level
        retry_strategy = UrlLibRetry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy, pool_connections=10, pool_maxsize=20
        )
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        # Response cache with 5-minute TTL
        self.cache = TTLCache(maxsize=1000, ttl=300)

        logger.info(
            "CongressAPIClient initialized with rate limit: %s req/s", self.rate_limit
        )

    def _rate_limit_wait(self) -> None:
        """Implement rate limiting between requests (1000 req/hour = ~0.28 req/sec)."""
        if self.rate_limit > 0:
            time_since_last_request = time.time() - self.last_request_time
            min_interval = 1.0 / self.rate_limit
            wait_time = min_interval - time_since_last_request
            if wait_time > 0:
                time.sleep(wait_time)
        self.last_request_time = time.time()

    def _get_cache_key(self, endpoint: str, params: Optional[Dict] = None) -> str:
        """Generate cache key from endpoint and params."""
        params_str = str(sorted((params or {}).items()))
        return f"{endpoint}:{params_str}"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((APIConnectionError, APIRateLimitError)),
    )
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the Congress API with retry logic and caching.

        Args:
            endpoint: API endpoint path (e.g., "bill/118/hr/1")
            params: Query parameters

        Returns:
            JSON response as dictionary

        Raises:
            BillNotFoundError: If the requested resource is not found (404)
            APIRateLimitError: If rate limit is exceeded (429)
            APIConnectionError: If there's a connection error
            CongressAPIError: For other API errors
        """
        # Check cache first
        cache_key = self._get_cache_key(endpoint, params)
        if cache_key in self.cache:
            logger.debug(f"Cache hit for {endpoint}")
            return self.cache[cache_key]

        self._rate_limit_wait()

        url = f"{self.base_url}/{endpoint}"
        params = params or {}
        params["api_key"] = self.api_key

        logger.debug(f"[{datetime.now().isoformat()}] Making request to {endpoint}")

        try:
            response = self.session.get(url, params=params, timeout=30)

            if response.status_code == 404:
                raise BillNotFoundError(f"Resource not found: {endpoint}")
            elif response.status_code == 429:
                logger.warning("Rate limit exceeded, retrying with backoff...")
                raise APIRateLimitError("API rate limit exceeded")
            elif response.status_code >= 500:
                logger.warning(f"Server error {response.status_code}, retrying...")
                raise APIConnectionError(f"Server error: {response.status_code}")

            response.raise_for_status()
            data = response.json()

            # Cache the response
            self.cache[cache_key] = data

            return data

        except requests.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise APIConnectionError(f"Connection failed: {e}") from e
        except requests.Timeout as e:
            logger.error(f"Request timeout: {e}")
            raise APIConnectionError(f"Request timeout: {e}") from e
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise CongressAPIError(f"Request failed: {e}") from e

    def _parse_bill_number(self, bill_number: str) -> tuple:
        """
        Parse bill number string into components.

        Args:
            bill_number: e.g., "H.R. 1234" or "S. 456"

        Returns:
            Tuple of (bill_type, number) e.g., ("hr", 1234)
        """
        # Remove dots and spaces, convert to lowercase
        clean = bill_number.replace(".", "").replace(" ", "").lower()

        # Extract type and number using regex
        match = re.match(r"([a-z]+)(\d+)", clean)
        if not match:
            raise ValueError(f"Invalid bill number format: {bill_number}")

        bill_type = match.group(1)
        number = int(match.group(2))

        return bill_type, number

    # ========================================================================
    # Main API Methods
    # ========================================================================

    def fetch_recent_bills(
        self, limit: int = 10, congress: int = 118, bill_type: str = "hr"
    ) -> List[Dict]:
        """
        Fetch most recent bills from Congress.gov.

        Args:
            limit: Number of bills to fetch (max 250 per request)
            congress: Congress number (default 118 for current)
            bill_type: "hr" (House), "s" (Senate), "hjres", "sjres"

        Returns:
            List of bill dictionaries with:
                - bill_number: str (e.g., "H.R. 1234")
                - title: str
                - sponsor: Dict (name, party, state, bioguide_id)
                - cosponsors_count: int
                - status: str
                - introduced_date: str (ISO 8601)
                - last_updated: str (ISO 8601)
                - text_url: str (link to bill text)
                - congress_gov_url: str
                - topic: List[str] (policy areas)

        Example:
            >>> client = CongressAPIClient()
            >>> bills = client.fetch_recent_bills(limit=5, congress=118, bill_type="hr")
            >>> print(bills[0]['bill_number'])  # "H.R. 1234"
        """
        logger.info(
            f"Fetching {limit} recent bills from {congress}th Congress ({bill_type})"
        )

        params = {
            "limit": min(limit, 250),
            "sort": "updateDate+desc",
            "format": "json",
        }

        endpoint = f"bill/{congress}/{bill_type.lower()}"
        response = self._make_request(endpoint, params)

        raw_bills = response.get("bills", [])
        logger.info(f"Retrieved {len(raw_bills)} bills from API")

        # Format bills with detailed information
        formatted_bills = []
        for raw_bill in tqdm(
            raw_bills, desc="Processing bills", disable=len(raw_bills) < 10
        ):
            bill_data = self._format_bill(raw_bill, congress)
            formatted_bills.append(bill_data)

        return formatted_bills

    def _format_bill(self, raw_bill: Dict, congress: int) -> Dict:
        """Format raw bill data into standardized structure."""
        bill_number = raw_bill.get("number", "")
        bill_type = raw_bill.get("type", "").lower()

        # Format bill number (e.g., "H.R. 1234")
        formatted_number = self._format_bill_number(bill_type, bill_number)

        # Extract sponsor information
        sponsors = raw_bill.get("sponsors", [])
        sponsor = {}
        if sponsors:
            sponsor_data = sponsors[0]
            sponsor = {
                "name": sponsor_data.get("fullName", "Unknown"),
                "party": sponsor_data.get("party", ""),
                "state": sponsor_data.get("state", ""),
                "bioguide_id": sponsor_data.get("bioguideId", ""),
            }

        # Get policy area/topics
        policy_area = raw_bill.get("policyArea", {})
        topics = [policy_area.get("name")] if policy_area.get("name") else []

        # Build congress.gov URL
        congress_gov_url = f"https://www.congress.gov/bill/{congress}th-congress/{bill_type}-bill/{bill_number}"

        return {
            "bill_number": formatted_number,
            "title": raw_bill.get("title", ""),
            "sponsor": sponsor,
            "cosponsors_count": len(raw_bill.get("cosponsors", [])),
            "status": raw_bill.get("latestAction", {}).get("text", "Unknown"),
            "introduced_date": raw_bill.get("introducedDate", ""),
            "last_updated": raw_bill.get("updateDate", ""),
            "text_url": raw_bill.get("textVersions", {}).get("url", ""),
            "congress_gov_url": congress_gov_url,
            "topic": topics,
        }

    def _format_bill_number(self, bill_type: str, number: str) -> str:
        """Format bill type and number into standard format."""
        type_map = {
            "hr": "H.R.",
            "s": "S.",
            "hjres": "H.J.Res.",
            "sjres": "S.J.Res.",
            "hconres": "H.Con.Res.",
            "sconres": "S.Con.Res.",
            "hres": "H.Res.",
            "sres": "S.Res.",
        }
        formatted_type = type_map.get(bill_type.lower(), bill_type.upper())
        return f"{formatted_type} {number}"

    def get_bill_text(self, bill_number: str, congress: int = 118) -> Dict:
        """
        Get bill text metadata including URL and version info.

        Args:
            bill_number: e.g., "H.R. 1234" or "S. 456"
            congress: Congress number

        Returns:
            Dictionary with:
                - url: URL to bill text
                - version: Text version identifier
                - type: Format type (HTML, PDF, etc.)

        Raises:
            BillNotFoundError: If bill text is not available

        Example:
            >>> client = CongressAPIClient()
            >>> text_data = client.get_bill_text("H.R. 1234", congress=118)
            >>> print(text_data['url'])
        """
        bill_type, number = self._parse_bill_number(bill_number)

        endpoint = f"bill/{congress}/{bill_type}/{number}/text"
        logger.info(f"Fetching text for {bill_number} ({congress}th Congress)")

        try:
            response = self._make_request(endpoint)
            text_versions = response.get("textVersions", [])

            if not text_versions:
                raise BillNotFoundError(f"No text available for {bill_number}")

            # Get the most recent version
            latest_version = text_versions[0]
            formats = latest_version.get("formats", [])

            # Prefer formats in order: HTML, PDF, XML
            format_priority = ["Formatted Text", "PDF", "XML"]
            text_url = None
            format_type = None

            for priority_format in format_priority:
                for fmt in formats:
                    if priority_format.lower() in fmt.get("type", "").lower():
                        text_url = fmt.get("url")
                        format_type = fmt.get("type")
                        break
                if text_url:
                    break

            if not text_url and formats:
                text_url = formats[0].get("url")
                format_type = formats[0].get("type")

            if not text_url:
                raise BillNotFoundError(f"No text URL found for {bill_number}")

            # Return metadata (downloading happens in parser)
            return {
                "url": text_url,
                "version": latest_version.get("type", "Unknown"),
                "type": format_type or "Unknown",
            }

        except BillNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error fetching bill text: {e}")
            raise CongressAPIError(f"Failed to fetch bill text: {e}") from e

    def get_bill_details(self, bill_number: str, congress: int = 118) -> Dict:
        """
        Get comprehensive bill information.

        Args:
            bill_number: e.g., "H.R. 1234" or "S. 456"
            congress: Congress number

        Returns:
            Full bill metadata including:
                - All fields from fetch_recent_bills()
                - actions: List of legislative actions
                - committees: List of committees
                - related_bills: List of related bill numbers
                - subjects: Detailed policy area tags
                - cbo_cost_estimate: URL if available

        Example:
            >>> client = CongressAPIClient()
            >>> details = client.get_bill_details("H.R. 1234", congress=118)
            >>> print(details['actions'][:3])
        """
        bill_type, number = self._parse_bill_number(bill_number)

        endpoint = f"bill/{congress}/{bill_type}/{number}"
        logger.info(f"Fetching details for {bill_number} ({congress}th Congress)")

        response = self._make_request(endpoint)
        bill_data = response.get("bill", {})

        if not bill_data:
            raise BillNotFoundError(f"Bill not found: {bill_number}")

        # Format basic bill info
        formatted_bill = self._format_bill(bill_data, congress)

        # Add detailed information
        # Fetch actions
        actions = []
        if "actions" in bill_data and "url" in bill_data["actions"]:
            actions_endpoint = bill_data["actions"]["url"].replace(
                self.base_url + "/", ""
            )
            actions_response = self._make_request(actions_endpoint)
            actions = actions_response.get("actions", [])

        # Fetch committees
        committees = []
        if "committees" in bill_data and "url" in bill_data["committees"]:
            committees_endpoint = bill_data["committees"]["url"].replace(
                self.base_url + "/", ""
            )
            committees_response = self._make_request(committees_endpoint)
            committees = committees_response.get("committees", [])

        # Fetch related bills
        related_bills = []
        if "relatedBills" in bill_data and "url" in bill_data["relatedBills"]:
            related_endpoint = bill_data["relatedBills"]["url"].replace(
                self.base_url + "/", ""
            )
            related_response = self._make_request(related_endpoint)
            related_bills = related_response.get("relatedBills", [])

        # Fetch subjects
        subjects = []
        if "subjects" in bill_data and "url" in bill_data["subjects"]:
            subjects_endpoint = bill_data["subjects"]["url"].replace(
                self.base_url + "/", ""
            )
            subjects_response = self._make_request(subjects_endpoint)
            subjects = subjects_response.get("subjects", {}).get(
                "legislativeSubjects", []
            )

        # CBO cost estimate
        cbo_url = None
        if "cboCostEstimates" in bill_data:
            estimates = bill_data["cboCostEstimates"]
            if estimates and len(estimates) > 0:
                cbo_url = estimates[0].get("url", "")

        # Combine all data
        formatted_bill.update(
            {
                "actions": actions,
                "committees": [c.get("name", "") for c in committees],
                "related_bills": [
                    self._format_bill_number(rb.get("type", ""), rb.get("number", ""))
                    for rb in related_bills
                ],
                "subjects": [s.get("name", "") for s in subjects],
                "cbo_cost_estimate": cbo_url,
            }
        )

        return formatted_bill

    def get_representative(self, bioguide_id: str) -> Dict:
        """
        Get representative information.

        Args:
            bioguide_id: Bioguide ID of the representative

        Returns:
            Dict with:
                - name: Full name
                - party: Political party
                - state: State abbreviation
                - district: District number (for House members)
                - photo_url: URL to official photo
                - office: Office address

        Example:
            >>> client = CongressAPIClient()
            >>> rep = client.get_representative("P000197")
            >>> print(rep['name'], rep['party'])
        """
        endpoint = f"member/{bioguide_id}"
        logger.info(f"Fetching representative info for bioguide_id: {bioguide_id}")

        response = self._make_request(endpoint)
        member_data = response.get("member", {})

        if not member_data:
            raise BillNotFoundError(f"Representative not found: {bioguide_id}")

        # Get current term info
        terms = member_data.get("terms", [])
        current_term = terms[-1] if terms else {}

        return {
            "name": f"{member_data.get('firstName', '')} {member_data.get('lastName', '')}".strip(),
            "party": member_data.get("partyName", ""),
            "state": member_data.get("state", ""),
            "district": member_data.get("district", ""),
            "photo_url": member_data.get("depiction", {}).get("imageUrl", ""),
            "office": current_term.get("office", ""),
        }


# ============================================================================
# Convenience Functions
# ============================================================================


def fetch_recent_bills(
    limit: int = 10, congress: int = 118, bill_type: str = "hr"
) -> List[Dict]:
    """
    Convenience function to fetch recent bills.

    Args:
        limit: Number of bills to fetch (max 250)
        congress: Congress number (default 118)
        bill_type: "hr", "s", "hjres", "sjres", etc.

    Returns:
        List of formatted bill dictionaries

    Example:
        >>> bills = fetch_recent_bills(limit=5, congress=118, bill_type="s")
        >>> for bill in bills:
        ...     print(f"{bill['bill_number']}: {bill['title']}")
    """
    client = CongressAPIClient()
    return client.fetch_recent_bills(
        limit=limit, congress=congress, bill_type=bill_type
    )


def get_bill_text(bill_number: str, congress: int = 118) -> Dict:
    """
    Convenience function to get bill text metadata.

    Args:
        bill_number: e.g., "H.R. 1234"
        congress: Congress number

    Returns:
        Dictionary with url, version, and type
    """
    client = CongressAPIClient()
    return client.get_bill_text(bill_number=bill_number, congress=congress)


def get_bill_details(bill_number: str, congress: int = 118) -> Dict:
    """
    Convenience function to get bill details.

    Args:
        bill_number: e.g., "H.R. 1234"
        congress: Congress number

    Returns:
        Comprehensive bill information
    """
    client = CongressAPIClient()
    return client.get_bill_details(bill_number=bill_number, congress=congress)


def get_representative(bioguide_id: str) -> Dict:
    """
    Convenience function to get representative info.

    Args:
        bioguide_id: Bioguide ID

    Returns:
        Representative information
    """
    client = CongressAPIClient()
    return client.get_representative(bioguide_id=bioguide_id)


# ============================================================================
# Main / Testing
# ============================================================================

if __name__ == "__main__":
    # Test the API client
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        print("=" * 80)
        print("Testing Congress.gov API Client")
        print("=" * 80)

        # Test 1: Fetch recent bills
        print("\n1. Fetching recent House bills...")
        bills = fetch_recent_bills(limit=3, congress=118, bill_type="hr")
        for bill in bills:
            print(f"\n  {bill['bill_number']}: {bill['title'][:80]}...")
            print(
                f"  Sponsor: {bill['sponsor'].get('name', 'Unknown')} ({bill['sponsor'].get('party', '')})"
            )
            print(f"  Status: {bill['status'][:80]}...")
            print(f"  URL: {bill['congress_gov_url']}")

        # Test 2: Get bill details
        if bills:
            print(f"\n2. Getting details for {bills[0]['bill_number']}...")
            details = get_bill_details(bills[0]["bill_number"], congress=118)
            print(f"  Committees: {', '.join(details['committees'][:3])}")
            print(f"  Subjects: {', '.join(details['subjects'][:5])}")
            print(f"  Actions count: {len(details['actions'])}")

        # Test 3: Get representative (using a sponsor's bioguide_id)
        if bills and bills[0]["sponsor"].get("bioguide_id"):
            bioguide_id = bills[0]["sponsor"]["bioguide_id"]
            print(f"\n3. Getting representative info for {bioguide_id}...")
            rep = get_representative(bioguide_id)
            print(f"  Name: {rep['name']}")
            print(f"  Party: {rep['party']}")
            print(f"  State: {rep['state']}")

        print("\n" + "=" * 80)
        print("All tests completed successfully!")
        print("=" * 80)

    except Exception as e:
        logger.error(f"Error during testing: {e}", exc_info=True)
