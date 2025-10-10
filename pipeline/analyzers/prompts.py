"""
Structured prompt templates for Claude-based bill analysis.

All prompts are designed to produce JSON outputs for consistent parsing.
"""

# ============================================================================
# System Prompts
# ============================================================================

ANALYST_SYSTEM_PROMPT = """You are a non-partisan Congressional Research Service analyst for OpenUSPolitics.org.

Your role is to provide strictly objective, factual analysis of US legislation with NO political bias.

Core principles:
1. Base ALL analysis ONLY on the provided bill text - never use outside knowledge
2. Use clear, accessible language for general audiences
3. Remain completely neutral - no political spin or editorial commentary
4. Distinguish facts from potential implications
5. Acknowledge when information is not in the provided context
6. Focus on concrete provisions, not speculation

Output format: Always respond with valid JSON matching the specified schema."""


# ============================================================================
# Prompt 1: Plain English Summary
# ============================================================================

SUMMARY_PROMPT = """Analyze this bill and generate a plain English summary.

Bill: {bill_number}
Title: {bill_title}

Bill Context:
{context}

Generate a comprehensive but accessible summary following these instructions:

1. Write 2-3 paragraphs (300-500 words total)
2. First paragraph: What the bill does and its main purpose
3. Second paragraph: Key mechanisms and requirements
4. Third paragraph (if needed): Timeline, stakeholders, or implementation details

Requirements:
- Use simple, clear language (8th grade reading level)
- Explain technical terms when first used
- Focus on concrete actions the bill mandates
- Be strictly objective - no opinions or political framing
- Base ONLY on provided context - do not speculate
- If context is incomplete, note what's covered vs. not covered

Respond ONLY with valid JSON in this exact format:
{{
  "plain_english_summary": "Your 2-3 paragraph summary here..."
}}"""


# ============================================================================
# Prompt 2: Key Provisions
# ============================================================================

KEY_PROVISIONS_PROMPT = """Extract the key provisions from this bill.

Bill: {bill_number}
Title: {bill_title}

Bill Context:
{context}

Identify the 5-7 most important provisions in this bill.

Instructions:
1. Focus on concrete actions, requirements, or changes the bill creates
2. Each provision should be 1-2 clear sentences
3. Prioritize provisions by significance and impact
4. Include specific details (amounts, dates, entities) when present
5. Avoid vague or redundant provisions
6. Base ONLY on provided context

Examples of good provisions:
- "Authorizes $50 million annually for rural healthcare programs through 2030"
- "Requires companies with 500+ employees to report carbon emissions quarterly"
- "Establishes a new oversight board within the Department of Education"

Respond ONLY with valid JSON in this exact format:
{{
  "key_provisions": [
    "First key provision...",
    "Second key provision...",
    "Third key provision...",
    "Fourth key provision...",
    "Fifth key provision..."
  ]
}}"""


# ============================================================================
# Prompt 3: Practical Impact
# ============================================================================

PRACTICAL_IMPACT_PROMPT = """Explain how this bill affects ordinary citizens.

Bill: {bill_number}
Title: {bill_title}

Bill Context:
{context}

Analyze the practical, real-world impact on citizens.

Instructions:
1. Explain who is directly affected (individuals, businesses, organizations)
2. Describe concrete changes people will experience
3. Note timeline for implementation (when effects take place)
4. Provide specific examples where possible
5. Distinguish between mandatory requirements and voluntary provisions
6. Acknowledge if impacts are limited or unclear from context

Format:
- 2-3 paragraphs
- Lead with most significant impacts
- Use concrete examples ("parents of school-age children" not "stakeholders")
- Be specific about winners/losers WITHOUT political framing

Respond ONLY with valid JSON in this exact format:
{{
  "practical_impact": "Your 2-3 paragraph analysis of citizen impact..."
}}"""


# ============================================================================
# Prompt 4: Fiscal Impact
# ============================================================================

FISCAL_IMPACT_PROMPT = """Analyze the fiscal and budgetary impact of this bill.

Bill: {bill_number}
Title: {bill_title}

Bill Context:
{context}

Extract all budget-related information from the bill.

Instructions:
1. Identify ALL monetary amounts (appropriations, authorizations, costs, revenues)
2. Note funding sources (new taxes, existing budgets, deficit spending)
3. Extract time periods (annual, total, multi-year)
4. Mention CBO score or cost estimates if referenced
5. Distinguish between authorized (allowed) and appropriated (allocated) funds
6. If NO fiscal information is in context, set fiscal_impact to null

Look for keywords: "appropriated", "authorized", "$", "million", "billion", "funding", "budget"

Respond ONLY with valid JSON in this exact format:

If fiscal information is present:
{{
  "fiscal_impact": {{
    "total_cost": "Amount and timeframe, e.g., '$500 million over 5 years'",
    "annual_cost": "Annual amount if specified",
    "funding_sources": ["List of funding sources"],
    "revenue_effects": "Any revenue impacts (tax changes, fees, etc.)",
    "cbo_score": "CBO cost estimate if mentioned, otherwise null",
    "breakdown": "Detailed breakdown of where money goes"
  }}
}}

If NO fiscal information:
{{
  "fiscal_impact": null
}}"""


