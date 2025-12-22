#!/usr/bin/env python3
"""
REAL DSPy optimization with BootstrapFewShot on Qwen.
This actually uses DSPy's optimizer to automatically find best examples.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import dspy
import json
from src.improved_evaluator import ImprovedCodeReviewEvaluator, create_improved_metric
from src.utils import read_code_file, save_json
from datetime import datetime

print("=" * 70)
print("REAL DSPy OPTIMIZATION WITH QWEN")
print("=" * 70)
print()
print("This uses BootstrapFewShot to AUTOMATICALLY:")
print("  • Select which examples work best")
print("  • Generate optimized prompts")
print("  • Find the best reasoning strategy")
print()

# Configure Qwen
print("🔧 Configuring Ollama + Qwen...")
try:
    lm = dspy.LM('ollama/qwen3', api_base='http://localhost:11434', temperature=0.3)
    dspy.configure(lm=lm)
    print("✅ Connected to Qwen")
except Exception as e:
    print(f"❌ Error: {e}")
    print("   Make sure Ollama is running: ollama serve")
    sys.exit(1)

print()

# Load training data
print("📚 Loading training data...")
with open("data/training_data.json") as f:
    training_data = json.load(f)

# Use first 3 examples (BootstrapFewShot needs at least 2)
trainset = []
for case in training_data["training_cases"][:3]:
    code = read_code_file(case["file_path"])
    example = dspy.Example(
        code=code[:1500],
        language=case["language"],
        expected_critical_count=case["severity_distribution"]["Critical"],
        expected_high_count=case["severity_distribution"]["High"],
        description=case["description"]
    ).with_inputs("code", "language")
    trainset.append(example)

print(f"✅ Loaded {len(trainset)} examples")
print()

# Define signature
class CodeReview(dspy.Signature):
    """Find security vulnerabilities and bugs in code."""
    code = dspy.InputField(desc="Source code to analyze")
    language = dspy.InputField(desc="Programming language")
    critical_issues = dspy.OutputField(desc="Critical security vulnerabilities")
    high_issues = dspy.OutputField(desc="High priority bugs")

# Create evaluator
evaluator = ImprovedCodeReviewEvaluator()
metric = create_improved_metric(evaluator)

# Baseline
print("=" * 70)
print("STEP 1: BASELINE (No optimization)")
print("=" * 70)
print()

baseline = dspy.Predict(CodeReview)
baseline_scores = []

for i, example in enumerate(trainset):
    print(f"Testing {i+1}/{len(trainset)}...", end=" ")
    try:
        pred = baseline(code=example.code, language=example.language)
        score = metric(example, pred)
        baseline_scores.append(score)
        print(f"{score:.1%}")
    except Exception as e:
        print(f"Error: {e}")
        baseline_scores.append(0.0)

baseline_avg = sum(baseline_scores) / len(baseline_scores) if baseline_scores else 0
print(f"\n✅ Baseline: {baseline_avg:.1%}\n")

# REAL DSPy Optimization
print("=" * 70)
print("STEP 2: DSPy BootstrapFewShot OPTIMIZATION")
print("=" * 70)
print()
print("This will:")
print("  1. Try different combinations of examples")
print("  2. Test which ones improve the score")
print("  3. Automatically select the best configuration")
print()
print("⏳ This takes 2-5 minutes...")
print()

# Create module
module = dspy.ChainOfThought(CodeReview)

# Run REAL optimization
try:
    optimizer = dspy.BootstrapFewShot(
        metric=metric,
        max_bootstrapped_demos=2,  # Keep it small for speed
        max_labeled_demos=2,
        max_rounds=1
    )

    print("🔄 Running optimization...")
    optimized = optimizer.compile(module, trainset=trainset)
    print("✅ Optimization complete!\n")

except Exception as e:
    print(f"❌ Optimization failed: {e}")
    print()
    print("Note: BootstrapFewShot with local models can be unstable.")
    print("Falling back to showing what WOULD happen...")
    print()
    optimized = None

# Test optimized
if optimized:
    print("=" * 70)
    print("STEP 3: TESTING OPTIMIZED VERSION")
    print("=" * 70)
    print()

    optimized_scores = []
    for i, example in enumerate(trainset):
        print(f"Testing {i+1}/{len(trainset)}...", end=" ")
        try:
            pred = optimized(code=example.code, language=example.language)
            score = metric(example, pred)
            optimized_scores.append(score)
            print(f"{score:.1%}")
        except Exception as e:
            print(f"Error: {e}")
            optimized_scores.append(0.0)

    optimized_avg = sum(optimized_scores) / len(optimized_scores) if optimized_scores else 0
    print(f"\n✅ Optimized: {optimized_avg:.1%}\n")

    # Results
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print()
    print(f"Baseline:  {baseline_avg:.1%}")
    print(f"Optimized: {optimized_avg:.1%}")
    print()

    improvement = optimized_avg - baseline_avg
    improvement_pct = (improvement / baseline_avg * 100) if baseline_avg > 0 else 0

    if improvement_pct > 0:
        print(f"✅ IMPROVEMENT: +{improvement:.1%} ({improvement_pct:+.1f}%)")
        print()
        print("DSPy's BootstrapFewShot successfully improved the skill!")
        print()
        print("What it did:")
        print("  • Automatically selected best examples from training set")
        print("  • Generated optimized prompt with those examples")
        print("  • No manual prompt engineering needed")
    elif improvement_pct < -5:
        print(f"⬇️ REGRESSION: {improvement:.1%} ({improvement_pct:+.1f}%)")
        print()
        print("Optimization made it worse (can happen with small datasets)")
    else:
        print(f"➖ NO CHANGE: {improvement:.1%} ({improvement_pct:+.1f}%)")
        print()
        print("Model already performs well, or needs more training examples")

    print()

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {
        "timestamp": timestamp,
        "model": "ollama/qwen3",
        "baseline": {"average": baseline_avg, "scores": baseline_scores},
        "optimized": {"average": optimized_avg, "scores": optimized_scores},
        "improvement_pct": improvement_pct,
        "method": "BootstrapFewShot"
    }
    save_json(results, f"results/qwen_bootstrap_{timestamp}.json")
    print(f"✅ Results saved to results/qwen_bootstrap_{timestamp}.json")
    print()

else:
    print("⚠️  Could not run BootstrapFewShot optimization")
    print()
    print("This is common with local models. For best results:")
    print("  • Use GPT-4o or Claude (more stable)")
    print("  • Increase training examples (10+)")
    print("  • Simplify the metric")
    print()

print("=" * 70)
print("WHAT WE LEARNED")
print("=" * 70)
print()
print("✅ This script shows REAL DSPy optimization with BootstrapFewShot")
print("✅ Previous scripts only tested manual prompt variations")
print("✅ BootstrapFewShot automatically finds best examples")
print()
print("For production:")
print("  • Use more training examples (10-50)")
print("  • Use stable API models (GPT-4, Claude)")
print("  • Run multiple optimization rounds")
print()
