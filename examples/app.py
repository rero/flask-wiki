# -*- coding: utf-8 -*-
# This file is part of Flask-Wiki
# Copyright (C) 2020 RERO
#
# Flask-Wiki is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Simple Testing applications."""

from flask import Flask, current_app, g, redirect, request, session, url_for
from flask_babelex import Babel, Domain
from flask_babelex import gettext as _
from flask_bootstrap import Bootstrap
from pkg_resources import resource_filename

from flask_wiki import Wiki


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        WIKI_CURRENT_LANGUAGE=lambda: session.get('ln', 'fr'),
        WIKI_LANGUAGES=['en', 'fr', 'de', 'it'],
        # BABEL_TRANSLATION_DIRECTORIES = resource_filename('flask_wiki', 'translations'),
        BABEL_DEFAULT_LOCALE='en',
        DEBUG=True
    )
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    Bootstrap(app)
    Wiki(app)
    # use the flask-wiki translations
    domain = Domain(resource_filename('flask_wiki', 'translations'))
    babel = Babel(app, default_domain=domain)

    @babel.localeselector
    def get_locale():
        if 'ln' in session:
            return session['ln']
        ln = request.accept_languages.best_match(
            app.config.get('WIKI_LANGUAGES'))
        return ln

    @app.route('/language/<ln>')
    def change_language(ln):
        session['ln'] = ln
        return redirect(url_for('wiki.index'))
    return app


app = create_app()
