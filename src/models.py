"""
DSPy Signatures and Modules for Code Review Skill

This module defines the structured signatures and modules that decompose
the code review task into optimizable components.
"""

import dspy
from typing import List, Dict


class IssueDetection(dspy.Signature):
    """Detect code quality, security, and performance issues in code."""

    code = dspy.InputField(desc="The source code to review")
    language = dspy.InputField(desc="Programming language (python, javascript, etc)")

    issues = dspy.OutputField(
        desc="List of issues found. Each issue should include: "
             "title, severity (Critical/High/Medium/Low), location, "
             "description, and impact"
    )


class SeverityClassification(dspy.Signature):
    """Classify the severity of identified code issues."""

    issue_description = dspy.InputField(desc="Description of the code issue")
    context = dspy.InputField(desc="Code context where issue appears")

    severity = dspy.OutputField(
        desc="Severity level: Critical (security/data loss), "
             "High (bugs/performance), Medium (quality), Low (style)"
    )
    justification = dspy.OutputField(
        desc="Brief explanation of why this severity was assigned"
    )


class FixSuggestion(dspy.Signature):
    """Generate actionable fix suggestions for code issues."""

    issue = dspy.InputField(desc="The issue to fix")
    code_context = dspy.InputField(desc="Relevant code snippet")
    language = dspy.InputField(desc="Programming language")

    fix_description = dspy.OutputField(
        desc="Clear explanation of how to fix the issue"
    )
    code_example = dspy.OutputField(
        desc="Code snippet demonstrating the fix"
    )


class CodeReviewModule(dspy.Module):
    """
    Complete code review module using chain of thought reasoning.

    This module decomposes code review into three steps:
    1. Detect issues
    2. Classify severity
    3. Suggest fixes
    """

    def __init__(self):
        super().__init__()
        # Use ChainOfThought for complex reasoning tasks
        self.detect_issues = dspy.ChainOfThought(IssueDetection)
        self.classify_severity = dspy.Predict(SeverityClassification)
        self.suggest_fix = dspy.ChainOfThought(FixSuggestion)

    def forward(self, code: str, language: str):
        """
        Perform a complete code review.

        Args:
            code: Source code to review
            language: Programming language

        Returns:
            dspy.Prediction with detected issues, severities, and fixes
        """
        # Step 1: Detect all issues
        detection = self.detect_issues(code=code, language=language)

        # For this example, we'll return the detection results
        # In a full implementation, we'd process each issue through
        # severity classification and fix suggestion

        return dspy.Prediction(
            issues=detection.issues,
            reasoning=detection.rationale if hasattr(detection, 'rationale') else ""
        )


class OptimizedCodeReviewModule(dspy.Module):
    """
    Optimized version with separate paths for different issue types.

    This version uses different strategies for:
    - Security issues (most critical, detailed analysis)
    - Performance issues (require benchmarking context)
    - Code quality issues (best practices)
    """

    def __init__(self):
        super().__init__()

        # Security-focused detection
        self.detect_security = dspy.ChainOfThought(
            "code, language -> security_issues: List of security vulnerabilities with exploit scenarios"
        )

        # Performance analysis
        self.detect_performance = dspy.Predict(
            "code, language -> performance_issues: Performance bottlenecks and complexity issues"
        )

        # Code quality
        self.detect_quality = dspy.Predict(
            "code, language -> quality_issues: Code smells, maintainability issues, best practice violations"
        )

        # Fix generation with examples
        self.generate_fix = dspy.ChainOfThought(FixSuggestion)

    def forward(self, code: str, language: str):
        """Run multi-path analysis."""

        # Run all detections in parallel conceptually
        security = self.detect_security(code=code, language=language)
        performance = self.detect_performance(code=code, language=language)
        quality = self.detect_quality(code=code, language=language)

        # Combine results
        all_issues = {
            "security": security.security_issues,
            "performance": performance.performance_issues,
            "quality": quality.quality_issues
        }

        return dspy.Prediction(
            issues=all_issues,
            security_reasoning=security.rationale if hasattr(security, 'rationale') else ""
        )


class FewShotCodeReview(dspy.Module):
    """
    Code review with optimized few-shot examples.

    DSPy's BootstrapFewShot will automatically select the best examples.
    """

    def __init__(self):
        super().__init__()
        self.review = dspy.ChainOfThought(
            "code, language -> issues, severity_counts, overall_assessment"
        )

    def forward(self, code: str, language: str):
        result = self.review(code=code, language=language)
        return result


# Utility function to convert modules to skill prompts
def module_to_skill_prompt(module: dspy.Module, examples: List = None) -> str:
    """
    Convert a DSPy module to a Claude Skill markdown format.

    Args:
        module: The optimized DSPy module
        examples: Optional few-shot examples to include

    Returns:
        Markdown formatted skill prompt
    """
    # This is a simplified version - real implementation would
    # extract the optimized prompts from DSPy's compilation

    prompt = "# Optimized Code Review Skill\n\n"
    prompt += "## Instructions\n\n"

    # Extract instructions from module's components
    # In real DSPy, you'd access module.predictors and their prompts

    prompt += "## Examples\n\n"
    if examples:
        for ex in examples:
            prompt += f"### Example: {ex.get('title', 'Unnamed')}\n\n"
            prompt += f"```{ex.get('language', '')}\n{ex.get('code', '')}\n```\n\n"
            prompt += f"**Issues Found**: {ex.get('issues', '')}\n\n"

    return prompt
