"""
Federal Register API client for OpenUSPolitics.org.

This module provides a client for interacting with the Federal Register API
to fetch executive orders and presidential documents.

API Documentation: https://www.federalregister.gov/developers/documentation/api/v1
"""

import logging
import time
from typing import Dict, List, Optional
from datetime import datetime

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

logger = logging.getLogger(__name__)


# ============================================================================
# Custom Exceptions
# ============================================================================


class FederalRegisterAPIError(Exception):
    """Base exception for Federal Register API errors."""

    pass


class ExecutiveOrderNotFoundError(FederalRegisterAPIError):
    """Raised when an executive order cannot be found."""

    pass


class APIRateLimitError(FederalRegisterAPIError):
    """Raised when API rate limit is exceeded."""

    pass


class APIConnectionError(FederalRegisterAPIError):
    """Raised when there's a connection error to the API."""

    pass


# ============================================================================
# Federal Register API Client
# ============================================================================


class FederalRegisterClient:
    """
    Client for interacting with the Federal Register API.

    Features:
    - No API key required (public API)
    - Session pooling for efficient connection reuse
    - Exponential backoff retry logic
    - Response caching with TTL
    - Comprehensive error handling

    Example:
        >>> client = FederalRegisterClient()
        >>> orders = client.fetch_recent_executive_orders(limit=10)
        >>> for order in orders:
        ...     print(order['executive_order_number'], order['title'])
    """

    def __init__(self):
        """Initialize the Federal Register API client."""
        self.base_url = "https://www.federalregister.gov/api/v1"
        self.rate_limit = 2  # requests per second (conservative)
        self.last_request_time = 0

        # Session pooling for connection reuse
        self.session = requests.Session()

        # Configure retry strategy
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

        logger.info("FederalRegisterClient initialized")

    def _rate_limit_wait(self) -> None:
        """Implement rate limiting between requests."""
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
        Make a request to the Federal Register API with retry logic and caching.

        Args:
            endpoint: API endpoint path (e.g., "articles.json")
            params: Query parameters

        Returns:
            JSON response as dictionary

        Raises:
            ExecutiveOrderNotFoundError: If the requested resource is not found (404)
            APIRateLimitError: If rate limit is exceeded (429)
            APIConnectionError: If there's a connection error
            FederalRegisterAPIError: For other API errors
        """
        # Check cache first
        cache_key = self._get_cache_key(endpoint, params)
        if cache_key in self.cache:
            logger.debug(f"Cache hit for {endpoint}")
            return self.cache[cache_key]

        self._rate_limit_wait()

        url = f"{self.base_url}/{endpoint}"
        params = params or {}

        logger.debug(f"[{datetime.now().isoformat()}] Making request to {endpoint}")

        try:
            response = self.session.get(url, params=params, timeout=30)

            if response.status_code == 404:
                raise ExecutiveOrderNotFoundError(f"Resource not found: {endpoint}")
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
            raise FederalRegisterAPIError(f"Request failed: {e}") from e

    # ========================================================================
    # Main API Methods
    # ========================================================================

    def fetch_recent_executive_orders(
        self,
        limit: int = 20,
        president: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Dict]:
        """
        Fetch recent executive orders from Federal Register.

        Args:
            limit: Number of executive orders to fetch (max 1000 per request)
            president: Filter by president name (e.g., "joe-biden", "donald-trump")
            start_date: Start date in ISO format (YYYY-MM-DD)
            end_date: End date in ISO format (YYYY-MM-DD)

        Returns:
            List of executive order dictionaries with:
                - executive_order_number: str (e.g., "14110")
                - title: str
                - president: str
                - signing_date: str (ISO 8601)
                - publication_date: str (ISO 8601)
                - document_number: str
                - html_url: str
                - full_text_xml_url: str
                - abstract: str
                - topic: List[str]

        Example:
            >>> client = FederalRegisterClient()
            >>> orders = client.fetch_recent_executive_orders(limit=5, president="joe-biden")
            >>> print(orders[0]['executive_order_number'])
        """
        logger.info(f"Fetching {limit} recent executive orders")

        params = {
            "conditions[presidential_document_type_id]": 2,  # Executive orders
            "conditions[type]": "PRESDOCU",
            "per_page": min(limit, 1000),
            "order": "newest",
            "fields[]": [
                "executive_order_number",
                "title",
                "signing_date",
                "publication_date",
                "document_number",
                "html_url",
                "full_text_xml_url",
                "body_html_url",
                "abstract",
                "topics",
            ],
        }

        # Add optional filters
        if president:
            params["conditions[president]"] = president
        if start_date:
            params["conditions[publication_date][gte]"] = start_date
        if end_date:
            params["conditions[publication_date][lte]"] = end_date

        endpoint = "articles.json"
        response = self._make_request(endpoint, params)

        raw_orders = response.get("results", [])
        logger.info(f"Retrieved {len(raw_orders)} executive orders from API")

        # Format executive orders
        formatted_orders = []
        for raw_order in tqdm(
            raw_orders, desc="Processing executive orders", disable=len(raw_orders) < 10
        ):
            order_data = self._format_executive_order(raw_order)
            if order_data:  # Skip if no EO number (some administrative documents)
                formatted_orders.append(order_data)

        return formatted_orders

    def _format_executive_order(self, raw_order: Dict) -> Optional[Dict]:
        """Format raw executive order data into standardized structure."""
        # Skip if no executive order number (not a numbered EO)
        eo_number = raw_order.get("executive_order_number")
        if not eo_number:
            return None

        # Extract president from the data
        president = raw_order.get("president", {})
        president_name = (
            president.get("name", "Unknown")
            if isinstance(president, dict)
            else "Unknown"
        )

        # Get topics
        topics = [
            topic.get("name")
            for topic in raw_order.get("topics", [])
            if topic.get("name")
        ]

        return {
            "executive_order_number": str(eo_number),
            "title": raw_order.get("title", ""),
            "president": president_name,
            "signing_date": raw_order.get("signing_date", ""),
            "publication_date": raw_order.get("publication_date", ""),
            "document_number": raw_order.get("document_number", ""),
            "html_url": raw_order.get("html_url", ""),
            "full_text_xml_url": raw_order.get("full_text_xml_url", ""),
            "body_html_url": raw_order.get("body_html_url", ""),
            "abstract": raw_order.get("abstract", ""),
            "topics": topics,
        }

    def get_executive_order_details(self, document_number: str) -> Dict:
        """
        Get detailed information for a specific executive order.

        Args:
            document_number: Federal Register document number

        Returns:
            Detailed executive order information

        Raises:
            ExecutiveOrderNotFoundError: If executive order is not found

        Example:
            >>> client = FederalRegisterClient()
            >>> details = client.get_executive_order_details("2023-24283")
            >>> print(details['title'])
        """
        logger.info(f"Fetching details for document number: {document_number}")

        endpoint = f"articles/{document_number}.json"
        response = self._make_request(endpoint)

        raw_order = response
        if not raw_order:
            raise ExecutiveOrderNotFoundError(
                f"Executive order not found: {document_number}"
            )

        formatted = self._format_executive_order(raw_order)
        if not formatted:
            raise ExecutiveOrderNotFoundError(
                f"Not a valid executive order: {document_number}"
            )

        return formatted

    def get_executive_order_text(self, document_number: str) -> str:
        """
        Get the full text of an executive order.

        Args:
            document_number: Federal Register document number

        Returns:
            Full text of the executive order (HTML)

        Example:
            >>> client = FederalRegisterClient()
            >>> text = client.get_executive_order_text("2023-24283")
        """
        logger.info(f"Fetching full text for document number: {document_number}")

        # Get the body_html_url from the details
        details = self.get_executive_order_details(document_number)
        body_html_url = details.get("body_html_url")

        if not body_html_url:
            # Fall back to html_url
            body_html_url = details.get("html_url")

        if not body_html_url:
            raise ExecutiveOrderNotFoundError(
                f"No text URL found for {document_number}"
            )

        # Fetch the HTML content
        response = requests.get(body_html_url, timeout=30)
        response.raise_for_status()

        return response.text


# ============================================================================
# Convenience Functions
# ============================================================================


def fetch_recent_executive_orders(
    limit: int = 20, president: Optional[str] = None
) -> List[Dict]:
    """
    Convenience function to fetch recent executive orders.

    Args:
        limit: Number of executive orders to fetch
        president: Filter by president name

    Returns:
        List of formatted executive order dictionaries

    Example:
        >>> orders = fetch_recent_executive_orders(limit=5, president="joe-biden")
        >>> for order in orders:
        ...     print(f"EO {order['executive_order_number']}: {order['title']}")
    """
    client = FederalRegisterClient()
    return client.fetch_recent_executive_orders(limit=limit, president=president)


def get_executive_order_details(document_number: str) -> Dict:
    """
    Convenience function to get executive order details.

    Args:
        document_number: Federal Register document number

    Returns:
        Executive order information
    """
    client = FederalRegisterClient()
    return client.get_executive_order_details(document_number)


def get_executive_order_text(document_number: str) -> str:
    """
    Convenience function to get executive order text.

    Args:
        document_number: Federal Register document number

    Returns:
        Full text of the executive order
    """
    client = FederalRegisterClient()
    return client.get_executive_order_text(document_number)


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
        print("Testing Federal Register API Client")
        print("=" * 80)

        # Test 1: Fetch recent executive orders
        print("\n1. Fetching recent executive orders...")
        orders = fetch_recent_executive_orders(limit=5, president="joe-biden")
        for order in orders:
            print(f"\n  EO {order['executive_order_number']}: {order['title'][:80]}...")
            print(f"  President: {order['president']}")
            print(f"  Signed: {order['signing_date']}")
            print(f"  Topics: {', '.join(order['topics'][:3])}")

        # Test 2: Get executive order details
        if orders:
            print(
                f"\n2. Getting details for EO {orders[0]['executive_order_number']}..."
            )
            details = get_executive_order_details(orders[0]["document_number"])
            print(f"  Document Number: {details['document_number']}")
            print(f"  URL: {details['html_url']}")

        print("\n" + "=" * 80)
        print("All tests completed successfully!")
        print("=" * 80)

    except Exception as e:
        logger.error(f"Error during testing: {e}", exc_info=True)
