# Flask-Wiki

## About

Simple file based wiki for Flask.

## Getting started

### Requirements

* Python >=3.8.0,<4.0.0
* [Poetry](https://python-poetry.org/)

### Install dev environment

- Clone the git repository
- run `poetry install`
- `cd examples`, 
- `poetry run flask flask_wiki init-index`
- `poetry run flask flask_wiki index`
- then `poetry run flask run --debug`
- go to http://localhost:5000/help

## Configuration

### Templates

- WIKI_BASE_TEMPLATE = 'wiki/base.html'
- WIKI_SEARCH_TEMPLATE = 'wiki/search.html'
- WIKI_NOT_FOUND_TEMPLATE = 'wiki/404.html'
- WIKI_FORBIDDEN_TEMPLATE = 'wiki/403.html'
- WIKI_EDITOR_TEMPLATE = 'wiki/editor.html'
- WIKI_FILES_TEMPLATE = 'wiki/files.html'
- WIKI_PAGE_TEMPLATE = 'wiki/page.html'

### Miscs

- WIKI_HOME = 'home'
- WIKI_CURRENT_LANGUAGE = lambda: 'en'
- WIKI_LANGUAGES = {'en': 'English', 'fr': 'French', 'de': 'German', 'it': 'Italian'}
- WIKI_URL_PREFIX = '/help'
- WIKI_CONTENT_DIR = './data'
- WIKI_INDEX_DIR = './index'
- WIKI_UPLOAD_FOLDER = os.path.join(WIKI_CONTENT_DIR, 'files')
- WIKI_ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
- WIKI_MARKDOWN_EXTENSIONS = set(('codehilite', 'fenced_code'))

### Permissions

- WIKI_EDIT_VIEW_PERMISSION = lambda: True
- WIKI_READ_VIEW_PERMISSION = lambda: True
- WIKI_EDIT_UI_PERMISSION = WIKI_EDIT_VIEW_PERMISSION
- WIKI_READ_UI_PERMISSION = WIKI_READ_VIEW_PERMISSION
