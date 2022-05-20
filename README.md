# Flask-Wiki

## About

Simple file based wiki for Flask.

## Getting started

### Requirements

* Python >=3.6.2
* [Poetry](https://python-poetry.org/)

### Install

- Clone the git repository
- run `poetry install`
- If you want to enable debug mode, run `export FLASK_ENV=development`
- `cd examples`, then `poetry run flask run`
- go to http://localhost:5000/wiki

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
- WIKI_LANGUAGES = ['en']
- WIKI_URL_PREFIX = '/wiki'
- WIKI_CONTENT_DIR = './data'
- WIKI_UPLOAD_FOLDER = os.path.join(WIKI_CONTENT_DIR, 'files')
- WIKI_ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
- WIKI_MARKDOWN_EXTENSIONS = set(('codehilite', 'fenced_code'))

### Permssions

- WIKI_EDIT_VIEW_PERMISSION = lambda: True
- WIKI_READ_VIEW_PERMISSION = lambda: True
- WIKI_EDIT_UI_PERMISSION = WIKI_EDIT_VIEW_PERMISSION
- WIKI_READ_UI_PERMISSION = WIKI_READ_VIEW_PERMISSION
