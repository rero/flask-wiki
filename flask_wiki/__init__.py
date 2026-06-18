# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: BSD-3-Clause

"""This extension create a wiki from a tree directory."""

from werkzeug.middleware.shared_data import SharedDataMiddleware

from . import config
from .views import blueprint


class Wiki:
    """Flask extension that registers the wiki blueprint and middleware."""

    def __init__(self, app=None):
        """Initialize the extension, optionally binding it to an application.

        :param app: Flask application instance, or None for deferred initialization
        """
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.register_blueprint(blueprint, url_prefix=app.config.get("WIKI_URL_PREFIX"))
        app.add_url_rule(
            app.config.get("WIKI_URL_PREFIX") + "/files/<filename>",
            "uploaded_files",
            build_only=True,
        )

        app.wsgi_app = SharedDataMiddleware(
            app.wsgi_app,
            {app.config.get("WIKI_URL_PREFIX") + "/files": app.config["WIKI_UPLOAD_FOLDER"]},
        )
        app.extensions["flask-wiki"] = self

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith("WIKI_"):
                app.config.setdefault(k, getattr(config, k))
