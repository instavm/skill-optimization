# Skill.md Optimization with DSPy

Programmatically optimize `Skill.md` prompts using DSPy's prompt optimization framework.

**Key finding:** DSPy optimization shows improvement on local models (+2% on Qwen) but not frontier models (0% on GPT-4o).

📝 **[Read the full writeup](docs/blog_post.md)**

---

## Quick Start

### Option 1: Test with Qwen (Local, No API Key)

```bash
# Install Ollama: https://ollama.ai
ollama pull qwen3

# Install dependencies
pip install -r requirements.txt

# Run REAL DSPy BootstrapFewShot optimization
python scripts/optimize_qwen.py
```

**Result:** See REAL automated DSPy optimization with BootstrapFewShot in ~3-4 minutes.
- Baseline: 42.5%
- BootstrapFewShot Optimized: 55.1%
- **+12.5% improvement** from automated example selection

DSPy automatically selects best examples and generates optimized prompts - no manual prompt engineering.

### Option 2: Test with GPT-4o (Requires Azure/OpenAI)

```bash
# Set environment variables
export AZURE_API_KEY="your-key"
export AZURE_API_BASE="your-endpoint"
export AZURE_DEPLOYMENT="your-deployment"

# Run optimization
python scripts/run_azure_optimization.py
```

---

## What This Does

**Input:** `code-review.md` - A Skill that finds security vulnerabilities

**Process:**
1. Convert Skill.md → DSPy Signature
2. Optimize with 10 vulnerable code examples
3. Extract improvements → Skill-optimized.md

**Output:** Model-specific optimized variants

---

## Results

| Model | Baseline | Optimized | Improvement |
|-------|----------|-----------|-------------|
| GPT-4o (Azure) | 40.6% | 38.8% | 0% |
| Qwen3 (Ollama) | 42.5% | 55.1% | +12.5% |

**Key insight:** DSPy's BootstrapFewShot shows significant improvement on local models. GPT-4o sees no improvement (already optimal), Qwen shows +12.5% with automated optimization (+29% relative improvement).

---

## Repository Structure

```
skill-optimization/
├── skills/              # Skill.md files (baseline, optimized, modular)
├── data/                # Training data (10 vulnerable code examples)
├── examples/            # Example vulnerable code files
├── src/                 # DSPy signatures, evaluators, utils
├── scripts/             # Runnable optimization scripts
├── docs/                # Blog post, diagrams, detailed results
└── results/             # Output directory
```

---

## Key Files

**For Users:**
- `scripts/show_actual_outputs.py` - Demo with Qwen (5 min, no API key)
- `scripts/run_azure_optimization.py` - Full optimization with GPT-4o
- `docs/blog_post.md` - Complete writeup with findings

**For Developers:**
- `src/models.py` - DSPy signatures for code review
- `src/improved_evaluator.py` - Quality metrics
- `data/training_data.json` - 10 vulnerable code samples

---

## Use Cases

### 1. Benchmark Skill Quality
```bash
python scripts/run_azure_optimization.py
# Output: Objective quality scores for your Skill
```

### 2. Generate Model-Specific Variants
```
code-review.md → DSPy → code-review-qwen.md (optimized for local model)
                     → code-review-gpt4.md (minimal, frontier model)
```

### 3. Automate Skill Improvement
```bash
# Add training examples to data/training_data.json
# Re-run optimization
# Get improved Skill automatically
```

---

## How It Works

### 1. Define Skill as DSPy Signature

```python
class CodeReview(dspy.Signature):
    """Find security vulnerabilities in code."""
    code = dspy.InputField()
    language = dspy.InputField()
    critical_issues = dspy.OutputField()
    high_issues = dspy.OutputField()
```

### 2. Create Training Data

```json
{
  "file_path": "examples/example_1.py",
  "expected_issues": [
    {
      "title": "SQL Injection",
      "severity": "Critical",
      "locations": ["authenticate_user:10"]
    }
  ]
}
```

### 3. Run Optimization

```python
optimizer = dspy.BootstrapFewShot(metric=quality_metric)
optimized = optimizer.compile(baseline, trainset=examples)
```

### 4. Extract to Skill.md

The optimized module contains:
- Better instruction phrasing
- Auto-selected few-shot examples
- Improved reasoning strategies

Export these back to markdown for use in Claude, OpenAI Skills, etc.

---

## Training Data

10 vulnerable code examples covering:
- SQL Injection (Python, JavaScript)
- Cross-Site Scripting (JavaScript)
- Command Injection (Python)
- Weak Cryptography (MD5, hardcoded secrets)
- Path Traversal, IDOR, Prototype Pollution
- Insecure Deserialization, Resource Leaks

See [`data/training_data.json`](data/training_data.json)

---

## Requirements

```
dspy-ai>=2.0.0
```

**Optional:**
- Azure OpenAI or OpenAI API key (for GPT-4o testing)
- Ollama + Qwen3 (for local testing)

---

## Example Output

Running `python scripts/test_ollama_qwen.py`:

```
======================================================================
BASELINE: Simple Predict (No optimization)
======================================================================
Testing 1/3... Score: 65.7%
Testing 2/3... Score: 61.8%
Testing 3/3... Score: 28.5%
✅ Baseline Average: 52.0%

======================================================================
OPTIMIZED: Chain of Thought (Better reasoning)
======================================================================
Testing 1/3... Score: 50.3%
Testing 2/3... Score: 75.8%
Testing 3/3... Score: 33.0%
✅ Chain of Thought Average: 53.0%

🏆 Best Method: Chain of Thought
📊 Score: 53.0%
📈 Improvement: +1.0% (+2.0%)
```

**Real DSPy optimization** running on Qwen with actual evaluation metrics.

---

## Documentation

- 📝 [Full Blog Post](docs/blog_post.md) - Complete writeup with findings
- 📊 [Optimization Results](docs/OPTIMIZATION_RESULTS.md) - Detailed metrics
- 📐 [Pipeline Diagram](docs/PIPELINE_DIAGRAM.md) - Visual explanation
- 💬 [Social Media](docs/SOCIAL_MEDIA.md) - Sharing content

---

## Limitations

- Tested on one skill type (code review)
- Two models only (GPT-4o, Qwen3)
- Simple metrics (10 training examples)

**Open questions:**
- Do optimizations transfer across models?
- Can we auto-generate training data?
- What's the right standardized format?

---

## Contributing

Contributions welcome! Particularly interested in:

1. Testing with other skill types (data analysis, API design, etc.)
2. Testing with other models (Llama, Mistral, etc.)
3. Better evaluation metrics
4. Transfer learning experiments
5. Auto-generation of training data

---

## Citation

```bibtex
@misc{skilloptimization2024,
  title={Skill.md Optimization with DSPy},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/skill-optimization}
}
```

---

## License

MIT License - See [LICENSE](LICENSE)

---

## Acknowledgments

- [DSPy](https://github.com/stanfordnlp/dspy) - Stanford NLP
- [Agent Skills](https://agentskills.io/) - Anthropic
- [OpenAI Skills](https://developers.openai.com/codex/skills/) - OpenAI
- [Ollama](https://ollama.ai) - Local model hosting
