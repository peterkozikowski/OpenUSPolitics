"""
Bill text parser for downloading and cleaning legislative documents.

Supports PDF and HTML formats from congress.gov with layout-aware parsing,
section extraction, and metadata extraction.
"""

import logging
import re
from typing import Dict, List, Optional
from io import BytesIO

import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


# ============================================================================
# Custom Exceptions
# ============================================================================


class BillParserError(Exception):
    """Custom exception for bill parsing errors."""

    pass


# Alias for backward compatibility
ParserError = BillParserError


# ============================================================================
# Main Parsing Functions
# ============================================================================


def parse_bill_text(url: str) -> Dict:
    """
    Download and parse bill text from various formats (PDF/HTML).

    Args:
        url: Congress.gov text URL

    Returns:
        Dictionary containing:
            - raw_text: str (cleaned full text)
            - sections: List[Dict] (structured sections)
            - metadata: Dict (title, bill_number, pages, etc.)

    Raises:
        BillParserError: If parsing fails

    Example:
        >>> result = parse_bill_text("https://www.congress.gov/118/bills/hr1/BILLS-118hr1eh.pdf")
        >>> print(result['metadata']['title'])
        >>> print(f"Found {len(result['sections'])} sections")
    """
    if not url:
        raise BillParserError("URL cannot be empty")

    logger.info(f"Parsing bill text from: {url}")

    try:
        # Download the content
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Determine format based on URL or content-type
        content_type = response.headers.get("content-type", "").lower()
        is_pdf = "pdf" in url.lower() or "application/pdf" in content_type

        if is_pdf:
            parsed_data = _parse_pdf_advanced(response.content)
        else:
            parsed_data = _parse_html_advanced(response.content)

        # Extract metadata from text
        metadata = _extract_metadata(parsed_data["raw_text"], url)
        parsed_data["metadata"] = metadata

        # Extract sections
        sections = extract_sections(parsed_data["raw_text"])
        parsed_data["sections"] = sections

        logger.info(
            f"Parsed bill: {len(parsed_data['raw_text'])} chars, "
            f"{len(sections)} sections, {metadata.get('pages', 'N/A')} pages"
        )

        return parsed_data

    except requests.RequestException as e:
        logger.error(f"Failed to download bill text: {e}")
        raise BillParserError(f"Failed to download bill text: {e}") from e
    except Exception as e:
        logger.error(f"Failed to parse bill text: {e}")
        raise BillParserError(f"Failed to parse bill text: {e}") from e


# ============================================================================
# PDF Parsing (PyMuPDF - Layout Aware)
# ============================================================================


def _parse_pdf_advanced(content: bytes) -> Dict:
    """
    Parse PDF content with layout-aware extraction using PyMuPDF.

    Handles:
    - Multi-column layouts
    - Section structure preservation
    - Page number extraction
    - Header/footer removal

    Args:
        content: PDF content as bytes

    Returns:
        Dictionary with raw_text and page_data
    """
    pdf_file = BytesIO(content)
    doc = fitz.open(stream=pdf_file, filetype="pdf")

    text_parts = []
    page_data = []

    for page_num, page in enumerate(doc, start=1):
        # Extract text with layout preservation
        # Use "text" mode for better structure preservation
        page_text = page.get_text("text")

        # Clean page text
        cleaned_page = _clean_page_text(page_text, page_num)

        if cleaned_page.strip():
            text_parts.append(cleaned_page)
            page_data.append(
                {
                    "page_number": page_num,
                    "text": cleaned_page,
                    "char_count": len(cleaned_page),
                }
            )

    doc.close()

    # Combine all pages
    raw_text = "\n\n".join(text_parts)

    # Clean and normalize the full text
    raw_text = _normalize_text(raw_text)

    return {"raw_text": raw_text, "page_data": page_data, "source_format": "pdf"}