# ============================================================================
# Prompt 5: Traceability/Provenance
# ============================================================================

TRACEABILITY_PROMPT = """Generate provenance links for this summary.

Summary to trace:
{summary}

Available source chunks:
{chunks_context}

For EACH sentence in the summary, identify the exact source passage.

Instructions:
1. Take each sentence from the summary
2. Find the specific chunk(s) that support that sentence
3. Identify the exact character offsets within the chunk
4. A sentence may map to multiple chunks if it combines information

Validation:
- Every sentence must have at least one source
- Character offsets must be within chunk bounds
- Be precise - identify the exact supporting text, not the whole chunk

Respond ONLY with valid JSON in this exact format:
{{
  "provenance": [
    {{
      "summary_sentence": "First sentence from summary...",
      "source_chunk_id": "chunk_0",
      "source_text": "Exact text from chunk that supports this",
      "char_start": 150,
      "char_end": 230
    }},
    {{
      "summary_sentence": "Second sentence from summary...",
      "source_chunk_id": "chunk_2",
      "source_text": "Supporting text from chunk",
      "char_start": 50,
      "char_end": 180
    }}
  ]
}}"""


# ============================================================================
# Formatting Functions
# ============================================================================

def format_summary_prompt(bill_number: str, bill_title: str, context: str) -> str:
    """
    Format plain English summary prompt.

    Args:
        bill_number: Bill identifier (e.g., "H.R. 1234")
        bill_title: Bill title
        context: Retrieved bill context

    Returns:
        Formatted prompt string
    """
    return SUMMARY_PROMPT.format(
        bill_number=bill_number,
        bill_title=bill_title,
        context=context
    )


def format_provisions_prompt(bill_number: str, bill_title: str, context: str) -> str:
    """
    Format key provisions extraction prompt.

    Args:
        bill_number: Bill identifier
        bill_title: Bill title
        context: Retrieved bill context

    Returns:
        Formatted prompt string
    """
    return KEY_PROVISIONS_PROMPT.format(
        bill_number=bill_number,
        bill_title=bill_title,
        context=context
    )


def format_impact_prompt(bill_number: str, bill_title: str, context: str) -> str:
    """
    Format practical impact analysis prompt.

    Args:
        bill_number: Bill identifier
        bill_title: Bill title
        context: Retrieved bill context

    Returns:
        Formatted prompt string
    """
    return PRACTICAL_IMPACT_PROMPT.format(
        bill_number=bill_number,
        bill_title=bill_title,
        context=context
    )


def format_fiscal_prompt(bill_number: str, bill_title: str, context: str) -> str:
    """
    Format fiscal impact extraction prompt.

    Args:
        bill_number: Bill identifier
        bill_title: Bill title
        context: Retrieved bill context

    Returns:
        Formatted prompt string
    """
    return FISCAL_IMPACT_PROMPT.format(
        bill_number=bill_number,
        bill_title=bill_title,
        context=context
    )


def format_traceability_prompt(summary: str, chunks_context: str) -> str:
    """
    Format provenance/traceability prompt.

    Args:
        summary: Generated summary to trace
        chunks_context: Formatted context with chunk IDs

    Returns:
        Formatted prompt string
    """
    return TRACEABILITY_PROMPT.format(
        summary=summary,
        chunks_context=chunks_context
    )


# ============================================================================
# Negative Examples (What NOT to do)
# ============================================================================

NEGATIVE_CONSTRAINTS = """
DO NOT:
- Express political opinions or take sides
- Use loaded language ("controversial", "groundbreaking", "disastrous")
- Speculate beyond what's in the text ("this could lead to...", "critics argue...")
- Reference current events or political context not in the bill
- Make predictions about passage or political feasibility
- Include phrases like "based on my knowledge" or "from experience"
- Editorialize about whether provisions are good/bad
- Assume information not explicitly stated in the context

RED FLAGS to avoid:
- "This controversial bill..."
- "Experts believe..."
- "This will likely cause..."
- "As we all know..."
- "The administration wants..."
"""
