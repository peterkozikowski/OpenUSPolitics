"""
Comprehensive tests for Congress API client.

Tests cover:
- API client initialization
- Error handling and custom exceptions
- Rate limiting behavior
- Retry logic
- Caching functionality
- All API methods (bills, details, text, representatives)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import requests

from fetchers.congress_api import (
    CongressAPIClient,
    CongressAPIError,
    BillNotFoundError,
    APIRateLimitError,
    APIConnectionError,
    fetch_recent_bills,
    get_bill_text,
    get_bill_details,
    get_representative,
)


class TestCongressAPIClient:
    """Tests for CongressAPIClient class."""

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        client = CongressAPIClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.session is not None
        assert client.cache is not None

    def test_init_without_api_key_raises_error(self):
        """Test initialization without API key raises ValueError."""
        with patch("fetchers.congress_api.Config.CONGRESS_API_KEY", ""):
            with pytest.raises(ValueError, match="Congress API key is required"):
                CongressAPIClient()

    def test_cache_key_generation(self):
        """Test cache key generation from endpoint and params."""
        client = CongressAPIClient(api_key="test_key")
        key1 = client._get_cache_key("bill/118/hr", {"limit": 10})
        key2 = client._get_cache_key("bill/118/hr", {"limit": 10})
        key3 = client._get_cache_key("bill/118/hr", {"limit": 20})

        assert key1 == key2
        assert key1 != key3

    def test_parse_bill_number_hr(self):
        """Test parsing House bill number."""
        client = CongressAPIClient(api_key="test_key")
        bill_type, number = client._parse_bill_number("H.R. 1234")
        assert bill_type == "hr"
        assert number == 1234

    def test_parse_bill_number_senate(self):
        """Test parsing Senate bill number."""
        client = CongressAPIClient(api_key="test_key")
        bill_type, number = client._parse_bill_number("S. 456")
        assert bill_type == "s"
        assert number == 456

    def test_parse_bill_number_invalid(self):
        """Test parsing invalid bill number raises error."""
        client = CongressAPIClient(api_key="test_key")
        with pytest.raises(ValueError, match="Invalid bill number format"):
            client._parse_bill_number("INVALID")

    def test_format_bill_number(self):
        """Test bill number formatting."""
        client = CongressAPIClient(api_key="test_key")
        assert client._format_bill_number("hr", "1234") == "H.R. 1234"
        assert client._format_bill_number("s", "456") == "S. 456"
        assert client._format_bill_number("hjres", "10") == "H.J.Res. 10"
        assert client._format_bill_number("sjres", "20") == "S.J.Res. 20"


class TestAPIRequests:
    """Tests for API request handling."""

    @patch("fetchers.congress_api.requests.Session.get")
    def test_make_request_success(self, mock_get):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"bills": [{"number": "1234"}]}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = CongressAPIClient(api_key="test_key")
        client.rate_limit = 0  # Disable rate limiting for test
        result = client._make_request("bill")

        assert result == {"bills": [{"number": "1234"}]}
        mock_get.assert_called_once()

    @patch("fetchers.congress_api.requests.Session.get")
    def test_make_request_caching(self, mock_get):
        """Test that responses are cached."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"bills": []}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = CongressAPIClient(api_key="test_key")
        client.rate_limit = 0

        # First request
        result1 = client._make_request("bill", {"limit": 10})
        # Second request (should use cache)
        result2 = client._make_request("bill", {"limit": 10})

        assert result1 == result2
        # Should only make one actual HTTP request due to caching
        assert mock_get.call_count == 1

    @patch("fetchers.congress_api.requests.Session.get")
    def test_make_request_404_error(self, mock_get):
        """Test API request with 404 error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        client = CongressAPIClient(api_key="test_key")
        client.rate_limit = 0

        with pytest.raises(BillNotFoundError, match="Resource not found"):
            client._make_request("bill/118/hr/999999")

    @patch("fetchers.congress_api.requests.Session.get")
    def test_make_request_rate_limit_error(self, mock_get):
        """Test API request with rate limit error."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response

        client = CongressAPIClient(api_key="test_key")
        client.rate_limit = 0

        with pytest.raises(APIRateLimitError, match="API rate limit exceeded"):
            client._make_request("bill")

    @patch("fetchers.congress_api.requests.Session.get")
    def test_make_request_server_error(self, mock_get):
        """Test API request with server error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        client = CongressAPIClient(api_key="test_key")
        client.rate_limit = 0

        with pytest.raises(APIConnectionError, match="Server error: 500"):
            client._make_request("bill")

    @patch("fetchers.congress_api.requests.Session.get")
    def test_make_request_connection_error(self, mock_get):
        """Test API request with connection error."""
        mock_get.side_effect = requests.ConnectionError("Network error")

        client = CongressAPIClient(api_key="test_key")
        client.rate_limit = 0

        with pytest.raises(APIConnectionError, match="Connection failed"):
            client._make_request("bill")

    @patch("fetchers.congress_api.requests.Session.get")
    def test_make_request_timeout_error(self, mock_get):
        """Test API request with timeout error."""
        mock_get.side_effect = requests.Timeout("Request timed out")

        client = CongressAPIClient(api_key="test_key")
        client.rate_limit = 0

        with pytest.raises(APIConnectionError, match="Request timeout"):
            client._make_request("bill")


class TestRateLimiting:
    """Tests for rate limiting functionality."""

    @patch("fetchers.congress_api.time.sleep")
    @patch("fetchers.congress_api.time.time")
    def test_rate_limiting_enforced(self, mock_time, mock_sleep):
        """Test that rate limiting enforces wait time between requests."""
        # Simulate time progression
        mock_time.side_effect = [
            0,
            0.1,
            0.1,
            0.5,
        ]  # Start, first request, second request

        client = CongressAPIClient(api_key="test_key")
        client.rate_limit = 1  # 1 request per second

        client._rate_limit_wait()
        client._rate_limit_wait()

        # Should have slept to enforce 1 second interval
        mock_sleep.assert_called()

    def test_rate_limiting_disabled(self):
        """Test that rate limiting can be disabled."""
        client = CongressAPIClient(api_key="test_key")
        client.rate_limit = 0

        # Should not raise any errors or sleep
        client._rate_limit_wait()
        client._rate_limit_wait()


class TestFetchRecentBills:
    """Tests for fetch_recent_bills method."""

    @patch.object(CongressAPIClient, "_make_request")
    def test_fetch_recent_bills_success(self, mock_request):
        """Test fetching recent bills."""
        mock_request.return_value = {
            "bills": [
                {
                    "number": "1234",
                    "type": "hr",
                    "congress": 118,
                    "title": "Test Bill Act",
                    "sponsors": [
                        {
                            "fullName": "John Doe",
                            "party": "D",
                            "state": "CA",
                            "bioguideId": "D000001",
                        }
                    ],
                    "cosponsors": [{"name": "Jane Smith"}],
                    "latestAction": {"text": "Referred to committee"},
                    "introducedDate": "2024-01-01",
                    "updateDate": "2024-01-15",
                    "policyArea": {"name": "Healthcare"},
                    "textVersions": {"url": "https://example.com/text"},
                }
            ]
        }

        client = CongressAPIClient(api_key="test_key")
        bills = client.fetch_recent_bills(limit=10, congress=118, bill_type="hr")

        assert len(bills) == 1
        assert bills[0]["bill_number"] == "H.R. 1234"
        assert bills[0]["title"] == "Test Bill Act"
        assert bills[0]["sponsor"]["name"] == "John Doe"
        assert bills[0]["sponsor"]["party"] == "D"
        assert bills[0]["sponsor"]["state"] == "CA"
        assert bills[0]["sponsor"]["bioguide_id"] == "D000001"
        assert bills[0]["cosponsors_count"] == 1
        assert bills[0]["topic"] == ["Healthcare"]
        assert "118th-congress" in bills[0]["congress_gov_url"]

    @patch.object(CongressAPIClient, "_make_request")
    def test_fetch_recent_bills_no_sponsor(self, mock_request):
        """Test fetching bills with no sponsor."""
        mock_request.return_value = {
            "bills": [
                {
                    "number": "5678",
                    "type": "s",
                    "congress": 118,
                    "title": "Senate Bill",
                    "sponsors": [],
                    "cosponsors": [],
                    "latestAction": {"text": "Passed Senate"},
                    "introducedDate": "2024-02-01",
                    "updateDate": "2024-02-15",
                    "policyArea": {},
                }
            ]
        }

        client = CongressAPIClient(api_key="test_key")
        bills = client.fetch_recent_bills(limit=1, congress=118, bill_type="s")

        assert len(bills) == 1
        assert bills[0]["sponsor"] == {}
        assert bills[0]["topic"] == []


class TestGetBillText:
    """Tests for get_bill_text method."""

    @patch.object(CongressAPIClient, "_make_request")
    @patch("fetchers.congress_api.requests.Session.get")
    def test_get_bill_text_success(self, mock_get, mock_request):
        """Test getting bill text successfully."""
        # Mock API response for text versions
        mock_request.return_value = {
            "textVersions": [
                {
                    "formats": [
                        {
                            "type": "Formatted Text",
                            "url": "https://example.com/bill.html",
                        }
                    ]
                }
            ]
        }

        # Mock actual text download
        mock_response = Mock()
        mock_response.text = "<html>Bill text here</html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = CongressAPIClient(api_key="test_key")
        text = client.get_bill_text("H.R. 1234", congress=118)

        assert text == "<html>Bill text here</html>"
        mock_request.assert_called_once()
        mock_get.assert_called_once()

    @patch.object(CongressAPIClient, "_make_request")
    def test_get_bill_text_no_text_available(self, mock_request):
        """Test getting bill text when no text is available."""
        mock_request.return_value = {"textVersions": []}

        client = CongressAPIClient(api_key="test_key")

        with pytest.raises(BillNotFoundError, match="No text available"):
            client.get_bill_text("H.R. 1234", congress=118)

    @patch.object(CongressAPIClient, "_make_request")
    @patch("fetchers.congress_api.requests.Session.get")
    def test_get_bill_text_prefer_html(self, mock_get, mock_request):
        """Test that HTML format is preferred over PDF."""
        mock_request.return_value = {
            "textVersions": [
                {
                    "formats": [
                        {"type": "PDF", "url": "https://example.com/bill.pdf"},
                        {
                            "type": "Formatted Text",
                            "url": "https://example.com/bill.html",
                        },
                    ]
                }
            ]
        }

        mock_response = Mock()
        mock_response.text = "<html>Bill text</html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = CongressAPIClient(api_key="test_key")
        client.get_bill_text("H.R. 1234", congress=118)

        # Should request HTML, not PDF
        assert "bill.html" in str(mock_get.call_args)


class TestGetBillDetails:
    """Tests for get_bill_details method."""

    @patch.object(CongressAPIClient, "_make_request")
    def test_get_bill_details_success(self, mock_request):
        """Test getting comprehensive bill details."""

        # Mock responses for different endpoints
        def make_request_side_effect(endpoint, params=None):
            if endpoint == "bill/118/hr/1234":
                return {
                    "bill": {
                        "number": "1234",
                        "type": "hr",
                        "congress": 118,
                        "title": "Test Bill",
                        "sponsors": [
                            {
                                "fullName": "John Doe",
                                "party": "D",
                                "state": "CA",
                                "bioguideId": "D001",
                            }
                        ],
                        "cosponsors": [],
                        "latestAction": {"text": "Referred"},
                        "introducedDate": "2024-01-01",
                        "updateDate": "2024-01-15",
                        "policyArea": {"name": "Healthcare"},
                        "actions": {
                            "url": "https://api.congress.gov/v3/bill/118/hr/1234/actions"
                        },
                        "committees": {
                            "url": "https://api.congress.gov/v3/bill/118/hr/1234/committees"
                        },
                        "relatedBills": {
                            "url": "https://api.congress.gov/v3/bill/118/hr/1234/relatedBills"
                        },
                        "subjects": {
                            "url": "https://api.congress.gov/v3/bill/118/hr/1234/subjects"
                        },
                        "cboCostEstimates": [{"url": "https://cbo.gov/estimate"}],
                    }
                }
            elif "actions" in endpoint:
                return {
                    "actions": [
                        {"text": "Introduced"},
                        {"text": "Referred to committee"},
                    ]
                }
            elif "committees" in endpoint:
                return {"committees": [{"name": "Ways and Means"}]}
            elif "relatedBills" in endpoint:
                return {"relatedBills": [{"type": "s", "number": "456"}]}
            elif "subjects" in endpoint:
                return {
                    "subjects": {"legislativeSubjects": [{"name": "Health insurance"}]}
                }
            return {}

        mock_request.side_effect = make_request_side_effect

        client = CongressAPIClient(api_key="test_key")
        details = client.get_bill_details("H.R. 1234", congress=118)

        assert details["bill_number"] == "H.R. 1234"
        assert len(details["actions"]) == 2
        assert "Ways and Means" in details["committees"]
        assert "S. 456" in details["related_bills"]
        assert "Health insurance" in details["subjects"]
        assert details["cbo_cost_estimate"] == "https://cbo.gov/estimate"

    @patch.object(CongressAPIClient, "_make_request")
    def test_get_bill_details_not_found(self, mock_request):
        """Test getting details for non-existent bill."""
        mock_request.return_value = {}

        client = CongressAPIClient(api_key="test_key")

        with pytest.raises(BillNotFoundError, match="Bill not found"):
            client.get_bill_details("H.R. 999999", congress=118)


class TestGetRepresentative:
    """Tests for get_representative method."""

    @patch.object(CongressAPIClient, "_make_request")
    def test_get_representative_success(self, mock_request):
        """Test getting representative information."""
        mock_request.return_value = {
            "member": {
                "firstName": "Nancy",
                "lastName": "Pelosi",
                "partyName": "Democratic",
                "state": "CA",
                "district": "11",
                "depiction": {"imageUrl": "https://example.com/photo.jpg"},
                "terms": [{"office": "2371 Rayburn House Office Building"}],
            }
        }

        client = CongressAPIClient(api_key="test_key")
        rep = client.get_representative("P000197")

        assert rep["name"] == "Nancy Pelosi"
        assert rep["party"] == "Democratic"
        assert rep["state"] == "CA"
        assert rep["district"] == "11"
        assert rep["photo_url"] == "https://example.com/photo.jpg"
        assert "Rayburn" in rep["office"]

    @patch.object(CongressAPIClient, "_make_request")
    def test_get_representative_not_found(self, mock_request):
        """Test getting non-existent representative."""
        mock_request.return_value = {}

        client = CongressAPIClient(api_key="test_key")

        with pytest.raises(BillNotFoundError, match="Representative not found"):
            client.get_representative("INVALID")


class TestConvenienceFunctions:
    """Tests for convenience wrapper functions."""

    @patch.object(CongressAPIClient, "fetch_recent_bills")
    def test_fetch_recent_bills_function(self, mock_method):
        """Test convenience function for fetching bills."""
        mock_method.return_value = [{"bill_number": "H.R. 1"}]

        bills = fetch_recent_bills(limit=5, congress=118, bill_type="hr")

        assert len(bills) == 1
        mock_method.assert_called_once_with(limit=5, congress=118, bill_type="hr")

    @patch.object(CongressAPIClient, "get_bill_text")
    def test_get_bill_text_function(self, mock_method):
        """Test convenience function for getting bill text."""
        mock_method.return_value = "Bill text"

        text = get_bill_text("H.R. 1234", congress=118)

        assert text == "Bill text"
        mock_method.assert_called_once_with(bill_number="H.R. 1234", congress=118)

    @patch.object(CongressAPIClient, "get_bill_details")
    def test_get_bill_details_function(self, mock_method):
        """Test convenience function for getting bill details."""
        mock_method.return_value = {"bill_number": "H.R. 1"}

        details = get_bill_details("H.R. 1234", congress=118)

        assert details["bill_number"] == "H.R. 1"
        mock_method.assert_called_once_with(bill_number="H.R. 1234", congress=118)

    @patch.object(CongressAPIClient, "get_representative")
    def test_get_representative_function(self, mock_method):
        """Test convenience function for getting representative."""
        mock_method.return_value = {"name": "John Doe"}

        rep = get_representative("D000001")

        assert rep["name"] == "John Doe"
        mock_method.assert_called_once_with(bioguide_id="D000001")


class TestRetryLogic:
    """Tests for retry logic on failures."""

    @patch("fetchers.congress_api.requests.Session.get")
    def test_retry_on_rate_limit(self, mock_get):
        """Test that rate limit errors trigger retry."""
        # First call raises rate limit, second succeeds
        mock_response_fail = Mock()
        mock_response_fail.status_code = 429

        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"bills": []}
        mock_response_success.raise_for_status = Mock()

        mock_get.side_effect = [mock_response_fail, mock_response_success]

        client = CongressAPIClient(api_key="test_key")
        client.rate_limit = 0

        # Should retry and eventually succeed
        result = client._make_request("bill")
        assert result == {"bills": []}
        assert mock_get.call_count == 2

    @patch("fetchers.congress_api.requests.Session.get")
    def test_retry_on_server_error(self, mock_get):
        """Test that server errors trigger retry."""
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500

        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"data": "success"}
        mock_response_success.raise_for_status = Mock()

        mock_get.side_effect = [mock_response_fail, mock_response_success]

        client = CongressAPIClient(api_key="test_key")
        client.rate_limit = 0

        result = client._make_request("bill")
        assert result == {"data": "success"}
        assert mock_get.call_count == 2


# Integration test (requires API key and network access)
@pytest.mark.skip(reason="Requires valid API key and network access")
def test_fetch_recent_bills_integration():
    """Integration test for fetching real bills from Congress.gov API."""
    bills = fetch_recent_bills(limit=5, congress=118, bill_type="hr")

    assert len(bills) <= 5
    for bill in bills:
        assert "bill_number" in bill
        assert "title" in bill
        assert "sponsor" in bill
        assert "congress_gov_url" in bill
        assert bill["bill_number"].startswith("H.R.")


@pytest.mark.skip(reason="Requires valid API key and network access")
def test_get_bill_details_integration():
    """Integration test for getting bill details."""
    # Use a well-known bill
    details = get_bill_details("H.R. 1", congress=118)

    assert details["bill_number"] == "H.R. 1"
    assert "actions" in details
    assert "committees" in details
    assert isinstance(details["actions"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
