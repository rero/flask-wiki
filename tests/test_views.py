# This file is part of Flask-Wiki
# Copyright (C) 2025 RERO
#
# Flask-Wiki is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Tests for flask_wiki.views (routes and HTTP behavior)."""

import io
import os

from tests.conftest import TINY_PNG


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


def test_edit_page_post(client, app):
    """Test POST to edit a page updates it."""
    # Capture original page content before modifying
    original_path = os.path.join(app.config["WIKI_CONTENT_DIR"], "home.md")
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
    path = os.path.join(app.config["WIKI_CONTENT_DIR"], "brandnew.md")
    try:
        res = client.post(
            "/help/edit/brandnew/",
            data={"title": "Brand New", "body": "# Brand New\n\nCreated via test.", "tags": "new"},
            follow_redirects=True,
        )
        assert res.status_code == 200
        assert b"Brand New" in res.data

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
    path = os.path.join(app.config["WIKI_CONTENT_DIR"], "todelete.md")
    assert not os.path.isfile(path)


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
