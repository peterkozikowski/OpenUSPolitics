"""Bias auditing for bill analyses to ensure non-partisan content."""

import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class BiasAuditor:
    """
    Audit bill analyses for potential political bias.

    Checks for:
    - Partisan language
    - Opinionated statements
    - Unbalanced framing
    - Speculation vs. fact
    """

    # Lists of potentially biased terms (can be expanded)
    PARTISAN_KEYWORDS = [
        # Left-leaning terms
        "socialist", "radical left", "progressive agenda", "liberal bias",
        # Right-leaning terms
        "conservative values", "right-wing", "traditional values", "patriotic duty",
        # General partisan terms
        "extremist", "radical", "activist judges", "special interests",
        # Charged language
        "disaster", "catastrophe", "brilliant", "genius", "idiotic", "stupid",
    ]

    OPINION_INDICATORS = [
        "clearly", "obviously", "undoubtedly", "certainly should",
        "must", "everyone knows", "the fact is", "the truth is",
        "it's clear that", "without question",
    ]

    SPECULATION_INDICATORS = [
        "might lead to", "could result in", "may cause", "likely to",
        "probably will", "potentially", "possibly", "presumably",
    ]

    def __init__(self):
        """Initialize the bias auditor."""
        logger.info("Initialized bias auditor")

    def audit_analysis(self, analysis_text: str) -> Dict:
        """
        Audit an analysis for potential bias.

        Args:
            analysis_text: Analysis text to audit

        Returns:
            Dictionary with audit results:
                - bias_score: Overall bias score (0-100, lower is better)
                - issues: List of detected issues
                - warnings: List of warnings
                - passed: Whether analysis passed audit
        """
        logger.info("Auditing analysis for bias")

        issues = []
        warnings = []

        # Check for partisan keywords
        partisan_issues = self._check_partisan_language(analysis_text)
        issues.extend(partisan_issues)

        # Check for opinion indicators
        opinion_issues = self._check_opinion_language(analysis_text)
        warnings.extend(opinion_issues)

        # Check for speculation
        speculation_issues = self._check_speculation(analysis_text)
        warnings.extend(speculation_issues)

        # Check for emotional language
        emotional_issues = self._check_emotional_language(analysis_text)
        issues.extend(emotional_issues)

        # Check for balance
        balance_issues = self._check_balance(analysis_text)
        warnings.extend(balance_issues)

        # Calculate bias score (0-100, lower is better)
        bias_score = self._calculate_bias_score(issues, warnings)

        # Determine if passed (score < 30)
        passed = bias_score < 30

        result = {
            "bias_score": bias_score,
            "issues": issues,
            "warnings": warnings,
            "passed": passed,
            "summary": self._generate_summary(bias_score, issues, warnings),
        }

        logger.info(
            f"Audit complete: score={bias_score}, "
            f"issues={len(issues)}, warnings={len(warnings)}, passed={passed}"
        )

        return result

    def _check_partisan_language(self, text: str) -> List[Dict]:
        """Check for partisan keywords and phrases."""
        issues = []
        text_lower = text.lower()

        for keyword in self.PARTISAN_KEYWORDS:
            if keyword.lower() in text_lower:
                # Find context
                pattern = re.compile(rf".{{0,50}}{re.escape(keyword)}.{{0,50}}", re.IGNORECASE)
                matches = pattern.findall(text)

                for match in matches:
                    issues.append({
                        "type": "partisan_language",
                        "severity": "high",
                        "keyword": keyword,
                        "context": match.strip(),
                        "suggestion": f"Remove or rephrase partisan term '{keyword}'",
                    })

        return issues

    def _check_opinion_language(self, text: str) -> List[Dict]:
        """Check for opinion indicators."""
        issues = []
        text_lower = text.lower()

        for indicator in self.OPINION_INDICATORS:
            if indicator.lower() in text_lower:
                pattern = re.compile(rf".{{0,50}}{re.escape(indicator)}.{{0,50}}", re.IGNORECASE)
                matches = pattern.findall(text)

                for match in matches:
                    issues.append({
                        "type": "opinion_language",
                        "severity": "medium",
                        "indicator": indicator,
                        "context": match.strip(),
                        "suggestion": f"Replace opinion indicator '{indicator}' with factual statement",
                    })

        return issues

    def _check_speculation(self, text: str) -> List[Dict]:
        """Check for speculative language."""
        issues = []
        text_lower = text.lower()

        speculation_count = 0
        for indicator in self.SPECULATION_INDICATORS:
            if indicator.lower() in text_lower:
                speculation_count += text_lower.count(indicator.lower())

        # Only flag if excessive speculation
        if speculation_count > 3:
            issues.append({
                "type": "excessive_speculation",
                "severity": "low",
                "count": speculation_count,
                "suggestion": "Reduce speculative language and focus on factual content",
            })

        return issues

    def _check_emotional_language(self, text: str) -> List[Dict]:
        """Check for emotionally charged language."""
        issues = []

        # Check for excessive exclamation marks
        exclamation_count = text.count("!")
        if exclamation_count > 2:
            issues.append({
                "type": "emotional_punctuation",
                "severity": "medium",
                "count": exclamation_count,
                "suggestion": "Remove excessive exclamation marks",
            })

        # Check for all caps (shouting)
        all_caps_words = re.findall(r'\b[A-Z]{4,}\b', text)
        if len(all_caps_words) > 3:
            issues.append({
                "type": "excessive_emphasis",
                "severity": "medium",
                "words": all_caps_words[:3],
                "suggestion": "Avoid excessive use of all-caps words",
            })

        return issues

    def _check_balance(self, text: str) -> List[Dict]:
        """Check for balanced presentation."""
        issues = []

        # Check for one-sided language
        # Count positive vs. negative framing words
        positive_words = ["benefit", "improve", "enhance", "support", "protect"]
        negative_words = ["harm", "damage", "threaten", "undermine", "destroy"]

        text_lower = text.lower()
        positive_count = sum(text_lower.count(word) for word in positive_words)
        negative_count = sum(text_lower.count(word) for word in negative_words)

        # Flag if highly imbalanced (ratio > 3:1)
        if positive_count > 0 or negative_count > 0:
            ratio = max(positive_count, negative_count) / max(min(positive_count, negative_count), 1)
            if ratio > 3:
                issues.append({
                    "type": "imbalanced_framing",
                    "severity": "low",
                    "positive_count": positive_count,
                    "negative_count": negative_count,
                    "suggestion": "Ensure balanced presentation of bill impacts",
                })

        return issues

    def _calculate_bias_score(self, issues: List[Dict], warnings: List[Dict]) -> int:
        """
        Calculate overall bias score.

        Args:
            issues: List of detected issues
            warnings: List of warnings

        Returns:
            Bias score (0-100, lower is better)
        """
        score = 0

        # Weight issues by severity
        for issue in issues:
            severity = issue.get("severity", "low")
            if severity == "high":
                score += 15
            elif severity == "medium":
                score += 10
            else:
                score += 5

        # Add warnings (lower weight)
        score += len(warnings) * 3

        # Cap at 100
        return min(score, 100)

    def _generate_summary(self, score: int, issues: List[Dict], warnings: List[Dict]) -> str:
        """Generate human-readable summary of audit results."""
        if score < 10:
            return "Excellent: No significant bias detected."
        elif score < 30:
            return f"Good: Minor issues detected ({len(issues)} issues, {len(warnings)} warnings)."
        elif score < 60:
            return f"Concerning: Moderate bias detected ({len(issues)} issues, {len(warnings)} warnings). Review recommended."
        else:
            return f"Failed: Significant bias detected ({len(issues)} issues, {len(warnings)} warnings). Revision required."


if __name__ == "__main__":
    # Test the bias auditor
    logging.basicConfig(level=logging.INFO)

    auditor = BiasAuditor()

    # Test with neutral text
    neutral_text = """
    This bill provides funding for infrastructure improvements.
    Section 1 allocates $100 million for road repairs.
    Section 2 establishes a committee to oversee implementation.
    """

    print("Testing neutral text...")
    result = auditor.audit_analysis(neutral_text)
    print(f"Score: {result['bias_score']}")
    print(f"Passed: {result['passed']}")
    print(f"Summary: {result['summary']}\n")

    # Test with biased text
    biased_text = """
    This is clearly a radical socialist agenda that will destroy the economy!
    Obviously, this bill is a disaster. Everyone knows it will lead to catastrophe.
    The liberal bias is undoubtedly evident in every section.
    """

    print("Testing biased text...")
    result = auditor.audit_analysis(biased_text)
    print(f"Score: {result['bias_score']}")
    print(f"Passed: {result['passed']}")
    print(f"Summary: {result['summary']}")
    print(f"\nIssues found ({len(result['issues'])}):")
    for issue in result['issues'][:3]:
        print(f"  - {issue['type']}: {issue.get('keyword', issue.get('indicator', 'N/A'))}")
