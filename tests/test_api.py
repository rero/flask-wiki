# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: BSD-3-Clause

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


def test_processor_figure(app):
    """Test that a titled image standing alone in its paragraph becomes a figure."""
    with app.test_request_context():
        text = 'title: T\n\n![Alt text](image.png "A caption")'
        processor = Processor(text)
        html, _body, _meta, _toc = processor.process()

        assert "<figure>" in html
        assert "<figcaption>A caption</figcaption>" in html
        # the figure is a block of its own, not nested in a paragraph
        assert "<p>" not in html
        # the alt text keeps describing the image, the title is consumed
        assert 'alt="Alt text"' in html
        assert "title=" not in html


def test_processor_image_left_alone(app):
    """Test that an image is only made a figure when it can be a captioned block."""
    with app.test_request_context():
        # without a title there is nothing to caption the image with
        html, _body, _meta, _toc = Processor("title: T\n\n![Alt text](image.png)").process()
        assert "<figure>" not in html

        # an image inside a sentence stays inline, a figure being a block
        text = 'title: T\n\nSee ![Alt text](image.png "A caption") here.'
        html, _body, _meta, _toc = Processor(text).process()
        assert "<figure>" not in html
        assert 'title="A caption"' in html


def test_page_load_and_render(app):
    """Test loading and rendering a page from disk."""
    with app.test_request_context():
        path = os.path.join(app.config["WIKI_CONTENT_DIR"], "home_en.md")
        page = Page(path, "home")

        assert page.title == "Home"
        assert "welcome" in page.tags
        assert "<h1" in page.html
        assert page.raw_body  # non-empty text


def test_page_save(app):
    """Test saving a new page and reading it back."""
    with app.test_request_context():
        content_dir = app.config["WIKI_CONTENT_DIR"]
        path = os.path.join(content_dir, "newpage_en.md")

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

            # Reset to "en", should load sample_en.md
            app.config["WIKI_CURRENT_LANGUAGE"] = lambda: "en"
            wiki = WikiBase(content_dir)
            page = wiki.get("sample")
            assert page is not None
            assert page.title == "Sample Page"
        finally:
            if original_language is not None:
                app.config["WIKI_CURRENT_LANGUAGE"] = original_language


def test_wiki_get_fallback_cascade(app):
    """Test that a page missing in the current language follows the fallback cascade."""
    with app.test_request_context():
        content_dir = app.config["WIKI_CONTENT_DIR"]
        original_language = app.config["WIKI_CURRENT_LANGUAGE"]

        try:
            app.config["WIKI_CURRENT_LANGUAGE"] = lambda: "it"
            wiki = WikiBase(content_dir)

            # first fallback language: sample is translated in english
            page = wiki.get("sample")
            assert page.title == "Sample Page"
            assert page.fallback_language == "en"

            # second fallback language: translated only exists in french
            page = wiki.get("translated")
            assert page.title == "Page Traduite"
            assert page.fallback_language == "fr"

            # writing must never target another language variant
            assert wiki.get("translated", fallback=False) is None
        finally:
            app.config["WIKI_CURRENT_LANGUAGE"] = original_language


def test_wiki_get_explicit_language(app):
    """Test that a URL carrying a language code is never served in another language."""
    with app.test_request_context():
        content_dir = app.config["WIKI_CONTENT_DIR"]
        original_language = app.config["WIKI_CURRENT_LANGUAGE"]

        try:
            app.config["WIKI_CURRENT_LANGUAGE"] = lambda: "it"
            wiki = WikiBase(content_dir)

            page = wiki.get("sample_fr")
            assert page.title == "Page Exemple"
            assert page.fallback_language is None

            assert wiki.get("translated_it") is None
        finally:
            app.config["WIKI_CURRENT_LANGUAGE"] = original_language


def test_wiki_get_legacy_page(wiki, app):
    """Test that a page without a language code is served as a last resort."""
    original_language = app.config["WIKI_CURRENT_LANGUAGE"]
    page = wiki.get("legacy_page")
    assert page.title == "Legacy Page"
    assert page.fallback_language is None

    try:
        # served in the language it is assumed to be in, not in the reader's one
        app.config["WIKI_CURRENT_LANGUAGE"] = lambda: "it"
        page = wiki.get("legacy_page")
        assert page.fallback_language == "en"
    finally:
        app.config["WIKI_CURRENT_LANGUAGE"] = original_language


def test_wiki_fallback_languages_default(app):
    """Test that the fallback cascade defaults to the configured languages."""
    with app.test_request_context():
        wiki = WikiBase(app.config["WIKI_CONTENT_DIR"])
        original_fallback = app.config["WIKI_FALLBACK_LANGUAGES"]

        try:
            # left unset, the cascade covers the languages of this wiki, not the
            # ones of the default configuration
            app.config["WIKI_FALLBACK_LANGUAGES"] = None
            assert wiki.fallback_languages == list(app.config["WIKI_LANGUAGES"])

            # an empty list disables the cascade
            app.config["WIKI_FALLBACK_LANGUAGES"] = []
            assert wiki.get("translated") is None
        finally:
            app.config["WIKI_FALLBACK_LANGUAGES"] = original_fallback


def test_page_language(app):
    """Test the language a page has been saved in."""
    with app.test_request_context():
        content_dir = app.config["WIKI_CONTENT_DIR"]

        page = Page(os.path.join(content_dir, "sample_fr.md"), "sample_fr")
        assert page.language == "fr"

        # a legacy page falls back to the first configured language, even when
        # its name contains an underscore
        page = Page(os.path.join(content_dir, "legacy_page.md"), "legacy_page")
        assert page.language == "en"


