# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: BSD-3-Clause

"""Tests for flask_wiki.views (routes and HTTP behavior)."""

import io
import os
import re
from html.parser import HTMLParser
from pathlib import Path

from tests.conftest import TINY_PNG

# Attribute carrying the resource URL, per tag that loads one.
RESOURCE_ATTRIBUTES = {"img": "src", "script": "src", "source": "src", "link": "href"}


class AssetCollector(HTMLParser):
    """Collect the URLs a page loads resources from."""

    def __init__(self):
        """Initialize the collected URL list."""
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        """Record the resource URL carried by the tag, if any."""
        attrs = dict(attrs)
        if tag == "link" and "stylesheet" not in attrs.get("rel", ""):
            return
        if url := attrs.get(RESOURCE_ATTRIBUTES.get(tag, "")):
            self.urls.append(url)


def asset_urls(html):
    """Return the CSS, JavaScript and image URLs referenced by the HTML."""
    collector = AssetCollector()
    collector.feed(html)
    return collector.urls


def test_index_redirect(client):
    """Test that / redirects to the home page."""
    res = client.get("/help/")
    assert res.status_code == 302
    assert "/help/home/" in res.headers["Location"]


def test_page_display(client):
    """Test displaying an existing page."""
    res = client.get("/help/home/")
    assert res.status_code == 200
    assert b"Home" in res.data


def test_page_not_found(client):
    """Test that a missing page returns 404."""
    res = client.get("/help/nonexistent/")
    assert res.status_code == 404


def test_edit_page_get(client):
    """Test GET on the edit page shows the form."""
    res = client.get("/help/edit/home/")
    assert res.status_code == 200
    assert b"title" in res.data
    assert b"body" in res.data


def test_edit_page_language(client):
    """Test that the editor tells which language variant is being edited."""
    res = client.get("/help/edit/home/")
    assert b"Editing in English" in res.data
    # the language being edited is not offered by the "Edit in" dropdown
    assert b"/help/edit/home_en/" not in res.data
    assert b"/help/edit/home_fr/" in res.data

    # a URL carrying a language code is edited in that language
    res = client.get("/help/edit/home_fr/")
    assert b"Editing in French" in res.data
    assert b"/help/edit/home_fr/" not in res.data
    assert b"/help/edit/home_en/" in res.data


def test_edit_page_post(client, app):
    """Test POST to edit a page updates it."""
    # Capture original page content before modifying
    original_path = os.path.join(app.config["WIKI_CONTENT_DIR"], "home_en.md")
    with open(original_path) as f:
        original_content = f.read()

    try:
        res = client.post(
            "/help/edit/home/",
            data={"title": "Home Updated", "body": "# Updated\n\nNew content.", "tags": "updated"},
            follow_redirects=True,
        )
        assert res.status_code == 200
        assert b"Updated" in res.data
    finally:
        # Restore original content
        with open(original_path, "w") as f:
            f.write(original_content)


def test_create_new_page(client, app):
    """Test creating a new page via POST."""
    path = os.path.join(app.config["WIKI_CONTENT_DIR"], "brandnew_en.md")
    try:
        res = client.post(
            "/help/edit/brandnew/",
            data={"title": "Brand New", "body": "# Brand New\n\nCreated via test.", "tags": "new"},
            follow_redirects=True,
        )
        assert res.status_code == 200
        assert b"Brand New" in res.data

        # A page is never saved without a language code
        assert not os.path.isfile(os.path.join(app.config["WIKI_CONTENT_DIR"], "brandnew.md"))

        # Verify page is accessible
        res = client.get("/help/brandnew/")
        assert res.status_code == 200
    finally:
        if os.path.isfile(path):
            os.remove(path)


def test_delete_page(client, app):
    """Test deleting a page."""
    # Create a page first
    client.post(
        "/help/edit/todelete/",
        data={"title": "To Delete", "body": "# Delete Me\n\nTemporary.", "tags": ""},
    )

    res = client.get("/help/page/delete/todelete", follow_redirects=True)
    assert res.status_code == 200

    # Page should be gone
    path = os.path.join(app.config["WIKI_CONTENT_DIR"], "todelete_en.md")
    assert not os.path.isfile(path)


def test_page_fallback_banner(client, app):
    """Test that a page served in a fallback language displays a banner."""
    banner = b"does not exist yet in your language"

    # the page exists in english, the current language
    res = client.get("/help/sample/")
    assert banner not in res.data

    try:
        app.config["WIKI_CURRENT_LANGUAGE"] = lambda: "it"
        res = client.get("/help/sample/")
        assert res.status_code == 200
        assert banner in res.data

        # a legacy page is not in the reader's language either
        res = client.get("/help/legacy_page/")
        assert res.status_code == 200
        assert banner in res.data
    finally:
        app.config["WIKI_CURRENT_LANGUAGE"] = lambda: "en"


def test_edit_legacy_page(client, app):
    """Test that editing a legacy page writes a language variant and leaves it alone."""
    content_dir = app.config["WIKI_CONTENT_DIR"]
    legacy_path = os.path.join(content_dir, "legacy_page.md")
    variant_path = os.path.join(content_dir, "legacy_page_en.md")
    with open(legacy_path) as f:
        original_content = f.read()

    try:
        res = client.post(
            "/help/edit/legacy_page/",
            data={"title": "Legacy Page", "body": "# Legacy\n\nEdited.", "tags": "legacy"},
            follow_redirects=True,
        )
        assert res.status_code == 200
        assert os.path.isfile(variant_path)

        # the legacy page is read-only
        with open(legacy_path) as f:
            assert f.read() == original_content
    finally:
        if os.path.isfile(variant_path):
            os.remove(variant_path)


