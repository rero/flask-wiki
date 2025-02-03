# -*- coding: utf-8 -*-
#
# This file is part of Flask-Wiki
# Copyright (C) 2020 RERO
#
# Flask-Wiki is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Default configuration."""

import os

# TEMPLATES
# =========
WIKI_BASE_TEMPLATE = "wiki/base.html"
WIKI_SEARCH_TEMPLATE = "wiki/search.html"
WIKI_NOT_FOUND_TEMPLATE = "wiki/404.html"
WIKI_FORBIDDEN_TEMPLATE = "wiki/403.html"
WIKI_EDITOR_TEMPLATE = "wiki/editor.html"
WIKI_FILES_TEMPLATE = "wiki/files.html"
WIKI_PAGE_TEMPLATE = "wiki/page.html"


# MISCS
# =====
WIKI_HOME = "home"
WIKI_CURRENT_LANGUAGE = lambda: "en"
WIKI_LANGUAGES = {"en": "English", "fr": "French", "de": "German", "it": "Italian"}
WIKI_URL_PREFIX = "/help"
WIKI_CONTENT_DIR = "./data"
WIKI_UPLOAD_FOLDER = os.path.join(WIKI_CONTENT_DIR, "files")
WIKI_INDEX_DIR = "./index"
WIKI_ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "svg"}

"""Markdown Extensions.

See: https://python-markdown.github.io/extensions/ for more details

Already includes:
-  flask.wiki.api.BootstrapExtension
- toc
- meta
- tables
"""
WIKI_MARKDOWN_EXTENSIONS = set(("codehilite", "fenced_code"))

# PERMISSIONS
# ===========
WIKI_EDIT_VIEW_PERMISSION = lambda: True
WIKI_READ_VIEW_PERMISSION = lambda: True
WIKI_EDIT_UI_PERMISSION = WIKI_EDIT_VIEW_PERMISSION
WIKI_READ_UI_PERMISSION = WIKI_READ_VIEW_PERMISSION
