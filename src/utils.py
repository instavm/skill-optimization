"""
Utility functions for skill optimization.
"""

import json
from pathlib import Path
from typing import Dict, Any, List


def load_json(file_path: str) -> Dict[str, Any]:
    """
    Load JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON data
    """
    with open(file_path, 'r') as f:
        return json.load(f)


def save_json(data: Dict[str, Any], file_path: str, indent: int = 2):
    """
    Save data to JSON file.

    Args:
        data: Data to save
        file_path: Output path
        indent: JSON indentation
    """
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=indent)


def read_code_file(file_path: str) -> str:
    """
    Read a code file.

    Args:
        file_path: Path to code file

    Returns:
        File contents as string
    """
    with open(file_path, 'r') as f:
        return f.read()


def format_evaluation_results(results: Dict[str, Any]) -> str:
    """
    Format evaluation results as a readable string.

    Args:
        results: Evaluation results dictionary

    Returns:
        Formatted string
    """
    output = []
    output.append("=" * 60)
    output.append("EVALUATION RESULTS")
    output.append("=" * 60)
    output.append("")

    if "average_precision" in results:
        output.append(f"Average Precision:       {results['average_precision']:.2%}")
        output.append(f"Average Recall:          {results['average_recall']:.2%}")
        output.append(f"Average F1 Score:        {results['average_f1']:.2%}")
        output.append(f"Average Critical Recall: {results['average_critical_recall']:.2%}")
        output.append(f"Average Overall Score:   {results['average_overall']:.2%}")
        output.append("")

    if "individual_results" in results:
        output.append("Individual Test Results:")
        output.append("-" * 60)
        for result in results["individual_results"]:
            output.append(f"\nTest: {result['test_id']}")
            output.append(f"  Precision: {result['precision']:.2%}")
            output.append(f"  Recall:    {result['recall']:.2%}")
            output.append(f"  F1 Score:  {result['f1_score']:.2%}")
            output.append(f"  Critical Recall: {result['critical_recall']:.2%}")
            output.append(f"  Overall:   {result['overall_score']:.2%}")

    output.append("")
    output.append("=" * 60)

    return "\n".join(output)


def create_comparison_report(
    baseline_results: Dict[str, Any],
    optimized_results: Dict[str, Any],
    output_path: str
):
    """
    Create a markdown comparison report.

    Args:
        baseline_results: Baseline evaluation results
        optimized_results: Optimized evaluation results
        output_path: Where to save the report
    """
    report = []

    report.append("# Skill Optimization Results\n")
    report.append(f"Generated: {Path(output_path).stem}\n")

    report.append("## Summary\n")
    report.append("| Metric | Baseline | Optimized | Improvement |\n")
    report.append("|--------|----------|-----------|-------------|\n")

    metrics = [
        ("Precision", "average_precision"),
        ("Recall", "average_recall"),
        ("F1 Score", "average_f1"),
        ("Critical Recall", "average_critical_recall"),
        ("Overall Score", "average_overall")
    ]

    for metric_name, metric_key in metrics:
        baseline_val = baseline_results.get(metric_key, 0)
        optimized_val = optimized_results.get(metric_key, 0)
        improvement = optimized_val - baseline_val

        report.append(
            f"| {metric_name} | {baseline_val:.2%} | {optimized_val:.2%} | "
            f"{'+' if improvement >= 0 else ''}{improvement:.2%} |\n"
        )

    report.append("\n## Key Improvements\n")

    # Highlight significant improvements
    for metric_name, metric_key in metrics:
        baseline_val = baseline_results.get(metric_key, 0)
        optimized_val = optimized_results.get(metric_key, 0)
        improvement = optimized_val - baseline_val

        if improvement >= 0.10:  # 10% improvement
            report.append(f"- **{metric_name}** improved by {improvement:.1%}\n")

    report.append("\n## Detailed Results\n")
    report.append("### Baseline\n")
    report.append("```\n")
    report.append(format_evaluation_results(baseline_results))
    report.append("```\n\n")

    report.append("### Optimized\n")
    report.append("```\n")
    report.append(format_evaluation_results(optimized_results))
    report.append("```\n")

    # Save report
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text("".join(report))


def extract_issues_from_llm_output(output: str) -> List[Dict[str, Any]]:
    """
    Parse LLM output to extract structured issues.

    This is a helper for when DSPy returns unstructured text.

    Args:
        output: LLM output string

    Returns:
        List of issue dictionaries
    """
    import re

    issues = []

    # Look for patterns like "Issue #1:", "**Issue 1**:", etc.
    issue_pattern = r'(?:Issue|Problem)\s*#?(\d+)[:\s]*([^\n]+)'

    matches = re.finditer(issue_pattern, output, re.IGNORECASE | re.MULTILINE)

    for match in matches:
        issue_num = match.group(1)
        issue_title = match.group(2).strip()

        # Try to find severity
        severity = "Medium"  # Default
        severity_match = re.search(
            r'Severity[:\s]*(Critical|High|Medium|Low)',
            output[match.end():match.end()+200],
            re.IGNORECASE
        )
        if severity_match:
            severity = severity_match.group(1).capitalize()

        issues.append({
            "title": issue_title,
            "severity": severity,
            "description": ""  # Would need more sophisticated parsing
        })

    return issues


def print_progress_bar(iteration: int, total: int, prefix: str = '', suffix: str = '', length: int = 50):
    """
    Print a progress bar.

    Args:
        iteration: Current iteration
        total: Total iterations
        prefix: Prefix string
        suffix: Suffix string
        length: Character length of bar
    """
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='')

    if iteration == total:
        print()
