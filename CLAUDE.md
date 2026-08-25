<!--
SPDX-FileCopyrightText: Fondation RERO+
SPDX-License-Identifier: BSD-3-Clause
-->

# Flask-Wiki Claude guide

## Overview

flask-wiki is a lightweight, file-based wiki packaged as a Flask extension. Wiki pages are plain Markdown files on the filesystem (no database) and the URL structure mirrors the directory tree. The extension registers a Flask Blueprint plus middleware for serving uploaded files.

See [README.md](README.md) for user-facing documentation (features, configuration keys, permissions, quick start).

## Commands

During development, all commands are run through uv's virtual env with `uv run`.

### Linting and formatting

**IMPORTANT:** After editing files, make sure that there are no errors in the formatting and linting.

```bash
uv run poe lint     # ruff check
uv run poe format   # ruff format .
```

### Tests

```bash
uv run poe run_tests
```

### Running the example app

```bash
cd examples
uv run flask flask_wiki init-index
uv run flask flask_wiki index
uv run flask run --debug   # http://localhost:5000/help
```

## i18n

User-facing strings are marked with `gettext`/`lazy_gettext` (Python) and in Jinja templates. Translation catalogs are managed via `uv run poe extract_messages` / `update_catalog` / `compile_catalog` — only touch catalogs when explicitly working on translations.

## Code Style

- Be clear and concise in the docstrings and do not over-comment the code.
- Ruff is configured in `pyproject.toml` under `[tool.ruff]`: every rule set is enabled (`extend-select = ["ALL"]`), so expect strict linting.
- Do not use Python type annotations (no `-> str`, `: str`, etc. in signatures) — the `ANN` rules are intentionally disabled.
- Every source file starts with the SPDX header (`# SPDX-FileCopyrightText: Fondation RERO+` / `# SPDX-License-Identifier: BSD-3-Clause`).
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org).

## Testing Notes

- Tests use function-based style (no class-based tests).
- Follow a test-driven methodology: each behavioral change should come with tests. Tests should cover this app's behavior, not the behavior of external dependencies (Flask, Whoosh, Markdown).
- pytest runs with `--doctest-modules` over `flask_wiki`, so every docstring example is executed — keep them correct.

## Behavioral guidelines

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:

- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:

- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

```text
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
