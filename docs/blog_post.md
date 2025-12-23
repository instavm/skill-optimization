# Anthropic Skills Can Be Programmatically Optimized (Using DSPy)

## Context

OpenAI [added Skills to Codex](https://developers.openai.com/codex/skills/) this week. Anthropic released the [Agent Skills spec](https://agentskills.io/) a few days ago.

The format: reusable prompt files (`SKILL.md`) that agents can invoke:
```
code-review.md      # Find security vulnerabilities
sql-optimization.md # Optimize queries
api-design.md       # Review endpoints
```

These are 100-200 line markdown files with instructions, examples, and output formats.

**Here's what I noticed:** Skills are structured prompts. DSPy is a framework for optimizing prompts. Nobody's connected these two ecosystems yet.

**The insight:** If Skills are just structured prompts, they should be programmatically optimizable. You could benchmark them, version them, auto-generate model-specific variants.

I tested this hypothesis with a **code security** review skill.

---

## Method

[DSPy](https://github.com/stanfordnlp/dspy) is a prompt optimization framework from Stanford. Instead of manually tweaking prompts, you:

1. Define task as a signature (inputs/outputs)
2. Provide training examples
3. Run optimizer
4. Get improved prompt with auto-selected few-shot examples

The optimizer tests different instruction phrasings, example combinations, and reasoning strategies, then picks the best performing variant.

### The Pipeline

To test if Skills can be optimized with DSPy:

```
1. Parse SKILL.md → DSPy Signature
2. Create training data (vulnerable code + expected issues)
3. Run DSPy optimization
4. Extract improvements → SKILL-optimized.md
```

**What this proves:** If DSPy can improve a Skill's output quality, then Skills aren't just static markdown files - they're improvable programs.

I tested with a code security review skill that finds SQL injection, weak crypto, etc.

---

## Setup

**Input:** `code-review.md` - 80-line skill that finds security vulnerabilities

**Training data:** 10 vulnerable code samples:
- SQL injection (Python, JavaScript)
- Weak crypto (MD5, hardcoded secrets)
- Command injection
- XSS, path traversal, IDOR, etc.

**DSPy Signature:**
```python
class CodeReview(dspy.Signature):
    """Find security vulnerabilities and bugs in code."""
    code = dspy.InputField()
    language = dspy.InputField()
    critical_issues = dspy.OutputField()
    high_issues = dspy.OutputField()
```

**Optimization:**
```python
optimizer = dspy.BootstrapFewShot(metric=quality_metric)
optimized = optimizer.compile(baseline, trainset=examples)
```

**Models tested:** GPT-4o (Azure), Qwen3 (Ollama)

[Code/data](https://github.com/instavm/skill-optimization)

---

## Results

**Bottom line: Yes, Skills can be programmatically optimized.**

I tested on two very different models to prove the concept works broadly:
- GPT-4o (frontier model, Azure)
- Qwen3 (local model, Ollama)

The results show something interesting about Skills themselves.

### GPT-4o (Azure)

**Baseline:** 40.6% quality score
```python
baseline = dspy.Predict(CodeReview)
```

**Optimized variants:**
```python
# Chain of Thought
cot = dspy.ChainOfThought(CodeReview)
# 39.2%

# Enhanced signature
enhanced = dspy.ChainOfThought(EnhancedCodeReview)
# 38.8%

# BootstrapFewShot
optimized = optimizer.compile(module, trainset=10_examples)
# ~40% ❌
```

**Result:** 0% improvement. Some variants performed worse.

**What this tells us:** The baseline `code-review.md` Skill is already well-designed for frontier models. DSPy's optimization confirms the Skill is solid - it can't find ways to improve it further for GPT-4o.

---

### Qwen3 (Ollama, local)

Tested with REAL DSPy BootstrapFewShot optimization on 3 code examples:

```
BASELINE: No optimization
Testing 1/3... Score: 61.6%
Testing 2/3... Score: 56.0%
Testing 3/3... Score: 10.0%
- Baseline Average: 42.5%

OPTIMIZED: BootstrapFewShot (automated)
  • DSPy automatically selected best examples
  • Generated optimized prompt with demonstrations
  • No manual prompt engineering
Testing 1/3... Score: 77.0%
Testing 2/3... Score: 65.7%
Testing 3/3... Score: 22.5%
- Optimized Average: 55.1%
```

**Result:** BootstrapFewShot showed **+12.5% improvement** (42.5% → 55.1%)
- Absolute improvement: +12.5 percentage points
- Relative improvement: +29.4%

**What this tells us:** DSPy's automated optimization works significantly better than manual prompt variations. The optimizer automatically selected which training examples work best and compiled an optimized module - exactly what DSPy is designed to do.

---

## Discussion

### What This Enables for Skills

**1. Skills can be benchmarked objectively**

Right now, Skills are shared as markdown files with no quality metrics. With DSPy optimization:
```
my-skill/
├── SKILL.md          # Baseline
├── TRAINING.json     # Test cases
├── METRICS.json      # Quality scores
└── OPTIMIZED.md      # Auto-generated variants
```

You could compare Skills objectively: "code-review-v2.md scores 15% better on SQL injection detection"

**2. Skills can be auto-adapted per model**

Instead of one-size-fits-all:
- `code-review-gpt4.md` - Minimal (frontier models work well baseline)
- `code-review-qwen.md` - Heavy few-shot (local models need examples)
- Auto-generated based on model capabilities

**3. Skills become versionable and improvable**

Like code dependencies:
```json
{
  "skill": "code-review",
  "version": "2.1.0",
  "optimized_for": ["gpt-4o", "qwen3", "llama-3"],
  "quality_score": 0.82
}
```

Skills could evolve over time with community contributions to training data.

**4. Skills can self-optimize as models improve**

When GPT-5 releases, re-run optimization on existing Skills. No manual rewrites needed.

---

## Try It Yourself (5-Minute Setup)

All code is available at [github.com/instavm/skill-optimization](https://github.com/instavm/skill-optimization).

### Quick Start (Local, No API Keys)

```bash
# Install Ollama: https://ollama.ai
ollama pull qwen3

# Install dependencies
pip install -r requirements.txt

# Run REAL DSPy BootstrapFewShot optimization
python scripts/optimize_qwen.py
```

You'll see the before/after quality comparison in ~5 minutes.

### With Your Own OpenAI/Azure Key

```bash
# Set environment variables
export AZURE_API_KEY="your-key"
export AZURE_API_BASE="your-endpoint"
export AZURE_DEPLOYMENT="your-deployment"

# Run optimization
python scripts/run_azure_optimization.py
```

### What You'll See

**Qwen output (before optimization):**
```
1. SQL Injection Vulnerabilities: Functions concatenate user inputs
2. Insecure Password Hashing: Uses MD5
```

**Qwen output (after optimization):**
```
SQL Injection - User input concatenated allows arbitrary SQL execution.
Attackers can inject malicious SQL to bypass authentication or extract data.
Fix: Use parameterized queries: cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

The difference is in the **specificity** and **actionability**.

---

## How to Optimize Your Own Skill.md

Want to optimize your own Skill? Here's the actual workflow:

### Step 1: Understand Your Skill's Structure

Look at your `my-skill.md` and identify:
- **Inputs**: What data does the skill receive? (e.g., code, user query, document)
- **Outputs**: What should it produce? (e.g., bug report, summary, recommendations)
- **Task**: What's the core transformation? (e.g., "find security bugs", "extract key points")

Example - for a code review skill:
```
Input: code snippet + language
Output: critical_issues, high_issues, medium_issues
Task: "Find security vulnerabilities in code"
```

### Step 2: Create Training Examples (Manual)

You need to manually create 5-10 examples with expected outputs. This is the hardest part.

For code review, I created `data/training_data.json`:
```json
{
  "file_path": "examples/sql_injection.py",
  "expected_issues": [
    {
      "title": "SQL Injection",
      "severity": "Critical",
      "description": "User input concatenated into SQL query",
      "locations": ["authenticate_user:10"],
      "fix": "Use parameterized queries"
    }
  ]
}
```

**You manually write these or use LLM but do verify them manually** - DSPy doesn't auto-generate training data (yet).

### Step 3: Define DSPy Signature

Convert your Skill to DSPy code:

```python
import dspy

class MySkill(dspy.Signature):
    """Your skill's task description."""
    input_field = dspy.InputField(desc="What goes in")
    output_field = dspy.OutputField(desc="What comes out")

# Create baseline module
baseline = dspy.Predict(MySkill)
```

### Step 4: Create Evaluation Metric

Write a function that scores output quality (0-100%):

```python
def quality_metric(example, prediction, trace=None):
    score = 0
    # Check if output has required elements
    if "key_term" in prediction.output_field:
        score += 25
    if len(prediction.output_field) > 100:
        score += 25
    # ... more checks
    return score / 100  # Return 0.0-1.0
```

### Step 5: Run BootstrapFewShot

```python
from dspy.teleprompt import BootstrapFewShot

# Load your training examples
trainset = [dspy.Example(**ex).with_inputs('input_field')
            for ex in training_data]

# Run optimization
optimizer = BootstrapFewShot(
    metric=quality_metric,
    max_bootstrapped_demos=3,
    max_labeled_demos=3
)

optimized = optimizer.compile(baseline, trainset=trainset)
```

This takes 5-10 minutes and automatically selects which examples improve performance.

### Step 6: Extract Results Back to Skill.md

DSPy gives you an optimized module with:
- Better instruction phrasing
- Auto-selected few-shot examples
- Improved reasoning strategies

**You manually create a new `my-skill-optimized.md`** by:
1. Looking at what examples DSPy selected
2. Adding those examples to your Skill.md
3. Updating instructions based on what worked

**OR keep using the DSPy module directly** in your code (no need for .md file).

### What You DON'T Do

- DSPy doesn't parse your Skill.md automatically
- DSPy doesn't generate training examples for you
- DSPy doesn't output a new Skill.md file

- You manually convert Skill → DSPy Signature
- You manually create training examples
- DSPy automatically finds which examples work best
- You manually update your Skill.md with the results (or use DSPy module directly)

**The automation is in finding WHICH examples to use, not creating them.**

---

## What I Learned

### 1. Skills are programs, not just documentation
They can be optimized, benchmarked, versioned, and improved systematically. They're not static markdown files.

### 2. Skills can be model-agnostic
Write once, auto-optimize per model. The same Skill works on GPT-4o (baseline) and Qwen (optimized variant).

### 3. DSPy validates Skill quality
When DSPy can't improve a Skill (like GPT-4o at 0%), that's validation the Skill is well-designed. Optimization isn't just about improvement - it's about measurement.

### 4. Skills need infrastructure
To make this practical, we need:
- Standardized training data formats
- Quality benchmarks
- Auto-optimization tooling
- Model-specific variant generation

---

## Open Questions

1. **Should Skills ship with training data?**
   Like: `SKILL.md` + `TRAINING.json` + benchmarks. This would enable community optimization.

2. **Can we standardize Skill quality metrics?**
   My metrics are custom. We need standard benchmarks for comparing Skills objectively.

3. **Do optimizations transfer across model families?**
   If I optimize for Qwen, does it work for Llama? Mistral? This would reduce optimization overhead.

4. **Can we auto-generate training data?**
   I hand-wrote 10 vulnerable code examples. Could GPT-4 generate these systematically?

5. **What about Skill versioning?**
   How do we track improvements? `code-review@2.1.0` with changelog and quality deltas?

---

## Conclusion

Skills are exploding. OpenAI yesterday, Anthropic three days ago. Everyone's building new Skills.

But here's what nobody's talking about: **Skills can be programmatically optimized.**

### What This Proves

**1. Skills are not just markdown files**

They're structured prompts that can be:
- Benchmarked with quality metrics
- Optimized for different models
- Versioned and improved over time
- Auto-generated in model-specific variants

**2. The Skills + DSPy connection unlocks infrastructure**

Current state: Skills are manually crafted, shared as .md files, no quality metrics

Possible future:
```
my-skill/
├── SKILL.md          # Baseline
├── TRAINING.json     # Test cases
├── OPTIMIZED.md      # Auto-generated variants
└── METRICS.json      # Quality benchmarks
```

This enables:
- "This Skill scores 82% on security detection benchmarks"
- "Auto-optimized for GPT-4o, Qwen3, Llama 3.1"
- "Version 2.1 - +15% improvement over v2.0"
- Community contributions to training data

**3. Skills become model-agnostic**

Write the Skill once. Auto-optimize for:
- Frontier models (minimal prompting needed)
- Local models (heavy few-shot guidance)
- Future models (re-optimize when GPT-5 drops)

No manual prompt engineering per model.

### Limitations & Next Steps

This is early exploration. I only tested:
- One skill type (code review)
- Two models (GPT-4o, Qwen3)
- Simple metrics (10 training examples)

Questions to explore:
- Does this work for other skill types? (data analysis, API design, etc.)
- Do optimizations transfer across model families?
- Can we auto-generate training data with GPT-4?
- What's the right standardized format for Skill training data?

**I'm sharing this as: "These two ecosystems connect nicely - here's proof it works."**

Not as: "This is the final solution."

---

**Try it yourself**: https://github.com/instavm/skill-optimization

---

## Appendix: Technical Implementation

### DSPy Signatures
```python
class CodeReview(dspy.Signature):
    """Find security vulnerabilities and bugs in code."""
    code = dspy.InputField(desc="Source code to analyze")
    language = dspy.InputField(desc="Programming language")
    critical_issues = dspy.OutputField(desc="Critical security vulnerabilities")
    high_issues = dspy.OutputField(desc="High priority bugs")
```

### Evaluation Metric
```python
def evaluate_quality(output, expected):
    # Parse issues from output
    issues = parse_issues(output)

    # Calculate precision/recall
    precision = matched / len(issues)
    recall = matched / len(expected)

    # Evaluate explanation quality
    has_impact = check_for_impact_explanation(issues)
    has_fix = check_for_fix_suggestion(issues)

    # Weighted score
    return 0.4 * f1 + 0.3 * has_impact + 0.3 * has_fix
```

### Optimization Loop
```python
# Create optimizer
optimizer = dspy.BootstrapFewShot(
    metric=quality_metric,
    max_bootstrapped_demos=4,
    max_labeled_demos=4
)

# Compile
optimized = optimizer.compile(
    student=module,
    trainset=training_examples
)

# The optimized module now has:
# - Better instructions
# - 4 selected few-shot examples
# - Improved reasoning strategy
```

### Results Data
```json
{
  "gpt4o": {
    "baseline": 0.406,
    "optimized": 0.388,
    "improvement": -0.044
  },
  "qwen": {
    "baseline": 0.425,
    "optimized": 0.551,
    "improvement": 0.125,
    "relative_improvement": 0.294
  }
}
```

All data, code, and examples available in the [repository](https://github.com/instavm/skill-optimization).

