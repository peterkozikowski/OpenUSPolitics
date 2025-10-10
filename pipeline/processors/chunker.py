"""
Document chunker for splitting bill text into RAG-ready chunks.

Uses token-aware chunking with sentence boundary detection and section preservation.
"""

import logging
import re
from typing import Dict, List, Optional

import tiktoken
from tqdm import tqdm

logger = logging.getLogger(__name__)


# ============================================================================
# Custom Exceptions
# ============================================================================

class ChunkerError(Exception):
    """Custom exception for chunking errors."""
    pass


# ============================================================================
# Configuration
# ============================================================================

DEFAULT_CHUNK_SIZE = 1500  # tokens
DEFAULT_OVERLAP = 300  # tokens
TOKEN_ENCODING = "cl100k_base"  # OpenAI's encoding


# ============================================================================
# Main Chunking Functions
# ============================================================================

def chunk_document(
    parsed_bill: Dict,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP
) -> List[Dict]:
    """
    Split bill into overlapping chunks for RAG processing.

    Args:
        parsed_bill: Output from parse_bill_text() containing:
            - raw_text: str
            - sections: List[Dict]
            - metadata: Dict
        chunk_size: Target tokens per chunk
        overlap: Overlapping tokens between chunks

    Returns:
        List of chunks with:
            - id: str (unique chunk identifier)
            - text: str (chunk text)
            - section: str (parent section number)
            - section_title: str
            - start_char: int (position in full text)
            - end_char: int
            - page: int | None
            - tokens: int (approximate)

    Example:
        >>> parsed = parse_bill_text(url)
        >>> chunks = chunk_document(parsed, chunk_size=1500, overlap=300)
        >>> print(f"Created {len(chunks)} chunks")
    """
    raw_text = parsed_bill.get("raw_text", "")
    sections = parsed_bill.get("sections", [])
    metadata = parsed_bill.get("metadata", {})
    page_data = parsed_bill.get("page_data", [])

    if not raw_text:
        logger.warning("No text to chunk")
        return []

    logger.info(
        f"Chunking document: {len(raw_text)} chars, "
        f"{len(sections)} sections, chunk_size={chunk_size}, overlap={overlap}"
    )

    # Initialize tokenizer
    tokenizer = tiktoken.get_encoding(TOKEN_ENCODING)

    chunks = []

    # If we have sections, use section-aware chunking
    if sections:
        logger.info("Using section-aware chunking")
        chunks = _chunk_with_sections(
            raw_text=raw_text,
            sections=sections,
            page_data=page_data,
            chunk_size=chunk_size,
            overlap=overlap,
            tokenizer=tokenizer
        )
    else:
        # Fallback to simple chunking
        logger.info("No sections found, using simple chunking")
        chunks = _chunk_simple(
            text=raw_text,
            chunk_size=chunk_size,
            overlap=overlap,
            tokenizer=tokenizer
        )

    logger.info(f"Created {len(chunks)} chunks")
    return chunks


def _chunk_with_sections(
    raw_text: str,
    sections: List[Dict],
    page_data: List[Dict],
    chunk_size: int,
    overlap: int,
    tokenizer
) -> List[Dict]:
    """
    Section-aware chunking strategy.

    Preserves section boundaries when possible and includes section context
    in each chunk.

    Args:
        raw_text: Full bill text
        sections: List of section dictionaries
        page_data: List of page data (for page number mapping)
        chunk_size: Target tokens per chunk
        overlap: Overlap tokens
        tokenizer: Tiktoken tokenizer

    Returns:
        List of chunk dictionaries
    """
    chunks = []
    chunk_id = 0

    # Create page mapping for char position -> page number
    page_map = _create_page_map(page_data)

    for section in tqdm(sections, desc="Chunking sections", disable=len(sections) < 10):
        section_text = section["text"]
        section_num = section["section_number"]
        section_title = section["title"]
        section_start = section["start_char"]

        # Count tokens in section
        section_tokens = len(tokenizer.encode(section_text))

        if section_tokens <= chunk_size:
            # Section fits in one chunk
            chunk = {
                "id": f"chunk_{chunk_id}",
                "text": section_text,
                "section": section_num,
                "section_title": section_title,
                "start_char": section_start,
                "end_char": section_start + len(section_text),
                "page": _get_page_number(section_start, page_map),
                "tokens": section_tokens,
            }
            chunks.append(chunk)
            chunk_id += 1
        else:
            # Section too large, split with smart boundaries
            section_chunks = _split_large_section(
                section_text=section_text,
                section_num=section_num,
                section_title=section_title,
                section_start=section_start,
                chunk_size=chunk_size,
                overlap=overlap,
                tokenizer=tokenizer,
                page_map=page_map,
                chunk_id_start=chunk_id
            )
            chunks.extend(section_chunks)
            chunk_id += len(section_chunks)

    return chunks


