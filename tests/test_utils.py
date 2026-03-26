# This file is part of Flask-Wiki
# Copyright (C) 2025 RERO
#
# Flask-Wiki is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Tests for flask_wiki.utils."""

from flask_wiki.utils import clean_url, wikilink


def test_clean_url_normalizes_spaces():
    """Test that multiple spaces are reduced to one."""
    assert clean_url("hello   world") == "hello world"
    assert clean_url("  leading") == "leading"
    assert clean_url("trailing  ") == "trailing"


def test_clean_url_normalizes_backslashes():
    """Test that backslashes are converted to forward slashes."""
    assert clean_url("path\\to\\page") == "path/to/page"
    assert clean_url("path\\\\to") == "path/to"


def test_wikilink_simple(app):
    """Test basic [[Page]] syntax."""
    with app.test_request_context():
        captured = {}

        def url_fmt(endpoint, url):
            captured["endpoint"] = endpoint
            return f"/wiki/{url}"

        result = wikilink("<p>See [[Home]]</p>", url_formatter=url_fmt)
        assert captured["endpoint"] == "wiki.page"
        assert '<a href="/wiki/Home">Home</a>' in result


def test_wikilink_with_display_text(app):
    """Test [[url|Display Text]] syntax."""
    with app.test_request_context():
        captured = {}

        def url_fmt(endpoint, url):
            captured["endpoint"] = endpoint
            return f"/wiki/{url}"

        result = wikilink("<p>See [[path/page|Click Here]]</p>", url_formatter=url_fmt)
        assert captured["endpoint"] == "wiki.page"
        assert '<a href="/wiki/path/page">Click Here</a>' in result


def test_wikilink_inside_code_untouched(app):
    """Test that wikilinks inside <code> blocks are left alone."""
    with app.test_request_context():
        captured = {}

        def url_fmt(endpoint, url):
            captured["endpoint"] = endpoint
            return f"/wiki/{url}"

        text = "<code>[[NotALink]]</code>"
        result = wikilink(text, url_formatter=url_fmt)
        assert "endpoint" not in captured
        assert "[[NotALink]]" in result


def test_wikilink_no_links(app):
    """Test text without wikilinks is returned unchanged."""
    with app.test_request_context():
        captured = {}

        def url_fmt(endpoint, url):
            captured["endpoint"] = endpoint
            return f"/wiki/{url}"

        text = "<p>No links here</p>"
        assert wikilink(text, url_formatter=url_fmt) == text
        assert "endpoint" not in captured
