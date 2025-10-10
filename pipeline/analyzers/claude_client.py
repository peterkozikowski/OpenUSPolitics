"""
Claude API client for comprehensive bill analysis.

Features:
- Structured JSON outputs with Pydantic validation
- Rate limiting and retry logic
- Response caching
- Cost tracking
- Provenance/traceability generation
"""

import logging
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict

import anthropic
from anthropic import Anthropic
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from pydantic import BaseModel, Field, ValidationError
from cachetools import TTLCache

from config import Config
from .prompts import (
    ANALYST_SYSTEM_PROMPT,
    format_summary_prompt,
    format_provisions_prompt,
    format_impact_prompt,
    format_fiscal_prompt,
    format_traceability_prompt,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Custom Exceptions
# ============================================================================

class ClaudeAPIError(Exception):
    """Base exception for Claude API errors."""
    pass


class InvalidJSONError(ClaudeAPIError):
    """Raised when Claude returns invalid JSON."""
    pass


class RateLimitError(ClaudeAPIError):
    """Raised when rate limit is exceeded."""
    pass


# ============================================================================
# Pydantic Models for Validation
# ============================================================================

class SummaryResponse(BaseModel):
    """Validation model for summary response."""
    plain_english_summary: str = Field(..., min_length=300, max_length=5000)


class ProvisionsResponse(BaseModel):
    """Validation model for key provisions response."""
    key_provisions: List[str] = Field(..., min_items=1, max_items=15)


class ImpactResponse(BaseModel):
    """Validation model for practical impact response."""
    practical_impact: str = Field(..., min_length=200, max_length=5000)


class FiscalDetails(BaseModel):
    """Fiscal impact details."""
    total_cost: Optional[str] = None
    annual_cost: Optional[str] = None
    funding_sources: List[str] = Field(default_factory=list)
    revenue_effects: Optional[str] = None
    cbo_score: Optional[str] = None
    breakdown: Optional[str] = None


class FiscalResponse(BaseModel):
    """Validation model for fiscal impact response."""
    fiscal_impact: Optional[FiscalDetails] = None


class ProvenanceEntry(BaseModel):
    """Single provenance entry."""
    summary_sentence: str
    source_chunk_id: str
    source_text: str
    char_start: int = Field(..., ge=0)
    char_end: int = Field(..., ge=0)


class ProvenanceResponse(BaseModel):
    """Validation model for provenance response."""
    provenance: List[ProvenanceEntry]


class BillAnalysis(BaseModel):
    """Complete bill analysis structure."""
    bill_number: str
    bill_title: str
    plain_english_summary: str
    key_provisions: List[str]
    practical_impact: str
    fiscal_impact: Optional[FiscalDetails] = None
    generated_at: str
    model_used: str
    total_tokens: int
    estimated_cost: float


# ============================================================================
# Rate Limiter
# ============================================================================

class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, calls_per_minute: int = 50):
        self.calls_per_minute = calls_per_minute
        self.calls = []

    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        now = time.time()

        # Remove calls older than 1 minute
        self.calls = [t for t in self.calls if now - t < 60]

        if len(self.calls) >= self.calls_per_minute:
            sleep_time = 60 - (now - self.calls[0])
            if sleep_time > 0:
                logger.info(f"Rate limit reached, sleeping {sleep_time:.1f}s")
                time.sleep(sleep_time)

        self.calls.append(now)


# ============================================================================
# Cost Calculator
# ============================================================================

class CostTracker:
    """Track API costs across sessions."""

    # Claude Sonnet 4.5 pricing (per million tokens)
    INPUT_COST_PER_1M = 3.00
    OUTPUT_COST_PER_1M = 15.00

    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        self.calls = []

    def add_call(self, input_tokens: int, output_tokens: int):
        """Record an API call."""
        cost = self.estimate_cost(input_tokens, output_tokens)

        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += cost

        self.calls.append({
            "timestamp": datetime.now().isoformat(),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost
        })

        logger.info(
            f"API call: {input_tokens} in, {output_tokens} out, ${cost:.4f} "
            f"(Total: ${self.total_cost:.4f})"
        )

    @staticmethod
    def estimate_cost(input_tokens: int, output_tokens: int) -> float:
        """
        Calculate cost for a single API call.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost in dollars
        """
        input_cost = (input_tokens / 1_000_000) * CostTracker.INPUT_COST_PER_1M
        output_cost = (output_tokens / 1_000_000) * CostTracker.OUTPUT_COST_PER_1M
        return input_cost + output_cost

    def get_summary(self) -> Dict:
        """Get cost tracking summary."""
        return {
            "total_calls": len(self.calls),
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_cost": self.total_cost,
            "average_cost_per_call": self.total_cost / len(self.calls) if self.calls else 0
        }


