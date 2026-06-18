<!--
SPDX-FileCopyrightText: Fondation RERO+
SPDX-License-Identifier: BSD-3-Clause
-->

# Flask-Wiki Claude guide

## Overview

flask-wiki is a lightweight, file-based wiki packaged as a Flask extension. Wiki pages are plain Markdown files on the filesystem (no database) and the URL structure mirrors the directory tree. The extension registers a Flask Blueprint plus middleware for serving uploaded files.

See [README.md](README.md) for user-facing documentation (features, configuration keys, permissions, quick start).

**Stack**: Python >=3.12,<3.15, Flask, Jinja templates, Whoosh (search), Python-Markdown, EasyMDE (editor), Flask-Babel (i18n)
**Package manager**: `uv` with `poethepoet` for task running

## Commands

During development, all commands are run through uv's virtual env with `uv run`.

### Linting and formatting

**IMPORTANT:** After editing files, make sure that there are no errors in the formatting and linting.

```bash
uv run poe lint     # ruff check
uv run poe format   # ruff format .
```

Ruff is configured with `extend-select = ["ALL"]`; type annotations (`ANN`) are intentionally disabled — do not add them.

### Tests

```bash
uv run poe run_tests   # runs ./scripts/test: pip-audit, ruff format --check, ruff check, pytest
```

`scripts/test` must be run inside the uv virtual env (it checks `VIRTUAL_ENV`). pytest also runs `--doctest-modules` over `flask_wiki`, so docstring examples are tested.

### Running the example app

```bash
cd examples
uv run flask flask_wiki init-index
uv run flask flask_wiki index
uv run flask run --debug   # http://localhost:5000/help
```

## Architecture

The whole extension lives under `flask_wiki/`:

```text
flask_wiki/
├── __init__.py       # Wiki extension class (init_app, blueprint + middleware registration)
├── views.py          # Flask blueprint: routes, permission decorators, template processors
├── api.py            # Core domain logic: Page, WikiBase, Processor, TOC classes
├── forms.py          # WTForms for the editor
├── cli.py            # `flask flask_wiki` CLI group (init-index, index)
├── config.py         # Default WIKI_* config values (excluded from lint/doctest)
├── markdown_ext.py   # Custom Bootstrap Markdown extension
├── utils.py          # Helpers
├── templates/wiki/   # Jinja templates (overridable via WIKI_*_TEMPLATE config)
├── static/           # CSS/JS (wiki.css, wiki.js)
└── translations/     # Babel message catalogs
```

### Core classes (`api.py`)

- **`Page`**: a single wiki page — loads/parses a Markdown file, exposes metadata (title, tags, language), renders HTML, saves, and indexes itself.
- **`WikiBase`**: filesystem-level access — maps URLs to file paths (`path`, `ln_path`), `exists`, `get`/`get_or_404`, language-variant resolution.
- **`Processor`** / **`TOC`**: Markdown pre/post-processing pipeline and table-of-contents handling.

### Permissions

Access control is callable-based, configured by the host app via four `WIKI_*_PERMISSION` settings (see README). In code:

- `can_read_permission` / `can_edit_permission` decorators in `views.py` enforce the `*_VIEW_PERMISSION` callables server-side (return 403 on failure).
- The `*_UI_PERMISSION` callables only toggle visibility of template elements and enforce nothing on their own.

### i18n

User-facing strings are marked with `gettext`/`lazy_gettext` (Python) and in Jinja templates. Babel mappings are configured in `pyproject.toml`. Translation catalogs are managed via `uv run poe extract_messages` / `update_catalog` / `compile_catalog` — only touch catalogs when explicitly working on translations.

## Code Style

- Be clear and concise in the docstrings and do not over-comment the code.
- Do not use Python type annotations (no `-> str`, `: str`, etc. in signatures) — enforced by ruff `ANN` ignore.
- Every source file starts with the SPDX header (`# SPDX-FileCopyrightText: Fondation RERO+` / `# SPDX-License-Identifier: BSD-3-Clause`).
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org).

## Testing Notes

- Tests use function-based style (no class-based tests) and live in `tests/` (`test_api.py`, `test_views.py`, `test_utils.py`).
- Shared fixtures are in `tests/conftest.py`; sample wiki content is in `tests/data/` (ignored by pytest collection).
- Follow a test-driven methodology: each behavioral change should come with tests. Tests should cover this app's behavior, not the behavior of external dependencies (Flask, Whoosh, Markdown).
- Doctests in `flask_wiki` modules run as part of the suite — keep docstring examples correct.

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