def _split_large_section(
    section_text: str,
    section_num: str,
    section_title: str,
    section_start: int,
    chunk_size: int,
    overlap: int,
    tokenizer,
    page_map: Dict,
    chunk_id_start: int
) -> List[Dict]:
    """
    Split a large section into multiple chunks at sentence boundaries.

    Args:
        section_text: Text of the section
        section_num: Section number
        section_title: Section title
        section_start: Start position in full text
        chunk_size: Target tokens
        overlap: Overlap tokens
        tokenizer: Tiktoken tokenizer
        page_map: Page number mapping
        chunk_id_start: Starting chunk ID

    Returns:
        List of chunk dictionaries
    """
    chunks = []

    # Split section into sentences
    sentences = smart_split(section_text, max_tokens=chunk_size)

    current_chunk_text = ""
    current_tokens = 0
    chunk_start_pos = 0

    for sentence in sentences:
        sentence_tokens = len(tokenizer.encode(sentence))

        # Check if adding this sentence exceeds chunk size
        if current_tokens + sentence_tokens > chunk_size and current_chunk_text:
            # Save current chunk
            chunk = {
                "id": f"chunk_{chunk_id_start + len(chunks)}",
                "text": current_chunk_text.strip(),
                "section": section_num,
                "section_title": section_title,
                "start_char": section_start + chunk_start_pos,
                "end_char": section_start + chunk_start_pos + len(current_chunk_text),
                "page": _get_page_number(section_start + chunk_start_pos, page_map),
                "tokens": current_tokens,
            }
            chunks.append(chunk)

            # Start new chunk with overlap
            # Calculate overlap text from end of current chunk
            overlap_text = _get_overlap_text(current_chunk_text, overlap, tokenizer)
            overlap_tokens = len(tokenizer.encode(overlap_text))

            current_chunk_text = overlap_text + " " + sentence
            current_tokens = overlap_tokens + sentence_tokens
            chunk_start_pos = chunk_start_pos + len(current_chunk_text) - len(overlap_text + " " + sentence)
        else:
            # Add sentence to current chunk
            if current_chunk_text:
                current_chunk_text += " " + sentence
            else:
                current_chunk_text = sentence
                chunk_start_pos = section_text.find(sentence)

            current_tokens += sentence_tokens

    # Add final chunk if it has content
    if current_chunk_text.strip():
        chunk = {
            "id": f"chunk_{chunk_id_start + len(chunks)}",
            "text": current_chunk_text.strip(),
            "section": section_num,
            "section_title": section_title,
            "start_char": section_start + chunk_start_pos,
            "end_char": section_start + chunk_start_pos + len(current_chunk_text),
            "page": _get_page_number(section_start + chunk_start_pos, page_map),
            "tokens": current_tokens,
        }
        chunks.append(chunk)

    return chunks


