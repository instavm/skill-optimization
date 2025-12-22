"""
Evaluation Metrics for Code Review Skills

This module provides comprehensive metrics to evaluate the quality
of code review outputs.
"""

import json
from typing import Dict, List, Any, Set
from dataclasses import dataclass
import re


@dataclass
class EvaluationResult:
    """Results from evaluating a code review."""
    precision: float  # % of reported issues that are real
    recall: float  # % of real issues that were found
    f1_score: float  # Harmonic mean of precision and recall
    severity_accuracy: float  # % of issues with correct severity
    critical_recall: float  # % of critical issues found (must be high!)
    false_positive_rate: float  # % of reported issues that are false
    fix_quality_score: float  # Quality of suggested fixes (0-1)
    overall_score: float  # Weighted composite score


class CodeReviewEvaluator:
    """
    Evaluates code review outputs against expected results.
    """

    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize evaluator with metric weights.

        Args:
            weights: Dictionary of metric names to weights for overall score
        """
        self.weights = weights or {
            "precision": 0.15,
            "recall": 0.25,
            "critical_recall": 0.30,  # Most important!
            "severity_accuracy": 0.15,
            "fix_quality": 0.15
        }

    def evaluate(
        self,
        predicted_issues: List[Dict[str, Any]],
        expected_issues: List[Dict[str, Any]],
        code_context: str = ""
    ) -> EvaluationResult:
        """
        Evaluate predicted issues against expected issues.

        Args:
            predicted_issues: Issues found by the skill
            expected_issues: Ground truth issues
            code_context: The code that was reviewed (for context)

        Returns:
            EvaluationResult with all metrics
        """
        # Match predicted issues to expected issues
        matched = self._match_issues(predicted_issues, expected_issues)

        # Calculate metrics
        precision = self._calculate_precision(matched)
        recall = self._calculate_recall(matched, len(expected_issues))
        f1 = self._calculate_f1(precision, recall)
        severity_acc = self._calculate_severity_accuracy(matched)
        critical_recall = self._calculate_critical_recall(matched, expected_issues)
        fpr = self._calculate_false_positive_rate(matched, len(predicted_issues))
        fix_quality = self._evaluate_fix_quality(predicted_issues)

        # Weighted overall score
        overall = (
            self.weights["precision"] * precision +
            self.weights["recall"] * recall +
            self.weights["critical_recall"] * critical_recall +
            self.weights["severity_accuracy"] * severity_acc +
            self.weights["fix_quality"] * fix_quality
        )

        return EvaluationResult(
            precision=precision,
            recall=recall,
            f1_score=f1,
            severity_accuracy=severity_acc,
            critical_recall=critical_recall,
            false_positive_rate=fpr,
            fix_quality_score=fix_quality,
            overall_score=overall
        )

    def _match_issues(
        self,
        predicted: List[Dict],
        expected: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        Match predicted issues to expected issues using fuzzy matching.

        Returns:
            List of matches with format:
            {
                "predicted": predicted_issue or None,
                "expected": expected_issue or None,
                "match_score": float (0-1)
            }
        """
        matches = []
        used_predicted = set()
        used_expected = set()

        # First pass: find exact matches
        for i, exp in enumerate(expected):
            best_match = None
            best_score = 0.0

            for j, pred in enumerate(predicted):
                if j in used_predicted:
                    continue

                score = self._issue_similarity(pred, exp)
                if score > best_score and score > 0.6:  # Threshold for match
                    best_score = score
                    best_match = j

            if best_match is not None:
                matches.append({
                    "predicted": predicted[best_match],
                    "expected": exp,
                    "match_score": best_score
                })
                used_predicted.add(best_match)
                used_expected.add(i)

        # Add unmatched expected (false negatives)
        for i, exp in enumerate(expected):
            if i not in used_expected:
                matches.append({
                    "predicted": None,
                    "expected": exp,
                    "match_score": 0.0
                })

        # Add unmatched predicted (false positives)
        for j, pred in enumerate(predicted):
            if j not in used_predicted:
                matches.append({
                    "predicted": pred,
                    "expected": None,
                    "match_score": 0.0
                })

        return matches

    def _issue_similarity(self, pred: Dict, exp: Dict) -> float:
        """
        Calculate similarity between predicted and expected issue.

        Uses multiple signals:
        - Title/description text similarity
        - Category match
        - Location match
        """
        score = 0.0

        # Text similarity (simple word overlap)
        pred_text = (pred.get("title", "") + " " + pred.get("description", "")).lower()
        exp_text = (exp.get("title", "") + " " + exp.get("description", "")).lower()

        pred_words = set(re.findall(r'\w+', pred_text))
        exp_words = set(re.findall(r'\w+', exp_text))

        if pred_words and exp_words:
            overlap = len(pred_words & exp_words)
            total = len(pred_words | exp_words)
            score += 0.6 * (overlap / total)

        # Category match
        if pred.get("category") == exp.get("category"):
            score += 0.2

        # Location match (if provided)
        pred_locs = set(pred.get("locations", []))
        exp_locs = set(exp.get("locations", []))
        if pred_locs and exp_locs:
            loc_overlap = len(pred_locs & exp_locs)
            loc_total = len(pred_locs | exp_locs)
            score += 0.2 * (loc_overlap / loc_total)

        return min(score, 1.0)

    def _calculate_precision(self, matches: List[Dict]) -> float:
        """Precision: TP / (TP + FP)"""
        true_positives = sum(1 for m in matches if m["predicted"] and m["expected"])
        false_positives = sum(1 for m in matches if m["predicted"] and not m["expected"])

        total_predicted = true_positives + false_positives
        if total_predicted == 0:
            return 1.0  # No predictions = no false positives

        return true_positives / total_predicted

    def _calculate_recall(self, matches: List[Dict], total_expected: int) -> float:
        """Recall: TP / (TP + FN)"""
        true_positives = sum(1 for m in matches if m["predicted"] and m["expected"])

        if total_expected == 0:
            return 1.0  # No expected issues = perfect recall

        return true_positives / total_expected

    def _calculate_f1(self, precision: float, recall: float) -> float:
        """F1 Score: 2 * (precision * recall) / (precision + recall)"""
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)

    def _calculate_severity_accuracy(self, matches: List[Dict]) -> float:
        """
        Percentage of matched issues with correct severity.
        Allows ±1 level tolerance (e.g., High vs Medium is acceptable).
        """
        severity_order = ["Low", "Medium", "High", "Critical"]

        correct = 0
        total = 0

        for match in matches:
            if match["predicted"] and match["expected"]:
                pred_sev = match["predicted"].get("severity", "")
                exp_sev = match["expected"].get("severity", "")

                try:
                    pred_idx = severity_order.index(pred_sev)
                    exp_idx = severity_order.index(exp_sev)

                    # Exact match or ±1 level
                    if abs(pred_idx - exp_idx) <= 1:
                        correct += 1
                    total += 1
                except ValueError:
                    # Severity not in list
                    total += 1

        return correct / total if total > 0 else 1.0

    def _calculate_critical_recall(
        self,
        matches: List[Dict],
        expected_issues: List[Dict]
    ) -> float:
        """
        Critical recall: % of critical issues found.
        This is the MOST IMPORTANT metric for security.
        """
        critical_expected = [
            exp for exp in expected_issues
            if exp.get("severity") == "Critical"
        ]

        if not critical_expected:
            return 1.0  # No critical issues = perfect score

        critical_found = sum(
            1 for m in matches
            if m["expected"] and m["expected"].get("severity") == "Critical"
            and m["predicted"] is not None
        )

        return critical_found / len(critical_expected)

    def _calculate_false_positive_rate(
        self,
        matches: List[Dict],
        total_predicted: int
    ) -> float:
        """False positive rate: FP / (FP + TP)"""
        false_positives = sum(1 for m in matches if m["predicted"] and not m["expected"])

        if total_predicted == 0:
            return 0.0

        return false_positives / total_predicted

    def _evaluate_fix_quality(self, predicted_issues: List[Dict]) -> float:
        """
        Evaluate the quality of suggested fixes.

        Criteria:
        - Is a fix provided?
        - Is it actionable (specific)?
        - Does it include code example?
        - Is the explanation clear?
        """
        if not predicted_issues:
            return 0.0

        total_score = 0.0

        for issue in predicted_issues:
            fix_score = 0.0

            # Has fix description
            if issue.get("fix_description") or issue.get("suggested_fix"):
                fix_score += 0.3

            # Has code example
            if issue.get("code_example") or "```" in str(issue.get("suggested_fix", "")):
                fix_score += 0.4

            # Has explanation
            if issue.get("explanation") or len(str(issue.get("fix_description", ""))) > 50:
                fix_score += 0.3

            total_score += fix_score

        return total_score / len(predicted_issues)


def create_metric_function(evaluator: CodeReviewEvaluator):
    """
    Create a DSPy-compatible metric function.

    Args:
        evaluator: CodeReviewEvaluator instance

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
        # Extract predicted issues from prediction
        predicted = prediction.issues if hasattr(prediction, 'issues') else []

        # Parse if it's a string
        if isinstance(predicted, str):
            try:
                predicted = json.loads(predicted)
            except:
                predicted = []

        # Get expected issues from example
        expected = example.expected_issues if hasattr(example, 'expected_issues') else []

        # Evaluate
        result = evaluator.evaluate(predicted, expected)

        return result.overall_score

    return metric
