# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: BSD-3-Clause

"""Tests for flask_wiki.cli (command-line interface)."""

from flask_wiki.cli import index


def test_cli_index(app):
    """Test that pages are indexed outside of a request."""
    server_name = app.config["SERVER_NAME"]
    try:
        # without a server name, the URL of a wikilink, as held by the home
        # page, can only be built within a request
        app.config["SERVER_NAME"] = None
        result = app.test_cli_runner().invoke(index)
        assert result.exit_code == 0, result.exception
    finally:
        app.config["SERVER_NAME"] = server_name
