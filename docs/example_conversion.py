#!/usr/bin/env python3
"""
CONCRETE EXAMPLE: Converting between Skill.md and DSPy

This shows how plain text skills and DSPy work together.
"""

import dspy

# ============================================================================
# STEP 1: You have a plain text Skill.md
# ============================================================================

SKILL_MD_BASELINE = """
# Code Review Skill

You are a code reviewer. Review code and find bugs.

Instructions:
1. Find security issues
2. Find bugs
3. Provide fixes

Output:
- List of issues
- Suggested fixes
"""

print("=" * 70)
print("STEP 1: Plain Text Skill (What you write)")
print("=" * 70)
print(SKILL_MD_BASELINE)
print()


# ============================================================================
# STEP 2: Convert skill instructions to DSPy Signature
# ============================================================================

print("=" * 70)
print("STEP 2: Convert to DSPy Signature (Python)")
print("=" * 70)
print()

# The skill's instructions become a Python class
class CodeReviewSkill(dspy.Signature):
    """You are a code reviewer. Review code and find bugs."""  # From skill header

    # Inputs (what the skill receives)
    code = dspy.InputField(desc="Source code to review")  # From skill context
    language = dspy.InputField(desc="Programming language")

    # Outputs (what the skill produces)
    issues = dspy.OutputField(desc="List of issues found")  # From skill output format
    fixes = dspy.OutputField(desc="Suggested fixes")

print("Python DSPy Signature created:")
print(f"  Class: {CodeReviewSkill.__name__}")
print(f"  Docstring: {CodeReviewSkill.__doc__}")
print(f"  Input fields: code, language")
print(f"  Output fields: issues, fixes")
print()


# ============================================================================
# STEP 3: DSPy runs optimization (in Python)
# ============================================================================

print("=" * 70)
print("STEP 3: DSPy Optimization (Python)")
print("=" * 70)
print()

# Create a module from the signature
module = dspy.ChainOfThought(CodeReviewSkill)

print("DSPy module created with Chain-of-Thought reasoning")
print()

# In real optimization, we'd do:
# optimizer = dspy.BootstrapFewShot(metric=metric)
# optimized_module = optimizer.compile(module, trainset=examples)
#
# DSPy would:
# - Test different phrasings
# - Select best examples
# - Optimize the prompt

print("DSPy optimization would:")
print("  1. Generate multiple prompt variations")
print("  2. Test each on training data")
print("  3. Select best-performing version")
print("  4. Add most helpful examples")
print()


# ============================================================================
# STEP 4: Extract optimized prompt (Python → Text)
# ============================================================================

print("=" * 70)
print("STEP 4: Extract Optimized Prompt")
print("=" * 70)
print()

# After optimization, DSPy has learned:
# - Better instructions
# - Best examples to include
# - Optimal reasoning strategy

# We extract this and convert to markdown
OPTIMIZED_SKILL_MD = """
# Code Review Skill (Optimized by DSPy)

You are an expert security-focused code reviewer. Systematically analyze code for vulnerabilities and bugs with specific, actionable feedback.

## Optimized Instructions

Analyze code in this priority order:
1. **Critical Security Issues**: SQL injection, command injection, XSS, hardcoded secrets
2. **High Priority Bugs**: Logic errors, resource leaks, error handling gaps
3. **Quality Issues**: Code smells, maintainability concerns

For each issue provide:
- Specific vulnerability/bug name
- Exact location (function:line)
- Impact description
- Fix with code example

## Few-Shot Examples (DSPy Selected These)

### Example 1: SQL Injection (Most Helpful)
**Bad**: `query = "SELECT * FROM users WHERE id = " + user_id`
**Issue**: SQL Injection - arbitrary SQL execution
**Fix**: `cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))`

### Example 2: Weak Crypto
**Bad**: `hashlib.md5(password.encode())`
**Issue**: MD5 is cryptographically broken
**Fix**: `bcrypt.hashpw(password.encode(), bcrypt.gensalt())`

## Output Format

**Issues Found:**
1. [CRITICAL/HIGH/MEDIUM] Issue name at location
   - Impact: [what could happen]
   - Fix: `[code example]`
"""

print("Optimized Skill.md created:")
print(OPTIMIZED_SKILL_MD[:500] + "...")
print()


# ============================================================================
# STEP 5: Both are plain text markdown - Use with Claude
# ============================================================================

print("=" * 70)
print("STEP 5: Use Plain Text Skill with Claude")
print("=" * 70)
print()

print("Both files are plain markdown:")
print("  • code-review.md (baseline)")
print("  • code-review-optimized.md (DSPy improved)")
print()
print("Claude reads them as regular Skills!")
print("DSPy was just the TOOL to make the second one better.")
print()


# ============================================================================
# THE KEY INSIGHT
# ============================================================================

print("=" * 70)
print("KEY INSIGHT")
print("=" * 70)
print()
print("DSPy IS NOT THE SKILL - it's the OPTIMIZER")
print()
print("  Skill.md (text)")
print("       ↓")
print("  DSPy optimization (Python)")
print("       ↓")
print("  Better Skill.md (text)")
print()
print("Both input and output are PLAIN TEXT MARKDOWN.")
print("The Python code is temporary - just for optimization.")
print()
print("It's like using a spell-checker:")
print("  • Input: Your writing (text)")
print("  • Tool: Spell-checker (software)")
print("  • Output: Corrected writing (text)")
print()
print("DSPy is the spell-checker for prompts!")
print()
