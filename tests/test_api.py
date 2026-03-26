# This file is part of Flask-Wiki
# Copyright (C) 2025 RERO
#
# Flask-Wiki is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Tests for flask_wiki.api (Processor, Page, WikiBase)."""

import os

import pytest
from werkzeug.exceptions import NotFound

from flask_wiki.api import Page, Processor, WikiBase


def test_processor_render(app):
    """Test that Processor converts markdown to HTML with metadata."""
    with app.test_request_context():
        text = "title: Test\ntags: a, b\n\n# Hello\n\nSome **bold** text."
        processor = Processor(text)
        html, _body, meta, _toc = processor.process()

        assert "<h1" in html
        assert "<strong>bold</strong>" in html
        assert meta["title"] == "Test"
        assert meta["tags"] == "a, b"


def test_processor_toc(app):
    """Test that Processor generates a table of contents."""
    with app.test_request_context():
        text = "title: T\n\n## Section One\n\n## Section Two"
        processor = Processor(text)
        _html, _body, _meta, toc = processor.process()

        assert toc  # truthy when there are headings
        toc_html = toc.__html__()
        assert "Section One" in toc_html
        assert "Section Two" in toc_html


def test_processor_fenced_code(app):
    """Test that fenced code blocks are rendered."""
    with app.test_request_context():
        text = "title: T\n\n```python\nprint('hello')\n```"
        processor = Processor(text)
        html, _body, _meta, _toc = processor.process()

        assert "<code" in html
        assert "print" in html


def test_processor_table_bootstrap(app):
    """Test that tables get Bootstrap classes."""
    with app.test_request_context():
        text = "title: T\n\n| A | B |\n|---|---|\n| 1 | 2 |"
        processor = Processor(text)
        html, _body, _meta, _toc = processor.process()

        assert "table-striped" in html


def test_page_load_and_render(app):
    """Test loading and rendering a page from disk."""
    with app.test_request_context():
        path = os.path.join(app.config["WIKI_CONTENT_DIR"], "home.md")
        page = Page(path, "home")

        assert page.title == "Home"
        assert "welcome" in page.tags
        assert "<h1" in page.html
        assert page.raw_body  # non-empty text


def test_page_save(app):
    """Test saving a new page and reading it back."""
    with app.test_request_context():
        content_dir = app.config["WIKI_CONTENT_DIR"]
        path = os.path.join(content_dir, "newpage.md")

        try:
            # Create and save
            page = Page(path, "newpage", new=True)
            page["title"] = "New Page"
            page["tags"] = "new"
            page.body = "# New\n\nFresh content."
            page.save()

            # Verify file exists
            assert os.path.isfile(path)

            # Read it back
            page2 = Page(path, "newpage")
            assert page2.title == "New Page"
            assert "Fresh content" in page2.raw_body
        finally:
            if os.path.isfile(path):
                os.remove(path)


def test_page_language_variant(app):
    """Test that language-specific files are loaded when available."""
    with app.test_request_context():
        content_dir = app.config["WIKI_CONTENT_DIR"]
        original_language = app.config.get("WIKI_CURRENT_LANGUAGE")

        try:
            # With language set to "fr", should load sample_fr.md
            app.config["WIKI_CURRENT_LANGUAGE"] = lambda: "fr"
            wiki = WikiBase(content_dir)
            page = wiki.get("sample")
            assert page is not None
            assert page.title == "Page Exemple"

            # Reset to "en", should load sample.md (no sample_en.md exists)
            app.config["WIKI_CURRENT_LANGUAGE"] = lambda: "en"
            wiki = WikiBase(content_dir)
            page = wiki.get("sample")
            assert page is not None
            assert page.title == "Sample Page"
        finally:
            if original_language is not None:
                app.config["WIKI_CURRENT_LANGUAGE"] = original_language


def test_wiki_list_pages(wiki):
    """Test listing all pages."""
    pages = wiki.list_pages()
    titles = [p.title for p in pages]

    assert "Home" in titles
    assert "Sample Page" in titles
    assert len(pages) >= 2


