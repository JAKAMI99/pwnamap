# ⚠️ vibecoded branch — code not manually reviewed

> **This branch contains code generated with significant AI assistance.
> The author (`JAKAMI99`) has not read every line.**

## What this means

- The diffs in this branch were authored by an AI coding agent (Claude Opus 4.6)
  working from the maintainer's intent and the existing `main` branch.
- The author reviewed the *intent* of each commit, but **not every line of code**.
- Bugs, security issues, and anti-patterns are therefore possible — including
  subtle ones an LLM can introduce even when superficially correct.

## Before merging anything from `vibecoded` into `main`

1. **Read every changed file end-to-end.** The branch name is the warning,
   not a substitute for review.
2. **Run the test suite** (`pytest`) and check that smoke tests pass.
3. **Run the linter** (`ruff check .`) and resolve all findings.
4. **Diff against `main`** and ask: "does this match what the commit message says?"
5. **Treat the security model skeptically.** AI code commonly:
   - Misses auth/authz edge cases
   - Has injection vectors the model didn't imagine
   - Uses outdated or insecure patterns confidently
6. **Verify the CI pipeline** (`Actions` tab) is green on this branch before merge.

## When to use this branch

- ✅ Drafts of refactors the maintainer wants to learn from
- ✅ Exploring what an AI-assisted approach would look like
- ✅ Reviews of AI-generated approaches by a human reviewer

## When NOT to use this branch

- ❌ As a basis for production deployments without human review
- ❌ As a reference for "best practice" code (it isn't, by definition)
- ❌ Without verifying every change manually before merging

## For reviewers

If you're reviewing a PR from `vibecoded`, the burden of review is on you —
not the AI. The branch exists *precisely* to make this trade-off explicit.

— `JAKAMI99`