# ============================================================================
# Claude Analyzer
# ============================================================================

class ClaudeAnalyzer:
    """
    Complete Claude-based bill analysis system.

    Features:
    - Structured JSON outputs
    - Pydantic validation
    - Rate limiting
    - Response caching
    - Cost tracking
    - Retry logic
    """

    def __init__(self, api_key: Optional[str] = None, rate_limit_rpm: int = 50):
        """
        Initialize Claude analyzer.

        Args:
            api_key: Anthropic API key (defaults to config)
            rate_limit_rpm: Requests per minute limit
        """
        self.api_key = api_key or Config.ANTHROPIC_API_KEY
        if not self.api_key:
            raise ValueError("Anthropic API key is required")

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-5-20250929"

        # Rate limiting
        self.rate_limiter = RateLimiter(calls_per_minute=rate_limit_rpm)

        # Response caching (5 minute TTL)
        self.cache = TTLCache(maxsize=100, ttl=300)

        # Cost tracking
        self.cost_tracker = CostTracker()

        logger.info(f"Initialized ClaudeAnalyzer (model: {self.model}, rate: {rate_limit_rpm} RPM)")

    def analyze_bill(
        self,
        bill_data: Dict,
        context_chunks: List[Dict]
    ) -> Dict:
        """
        Complete bill analysis pipeline.

        Args:
            bill_data: Bill metadata from congress_api (must have bill_number, title)
            context_chunks: Retrieved chunks from RAG engine

        Returns:
            Complete analysis dictionary with all sections

        Example:
            >>> bill_data = {"bill_number": "H.R. 1234", "title": "Healthcare Act"}
            >>> chunks = rag_engine.hybrid_search("summary", top_k=10)
            >>> analysis = analyzer.analyze_bill(bill_data, chunks)
        """
        bill_number = bill_data.get("bill_number", "Unknown")
        bill_title = bill_data.get("title", "Unknown")

        logger.info(f"Starting analysis for {bill_number}")

        # Format context from chunks
        context = self._format_context(context_chunks)

        # Check if we have fiscal keywords for targeted retrieval
        has_fiscal_keywords = self._check_fiscal_keywords(context)

        # Run all analysis steps
        try:
            summary_data = self._generate_summary(bill_number, bill_title, context)
            provisions_data = self._extract_provisions(bill_number, bill_title, context)
            impact_data = self._analyze_impact(bill_number, bill_title, context)

            # Only analyze fiscal if keywords present
            if has_fiscal_keywords:
                fiscal_data = self._extract_fiscal(bill_number, bill_title, context)
            else:
                fiscal_data = {"fiscal_impact": None}

            # Combine results
            analysis = {
                "bill_number": bill_number,
                "bill_title": bill_title,
                "plain_english_summary": summary_data["plain_english_summary"],
                "key_provisions": provisions_data["key_provisions"],
                "practical_impact": impact_data["practical_impact"],
                "fiscal_impact": fiscal_data.get("fiscal_impact"),
                "generated_at": datetime.now().isoformat(),
                "model_used": self.model,
                "total_tokens": self.cost_tracker.total_input_tokens + self.cost_tracker.total_output_tokens,
                "estimated_cost": self.cost_tracker.total_cost
            }

            # Validate complete analysis
            validated = self.validate_analysis(analysis)

            logger.info(f"Analysis complete for {bill_number}")
            return validated

        except Exception as e:
            logger.error(f"Analysis failed for {bill_number}: {e}")
            raise ClaudeAPIError(f"Bill analysis failed: {e}") from e

    def _generate_summary(self, bill_number: str, bill_title: str, context: str) -> Dict:
        """Generate plain English summary."""
        prompt = format_summary_prompt(bill_number, bill_title, context)
        response = self._call_claude(prompt, max_tokens=1500)

        # Validate
        validated = SummaryResponse.model_validate(response)
        return validated.model_dump()

    def _extract_provisions(self, bill_number: str, bill_title: str, context: str) -> Dict:
        """Extract key provisions."""
        prompt = format_provisions_prompt(bill_number, bill_title, context)
        response = self._call_claude(prompt, max_tokens=1000)

        # Validate
        validated = ProvisionsResponse.model_validate(response)
        return validated.model_dump()

    def _analyze_impact(self, bill_number: str, bill_title: str, context: str) -> Dict:
        """Analyze practical citizen impact."""
        prompt = format_impact_prompt(bill_number, bill_title, context)
        response = self._call_claude(prompt, max_tokens=1500)

        # Validate
        validated = ImpactResponse.model_validate(response)
        return validated.model_dump()

    def _extract_fiscal(self, bill_number: str, bill_title: str, context: str) -> Dict:
        """Extract fiscal impact if present."""
        prompt = format_fiscal_prompt(bill_number, bill_title, context)
        response = self._call_claude(prompt, max_tokens=1000)

        # Validate
        validated = FiscalResponse.model_validate(response)
        return validated.model_dump()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((RateLimitError, anthropic.APIConnectionError))
    )
    def _call_claude(self, prompt: str, max_tokens: int = 1500) -> Dict:
        """
        Low-level API call wrapper with retry logic.

        Args:
            prompt: User prompt
            max_tokens: Maximum response tokens

        Returns:
            Parsed JSON response

        Raises:
            ClaudeAPIError: On API failures
            InvalidJSONError: On malformed JSON
        """
        # Check cache
        cache_key = f"{prompt[:100]}:{max_tokens}"
        if cache_key in self.cache:
            logger.debug("Using cached response")
            return self.cache[cache_key]

        # Apply rate limiting
        self.rate_limiter.wait_if_needed()

        logger.debug(f"Calling Claude API (max_tokens={max_tokens})")

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.0,  # Deterministic
                system=ANALYST_SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract response
            response_text = response.content[0].text

            # Parse JSON (strip markdown code fences if present)
            try:
                # Remove markdown code fences if present
                json_text = response_text.strip()
                if json_text.startswith("```json"):
                    json_text = json_text[7:]  # Remove ```json
                if json_text.startswith("```"):
                    json_text = json_text[3:]  # Remove ```
                if json_text.endswith("```"):
                    json_text = json_text[:-3]  # Remove trailing ```
                json_text = json_text.strip()

                parsed = json.loads(json_text, strict=False)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON from Claude: {response_text[:200]}")
                raise InvalidJSONError(f"Claude returned invalid JSON: {e}") from e

            # Track cost
            self.cost_tracker.add_call(
                response.usage.input_tokens,
                response.usage.output_tokens
            )

            # Cache successful response
            self.cache[cache_key] = parsed

            return parsed

        except anthropic.RateLimitError as e:
            logger.warning(f"Rate limit hit: {e}")
            raise RateLimitError("API rate limit exceeded") from e

        except anthropic.APIError as e:
            logger.error(f"Anthropic API error: {e}")
            raise ClaudeAPIError(f"API error: {e}") from e

        except Exception as e:
            logger.error(f"Unexpected error calling Claude: {e}")
            raise ClaudeAPIError(f"Unexpected error: {e}") from e

    def generate_traceability(
        self,
        summary: str,
        chunks: List[Dict]
    ) -> List[Dict]:
        """
        Generate provenance links mapping summary sentences to source chunks.

        Args:
            summary: Generated summary text
            chunks: Source chunks used for summary

        Returns:
            List of provenance mappings

        Example:
            >>> provenance = analyzer.generate_traceability(summary, chunks)
            >>> for entry in provenance:
            ...     print(f"{entry['summary_sentence']} -> {entry['source_chunk_id']}")
        """
        logger.info("Generating provenance links")

        # Format chunks with IDs
        chunks_context = self._format_chunks_for_traceability(chunks)

        # Create prompt
        prompt = format_traceability_prompt(summary, chunks_context)

        # Call Claude
        response = self._call_claude(prompt, max_tokens=2000)

        # Validate
        try:
            validated = ProvenanceResponse.model_validate(response)
            provenance = validated.model_dump()["provenance"]

            # Additional validation: check offsets are within chunk bounds
            for entry in provenance:
                chunk_id = entry["source_chunk_id"]
                chunk = next((c for c in chunks if c["id"] == chunk_id), None)

                if chunk:
                    chunk_len = len(chunk["text"])
                    if entry["char_end"] > chunk_len:
                        logger.warning(
                            f"Invalid offset for {chunk_id}: {entry['char_end']} > {chunk_len}"
                        )

            logger.info(f"Generated {len(provenance)} provenance links")
            return provenance

        except ValidationError as e:
            logger.error(f"Provenance validation failed: {e}")
            return []

    def _format_context(self, chunks: List[Dict]) -> str:
        """Format chunks into context string."""
        context_parts = []
        for chunk in chunks:
            section = chunk.get("metadata", {}).get("section", "Unknown")
            section_title = chunk.get("metadata", {}).get("section_title", "")

            header = f"[Section {section}"
            if section_title:
                header += f" - {section_title}"
            header += "]"

            context_parts.append(f"{header}\n{chunk['text']}\n")

        return "\n".join(context_parts)

    def _format_chunks_for_traceability(self, chunks: List[Dict]) -> str:
        """Format chunks with clear IDs for traceability."""
        parts = []
        for chunk in chunks:
            chunk_id = chunk.get("id", "unknown")
            text = chunk.get("text", "")
            parts.append(f"[Chunk ID: {chunk_id}]\n{text}\n")

        return "\n".join(parts)

    def _check_fiscal_keywords(self, context: str) -> bool:
        """Check if context contains fiscal keywords."""
        keywords = [
            "appropriated", "authorized", "$", "million", "billion",
            "funding", "budget", "cost", "revenue", "fiscal"
        ]
        context_lower = context.lower()
        return any(kw in context_lower for kw in keywords)

    def validate_analysis(self, analysis: Dict) -> Dict:
        """
        Validate complete analysis.

        Args:
            analysis: Analysis dictionary

        Returns:
            Validated analysis

        Raises:
            ValidationError: If validation fails
        """
        logger.info("Validating analysis")

        # Validate against Pydantic model
        try:
            validated = BillAnalysis.model_validate(analysis)

            # Additional checks
            summary = validated.plain_english_summary
            word_count = len(summary.split())

            if word_count < 100:
                logger.warning(f"Summary is short: {word_count} words")
            elif word_count > 700:
                logger.warning(f"Summary is long: {word_count} words")

            # Check for hallucination indicators
            hallucination_phrases = [
                "based on my knowledge",
                "from experience",
                "as we all know",
                "experts believe",
                "it is widely known"
            ]

            for phrase in hallucination_phrases:
                if phrase.lower() in summary.lower():
                    logger.error(f"Hallucination detected: '{phrase}' in summary")
                    raise ValueError(f"Potential hallucination detected: {phrase}")

            logger.info("Analysis validation passed")
            return validated.model_dump()

        except ValidationError as e:
            logger.error(f"Analysis validation failed: {e}")
            raise

    def get_cost_summary(self) -> Dict:
        """Get cost tracking summary."""
        return self.cost_tracker.get_summary()


