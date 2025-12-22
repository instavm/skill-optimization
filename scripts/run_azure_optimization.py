#!/usr/bin/env python3
"""
Run REAL skill optimization using Azure OpenAI.

This uses actual API calls to optimize the code review skill.
Cost: Approximately $0.50-2.00 depending on model and iterations.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / "src"))

import dspy
from src.utils import read_code_file, save_json


# Azure OpenAI Configuration
AZURE_API_KEY = "api_key"
AZURE_API_BASE = "base_url"
AZURE_API_VERSION = "2024-10-21"
AZURE_DEPLOYMENT = "4o-new"


def setup_azure():
    """Configure DSPy with Azure OpenAI."""
    print("🔧 Configuring Azure OpenAI...")
    lm = dspy.LM(
        f'azure/{AZURE_DEPLOYMENT}',
        api_key=AZURE_API_KEY,
        api_base=AZURE_API_BASE,
        api_version=AZURE_API_VERSION
    )
    dspy.configure(lm=lm)
    print("✅ Azure OpenAI configured\n")
    return lm


def load_training_data(limit=None):
    """Load training examples."""
    with open("data/training_data.json") as f:
        data = json.load(f)

    examples = []
    for i, case in enumerate(data["training_cases"]):
        if limit and i >= limit:
            break

        code = read_code_file(case["file_path"])

        # Create DSPy example
        example = dspy.Example(
            code=code,
            language=case["language"],
            file_path=case["file_path"],
            expected_critical_count=case["severity_distribution"]["Critical"],
            expected_high_count=case["severity_distribution"]["High"]
        ).with_inputs("code", "language")

        examples.append(example)

    return examples


def main():
    print("=" * 70)
    print("REAL SKILL OPTIMIZATION WITH AZURE OPENAI")
    print("=" * 70)
    print()

    # Setup
    lm = setup_azure()

    # Load limited training data to keep costs low
    print("📚 Loading training data (limited to 2 examples for cost)...")
    trainset = load_training_data(limit=2)
    print(f"   Loaded {len(trainset)} training examples\n")

    # Define Code Review Signature
    print("🎯 Defining code review task...")

    class CodeReview(dspy.Signature):
        """Analyze code and identify security vulnerabilities, bugs, and quality issues."""

        code = dspy.InputField(desc="Source code to review")
        language = dspy.InputField(desc="Programming language")

        critical_issues = dspy.OutputField(
            desc="List of CRITICAL security issues (SQL injection, weak crypto, etc.)"
        )
        high_issues = dspy.OutputField(
            desc="List of HIGH priority issues (bugs, resource leaks, etc.)"
        )
        summary = dspy.OutputField(
            desc="Brief summary of code quality"
        )

    print("✅ Task defined\n")

    # Create baseline module
    print("📝 Creating baseline code review module...")
    baseline = dspy.Predict(CodeReview)
    print("✅ Baseline created\n")

    # Test baseline on first example
    print("=" * 70)
    print("TESTING BASELINE (Before Optimization)")
    print("=" * 70)
    print()

    test_example = trainset[0]
    print(f"Testing on: {test_example.file_path}")
    print()

    print("🔄 Calling Azure OpenAI...")
    baseline_response = baseline(
        code=test_example.code[:1000] + "...[truncated]",  # Limit to save tokens
        language=test_example.language
    )

    print("✅ Response received\n")
    print("Baseline Results:")
    print(f"  Critical Issues: {baseline_response.critical_issues}")
    print(f"  High Issues: {baseline_response.high_issues}")
    print(f"  Summary: {baseline_response.summary}")
    print()

    # Optimize with Chain of Thought
    print("=" * 70)
    print("OPTIMIZING WITH CHAIN OF THOUGHT")
    print("=" * 70)
    print()

    print("🚀 Creating Chain of Thought version...")
    print("   This uses reasoning before answering...")
    optimized = dspy.ChainOfThought(CodeReview)
    print("✅ Optimized module created\n")

    # Test optimized
    print("🔄 Calling Azure OpenAI with CoT...")
    optimized_response = optimized(
        code=test_example.code[:1000] + "...[truncated]",
        language=test_example.language
    )

    print("✅ Response received\n")
    print("Optimized Results (with reasoning):")
    if hasattr(optimized_response, 'rationale'):
        print(f"  Reasoning: {optimized_response.rationale[:200]}...")
    print(f"  Critical Issues: {optimized_response.critical_issues}")
    print(f"  High Issues: {optimized_response.high_issues}")
    print(f"  Summary: {optimized_response.summary}")
    print()

    # Compare
    print("=" * 70)
    print("COMPARISON")
    print("=" * 70)
    print()

    print("Expected:")
    print(f"  Critical Issues: {test_example.expected_critical_count}")
    print(f"  High Issues: {test_example.expected_high_count}")
    print()

    print("Baseline (Simple Predict):")
    print(f"  Output length: {len(str(baseline_response.critical_issues))} chars")
    print()

    print("Optimized (Chain of Thought):")
    print(f"  Output length: {len(str(optimized_response.critical_issues))} chars")
    print(f"  Has reasoning: {hasattr(optimized_response, 'rationale')}")
    print()

    # Save results
    print("💾 Saving results...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    results = {
        "timestamp": timestamp,
        "model": f"azure/{AZURE_DEPLOYMENT}",
        "test_file": test_example.file_path,
        "baseline": {
            "critical_issues": str(baseline_response.critical_issues),
            "high_issues": str(baseline_response.high_issues),
            "summary": str(baseline_response.summary)
        },
        "optimized": {
            "rationale": str(getattr(optimized_response, 'rationale', 'N/A')),
            "critical_issues": str(optimized_response.critical_issues),
            "high_issues": str(optimized_response.high_issues),
            "summary": str(optimized_response.summary)
        },
        "expected": {
            "critical_count": test_example.expected_critical_count,
            "high_count": test_example.expected_high_count
        }
    }

    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    save_json(results, f"results/real_optimization_{timestamp}.json")
    print(f"✅ Results saved to results/real_optimization_{timestamp}.json\n")

    print("=" * 70)
    print("KEY INSIGHTS")
    print("=" * 70)
    print()
    print("1. ✅ Azure OpenAI API is working successfully")
    print("2. ✅ DSPy Predict (baseline) works")
    print("3. ✅ DSPy Chain of Thought (optimized) works")
    print()
    print("Next Steps:")
    print("  • Review the JSON output file")
    print("  • Compare baseline vs optimized responses")
    print("  • Try BootstrapFewShot for automatic example selection")
    print("  • Scale up to all training examples")
    print()
    print("For full optimization with BootstrapFewShot:")
    print("  • Requires more API calls (~20-50)")
    print("  • Estimated cost: $1-3")
    print("  • Takes 5-10 minutes")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
