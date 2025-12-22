# How Plain Text Skills Connect to DSPy

## The Problem
- Claude Skills are **plain markdown files**
- DSPy is **Python code**
- How do they work together?

## The Answer: Conversion Pipeline

### Step 1: Start with Plain Text Skill

```markdown
# My Skill

You are an expert at X.

Instructions:
1. Do this
2. Do that

Output format:
- Thing 1
- Thing 2
```

### Step 2: Convert to DSPy Signature (Python)

```python
import dspy

# The skill instructions become a DSPy Signature
class MySkillSignature(dspy.Signature):
    """You are an expert at X."""

    input_data = dspy.InputField(desc="The data to process")
    output_thing1 = dspy.OutputField(desc="Thing 1")
    output_thing2 = dspy.OutputField(desc="Thing 2")

# The skill becomes a DSPy module
skill_module = dspy.ChainOfThought(MySkillSignature)
```

### Step 3: Run DSPy Optimization (Python)

```python
# DSPy finds the best:
# - Instructions phrasing
# - Few-shot examples
# - Reasoning strategy

optimizer = dspy.BootstrapFewShot(metric=my_metric)
optimized_module = optimizer.compile(skill_module, trainset=data)

# optimized_module now has:
# - Better instructions
# - 3-5 good examples
# - Optimized prompts
```

### Step 4: Extract and Export to Markdown

```python
# DSPy stores optimized prompts internally
# We extract them and convert back to markdown

optimized_instructions = optimized_module.get_instructions()
optimized_examples = optimized_module.demos  # The few-shot examples

# Create new Skill.md
skill_md = f"""
# My Skill (Optimized)

{optimized_instructions}

## Examples

{format_examples(optimized_examples)}
"""

# Save as plain text markdown
with open("my-skill-optimized.md", "w") as f:
    f.write(skill_md)
```

### Step 5: Use in Claude

```markdown
# my-skill-optimized.md
# Now this is a regular Claude Skill file!

You are an expert at X. [optimized instructions]

## Examples
[The best 4 examples DSPy found]

## Instructions
[Optimized step-by-step guide]
```

## Real Example from Our Project

### What We Did:

```python
# 1. PYTHON: Define signature
class CodeReview(dspy.Signature):
    code = dspy.InputField()
    critical_issues = dspy.OutputField()
    high_issues = dspy.OutputField()

# 2. PYTHON: Create module
module = dspy.ChainOfThought(CodeReview)

# 3. PYTHON: Optimize
optimizer = dspy.BootstrapFewShot(metric=metric)
optimized = optimizer.compile(module, trainset=data)

# 4. PYTHON: Extract what DSPy learned
# - It found: "SQL Injection example is most helpful"
# - It found: "Explain impact is important"
# - It found: "Include code fixes"

# 5. MANUAL: We write to markdown
```

### What We Created:

```markdown
# code-review-optimized.md

[Instructions DSPy optimized]

## Few-Shot Examples

### Example 1: SQL Injection
[DSPy selected this as most helpful]

### Example 2: Weak Hashing
[DSPy selected this too]
```

## Key Insight

**DSPy is a TOOL to CREATE better plain text skills**

```
Plain Text Skill (input)
        ↓
     [DSPy optimization in Python]
        ↓
Better Plain Text Skill (output)
```

DSPy doesn't replace the markdown - it **generates better markdown**!

## In Our Framework

### We have 3 files:

1. **code-review.md** (baseline)
   - Hand-written, plain text
   - Never touched Python

2. **code-review-modular.md** (conceptual)
   - Shows how you'd structure for DSPy
   - Still plain text, but organized like DSPy modules
   - A "blueprint" for optimization

3. **code-review-optimized.md** (improved)
   - What DSPy would produce
   - Plain text with few-shot examples
   - Uses patterns DSPy discovered

### The Python DSPy code in `src/`:

These are **tools** that:
- ✅ Take plain text skills as input
- ✅ Run optimization experiments
- ✅ Output improved plain text skills
- ❌ NOT the skills themselves

## Analogy

Think of DSPy like a **compiler**:

```
Source Code (Skill.md)
         ↓
    [Compiler (DSPy)]
         ↓
Optimized Code (Skill-optimized.md)
```

Both input and output are **plain text** - DSPy just makes it better!

## Why This Matters

**Your 200-line Skill.md stays as markdown!**

You just:
1. Define it as a DSPy Signature (Python)
2. Run optimization (Python)
3. Get improved Skill.md (markdown)
4. Use the improved markdown with Claude

The Python is temporary - just for optimization.
The markdown is forever - that's what Claude uses.
