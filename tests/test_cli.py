# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: BSD-3-Clause

"""Tests for flask_wiki.cli (command-line interface)."""

from flask_wiki.cli import index
from tests.conftest import make_app


def test_cli_index(tmp_path_factory):
    """Test that pages are indexed outside of a request."""
    # without a server name, the URL of a wikilink, as held by the home page,
    # can only be built within a request: indexing must not need one
    app = make_app(tmp_path_factory, SERVER_NAME=None)

    result = app.test_cli_runner().invoke(index)

    assert result.exit_code == 0, result.exception
