# Code Review Skill (Modular Decomposition)

This skill demonstrates how a monolithic prompt can be decomposed into logical modules for optimization.

## Module 1: Security Issue Detection

**Purpose**: Find security vulnerabilities

**Inputs**: code, language

**Outputs**: List of security issues with severity and location

**Strategy**: Chain-of-thought reasoning focusing on OWASP Top 10

**Instructions**:
Systematically check for:
1. Injection flaws (SQL, command, code)
2. Authentication/authorization issues
3. Sensitive data exposure
4. Using components with known vulnerabilities
5. Insufficient logging/monitoring

For each finding, provide:
- Specific vulnerability type
- Exact location (function:line)
- Exploit scenario
- CVSS-like severity justification

---

## Module 2: Performance Issue Detection

**Purpose**: Identify performance bottlenecks

**Inputs**: code, language

**Outputs**: Performance issues with impact estimation

**Strategy**: Predict (faster than chain-of-thought for this task)

**Instructions**:
Look for:
1. Algorithmic complexity issues (O(n²) where O(n) possible)
2. Unnecessary iterations or computations
3. Inefficient data structures
4. Missing caching opportunities
5. N+1 query problems
6. Unbounded operations

Estimate impact as: Low (<10% slowdown), Medium (10-50%), High (>50% or scales poorly)

---

## Module 3: Code Quality Assessment

**Purpose**: Evaluate maintainability and best practices

**Inputs**: code, language

**Outputs**: Quality issues ranked by technical debt impact

**Strategy**: Predict

**Instructions**:
Assess:
1. Type safety (missing types, dangerous coercion)
2. Error handling completeness
3. Resource management (leaks, missing cleanup)
4. Code duplication
5. Naming conventions
6. Documentation coverage

Prioritize issues that increase technical debt or future bug risk.

---

## Module 4: Severity Classification

**Purpose**: Assign accurate severity levels

**Inputs**: issue_description, code_context

**Outputs**: Severity with justification

**Strategy**: Predict (fast classification)

**Severity Levels**:
- **Critical**: Security breach, data loss, system crash
- **High**: Functional bugs, performance degradation >50%
- **Medium**: Code quality, technical debt, minor bugs
- **Low**: Style, conventions, minor improvements

**Instructions**:
Consider:
1. Exploitability (for security issues)
2. Frequency of code path execution
3. Difficulty to fix vs. impact
4. Regulatory/compliance requirements

---

## Module 5: Fix Generation

**Purpose**: Provide actionable, correct fix suggestions

**Inputs**: issue, code_context, language

**Outputs**: Fix description with code example

**Strategy**: Chain-of-thought (reasoning about correctness)

**Instructions**:
For each fix:

1. **Explain the approach** (what to change and why)
2. **Show the code**:
   ```language
   [corrected code snippet]
   ```
3. **Verify correctness** (why this solves the problem)
4. **Note trade-offs** (if any)

Ensure fixes are:
- Minimal (change only what's needed)
- Correct (actually solve the problem)
- Idiomatic (follow language conventions)
- Safe (don't introduce new issues)

---

## Orchestration

Modules run in parallel for efficiency:
- Module 1 (Security) + Module 2 (Performance) + Module 3 (Quality) → all findings
- Module 4 (Severity) → classify each finding
- Module 5 (Fix) → generate fixes for high-priority issues

Final output combines all results in structured format.

---

## Why This Decomposition?

1. **Each module is independently optimizable** - DSPy can tune security detection separately from fix generation
2. **Different reasoning strategies** - Security needs deep analysis (CoT), severity is classification (Predict)
3. **Parallel execution possible** - Faster overall review
4. **Easier to debug** - Know which module needs improvement
5. **Reusable components** - Use security module in other skills

This modular approach enables systematic optimization of each component rather than treating the entire skill as a black box.