def test_wiki_get_or_404(app):
    """Test get_or_404 for existing and missing pages."""
    with app.test_request_context():
        wiki = WikiBase(app.config["WIKI_CONTENT_DIR"])

        # Existing page
        page = wiki.get_or_404("home")
        assert page.title == "Home"

        # Missing page
        with pytest.raises(NotFound):
            wiki.get_or_404("does_not_exist")


def test_wiki_get_bare(wiki):
    """Test get_bare returns a new Page for non-existing URLs."""
    page = wiki.get_bare("brand_new_page")
    assert isinstance(page, Page)
    assert page.url == "brand_new_page"

    # For existing pages, get_bare returns False
    result = wiki.get_bare("home")
    assert result is False


def test_wiki_delete(app):
    """Test deleting a page removes the file."""
    with app.test_request_context():
        content_dir = app.config["WIKI_CONTENT_DIR"]
        wiki = WikiBase(content_dir)

        # Create a page to delete
        path = os.path.join(content_dir, "to_delete.md")
        try:
            page = Page(path, "to_delete", new=True)
            page["title"] = "Delete Me"
            page["tags"] = ""
            page.body = "# Delete\n\nTemporary."
            page.save()
            assert os.path.isfile(path)

            # Delete it
            result = wiki.delete("to_delete")
            assert result is True
            assert not os.path.isfile(path)

            # Deleting again returns False
            result = wiki.delete("to_delete")
            assert result is False
        finally:
            if os.path.isfile(path):
                os.remove(path)


def test_wiki_move(app):
    """Test moving/renaming a page."""
    with app.test_request_context():
        content_dir = app.config["WIKI_CONTENT_DIR"]
        wiki = WikiBase(content_dir)

        src_path = os.path.join(content_dir, "moveme.md")
        dst_path = os.path.join(content_dir, "moved.md")
        try:
            # Create a page to move
            page = Page(src_path, "moveme", new=True)
            page["title"] = "Move Me"
            page["tags"] = ""
            page.body = "# Move\n\nContent."
            page.save()

            # Move it
            wiki.move("moveme", "moved")
            assert not os.path.isfile(src_path)
            assert os.path.isfile(dst_path)
        finally:
            for p in (src_path, dst_path):
                if os.path.isfile(p):
                    os.remove(p)


def test_wiki_move_path_traversal(app):
    """Test that path traversal is blocked in move."""
    with app.test_request_context():
        content_dir = app.config["WIKI_CONTENT_DIR"]
        wiki = WikiBase(content_dir)

        src_path = os.path.join(content_dir, "safe.md")
        try:
            # Create a source page
            page = Page(src_path, "safe", new=True)
            page["title"] = "Safe"
            page["tags"] = ""
            page.body = "# Safe\n\nContent."
            page.save()

            with pytest.raises(RuntimeError, match="outside content directory"):
                wiki.move("safe", "../../../etc/evil")
        finally:
            if os.path.isfile(src_path):
                os.remove(src_path)


def test_wiki_get_tags(wiki):
    """Test retrieving all tags across pages."""
    tags = wiki.get_tags()
    assert "test" in tags
    assert "welcome" in tags


def test_wiki_list_tagged_pages(wiki):
    """Test filtering pages by tag."""
    pages = wiki.list_tagged_pages("test")
    titles = [p.title for p in pages]
    assert "Sample Page" in titles


def test_wiki_search(app):
    """Test full-text search via Whoosh."""
    from whoosh import index

    with app.test_request_context():
        wiki = WikiBase(app.config["WIKI_CONTENT_DIR"])
        ix = index.open_dir(app.config["WIKI_INDEX_DIR"])
        with ix.searcher() as searcher:
            # Search for a word in the home page
            results = wiki.search("Welcome", ix, searcher)
            assert len(results) > 0

            # Search for something that doesn't exist
            results = wiki.search("xyznonexistent", ix, searcher)
            assert len(results) == 0
