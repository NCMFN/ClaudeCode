# Santa Loop

Adversarial dual-review convergence loop using the santa-method skill. Two independent reviewers — different models, no shared context — must both return NICE before code ships.

## Instructions

### Step 1: Identify What to Review

Determine the scope from `$ARGUMENTS` or fall back to uncommitted changes:

```bash
git diff --name-only HEAD
```

Read all changed files to build the full review context. If `$ARGUMENTS` specifies a path, file, or description, use that as the scope instead.

### Step 2: Build the Rubric

Construct a rubric appropriate to the file types under review. Every criterion must have an objective PASS/FAIL condition. Include at minimum:

| Criterion | Pass Condition |
|-----------|---------------|
| Correctness | Logic is sound, no bugs, handles edge cases |
| Security | No secrets, injection, XSS, or OWASP Top 10 issues |
| Error handling | Errors handled explicitly, no silent swallowing |
| Completeness | All requirements addressed, no missing cases |
| Internal consistency | No contradictions between files or sections |
| No regressions | Changes don't break existing behavior |

Add domain-specific criteria based on file types (e.g., type safety for TS, memory safety for Rust, migration safety for SQL).

### Step 3: Dual Independent Review

Launch two reviewers **in parallel** with identical rubric but **no shared context**.

#### Reviewer A: Claude Agent (always runs)

Launch an Agent (subagent_type: `code-reviewer`, model: `opus`) with the full rubric + all files under review. The prompt must include:
- The complete rubric
- All file contents under review
- "You are an independent quality reviewer. You have NOT seen any other review. Your job is to find problems, not to approve."
- Return structured verdict: NICE or NAUGHTY with findings

#### Reviewer B: External Model (preferred, with Claude fallback)

Try each option in order — use the first one available:

**Option 1: Codex CLI** (if `codex` is on PATH)
Write the full rubric + file contents to a temp file, then:
```bash
codex exec -p "full-auto" --model gpt-5.4 -C "$(pwd)" - < /tmp/santa-reviewer-b-prompt.txt
```

**Option 2: Gemini CLI** (if `gemini` is on PATH)
```bash
echo "<prompt>" | gemini -m gemini-3.1-pro-preview
```

**Option 3: Claude Agent fallback**
If neither external CLI is available, launch a second Claude Agent (subagent_type: `code-reviewer`, model: `opus`). Log a note that both reviewers share the same model family — true model diversity was not achieved but context isolation is still enforced.

In all cases, the prompt must contain the identical rubric and instructions as Reviewer A. The reviewer must return a structured verdict.

### Step 4: Verdict Gate

- **Both NICE** → proceed to Step 6 (push)
- **Either NAUGHTY** → merge all critical issues from both reviewers, deduplicate, proceed to Step 5

### Step 5: Fix Cycle (NAUGHTY path)

1. Display all critical issues from both reviewers
2. Fix every flagged issue — change only what was flagged, no drive-by refactors
3. Commit all fixes in a single commit:
   ```
   fix: address santa-loop review findings (round N)
   ```
4. Re-run Step 3 with **fresh reviewers** (no memory of previous rounds)
5. Repeat until both return NICE

**Maximum 3 iterations.** If still NAUGHTY after 3 rounds, stop and present all remaining issues to the user. Do NOT push.

### Step 6: Push (NICE path)

When both reviewers return NICE:

```bash
git push
```

### Step 7: Final Report

```
SANTA VERDICT: [NICE / NAUGHTY (escalated)]

Reviewer A (Claude Opus):   [NICE/NAUGHTY]
Reviewer B ([model used]):  [NICE/NAUGHTY]

Agreement:
  Both flagged:      [issues caught by both]
  Reviewer A only:   [issues only A caught]
  Reviewer B only:   [issues only B caught]

Iterations: [N]/3
Result:     [PUSHED / ESCALATED TO USER]
```

## Arguments

`$ARGUMENTS` can be:
- Empty — reviews uncommitted changes
- A file path or glob — reviews specific files
- A description — reviews files relevant to that task

## Notes

- Reviewer A (Claude Opus) always runs — guarantees at least one strong reviewer regardless of tooling.
- Model diversity is the goal for Reviewer B. GPT-5.4 or Gemini 3.1 Pro gives true independence — different training data, different biases, different blind spots. The Claude-only fallback still provides value via context isolation but loses model diversity.
- Strongest available models are used: Opus for Reviewer A, GPT-5.4 or Gemini 3.1 Pro for Reviewer B.
- Fresh reviewers each round prevents anchoring bias from prior findings.
- The rubric is the most important input. Tighten it if reviewers rubber-stamp or flag subjective style issues.
- Commits happen on NAUGHTY rounds so fixes are preserved even if the loop is interrupted.
- Push only happens after NICE — never mid-loop.
