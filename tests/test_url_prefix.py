# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: BSD-3-Clause

"""Tests for a WIKI_URL_PREFIX carrying a variable part."""

from pathlib import Path
from urllib.parse import urlsplit

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


@pytest.fixture(scope="module")
def default_value_app(tmp_path_factory):
    """Create an application serving one value of the prefix without naming it."""
    return make_app(
        tmp_path_factory,
        WIKI_URL_PREFIX="/<organisation>/help",
        WIKI_URL_PREFIX_DEFAULTS={"organisation": "global"},
        SERVER_NAME=None,
    )


@pytest.fixture(scope="module")
def default_value_client(default_value_app):
    """Create a test client for the application with a default prefix value."""
    return default_value_app.test_client()


def test_the_default_value_is_served_without_the_variable_part(default_value_client):
    """Test that the wiki answers under the prefix stripped of its variable part."""
    assert default_value_client.get("/help/home/").status_code == 200


def test_spelling_out_the_default_value_redirects_to_the_short_url(default_value_client):
    """Test that the URL naming the default value redirects to the one omitting it."""
    response = default_value_client.get("/global/help/home/")

    assert response.status_code == 308
    assert urlsplit(response.location).path == "/help/home/"


def test_urls_omit_the_default_value(default_value_client):
    """Test that the wiki leaves the default value out of every URL it builds."""
    html = default_value_client.get("/help/home/").data.decode()

    assert 'href="/help/"' in html
    assert 'action="/help/search"' in html
    assert 'href="/help/sample/"' in html
    assert "/global/help/" not in html


def test_another_value_keeps_its_variable_part(default_value_client):
    """Test that a value other than the default one stays in the URLs."""
    html = default_value_client.get("/hepvs/help/home/").data.decode()

    assert 'href="/hepvs/help/"' in html
    assert 'href="/hepvs/help/sample/"' in html


def test_urls_built_from_outside_honour_the_default_value(default_value_app):
    """Test that naming the default value from outside the wiki builds the short URL."""
    with default_value_app.test_request_context():
        assert url_for("wiki.index", organisation="global") == "/help/"
        assert url_for("wiki.index", organisation="hepvs") == "/hepvs/help/"


@pytest.fixture(scope="module")
def partial_default_client(tmp_path_factory):
    """Create a test client for a prefix whose second variable has no default."""
    app = make_app(
        tmp_path_factory,
        WIKI_URL_PREFIX="/<organisation>/<section>/help",
        WIKI_URL_PREFIX_DEFAULTS={"organisation": "global"},
        SERVER_NAME=None,
    )
    return app.test_client()


def test_a_variable_without_a_default_keeps_its_part_of_the_prefix(partial_default_client):
    """Test that only the variables named in the defaults leave the URL."""
    assert partial_default_client.get("/staff/help/home/").status_code == 200
    assert partial_default_client.get("/help/home/").status_code == 404

    html = partial_default_client.get("/staff/help/home/").data.decode()

    assert 'href="/staff/help/"' in html
    assert 'href="/staff/help/sample/"' in html


def test_spelling_out_the_default_redirects_beside_a_kept_variable(partial_default_client):
    """Test that the URL naming the default value still redirects to the short one."""
    response = partial_default_client.get("/global/staff/help/home/")

    assert response.status_code == 308
    assert urlsplit(response.location).path == "/staff/help/home/"


def test_a_default_naming_no_variable_of_the_prefix_is_ignored(tmp_path_factory):
    """Test that a default the prefix carries no variable for serves nothing new."""
    client = make_app(
        tmp_path_factory,
        WIKI_URL_PREFIX="/<organisation>/help",
        WIKI_URL_PREFIX_DEFAULTS={"typo": "global"},
        SERVER_NAME=None,
    ).test_client()

    assert client.get("/hepvs/help/home/").status_code == 200
    assert client.get("/help/home/").status_code == 404