def _chunk_simple(
    text: str,
    chunk_size: int,
    overlap: int,
    tokenizer
) -> List[Dict]:
    """
    Simple chunking without section awareness.

    Falls back to this when sections aren't detected.

    Args:
        text: Full text
        chunk_size: Target tokens
        overlap: Overlap tokens
        tokenizer: Tiktoken tokenizer

    Returns:
        List of chunk dictionaries
    """
    chunks = []
    sentences = smart_split(text, max_tokens=chunk_size)

    current_chunk_text = ""
    current_tokens = 0
    chunk_start_pos = 0
    chunk_id = 0

    for sentence in sentences:
        sentence_tokens = len(tokenizer.encode(sentence))

        if current_tokens + sentence_tokens > chunk_size and current_chunk_text:
            # Save current chunk
            chunk = {
                "id": f"chunk_{chunk_id}",
                "text": current_chunk_text.strip(),
                "section": None,
                "section_title": None,
                "start_char": chunk_start_pos,
                "end_char": chunk_start_pos + len(current_chunk_text),
                "page": None,
                "tokens": current_tokens,
            }
            chunks.append(chunk)
            chunk_id += 1

            # Start new chunk with overlap
            overlap_text = _get_overlap_text(current_chunk_text, overlap, tokenizer)
            overlap_tokens = len(tokenizer.encode(overlap_text))

            current_chunk_text = overlap_text + " " + sentence
            current_tokens = overlap_tokens + sentence_tokens
            chunk_start_pos = chunk_start_pos + len(current_chunk_text) - len(overlap_text + " " + sentence)
        else:
            if current_chunk_text:
                current_chunk_text += " " + sentence
            else:
                current_chunk_text = sentence
                chunk_start_pos = text.find(sentence)

            current_tokens += sentence_tokens

    # Add final chunk
    if current_chunk_text.strip():
        chunk = {
            "id": f"chunk_{chunk_id}",
            "text": current_chunk_text.strip(),
            "section": None,
            "section_title": None,
            "start_char": chunk_start_pos,
            "end_char": chunk_start_pos + len(current_chunk_text),
            "page": None,
            "tokens": current_tokens,
        }
        chunks.append(chunk)

    return chunks


# ============================================================================
# Helper Functions
# ============================================================================

def smart_split(text: str, max_tokens: int) -> List[str]:
    """
    Split text at sentence boundaries using regex-based sentence detection.

    Args:
        text: Text to split
        max_tokens: Maximum tokens (used as a guide, not strict limit)

    Returns:
        List of sentences

    Note:
        For production, consider using spacy for better sentence detection:
        ```python
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        return [sent.text.strip() for sent in doc.sents]
        ```
    """
    # Regex-based sentence splitting
    # This is a simplified version; spacy would be more accurate

    # Pattern matches sentence endings: . ! ? followed by space/newline/end
    # Handles common legal citations like "U.S.C." by requiring space after period
    sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])$'

    sentences = re.split(sentence_pattern, text)

    # Clean sentences
    sentences = [s.strip() for s in sentences if s.strip()]

    # Handle edge case where sentences are too long
    # Split very long sentences at other boundaries (semicolon, dash)
    final_sentences = []
    for sent in sentences:
        if len(sent) > max_tokens * 4:  # Rough char estimate (4 chars ~ 1 token)
            # Split at semicolons or dashes for very long sentences
            subsents = re.split(r'[;—]', sent)
            final_sentences.extend([s.strip() for s in subsents if s.strip()])
        else:
            final_sentences.append(sent)

    return final_sentences


def _get_overlap_text(text: str, overlap_tokens: int, tokenizer) -> str:
    """
    Get the last N tokens worth of text for overlap.

    Args:
        text: Source text
        overlap_tokens: Number of tokens to overlap
        tokenizer: Tiktoken tokenizer

    Returns:
        Overlap text
    """
    if overlap_tokens <= 0:
        return ""

    tokens = tokenizer.encode(text)

    if len(tokens) <= overlap_tokens:
        return text

    # Get last N tokens
    overlap_token_ids = tokens[-overlap_tokens:]
    overlap_text = tokenizer.decode(overlap_token_ids)

    return overlap_text


