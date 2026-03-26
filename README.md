# Flask-Wiki

A lightweight, file-based wiki system built as a Flask extension. Create, edit, search, and manage wiki pages stored as Markdown files on the filesystem -- no database required.

## Features

- Markdown pages with metadata (title, tags)
- Full-text search powered by Whoosh
- File/image uploads
- WikiLinks (`[[Page Name]]` syntax)
- Multilingual support
- Rich editor with live preview (EasyMDE)
- Customizable templates and permissions

## Installation

```bash
pip install flask-wiki
```

## Quick start

```python
from flask import Flask
from flask_wiki import Wiki

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
Wiki(app)
```

Or using the application factory pattern:

```python
from flask import Flask
from flask_wiki import Wiki

wiki = Wiki()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'
    wiki.init_app(app)
    return app
```

The wiki will be available at `/help` by default (configurable via `WIKI_URL_PREFIX`).

### Initialize the search index

Before using search, initialize the Whoosh index:

```bash
flask flask_wiki init-index
flask flask_wiki index
```

## How it works

Wiki pages are plain Markdown files stored in a content directory (`./data` by default). The URL structure mirrors the filesystem: `/help/guides/setup` maps to `data/guides/setup.md`.

Each page file has an optional metadata header followed by the Markdown body:

```markdown
title: My Page Title
tags: setup, guide

# Content starts here

Regular markdown content...
```

The wiki registers a Flask Blueprint with routes for viewing, editing, searching, and managing pages. Uploaded files (images) are stored in a subfolder and served via middleware.

## Permissions

Flask-Wiki uses a callable-based permission system. The host application provides functions that return `True` or `False` to control access. By default, everything is open (all lambdas return `True`).

There are four permission settings:

| Setting | Purpose |
|---------|---------|
| `WIKI_READ_VIEW_PERMISSION` | Controls access to read routes (view pages, search). Returns 403 if `False`. |
| `WIKI_EDIT_VIEW_PERMISSION` | Controls access to edit routes (edit, delete, upload). Returns 403 if `False`. |
| `WIKI_READ_UI_PERMISSION` | Controls visibility of read-related UI elements in templates. |
| `WIKI_EDIT_UI_PERMISSION` | Controls visibility of edit buttons/links in templates. |

Each permission is a callable (no arguments) that is evaluated per-request. This lets you integrate with any authentication system -- Flask-Login, session-based auth, API tokens, etc.

### Example: integrating with Flask-Login

```python
from flask_login import current_user

app.config['WIKI_READ_VIEW_PERMISSION'] = lambda: current_user.is_authenticated
app.config['WIKI_EDIT_VIEW_PERMISSION'] = lambda: current_user.is_authenticated and current_user.has_role('editor')
app.config['WIKI_EDIT_UI_PERMISSION'] = app.config['WIKI_EDIT_VIEW_PERMISSION']
```

The `VIEW` permissions are enforced server-side via route decorators. The `UI` permissions only toggle visibility of buttons and links in the templates -- they do not enforce access control on their own. Typically you'll set the UI permissions to match the view permissions, but you can separate them if needed (e.g., show a "log in to edit" button to anonymous users).

## Configuration

### Content & storage

| Key | Default | Description |
|-----|---------|-------------|
| `WIKI_HOME` | `'home'` | Default page for `/` |
| `WIKI_URL_PREFIX` | `'/help'` | URL prefix for the wiki blueprint |
| `WIKI_CONTENT_DIR` | `'./data'` | Directory for Markdown files |
| `WIKI_UPLOAD_FOLDER` | `'./data/files'` | Directory for uploaded images |
| `WIKI_ALLOWED_EXTENSIONS` | `{'png','jpg','jpeg','gif','svg'}` | Allowed upload types |
| `WIKI_INDEX_DIR` | `'./index'` | Whoosh search index directory |

### Templates

All templates can be overridden by setting these config values to your own template paths:

| Key | Default |
|-----|---------|
| `WIKI_BASE_TEMPLATE` | `'wiki/base.html'` |
| `WIKI_PAGE_TEMPLATE` | `'wiki/page.html'` |
| `WIKI_EDITOR_TEMPLATE` | `'wiki/editor.html'` |
| `WIKI_SEARCH_TEMPLATE` | `'wiki/search.html'` |
| `WIKI_FILES_TEMPLATE` | `'wiki/files.html'` |
| `WIKI_NOT_FOUND_TEMPLATE` | `'wiki/404.html'` |
| `WIKI_FORBIDDEN_TEMPLATE` | `'wiki/403.html'` |

### Internationalization

| Key | Default | Description |
|-----|---------|-------------|
| `WIKI_CURRENT_LANGUAGE` | `lambda: 'en'` | Callable returning the current language code |
| `WIKI_LANGUAGES` | `{'en': 'English', 'fr': 'French', 'de': 'German', 'it': 'Italian'}` | Available languages |

Pages can have per-language variants using filename suffixes: `page_fr.md`, `page_de.md`, etc. The wiki automatically loads the correct variant based on `WIKI_CURRENT_LANGUAGE`.

### Markdown

| Key | Default | Description |
|-----|---------|-------------|
| `WIKI_MARKDOWN_EXTENSIONS` | `{'codehilite', 'fenced_code'}` | Additional Python-Markdown extensions |

The extensions `toc`, `meta`, `tables`, and a built-in Bootstrap extension are always loaded.

## Development

### Requirements

- Python >=3.10,<3.15
- [uv](https://docs.astral.sh/uv/)

### Setup

```bash
git clone <repo-url>
cd flask-wiki
uv sync --frozen
```

### Run the example app

```bash
cd examples
uv run flask flask_wiki init-index
uv run flask flask_wiki index
uv run flask run --debug
# Visit http://localhost:5000/help
```

### Run tests

```bash
uv run poe run_tests
```

## License

BSD 3-Clause. See [LICENSE](LICENSE) for details.
