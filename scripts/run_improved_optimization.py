#!/usr/bin/env python3
"""
Run optimization with IMPROVED evaluation metric.

This metric measures:
- Issue detection (did it find the bugs?)
- Explanation quality (are issues well-described?)
- Fix quality (are fixes actionable with code examples?)
- Severity accuracy (right severity levels?)

This should show REAL improvements!
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import dspy
import json
from datetime import datetime
from src.improved_evaluator import ImprovedCodeReviewEvaluator, create_improved_metric
from src.utils import read_code_file, save_json

# Azure OpenAI Configuration
AZURE_API_KEY = "api_key"
AZURE_API_BASE = "base_url"
AZURE_API_VERSION = "2024-10-21"
AZURE_DEPLOYMENT = "4o-new"


def setup_azure():
    lm = dspy.LM(
        f'azure/{AZURE_DEPLOYMENT}',
        api_key=AZURE_API_KEY,
        api_base=AZURE_API_BASE,
        api_version=AZURE_API_VERSION
    )
    dspy.configure(lm=lm)
    return lm


def main():
    print("=" * 70)
    print("OPTIMIZATION WITH IMPROVED EVALUATION METRIC")
    print("=" * 70)
    print()
    print("This metric measures:")
    print("  ✅ Issue detection (finding the bugs)")
    print("  ✅ Explanation quality (clear descriptions)")
    print("  ✅ Fix quality (actionable solutions with code)")
    print("  ✅ Severity accuracy (right severity levels)")
    print()

    # Setup
    setup_azure()

    # Load training data
    with open("data/training_data.json") as f:
        training_data = json.load(f)

    # Create DSPy examples (limit to 5 to save cost/time)
    print("📚 Loading training examples (using 5 for faster results)...")
    trainset = []
    for i, case in enumerate(training_data["training_cases"][:5]):
        code = read_code_file(case["file_path"])

        example = dspy.Example(
            code=code[:2000],
            language=case["language"],
            expected_critical_count=case["severity_distribution"]["Critical"],
            expected_high_count=case["severity_distribution"]["High"],
            description=case["description"]
        ).with_inputs("code", "language")

        trainset.append(example)

    print(f"✅ Loaded {len(trainset)} examples\n")

    # Define signature
    class CodeReview(dspy.Signature):
        """Analyze code to find security vulnerabilities and bugs."""
        code = dspy.InputField(desc="Source code to review")
        language = dspy.InputField(desc="Programming language")
        critical_issues = dspy.OutputField(
            desc="CRITICAL security vulnerabilities. For each issue provide: "
                "1) Specific vulnerability name, "
                "2) Location in code, "
                "3) Impact/exploit scenario, "
                "4) Fix with code example. "
                "One issue per line."
        )
        high_issues = dspy.OutputField(
            desc="HIGH priority bugs and issues. For each provide: "
                "1) Bug description, "
                "2) Location, "
                "3) Impact, "
                "4) How to fix. "
                "One issue per line."
        )

    # Create evaluator with improved metric
    evaluator = ImprovedCodeReviewEvaluator()
    metric = create_improved_metric(evaluator)

    # Test 1: Simple Predict (baseline)
    print("=" * 70)
    print("BASELINE: Simple Predict")
    print("=" * 70)
    print()

    simple = dspy.Predict(CodeReview)
    simple_scores = []

    for i, example in enumerate(trainset):
        print(f"Testing {i+1}/{len(trainset)}...")
        pred = simple(code=example.code, language=example.language)
        score = metric(example, pred)
        simple_scores.append(score)
        print(f"  Score: {score:.1%}\n")

    simple_avg = sum(simple_scores) / len(simple_scores)
    print(f"✅ Simple Predict Average: {simple_avg:.1%}\n")

    # Test 2: Chain of Thought
    print("=" * 70)
    print("METHOD 1: Chain of Thought (Reasoning)")
    print("=" * 70)
    print()

    cot = dspy.ChainOfThought(CodeReview)
    cot_scores = []

    for i, example in enumerate(trainset):
        print(f"Testing {i+1}/{len(trainset)}...")
        pred = cot(code=example.code, language=example.language)
        score = metric(example, pred)
        cot_scores.append(score)
        print(f"  Score: {score:.1%}\n")

    cot_avg = sum(cot_scores) / len(cot_scores)
    print(f"✅ Chain of Thought Average: {cot_avg:.1%}\n")

    # Test 3: Enhanced Signature
    print("=" * 70)
    print("METHOD 2: Enhanced Signature (Better Instructions)")
    print("=" * 70)
    print()

    class EnhancedCodeReview(dspy.Signature):
        """You are a security expert. Find ALL vulnerabilities with specific details.

        IMPORTANT: For each issue you MUST provide:
        - Exact vulnerability name (e.g., "SQL Injection", not just "security issue")
        - Precise location (function name and line number)
        - Realistic exploit scenario
        - Specific fix with actual code example
        """
        code = dspy.InputField()
        language = dspy.InputField()
        critical_issues = dspy.OutputField(
            desc="List EVERY critical security vulnerability. "
                "Format each as: "
                "'VULNERABILITY_NAME at LOCATION: DESCRIPTION. Impact: IMPACT. Fix: USE_SPECIFIC_FUNCTION() example: `code`'"
        )
        high_issues = dspy.OutputField(
            desc="List EVERY high-priority bug. "
                "Format: 'BUG_NAME at LOCATION: DESCRIPTION. Fix with example code.'"
        )

    enhanced = dspy.ChainOfThought(EnhancedCodeReview)
    enhanced_scores = []

    for i, example in enumerate(trainset):
        print(f"Testing {i+1}/{len(trainset)}...")
        pred = enhanced(code=example.code, language=example.language)
        score = metric(example, pred)
        enhanced_scores.append(score)
        print(f"  Score: {score:.1%}\n")

    enhanced_avg = sum(enhanced_scores) / len(enhanced_scores)
    print(f"✅ Enhanced Signature Average: {enhanced_avg:.1%}\n")

    # Compare results
    print("=" * 70)
    print("REAL PERCENTAGE IMPROVEMENTS")
    print("=" * 70)
    print()

    methods = [
        ("Simple Predict (Baseline)", simple_avg, simple_scores),
        ("Chain of Thought", cot_avg, cot_scores),
        ("Enhanced Signature", enhanced_avg, enhanced_scores)
    ]

    print(f"{'Method':<30} {'Avg Score':<12} {'vs Baseline':<15}")
    print("-" * 70)

    baseline = simple_avg

    for name, avg, scores in methods:
        improvement = avg - baseline
        improvement_pct = (improvement / baseline * 100) if baseline > 0 else 0

        marker = ""
        if avg > baseline:
            marker = "✅"
        elif avg < baseline:
            marker = "⬇️"
        else:
            marker = "➖"

        print(f"{marker} {name:<28} {avg:>10.1%}  {improvement:>+9.1%} ({improvement_pct:>+6.1f}%)")

    print()

    # Find best method
    best_idx = methods.index(max(methods, key=lambda x: x[1]))
    best_name, best_avg, best_scores = methods[best_idx]

    overall_improvement = best_avg - baseline
    overall_improvement_pct = (overall_improvement / baseline * 100) if baseline > 0 else 0

    print("=" * 70)
    print("FINAL RESULT")
    print("=" * 70)
    print()
    print(f"🏆 Best Method: {best_name}")
    print(f"📊 Score: {best_avg:.1%}")
    print(f"📈 Improvement over baseline: {overall_improvement:+.1%} ({overall_improvement_pct:+.1f}%)")
    print()

    if overall_improvement > 0.05:
        print("✅ SIGNIFICANT IMPROVEMENT DETECTED!")
        print()
        print("The optimized method produces:")
        print("  • Better issue explanations")
        print("  • More specific location information")
        print("  • Actionable fixes with code examples")
        print("  • More accurate severity classification")
    elif overall_improvement > 0:
        print("✅ Modest improvement detected")
    else:
        print("➖ No improvement with current approaches")
        print("   Try: More training examples or different optimization strategy")

    print()

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {
        "timestamp": timestamp,
        "model": f"azure/{AZURE_DEPLOYMENT}",
        "baseline": {
            "method": "Simple Predict",
            "average": simple_avg,
            "scores": simple_scores
        },
        "chain_of_thought": {
            "method": "Chain of Thought",
            "average": cot_avg,
            "scores": cot_scores,
            "improvement": cot_avg - baseline,
            "improvement_pct": (cot_avg - baseline) / baseline * 100 if baseline > 0 else 0
        },
        "enhanced": {
            "method": "Enhanced Signature",
            "average": enhanced_avg,
            "scores": enhanced_scores,
            "improvement": enhanced_avg - baseline,
            "improvement_pct": (enhanced_avg - baseline) / baseline * 100 if baseline > 0 else 0
        },
        "best_method": best_name,
        "best_score": best_avg,
        "overall_improvement": overall_improvement,
        "overall_improvement_pct": overall_improvement_pct
    }

    save_json(results, f"results/improved_optimization_{timestamp}.json")
    print(f"✅ Detailed results saved to results/improved_optimization_{timestamp}.json")
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
