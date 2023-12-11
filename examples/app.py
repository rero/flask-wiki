# -*- coding: utf-8 -*-
#
# This file is part of Flask-Wiki
# Copyright (C) 2023 RERO
#
# Flask-Wiki is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Simple Testing applications."""

from flask import Flask, redirect, request, session, url_for
from flask_babel import Babel
from flask_bootstrap import Bootstrap4
from pkg_resources import resource_filename

from flask_wiki import Wiki


def create_app(test_config=None):
    # create and configure the app
    def get_locale():
        if ln := request.args.get('language'):
            session['language'] = ln
        ln = session.get('language', 'en')
        return ln

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        WIKI_CURRENT_LANGUAGE=lambda: session.get('language', app.config.get('BABEL_DEFAULT_LOCALE')),
        WIKI_LANGUAGES={
            'en': 'English',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian'
        },
        BABEL_TRANSLATION_DIRECTORIES=resource_filename(
            'flask_wiki', 'translations'
        ),
        BABEL_DEFAULT_LOCALE='fr',
        DEBUG=True
    )
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    Bootstrap4(app)
    Wiki(app)
    Babel(app, locale_selector=get_locale)

    @app.context_processor
    def inject_conf_var():
        return dict(
            AVAILABLE_LANGUAGES=app.config['WIKI_LANGUAGES'],
            CURRENT_LANGUAGE=session.get(
                'language', request.accept_languages.best_match(
                    app.config['WIKI_LANGUAGES'].keys()
                )
            )
        )

    @app.route('/language/<ln>')
    def change_language(ln=None):
        session['language'] = ln
        return redirect(url_for('wiki.index'))

    return app


app = create_app()