def test_wiki_list_pages(wiki):
    """Test listing all pages."""
    pages = wiki.list_pages()
    titles = [p.title for p in pages]

    assert "Home" in titles
    assert "Sample Page" in titles
    assert len(pages) >= 2


def test_wiki_list_pages_one_per_language(wiki):
    """Test that each page is listed once, in the current language."""
    titles = [p.title for p in wiki.list_pages()]

    assert "Sample Page" in titles
    assert "Page Exemple" not in titles  # french variant of the same page
    assert "Page Traduite" in titles  # only translated in french
    assert "Legacy Page" in titles


def test_wiki_list_all_pages(wiki):
    """Test that every language variant is listed for indexing."""
    titles = [p.title for p in wiki.list_all_pages()]

    assert "Sample Page" in titles
    assert "Page Exemple" in titles


def test_wiki_list_all_pages_cleaned_url(wiki):
    """Test that a file whose name the URL cleaner rewrites is still listed."""
    # the double space is collapsed by clean_url, so the URL of this file cannot
    # be turned back into the path it was built from
    path = os.path.join(wiki.root, "odd  name_en.md")
    with open(path, "w") as f:
        f.write("title: Odd Name\n\nBody.\n")

    try:
        assert "Odd Name" in [p.title for p in wiki.list_all_pages()]
    finally:
        os.remove(path)


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
    # a new page is always created with a language code
    assert os.path.basename(page.path) == "brand_new_page_en.md"

    # For existing pages, get_bare returns False
    result = wiki.get_bare("home")
    assert result is False


def test_wiki_delete(app):
    """Test deleting a page removes the file."""
    with app.test_request_context():
        content_dir = app.config["WIKI_CONTENT_DIR"]
        wiki = WikiBase(content_dir)

        # Create a page to delete
        path = os.path.join(content_dir, "to_delete_en.md")
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

        src_path = os.path.join(content_dir, "moveme_en.md")
        dst_path = os.path.join(content_dir, "moved_en.md")
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


def test_wiki_move_legacy_page(app):
    """Test moving a page saved without a language code."""
    with app.test_request_context():
        content_dir = app.config["WIKI_CONTENT_DIR"]
        wiki = WikiBase(content_dir)

        src_path = os.path.join(content_dir, "legacy_moveme.md")
        dst_path = os.path.join(content_dir, "legacy_moved_en.md")
        try:
            with open(src_path, "w") as f:
                f.write("title: Move Me\n\n# Move\n\nContent.")

            # the legacy page becomes the current language variant
            wiki.move("legacy_moveme", "legacy_moved")
            assert not os.path.isfile(src_path)
            assert os.path.isfile(dst_path)
        finally:
            for path in (src_path, dst_path):
                if os.path.isfile(path):
                    os.remove(path)


def test_wiki_move_path_traversal(app):
    """Test that path traversal is blocked in move."""
    with app.test_request_context():
        content_dir = app.config["WIKI_CONTENT_DIR"]
        wiki = WikiBase(content_dir)

        src_path = os.path.join(content_dir, "safe_en.md")
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


def test_wiki_get_by_title(wiki):
    """Test retrieving a page by its title."""
    assert wiki.get_by_title("Sample Page").url == "sample"
    assert wiki.get_by_title("No Such Page") is None


def test_wiki_index_by(wiki):
    """Test grouping the pages by the value of one of their attributes."""
    grouped = wiki.index_by("title")
    assert [page.url for page in grouped["Sample Page"]] == ["sample"]


def test_wiki_list_tagged_pages(wiki):
    """Test filtering pages by tag."""
    pages = wiki.list_tagged_pages("test")
    titles = [p.title for p in pages]
    assert "Sample Page" in titles


def test_wiki_list_tagged_pages_matches_a_whole_tag(wiki):
    """Test that a tag matches a whole tag, never a fragment of one."""
    # 'welcome' is a tag of the home page, 'come' is only a fragment of it
    assert [page.url for page in wiki.list_tagged_pages("welcome")] == ["home"]
    assert wiki.list_tagged_pages("come") == []

    # a tag written after a comma and a space is matched all the same
    assert "Sample Page" in [page.title for page in wiki.list_tagged_pages("example")]


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

            # A page matching in several languages is returned once, in the
            # current language
            titles = [hit["title"] for hit in wiki.search("test", ix, searcher)]
            assert "Sample Page" in titles
            assert "Page Exemple" not in titles


def test_wiki_search_every_match(app):
    """Test that every matching page is returned, not only the first ones scored."""
    from whoosh import index

    with app.test_request_context():
        content_dir = app.config["WIKI_CONTENT_DIR"]
        wiki = WikiBase(content_dir)
        # more pages than the number of results whoosh scores by default
        slugs = [f"scored{i}" for i in range(11)]

        try:
            for slug in slugs:
                page = Page(os.path.join(content_dir, f"{slug}_en.md"), slug, new=True)
                page["title"] = f"Scored {slug}"
                page.body = "xyzscoredterm"
                page.save()

            ix = index.open_dir(app.config["WIKI_INDEX_DIR"])
            with ix.searcher() as searcher:
                results = wiki.search("xyzscoredterm", ix, searcher)

            assert len(results) == len(slugs)
        finally:
            for slug in slugs:
                wiki.delete(slug)