def test_preview(client):
    """Test the preview endpoint returns rendered HTML."""
    res = client.post("/help/preview/", data={"body": "title: T\n\n# Hello\n\n**Bold**"})
    assert res.status_code == 200
    assert b"<h1" in res.data
    assert b"<strong>Bold</strong>" in res.data


def test_search_route(client):
    """Test the search endpoint."""
    res = client.get("/help/search?q=Welcome")
    assert res.status_code == 200


def test_files_page(client):
    """Test the files management page loads."""
    res = client.get("/help/files")
    assert res.status_code == 200


def test_file_upload_and_delete(client, app):
    """Test uploading a valid file and then deleting it."""
    data = {"file": (io.BytesIO(TINY_PNG), "upload_test.png")}
    res = client.post("/help/files", data=data, content_type="multipart/form-data", follow_redirects=True)
    assert res.status_code == 200

    # File should exist on disk
    upload_path = os.path.join(app.config["WIKI_UPLOAD_FOLDER"], "upload_test.png")
    assert os.path.isfile(upload_path)

    # Delete it
    res = client.get("/help/file/delete/upload_test.png", follow_redirects=True)
    assert res.status_code == 200
    assert not os.path.isfile(upload_path)


def test_file_upload_invalid_extension(client, app):
    """Test that uploading a disallowed file type is rejected."""
    data = {"file": (io.BytesIO(b"not a real exe"), "malware.exe")}
    res = client.post("/help/files", data=data, content_type="multipart/form-data", follow_redirects=True)
    assert res.status_code == 200

    # File should NOT exist
    upload_path = os.path.join(app.config["WIKI_UPLOAD_FOLDER"], "malware.exe")
    assert not os.path.isfile(upload_path)


def test_permissions_read_denied(app):
    """Test that read permission denial returns 403."""
    try:
        app.config["WIKI_READ_VIEW_PERMISSION"] = lambda: False
        with app.test_client() as c:
            res = c.get("/help/home/")
            assert res.status_code == 403
    finally:
        app.config["WIKI_READ_VIEW_PERMISSION"] = lambda: True


def test_permissions_edit_denied(app):
    """Test that edit permission denial returns 403."""
    try:
        app.config["WIKI_EDIT_VIEW_PERMISSION"] = lambda: False
        with app.test_client() as c:
            res = c.get("/help/edit/home/")
            assert res.status_code == 403

            res = c.get("/help/page/delete/home")
            assert res.status_code == 403
    finally:
        app.config["WIKI_EDIT_VIEW_PERMISSION"] = lambda: True


def test_pages_do_not_reference_external_assets(client):
    """Test that no page pulls an asset from a third-party host."""
    for url in ("/help/home/", "/help/edit/home/", "/help/files", "/help/search?q=home"):
        html = client.get(url).data.decode()
        for asset in asset_urls(html):
            assert not asset.startswith(("http://", "https://", "//")), f"{url}: {asset}"


def test_toasts_are_placed_by_their_own_wrapper(client, app):
    """Test that the toasts are positioned by a wiki class instead of `.toast`.

    Styling the Bootstrap component itself leaks into the host application, which
    places the wiki toasts with its own rules.
    """
    assert 'class="wiki-toasts"' in client.get("/help/home/").data.decode()

    stylesheet = Path(app.blueprints["wiki"].static_folder, "css", "wiki.css")
    css = re.sub(r"/\*.*?\*/", "", stylesheet.read_text(), flags=re.DOTALL)
    selectors = {
        selector.strip() for rule in css.split("}") if "{" in rule for selector in rule.rsplit("{", 1)[0].split(",")
    }
    assert ".wiki-toasts" in selectors
    for selector in selectors:
        assert "toast" not in re.findall(r"\.([-\w]+)", selector), selector


def test_icons_come_from_the_bootstrap_sprite(client):
    """Test that template icons are inline SVG from the Bootstrap Icons sprite."""
    html = client.get("/help/home/").data.decode()
    assert "fa fa-" not in html
    for name in ("search", "clipboard", "pencil"):
        assert f"icons/bootstrap-icons.svg#{name}" in html


def test_icon_template_can_be_swapped(app):
    """Test that WIKI_ICON_TEMPLATE selects the markup used for template icons."""
    try:
        app.config["WIKI_ICON_TEMPLATE"] = "wiki/icons/fontawesome.html"
        with app.test_client() as c:
            page = c.get("/help/home/").data.decode()
            editor = c.get("/help/edit/home/").data.decode()
        assert "bootstrap-icons.svg#" not in page
        for name in ("magnifying-glass", "clipboard", "pencil"):
            assert f'<i class="fa-solid fa-{name}"></i>' in page
        for name in ("floppy-disk", "language", "trash"):
            assert f'<i class="fa-solid fa-{name}"></i>' in editor
    finally:
        app.config["WIKI_ICON_TEMPLATE"] = "wiki/icons/bootstrap.html"


def test_icon_only_buttons_have_an_accessible_name(client, app):
    """Test that buttons rendered as a bare icon carry an aria-label."""
    assert 'aria-label="Search"' in client.get("/help/home/").data.decode()

    data = {"file": (io.BytesIO(TINY_PNG), "aria_test.png")}
    client.post("/help/files", data=data, content_type="multipart/form-data", follow_redirects=True)
    try:
        html = client.get("/help/files").data.decode()
        assert 'aria-label="Copy Markdown code"' in html
        assert 'aria-label="Delete file"' in html
    finally:
        client.get("/help/file/delete/aria_test.png", follow_redirects=True)
