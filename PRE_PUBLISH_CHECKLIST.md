# Pre-Publish Checklist

Before creating the GitHub repository, review and complete:

## 1. Personal Information

- [ ] Update LICENSE with your name
  - File: `LICENSE` line 3
  - Replace: `[Your Name]`

- [ ] Update README.md citations
  - File: `README.md` line ~220
  - Replace: `Your Name` and `yourusername`

- [ ] Update blog_post.md links
  - File: `docs/blog_post.md`
  - Replace all `[your-link]`, `yourusername`, etc.

## 2. Test the Code

### Quick Test (5 min - Local Only)
```bash
# Make sure Ollama + Qwen work
ollama pull qwen3
python scripts/show_actual_outputs.py
```

Expected: See quality comparison output

### Full Test (if you have Azure/OpenAI)
```bash
export AZURE_API_KEY="your-test-key"
export AZURE_API_BASE="your-endpoint"
export AZURE_DEPLOYMENT="your-deployment"

python scripts/run_azure_optimization.py
```

Expected: See optimization results

## 3. Verify File Structure

```
skill-optimization/
├── .gitignore          ✓ (blocks API keys, venv, etc.)
├── LICENSE             → Update your name
├── README.md           → Update links
├── requirements.txt    ✓
│
├── docs/               ✓ (blog, results, diagrams)
├── skills/             ✓ (skill files)
├── data/               ✓ (training data)
├── examples/           ✓ (vulnerable code)
├── src/                ✓ (DSPy code)
├── scripts/            ✓ (runnable scripts)
└── results/            ✓ (output directory)
```

## 4. Security Check

- [ ] No API keys in files
  ```bash
  grep -r "sk-" . --exclude-dir=venv --exclude-dir=.git
  grep -r "api_key.*=" . --exclude-dir=venv --exclude-dir=.git
  ```

- [ ] .gitignore blocks sensitive files
  ```bash
  cat .gitignore | grep -E "\.env|\.key"
  ```

## 5. Clean Up

- [ ] Remove any personal notes/comments
  ```bash
  grep -r "TODO" . --exclude-dir=venv --exclude-dir=.git
  grep -r "FIXME" . --exclude-dir=venv --exclude-dir=.git
  ```

- [ ] Verify no large files (>10MB)
  ```bash
  find . -type f -size +10M -not -path "*/venv/*"
  ```

## 6. Documentation Quality

- [ ] README.md renders correctly
  - View in VS Code markdown preview
  - Check all links work
  - Code blocks have proper syntax highlighting

- [ ] Blog post is finalized
  - File: `docs/blog_post.md`
  - No placeholder text
  - All links updated

## 7. Create GitHub Repo

### Option A: GitHub CLI
```bash
cd /Users/manish/Work/skill-optimization

# Initialize git
git init
git add .
git commit -m "Initial commit: Skill.md optimization with DSPy"

# Create GitHub repo (replace YOUR_GITHUB_USERNAME)
gh repo create YOUR_GITHUB_USERNAME/skill-optimization --public --source=. --push

# Or if you prefer private initially:
gh repo create YOUR_GITHUB_USERNAME/skill-optimization --private --source=. --push
```

### Option B: Manual
```bash
cd /Users/manish/Work/skill-optimization

git init
git add .
git commit -m "Initial commit: Skill.md optimization with DSPy"

# Then:
# 1. Go to github.com/new
# 2. Create repo named "skill-optimization"
# 3. Copy the remote URL
# 4. Run:

git remote add origin git@github.com:YOUR_GITHUB_USERNAME/skill-optimization.git
git branch -M main
git push -u origin main
```

## 8. Post-Publish

- [ ] Add topics/tags on GitHub:
  - `dspy`
  - `prompt-optimization`
  - `llm`
  - `skills`
  - `ai`
  - `prompt-engineering`

- [ ] Add description:
  "Programmatically optimize Skill.md prompts using DSPy - works better on local models (+11% on Qwen) than frontier models"

- [ ] Enable GitHub Pages (optional):
  - Settings → Pages → Deploy from branch → main/docs

## 9. Sharing Checklist

Once repo is published:

- [ ] Update blog post with GitHub URL
  - File: `docs/blog_post.md`
  - Replace all `[github.com/yourusername/...]` with actual URL

- [ ] Test the "Try It Yourself" instructions
  - Clone the repo in a fresh directory
  - Follow README.md instructions
  - Verify it works

- [ ] Post to Hacker News
  - Title: "Skills Can Be Programmatically Optimized (Using DSPy)"
  - URL: Link to `docs/blog_post.md` on GitHub
  - Submit as "Show HN"

- [ ] Tweet the thread
  - File: `docs/SOCIAL_MEDIA.md` has pre-written tweets
  - Update with GitHub URL

## 10. Maintenance

Consider creating these issues for future work:

1. "Test with other models (Llama, Mistral)"
2. "Create more skill types (API design, data analysis)"
3. "Standardize training data format"
4. "Add CI/CD for automated testing"
5. "Create web demo for non-technical users"

---

## Quick Commands

**Initialize git:**
```bash
cd /Users/manish/Work/skill-optimization
git init
```

**Check what will be committed:**
```bash
git status
```

**Preview .gitignore working:**
```bash
git status --ignored
```

**Test README rendering:**
```bash
# Install grip (GitHub README renderer)
pip install grip
grip README.md
# Opens browser to localhost:6419
```

**Double-check no secrets:**
```bash
git secrets --scan || echo "Install git-secrets first: brew install git-secrets"
```

---

## Ready to Publish?

When all checkboxes above are ✓:

```bash
# Final check
git status
git diff

# Commit
git add .
git commit -m "Initial commit: Skill.md optimization with DSPy"

# Push to GitHub
gh repo create YOUR_USERNAME/skill-optimization --public --source=. --push
```

Then share on HN and Twitter! 🚀
