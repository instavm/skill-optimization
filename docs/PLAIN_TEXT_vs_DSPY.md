# Plain Text Skills vs DSPy - Complete Explanation

## TL;DR

**Skills are ALWAYS plain text markdown.**
**DSPy is a Python tool to IMPROVE that text.**

## The Full Picture

```
┌─────────────────────────────────────────────────────────────┐
│                     YOUR WORKFLOW                            │
└─────────────────────────────────────────────────────────────┘

1. Write Skill.md (plain text)
   ↓
2. Define as DSPy Signature (Python - temporary)
   ↓
3. Run optimization (Python - temporary)
   ↓
4. Get improved Skill.md (plain text)
   ↓
5. Use with Claude (plain text)


┌─────────────────────────────────────────────────────────────┐
│                   FILE TYPES                                 │
└─────────────────────────────────────────────────────────────┘

PLAIN TEXT (What Claude uses):
  ✅ code-review.md
  ✅ code-review-optimized.md
  ✅ code-review-modular.md

PYTHON CODE (Optimization tools):
  🔧 src/models.py
  🔧 src/evaluator.py
  🔧 run_optimization.py


┌─────────────────────────────────────────────────────────────┐
│                 THE ANALOGY                                  │
└─────────────────────────────────────────────────────────────┘

Writing an Essay:
  1. Write draft (plain text)
  2. Use Grammarly (software tool)
  3. Get improved essay (plain text)

Optimizing Skills:
  1. Write Skill.md (plain text)
  2. Use DSPy (Python tool)
  3. Get improved Skill.md (plain text)


┌─────────────────────────────────────────────────────────────┐
│              WHAT EACH FILE IS                               │
└─────────────────────────────────────────────────────────────┘

📄 skills/code-review.md
   • Plain text markdown
   • Hand-written
   • Used directly by Claude
   • BASELINE

📄 skills/code-review-optimized.md
   • Plain text markdown
   • Has few-shot examples DSPy found
   • Used directly by Claude
   • IMPROVED VERSION

📄 skills/code-review-modular.md
   • Plain text markdown
   • Shows how to structure for optimization
   • Blueprint/template
   • CONCEPTUAL

🐍 src/models.py (Python)
   • DSPy signatures
   • TEMPORARY - just for optimization
   • NOT used by Claude
   • TOOL, NOT SKILL

🐍 run_optimization.py (Python)
   • Runs the optimization
   • TEMPORARY - just for improvement
   • NOT used by Claude
   • TOOL, NOT SKILL


┌─────────────────────────────────────────────────────────────┐
│          WHAT HAPPENS UNDER THE HOOD                         │
└─────────────────────────────────────────────────────────────┘

When you run: python run_optimization.py

1. Python reads: skills/code-review.md (text)

2. Python converts to DSPy:
   class CodeReview(dspy.Signature):
       code = dspy.InputField()
       issues = dspy.OutputField()

3. Python runs optimization:
   - Tests 10 different phrasings
   - Tries 20 different examples
   - Selects best performing combination

4. Python extracts results:
   - "These 4 examples work best"
   - "This instruction phrasing is clearest"
   - "Chain-of-Thought improves accuracy"

5. Python writes: skills/code-review-optimized.md (text)
   • Includes the 4 best examples
   • Uses the clearest phrasing
   • Adds reasoning prompts

6. You use the new .md file with Claude!


┌─────────────────────────────────────────────────────────────┐
│                WHY THIS MATTERS                              │
└─────────────────────────────────────────────────────────────┘

Your 200-line Skill.md:
  ✅ Stays as markdown
  ✅ Claude reads it directly
  ✅ No Python required to USE it

DSPy Python code:
  ✅ Temporary optimization tool
  ✅ Runs once to improve the skill
  ✅ Outputs better markdown
  ❌ NOT needed after optimization


┌─────────────────────────────────────────────────────────────┐
│                COMPARISON TABLE                              │
└─────────────────────────────────────────────────────────────┘

| Aspect | Plain Text Skill | DSPy Code |
|--------|-----------------|-----------|
| **Format** | Markdown (.md) | Python (.py) |
| **Used by** | Claude directly | Optimization process |
| **Lifetime** | Permanent | Temporary |
| **Purpose** | Define what to do | Find better way to do it |
| **Example** | skills/code-review.md | src/models.py |
| **Required?** | YES (always) | NO (only for optimization) |


┌─────────────────────────────────────────────────────────────┐
│              PRACTICAL WORKFLOW                              │
└─────────────────────────────────────────────────────────────┘

Week 1: Write your-skill.md (markdown)
        ↓
Week 2: Run DSPy optimization (Python)
        • Define signatures
        • Create training data
        • Run optimization
        • Get your-skill-optimized.md
        ↓
Week 3: Deploy your-skill-optimized.md to Claude
        ↓
Week 4-52: Use the markdown file
            (Python code not needed anymore!)
        ↓
Month 6: Re-optimize if needed
         (Run Python again to get new .md)


┌─────────────────────────────────────────────────────────────┐
│                 FINAL ANSWER                                 │
└─────────────────────────────────────────────────────────────┘

Q: "So plain text but still DSPy how?"

A: DSPy is a TOOL that:
   1. Takes plain text skill as input
   2. Optimizes it using Python
   3. Outputs better plain text skill

   The input is plain text.
   The output is plain text.
   DSPy is just the optimization process in between.

   Think: Plain Text → [DSPy Optimization] → Better Plain Text

                    │
                    │  The middle part is Python
                    │  But input and output are markdown!
                    │
                    ▼

   You give Claude the plain text markdown file.
   DSPy never runs in production.
   DSPy was just used ONCE to improve the text.


┌─────────────────────────────────────────────────────────────┐
│                  IN OUR PROJECT                              │
└─────────────────────────────────────────────────────────────┘

We have:

📁 skills/
  └── *.md files ← Plain text, Claude uses these

📁 src/
  └── *.py files ← Python DSPy code, just for optimization

📁 examples/
  └── *.py, *.js ← Sample code for training

📁 data/
  └── *.json ← Training data

The .md files are the SKILLS.
The .py files are the TOOLS.

Claude never sees the Python.
Claude only sees the markdown.

DSPy improved the markdown, then disappeared.
```

