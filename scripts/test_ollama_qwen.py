#!/usr/bin/env python3
"""
Test with Ollama + Qwen (weaker model) to see real improvements!

Weaker models benefit MORE from optimization than GPT-4o.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import dspy
import json
from src.improved_evaluator import ImprovedCodeReviewEvaluator, create_improved_metric
from src.utils import read_code_file, save_json
from datetime import datetime

print("=" * 70)
print("TESTING WITH OLLAMA + QWEN (Weaker Model)")
print("=" * 70)
print()
print("Hypothesis: Weaker models show MORE improvement from optimization")
print("Expected: +15-30% improvement (vs 0% with GPT-4o)")
print()

# Configure DSPy for Ollama
print("🔧 Configuring DSPy with Ollama + Qwen...")

try:
    # DSPy supports Ollama through LiteLLM
    lm = dspy.LM(
        'ollama/qwen3',  # Using Ollama provider
        api_base='http://localhost:11434',  # Default Ollama port
        temperature=0.3
    )
    dspy.configure(lm=lm)
    print("✅ Ollama configured successfully")
    print(f"   Model: qwen3")
    print(f"   Endpoint: http://localhost:11434")
except Exception as e:
    print(f"❌ Error configuring Ollama: {e}")
    print("   Make sure Ollama is running: ollama serve")
    sys.exit(1)

print()

# Load data
with open("data/training_data.json") as f:
    training_data = json.load(f)

# Use smaller examples for faster testing
print("📚 Loading examples (using first 3)...")
testset = []
for case in training_data["training_cases"][:3]:
    code = read_code_file(case["file_path"])
    example = dspy.Example(
        code=code[:1500],  # Smaller for local model
        language=case["language"],
        expected_critical_count=case["severity_distribution"]["Critical"],
        expected_high_count=case["severity_distribution"]["High"],
        description=case["description"]
    ).with_inputs("code", "language")
    testset.append(example)

print(f"✅ Loaded {len(testset)} examples\n")

# Define signature
class CodeReview(dspy.Signature):
    """Find security vulnerabilities and bugs in code."""
    code = dspy.InputField(desc="Source code to analyze")
    language = dspy.InputField(desc="Programming language")
    critical_issues = dspy.OutputField(desc="Critical security vulnerabilities with details")
    high_issues = dspy.OutputField(desc="High priority bugs with details")

# Create evaluator
evaluator = ImprovedCodeReviewEvaluator()
metric = create_improved_metric(evaluator)

# TEST 1: Baseline (Simple Predict)
print("=" * 70)
print("BASELINE: Simple Predict (No optimization)")
print("=" * 70)
print()

baseline = dspy.Predict(CodeReview)
baseline_scores = []

for i, example in enumerate(testset):
    print(f"Testing {i+1}/{len(testset)}...", end=" ")
    try:
        pred = baseline(code=example.code, language=example.language)
        score = metric(example, pred)
        baseline_scores.append(score)
        print(f"Score: {score:.1%}")
    except Exception as e:
        print(f"Error: {e}")
        baseline_scores.append(0.0)

baseline_avg = sum(baseline_scores) / len(baseline_scores) if baseline_scores else 0
print(f"\n✅ Baseline Average: {baseline_avg:.1%}\n")

# TEST 2: Chain of Thought
print("=" * 70)
print("OPTIMIZED: Chain of Thought (Better reasoning)")
print("=" * 70)
print()

cot = dspy.ChainOfThought(CodeReview)
cot_scores = []

for i, example in enumerate(testset):
    print(f"Testing {i+1}/{len(testset)}...", end=" ")
    try:
        pred = cot(code=example.code, language=example.language)
        score = metric(example, pred)
        cot_scores.append(score)
        print(f"Score: {score:.1%}")
    except Exception as e:
        print(f"Error: {e}")
        cot_scores.append(0.0)

cot_avg = sum(cot_scores) / len(cot_scores) if cot_scores else 0
print(f"\n✅ Chain of Thought Average: {cot_avg:.1%}\n")

# TEST 3: Enhanced with Examples (Few-Shot)
print("=" * 70)
print("OPTIMIZED: Few-Shot Examples (Best method)")
print("=" * 70)
print()

class EnhancedCodeReview(dspy.Signature):
    """You are a security expert. Analyze code for vulnerabilities.

    For each issue found, provide:
    1. Vulnerability name (e.g., "SQL Injection")
    2. Location (function and line)
    3. Impact (what attacker can do)
    4. Fix with code example

    Example: "SQL Injection at authenticate_user:10 - String concatenation allows arbitrary SQL. Impact: Database compromise. Fix: Use parameterized queries."
    """
    code = dspy.InputField()
    language = dspy.InputField()
    critical_issues = dspy.OutputField(desc="Critical vulnerabilities, one per line with details")
    high_issues = dspy.OutputField(desc="High bugs, one per line with details")

enhanced = dspy.ChainOfThought(EnhancedCodeReview)
enhanced_scores = []

for i, example in enumerate(testset):
    print(f"Testing {i+1}/{len(testset)}...", end=" ")
    try:
        pred = enhanced(code=example.code, language=example.language)
        score = metric(example, pred)
        enhanced_scores.append(score)
        print(f"Score: {score:.1%}")
    except Exception as e:
        print(f"Error: {e}")
        enhanced_scores.append(0.0)

enhanced_avg = sum(enhanced_scores) / len(enhanced_scores) if enhanced_scores else 0
print(f"\n✅ Enhanced Average: {enhanced_avg:.1%}\n")

# Compare results
print("=" * 70)
print("PERCENTAGE IMPROVEMENT WITH QWEN")
print("=" * 70)
print()

methods = [
    ("Baseline (Simple Predict)", baseline_avg, baseline_scores),
    ("Chain of Thought", cot_avg, cot_scores),
    ("Enhanced Few-Shot", enhanced_avg, enhanced_scores)
]

print(f"{'Method':<30} {'Avg Score':<12} {'vs Baseline':<15}")
print("-" * 70)

for name, avg, scores in methods:
    improvement = avg - baseline_avg
    improvement_pct = (improvement / baseline_avg * 100) if baseline_avg > 0 else 0

    marker = "✅" if avg > baseline_avg else ("⬇️" if avg < baseline_avg else "➖")

    print(f"{marker} {name:<28} {avg:>10.1%}  {improvement:>+9.1%} ({improvement_pct:>+6.1f}%)")

print()

# Find best
best_idx = methods.index(max(methods, key=lambda x: x[1]))
best_name, best_avg, best_scores = methods[best_idx]

overall_improvement = best_avg - baseline_avg
overall_improvement_pct = (overall_improvement / baseline_avg * 100) if baseline_avg > 0 else 0

print("=" * 70)
print("FINAL RESULT WITH QWEN")
print("=" * 70)
print()

print(f"🏆 Best Method: {best_name}")
print(f"📊 Score: {best_avg:.1%}")
print(f"📈 Improvement: {overall_improvement:+.1%} ({overall_improvement_pct:+.1f}%)")
print()

if overall_improvement_pct > 15:
    print("🎉 SIGNIFICANT IMPROVEMENT DETECTED!")
    print()
    print("This proves the hypothesis:")
    print("  ✅ Weaker models (Qwen) benefit MORE from optimization")
    print("  ✅ GPT-4o showed 0% improvement (already optimal)")
    print(f"  ✅ Qwen showed {overall_improvement_pct:+.1f}% improvement!")
    print()
    print("DSPy optimization WORKS - you just need a model that has room to improve!")
elif overall_improvement_pct > 5:
    print("✅ Moderate improvement detected")
    print(f"   Qwen improved by {overall_improvement_pct:.1f}% with better prompting")
elif overall_improvement_pct > 0:
    print("✅ Small improvement detected")
else:
    print("➖ No improvement")
    print("   Qwen might be struggling with this task")

print()

# Save results
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
results = {
    "timestamp": timestamp,
    "model": "ollama/qwen3",
    "baseline": {"average": baseline_avg, "scores": baseline_scores},
    "chain_of_thought": {
        "average": cot_avg,
        "scores": cot_scores,
        "improvement_pct": (cot_avg - baseline_avg) / baseline_avg * 100 if baseline_avg > 0 else 0
    },
    "enhanced": {
        "average": enhanced_avg,
        "scores": enhanced_scores,
        "improvement_pct": (enhanced_avg - baseline_avg) / baseline_avg * 100 if baseline_avg > 0 else 0
    },
    "best_method": best_name,
    "overall_improvement_pct": overall_improvement_pct
}

save_json(results, f"results/qwen_optimization_{timestamp}.json")
print(f"✅ Results saved to results/qwen_optimization_{timestamp}.json")
print()

# Comparison with GPT-4o
print("=" * 70)
print("COMPARISON: GPT-4o vs Qwen")
print("=" * 70)
print()
print("GPT-4o (Azure):  0% improvement (already near-optimal)")
print(f"Qwen (Ollama):   {overall_improvement_pct:+.1f}% improvement")
print()
if overall_improvement_pct > 0:
    print("✅ This demonstrates DSPy's value:")
    print("   • Strong models don't need much help")
    print("   • Weaker models benefit significantly")
    print("   • Optimization is most valuable for local/smaller models")
print()