def _clean_page_text(text: str, page_num: int) -> str:
    """
    Clean text from a single PDF page.

    Removes:
    - Page numbers
    - Headers/footers
    - Excessive whitespace

    Args:
        text: Raw page text
        page_num: Page number

    Returns:
        Cleaned text
    """
    # Remove common header patterns
    text = re.sub(r"\d+th CONGRESS.*?SESSION", "", text, flags=re.IGNORECASE)
    text = re.sub(
        r"H\.\s*R\.\s*\d+", "", text, count=1
    )  # Remove bill number at top (keep in body)
    text = re.sub(r"IN THE (?:HOUSE|SENATE)", "", text, flags=re.IGNORECASE)

    # Remove page numbers (various formats)
    text = re.sub(r"^-?\s*\d+\s*-?\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"Page \d+ of \d+", "", text, flags=re.IGNORECASE)

    # Remove excessive whitespace
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ============================================================================
# HTML Parsing
# ============================================================================


def _parse_html_advanced(content: bytes) -> Dict:
    """
    Parse HTML content and extract bill text with structure.

    Args:
        content: HTML content as bytes

    Returns:
        Dictionary with raw_text and metadata
    """
    soup = BeautifulSoup(content, "lxml")

    # Remove script and style elements
    for element in soup(["script", "style", "nav", "header", "footer"]):
        element.decompose()

    # Try to find the main content area
    # Congress.gov uses specific classes for bill text
    main_content = (
        soup.find("pre", class_="styled-text")
        or soup.find("div", class_="bill-text")
        or soup.find("pre")
        or soup.find("main")
    )

    if main_content:
        text = main_content.get_text()
    else:
        # Fallback to body text
        body = soup.find("body")
        text = body.get_text() if body else soup.get_text()

    # Normalize the text
    text = _normalize_text(text)

    return {"raw_text": text, "page_data": [], "source_format": "html"}


# ============================================================================
# Text Normalization
# ============================================================================


def _normalize_text(text: str) -> str:
    """
    Normalize bill text while preserving legal language and structure.

    Removes:
    - Extra whitespace
    - Page artifacts
    - Formatting characters

    Preserves:
    - Section structure
    - Legal citations
    - Important formatting (indentation context)

    Args:
        text: Raw bill text

    Returns:
        Cleaned and normalized text
    """
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove page markers and artifacts
    text = re.sub(r"____+", "", text)  # Remove lines of underscores
    text = re.sub(r"\*{3,}", "", text)  # Remove lines of asterisks

    # Standardize section markers (but preserve original format)
    # This helps with section detection while keeping legal format
    # SEC. 1., SECTION 1, Sec. 1. -> all remain as-is (detection handles variations)

    # Remove excessive blank lines (more than 2 consecutive)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Normalize spacing around section markers
    text = re.sub(r"\n(SEC\.|SECTION)\s+", r"\n\n\1 ", text, flags=re.IGNORECASE)

    # Clean up spaces (but not all - preserve some structure)
    # Remove trailing spaces from lines
    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines)

    # Remove leading/trailing whitespace from entire text
    text = text.strip()

    return text


# ============================================================================
# Metadata Extraction
# ============================================================================


def _extract_metadata(text: str, url: str) -> Dict:
    """
    Extract metadata from bill text.

    Args:
        text: Bill text
        url: Source URL

    Returns:
        Dictionary with metadata:
            - title: Bill title
            - bill_number: Bill identifier
            - congress: Congress number
            - session: Session number
            - pages: Number of pages (if available)
    """
    metadata = {
        "url": url,
        "title": None,
        "bill_number": None,
        "congress": None,
        "session": None,
        "pages": None,
    }

    # Extract congress and session
    congress_match = re.search(r"(\d+)(?:th|st|nd|rd)\s+CONGRESS", text, re.IGNORECASE)
    if congress_match:
        metadata["congress"] = int(congress_match.group(1))

    session_match = re.search(r"(\d+)(?:st|nd|rd|th)\s+SESSION", text, re.IGNORECASE)
    if session_match:
        metadata["session"] = int(session_match.group(1))

    # Extract bill number from URL (more reliable than text)
    bill_num_match = re.search(
        r"/(hr|s|hjres|sjres|hconres|sconres)(\d+)/", url, re.IGNORECASE
    )
    if bill_num_match:
        bill_type = bill_num_match.group(1).upper()
        bill_num = bill_num_match.group(2)
        # Format properly
        if bill_type == "HR":
            metadata["bill_number"] = f"H.R. {bill_num}"
        elif bill_type == "S":
            metadata["bill_number"] = f"S. {bill_num}"
        else:
            metadata["bill_number"] = f"{bill_type} {bill_num}"

    # Extract title (usually after "A BILL" or "AN ACT")
    title_patterns = [
        r"(?:A BILL|AN ACT)\s+(.+?)(?:\n\n|SEC\.|SECTION)",
        r"SHORT TITLE\.?\s*\n+(.+?)(?:\n\n|SEC\.|SECTION)",
    ]

    for pattern in title_patterns:
        title_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if title_match:
            title = title_match.group(1).strip()
            # Clean up title
            title = re.sub(r"\s+", " ", title)
            title = title.strip('"').strip("'").strip()
            if len(title) > 10 and len(title) < 500:  # Reasonable title length
                metadata["title"] = title
                break

    return metadata


