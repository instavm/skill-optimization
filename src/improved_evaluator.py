"""
Improved Evaluation Metric for Code Review Skills

This metric measures multiple dimensions:
1. Issue Detection - Did it find the critical issues?
2. Severity Accuracy - Are severity levels correct?
3. Explanation Quality - Are issues well-explained?
4. Fix Quality - Are fixes actionable with code examples?
5. False Positive Rate - How many bogus issues?
"""

import re
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class ImprovedEvaluationResult:
    """Comprehensive evaluation results."""
    issue_detection_score: float  # 0-1, how many issues found
    severity_accuracy: float  # 0-1, correct severity levels
    explanation_quality: float  # 0-1, quality of descriptions
    fix_quality: float  # 0-1, quality of suggested fixes
    false_positive_rate: float  # 0-1, bogus issues (lower is better)
    overall_score: float  # Weighted average


class ImprovedCodeReviewEvaluator:
    """
    Better evaluator that measures multiple quality dimensions.
    """

    def __init__(self):
        self.weights = {
            "issue_detection": 0.35,  # Most important
            "severity_accuracy": 0.20,
            "explanation_quality": 0.20,
            "fix_quality": 0.15,
            "false_positive_penalty": 0.10
        }

    def evaluate(
        self,
        critical_issues_text: str,
        high_issues_text: str,
        expected_critical_count: int,
        expected_high_count: int,
        code_sample: str = ""
    ) -> ImprovedEvaluationResult:
        """
        Evaluate LLM output comprehensively.

        Args:
            critical_issues_text: LLM's critical issues output
            high_issues_text: LLM's high issues output
            expected_critical_count: Expected number of critical issues
            expected_high_count: Expected number of high issues
            code_sample: Original code (for context)

        Returns:
            ImprovedEvaluationResult with scores
        """
        # Parse issues from text
        critical_issues = self._parse_issues(critical_issues_text)
        high_issues = self._parse_issues(high_issues_text)

        # 1. Issue Detection Score
        found_critical = len(critical_issues)
        found_high = len(high_issues)

        # Use F1-like score to balance precision and recall
        critical_recall = min(found_critical / expected_critical_count, 1.0) if expected_critical_count > 0 else 0
        high_recall = min(found_high / expected_high_count, 1.0) if expected_high_count > 0 else 0

        # Penalty for over-reporting (likely false positives)
        critical_precision = min(expected_critical_count / found_critical, 1.0) if found_critical > 0 else 0
        high_precision = min(expected_high_count / found_high, 1.0) if found_high > 0 else 0

        critical_f1 = self._f1_score(critical_precision, critical_recall)
        high_f1 = self._f1_score(high_precision, high_recall)

        issue_detection_score = (critical_f1 * 0.7 + high_f1 * 0.3)

        # 2. Severity Accuracy (are issues in right buckets?)
        # If we find issues in critical that should be high, or vice versa
        # For now, assume if counts match, severity is correct
        severity_score = 0.5  # Base score
        if found_critical >= expected_critical_count * 0.8:
            severity_score += 0.25
        if found_high >= expected_high_count * 0.8:
            severity_score += 0.25

        # 3. Explanation Quality
        explanation_score = self._evaluate_explanation_quality(
            critical_issues + high_issues
        )

        # 4. Fix Quality
        fix_score = self._evaluate_fix_quality(
            critical_issues + high_issues
        )

        # 5. False Positive Rate
        total_found = found_critical + found_high
        total_expected = expected_critical_count + expected_high_count
        over_reporting = max(0, total_found - total_expected)
        false_positive_rate = over_reporting / total_found if total_found > 0 else 0

        # Calculate overall score (0-1)
        overall = (
            self.weights["issue_detection"] * issue_detection_score +
            self.weights["severity_accuracy"] * severity_score +
            self.weights["explanation_quality"] * explanation_score +
            self.weights["fix_quality"] * fix_score -
            self.weights["false_positive_penalty"] * false_positive_rate
        )

        overall = max(0, min(1, overall))  # Clamp to [0, 1]

        return ImprovedEvaluationResult(
            issue_detection_score=issue_detection_score,
            severity_accuracy=severity_score,
            explanation_quality=explanation_score,
            fix_quality=fix_score,
            false_positive_rate=false_positive_rate,
            overall_score=overall
        )

    def _parse_issues(self, text: str) -> List[Dict[str, str]]:
        """Parse issues from LLM text output."""
        if not text or text == "N/A":
            return []

        issues = []
        lines = str(text).split('\n')

        for line in lines:
            line = line.strip()

            # Skip empty lines, headers, or very short lines
            if not line or len(line) < 15:
                continue

            # Skip markdown headers
            if line.startswith('#'):
                continue

            # Extract issue information
            issue = {
                "text": line,
                "has_details": len(line) > 50,
                "has_location": bool(re.search(r'in\s+\w+|at\s+line|location:', line, re.I)),
                "has_impact": any(word in line.lower() for word in ['impact', 'allows', 'can', 'enables', 'leads to']),
                "has_example": '```' in line or 'example:' in line.lower()
            }

            issues.append(issue)

        return issues

    def _evaluate_explanation_quality(self, issues: List[Dict]) -> float:
        """
        Evaluate how well issues are explained.

        Good explanations have:
        - Specific details (>50 chars)
        - Location information
        - Impact description
        """
        if not issues:
            return 0.0

        quality_scores = []

        for issue in issues:
            score = 0.0

            # Has substantial details
            if issue.get("has_details"):
                score += 0.4

            # Has location information
            if issue.get("has_location"):
                score += 0.3

            # Has impact description
            if issue.get("has_impact"):
                score += 0.3

            quality_scores.append(score)

        return sum(quality_scores) / len(quality_scores)

    def _evaluate_fix_quality(self, issues: List[Dict]) -> float:
        """
        Evaluate quality of suggested fixes.

        Good fixes:
        - Are specific
        - Include code examples
        - Explain why the fix works
        """
        if not issues:
            return 0.0

        fix_scores = []

        for issue in issues:
            score = 0.0

            text = issue.get("text", "").lower()

            # Has fix suggestion
            if any(word in text for word in ['use', 'should', 'replace', 'change', 'instead']):
                score += 0.4

            # Has code example
            if issue.get("has_example") or '`' in text:
                score += 0.4

            # Has explanation
            if len(text) > 100:
                score += 0.2

            fix_scores.append(score)

        return sum(fix_scores) / len(fix_scores)

    def _f1_score(self, precision: float, recall: float) -> float:
        """Calculate F1 score."""
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)


def create_improved_metric(evaluator: ImprovedCodeReviewEvaluator):
    """
    Create DSPy-compatible metric using improved evaluator.

    Args:
        evaluator: ImprovedCodeReviewEvaluator instance

    Returns:
        Function that can be used with DSPy optimizers
    """
    def metric(example, prediction, trace=None) -> float:
        """
        DSPy metric function.

        Args:
            example: DSPy Example with expected output
            prediction: Model prediction
            trace: Optional trace for debugging

        Returns:
            Score from 0.0 to 1.0 (higher is better)
        """
        # Extract predicted issues
        critical_text = str(getattr(prediction, 'critical_issues', ''))
        high_text = str(getattr(prediction, 'high_issues', ''))

        # Get expected counts from example
        expected_critical = getattr(example, 'expected_critical_count', 0)
        expected_high = getattr(example, 'expected_high_count', 0)

        # Get code for context
        code = getattr(example, 'code', '')

        # Evaluate
        result = evaluator.evaluate(
            critical_issues_text=critical_text,
            high_issues_text=high_text,
            expected_critical_count=expected_critical,
            expected_high_count=expected_high,
            code_sample=code
        )

        return result.overall_score

    return metric