def _create_page_map(page_data: List[Dict]) -> Dict[int, int]:
    """
    Create a mapping from character position to page number.

    Args:
        page_data: List of page dictionaries with page_number and text

    Returns:
        Dictionary mapping char positions to page numbers
    """
    page_map = {}
    char_pos = 0

    for page in page_data:
        page_num = page["page_number"]
        page_text = page["text"]
        page_length = len(page_text) + 2  # +2 for \n\n separator

        # Map all positions in this page to the page number
        for i in range(char_pos, char_pos + page_length):
            page_map[i] = page_num

        char_pos += page_length

    return page_map


def _get_page_number(char_pos: int, page_map: Dict[int, int]) -> Optional[int]:
    """
    Get page number for a character position.

    Args:
        char_pos: Character position
        page_map: Mapping from positions to page numbers

    Returns:
        Page number or None
    """
    if not page_map:
        return None

    # Find closest page
    return page_map.get(char_pos)


# ============================================================================
# Main / Testing
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Test data
    test_parsed_bill = {
        "raw_text": """
SEC. 1. SHORT TITLE.

This Act may be cited as the "Test Bill Act of 2024".

SEC. 2. DEFINITIONS.

In this Act:
(1) TERM 1.—The term "term 1" means something important that requires a detailed explanation to fully understand the legislative intent and scope of application within the context of this Act.
(2) TERM 2.—The term "term 2" means something else that is equally important and requires careful consideration when implementing the provisions set forth in subsequent sections.

SEC. 3. REQUIREMENTS.

The Secretary shall establish requirements for implementation. This section contains very long text that will definitely exceed the chunk size limit and will need to be split into multiple chunks to handle properly. The implementation must follow strict guidelines and ensure compliance with all applicable federal regulations and standards.
        """.strip(),
        "sections": [
            {
                "section_number": "1",
                "title": "SHORT TITLE",
                "level": 1,
                "text": 'SEC. 1. SHORT TITLE.\n\nThis Act may be cited as the "Test Bill Act of 2024".',
                "start_char": 0,
                "end_char": 70
            },
            {
                "section_number": "2",
                "title": "DEFINITIONS",
                "level": 1,
                "text": "SEC. 2. DEFINITIONS.\n\nIn this Act:\n(1) TERM 1.—The term \"term 1\" means something important that requires a detailed explanation to fully understand the legislative intent and scope of application within the context of this Act.\n(2) TERM 2.—The term \"term 2\" means something else that is equally important and requires careful consideration when implementing the provisions set forth in subsequent sections.",
                "start_char": 72,
                "end_char": 450
            },
            {
                "section_number": "3",
                "title": "REQUIREMENTS",
                "level": 1,
                "text": "SEC. 3. REQUIREMENTS.\n\nThe Secretary shall establish requirements for implementation. This section contains very long text that will definitely exceed the chunk size limit and will need to be split into multiple chunks to handle properly. The implementation must follow strict guidelines and ensure compliance with all applicable federal regulations and standards.",
                "start_char": 452,
                "end_char": 800
            }
        ],
        "metadata": {
            "bill_number": "H.R. TEST",
            "title": "Test Bill Act of 2024"
        },
        "page_data": []
    }

    print("=" * 80)
    print("Testing Document Chunker")
    print("=" * 80)

    # Test chunking
    chunks = chunk_document(test_parsed_bill, chunk_size=100, overlap=20)

    print(f"\n📦 Created {len(chunks)} chunks\n")

    for chunk in chunks[:5]:  # Show first 5 chunks
        print(f"\n{chunk['id']}:")
        print(f"  Section: {chunk['section']} - {chunk['section_title']}")
        print(f"  Tokens: {chunk['tokens']}")
        print(f"  Position: {chunk['start_char']}-{chunk['end_char']}")
        print(f"  Text: {chunk['text'][:150]}...")

    # Test smart_split
    print("\n" + "=" * 80)
    print("Testing Smart Split")
    print("=" * 80)

    test_text = "This is sentence one. This is sentence two! This is sentence three? And a fourth sentence."
    sentences = smart_split(test_text, max_tokens=50)

    print(f"\nSplit into {len(sentences)} sentences:")
    for i, sent in enumerate(sentences, 1):
        print(f"  {i}. {sent}")