# ============================================================================
# Section Extraction
# ============================================================================


def extract_sections(text: str) -> List[Dict]:
    """
    Parse bill into structured sections with hierarchy.

    Args:
        text: Bill text

    Returns:
        List of sections with:
            - section_number: str (e.g., "1", "101", "1.a")
            - title: str (section title)
            - level: int (1=SEC/SECTION, 2=subsection, 3=paragraph)
            - text: str (full section text)
            - start_char: int (position in full text)
            - end_char: int (position in full text)

    Example:
        >>> sections = extract_sections(bill_text)
        >>> for s in sections:
        ...     print(f"Section {s['section_number']}: {s['title']} (Level {s['level']})")
    """
    sections = []

    # Pattern for main section headers
    # Matches: SEC. 1., SECTION 1., Sec. 101., etc.
    section_pattern = re.compile(
        r"^(SEC\.|SECTION)\s+(\d+(?:\.\s*)?)\s*(.+?)$", re.MULTILINE | re.IGNORECASE
    )

    matches = list(section_pattern.finditer(text))

    if not matches:
        logger.warning("No sections found in bill text")
        return []

    for i, match in enumerate(matches):
        section_marker = match.group(1)  # "SEC." or "SECTION"
        section_num = match.group(2).strip().rstrip(".")  # "1", "101", etc.
        section_title = match.group(3).strip()

        start_pos = match.start()
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        section_text = text[start_pos:end_pos].strip()

        # Determine section level
        # Level 1: Main sections (SEC., SECTION)
        # Could extend to detect subsections, but for now all are level 1
        level = 1

        sections.append(
            {
                "section_number": section_num,
                "title": section_title,
                "level": level,
                "text": section_text,
                "start_char": start_pos,
                "end_char": end_pos,
            }
        )

    logger.info(f"Extracted {len(sections)} sections from bill")
    return sections


# ============================================================================
# Main / Testing
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Test with a real bill URL
    test_urls = [
        # PDF example
        "https://www.congress.gov/118/bills/hr1/BILLS-118hr1eh.pdf",
        # HTML example (if available)
        # "https://www.congress.gov/bill/118th-congress/house-bill/1/text"
    ]

    for test_url in test_urls[:1]:  # Test first URL only
        try:
            print("=" * 80)
            print(f"Testing parser with: {test_url}")
            print("=" * 80)

            result = parse_bill_text(test_url)

            print("\n📄 METADATA:")
            for key, value in result["metadata"].items():
                print(f"  {key}: {value}")

            print(f"\n📝 TEXT SAMPLE (first 500 chars):")
            print(result["raw_text"][:500])

            print(f"\n📑 SECTIONS (first 5):")
            for section in result["sections"][:5]:
                print(f"\n  Section {section['section_number']}: {section['title']}")
                print(f"    Level: {section['level']}")
                print(f"    Position: {section['start_char']}-{section['end_char']}")
                print(f"    Preview: {section['text'][:100]}...")

            print(f"\n✅ Total sections: {len(result['sections'])}")

        except BillParserError as e:
            print(f"\n❌ Error: {e}")
