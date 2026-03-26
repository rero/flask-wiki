# This file is part of Flask-Wiki
# Copyright (C) 2025 RERO
#
# Flask-Wiki is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Pytest fixtures for Flask-Wiki tests."""

import os
import shutil

import pytest
from flask import Flask
from flask_babel import Babel
from flask_bootstrap import Bootstrap4

from flask_wiki import Wiki
from flask_wiki.api import WikiBase

TESTDATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Minimal valid 1x1 PNG (67 bytes)
TINY_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
    b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18"
    b"\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)


@pytest.fixture(scope="module")
def app(tmp_path_factory):
    """Create a Flask application for testing."""
    tmp = tmp_path_factory.mktemp("wiki")
    content_dir = tmp / "data"
    content_dir.mkdir()
    upload_dir = content_dir / "files"
    upload_dir.mkdir()
    index_dir = tmp / "index"
    index_dir.mkdir()

    # Copy test data into the temp content dir
    for filename in os.listdir(TESTDATA_DIR):
        src = os.path.join(TESTDATA_DIR, filename)
        if os.path.isfile(src):
            shutil.copy2(src, content_dir / filename)

    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret",
        WTF_CSRF_ENABLED=False,
        WIKI_CONTENT_DIR=str(content_dir),
        WIKI_UPLOAD_FOLDER=str(upload_dir),
        WIKI_INDEX_DIR=str(index_dir),
        WIKI_CURRENT_LANGUAGE=lambda: "en",
        WIKI_LANGUAGES={"en": "English", "fr": "French"},
    )
    app.config["SERVER_NAME"] = "localhost"
    Bootstrap4(app)
    Babel(app, default_locale="en")
    Wiki(app)

    # Register endpoint expected by base template
    @app.route("/language/<ln>")
    def change_language(ln):
        return ""

    # Initialize search index and index test pages
    with app.app_context():
        wiki = WikiBase(str(content_dir))
        wiki.init_search_index()
        wiki.index_all_pages()

    yield app


@pytest.fixture(scope="module")
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture()
def wiki(app):
    """Create a WikiBase instance inside a request context."""
    with app.test_request_context():
        yield WikiBase(app.config["WIKI_CONTENT_DIR"])


@pytest.fixture()
def png_file():
    """Return a minimal valid PNG as bytes."""
    return TINY_PNG
