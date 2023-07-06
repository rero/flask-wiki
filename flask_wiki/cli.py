# -*- coding: utf-8 -*-
#
# This file is part of Flask-Wiki
# Copyright (C) 2023 RERO
#
# Flask-Wiki is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Click command-line interface for flask-wiki."""

import click
from flask.cli import with_appcontext

from .api import get_wiki


@click.group()
def flask_wiki():
    """Command-line interface for flask-wiki."""
    pass


@flask_wiki.command()
@with_appcontext
def init_index():
    """Init whoosh search index."""
    get_wiki().init_search_index()


@flask_wiki.command()
@with_appcontext
def index():
    """Index all wiki pages for whoosh search."""
    get_wiki().index_all_pages()
