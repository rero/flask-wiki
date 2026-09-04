# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: BSD-3-Clause

"""Tests for a WIKI_URL_PREFIX carrying a variable part."""

from pathlib import Path

import pytest
from flask import url_for

from tests.conftest import TINY_PNG, make_app


@pytest.fixture(scope="module")
def prefixed_app(tmp_path_factory):
    """Create an application serving the wiki under a variable URL prefix."""
    # no server name: answer on any host, as an application serving a section
    # on a domain of its own
    return make_app(tmp_path_factory, WIKI_URL_PREFIX="/<organisation>/help", SERVER_NAME=None)


@pytest.fixture(scope="module")
def prefixed_client(prefixed_app):
    """Create a test client for the application with a variable prefix."""
    return prefixed_app.test_client()


def test_pages_are_served_under_the_prefix(prefixed_client):
    """Test that the wiki answers under the variable prefix, and only there."""
    assert prefixed_client.get("/hepvs/help/home/").status_code == 200
    assert prefixed_client.get("/help/home/").status_code == 404


def test_urls_keep_the_prefix_they_were_reached_through(prefixed_client):
    """Test that every URL the wiki builds carries the variable part back."""
    html = prefixed_client.get("/hepvs/help/home/").data.decode()

    # the links of the templates, built with url_for
    assert 'href="/hepvs/help/"' in html
    assert 'action="/hepvs/help/search"' in html
    assert 'href="/hepvs/help/edit/home/"' in html

    # and the wikilinks of the page body, built with url_for as well
    assert 'href="/hepvs/help/sample/"' in html
    assert "/help/sample/" not in html.replace("/hepvs/help/sample/", "")


def test_the_404_page_offers_to_create_under_the_prefix(prefixed_client):
    """Test that the link of the 404 page stays inside the prefix it was reached through."""
    response = prefixed_client.get("/hepvs/help/missing/")

    assert response.status_code == 404
    assert 'href="/hepvs/help/edit/missing/"' in response.data.decode()


def test_uploaded_files_hang_from_a_static_path(prefixed_app, prefixed_client):
    """Test that the uploaded files are served outside the variable part.

    A WSGI mount point carries no variable, and neither does the URL of an
    image written in a page.
    """
    Path(prefixed_app.config["WIKI_UPLOAD_FOLDER"], "prefix_test.png").write_bytes(TINY_PNG)

    with prefixed_app.test_request_context():
        assert url_for("uploaded_files", filename="prefix_test.png") == "/help/files/prefix_test.png"

    assert prefixed_client.get("/help/files/prefix_test.png").status_code == 200


def test_each_host_keeps_its_own_prefix(prefixed_client):
    """Test that a section served on a domain of its own stays on it.

    The wiki builds relative URLs, so a reader keeps both the host and the
    prefix they came through, and two portals of the same application never
    send their readers to each other.
    """
    first = prefixed_client.get("/hepvs/help/home/", base_url="https://first.example.org").data.decode()
    second = prefixed_client.get("/de/help/home/", base_url="https://second.example.org").data.decode()

    assert 'href="/hepvs/help/sample/"' in first
    assert 'href="/de/help/sample/"' in second

    # neither page names a host, so no portal ever sends its readers to the other
    for html in (first, second):
        assert "first.example.org" not in html
        assert "second.example.org" not in html
