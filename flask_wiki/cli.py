# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: BSD-3-Clause

"""Click command-line interface for flask-wiki."""

import click
from flask import current_app
from flask.cli import with_appcontext

from .api import get_wiki


@click.group()
def flask_wiki():
    """Command-line interface for flask-wiki."""


@flask_wiki.command()
@with_appcontext
def init_index():
    """Init whoosh search index."""
    get_wiki().init_search_index()


@flask_wiki.command()
@with_appcontext
def index():
    """Index all wiki pages for whoosh search."""
    # rendering a page builds the URL of its wikilinks, which needs a request
    with current_app.test_request_context():
        get_wiki().index_all_pages()
