"""Fetchers module for retrieving data from external sources."""

from .congress_api import fetch_recent_bills

__all__ = ["fetch_recent_bills"]