# ============================================================================
# Main / Testing
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 80)
    print("Testing Claude Analyzer")
    print("=" * 80)

    try:
        # Initialize analyzer
        analyzer = ClaudeAnalyzer()

        # Test data
        bill_data = {
            "bill_number": "H.R. 1234",
            "title": "Healthcare Access and Funding Act of 2024"
        }

        test_chunks = [
            {
                "id": "chunk_0",
                "text": "SEC. 1. SHORT TITLE. This Act may be cited as the 'Healthcare Access and Funding Act of 2024'.",
                "metadata": {"section": "1", "section_title": "SHORT TITLE"}
            },
            {
                "id": "chunk_1",
                "text": "SEC. 2. APPROPRIATIONS. There is authorized to be appropriated $500 million annually for fiscal years 2025 through 2030 for rural healthcare infrastructure improvements.",
                "metadata": {"section": "2", "section_title": "APPROPRIATIONS"}
            }
        ]

        # Run analysis
        print("\n📊 Running bill analysis...")
        analysis = analyzer.analyze_bill(bill_data, test_chunks)

        print(f"\n✅ Analysis complete!")
        print(f"\nSummary ({len(analysis['plain_english_summary'].split())} words):")
        print(analysis['plain_english_summary'][:200] + "...")

        print(f"\nKey Provisions ({len(analysis['key_provisions'])} total):")
        for i, prov in enumerate(analysis['key_provisions'][:3], 1):
            print(f"  {i}. {prov}")

        print(f"\nFiscal Impact:")
        if analysis['fiscal_impact']:
            print(f"  Total: {analysis['fiscal_impact'].get('total_cost', 'N/A')}")
        else:
            print("  None identified")

        # Cost summary
        print(f"\n💰 Cost Summary:")
        cost_summary = analyzer.get_cost_summary()
        print(f"  Total calls: {cost_summary['total_calls']}")
        print(f"  Total cost: ${cost_summary['total_cost']:.4f}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
