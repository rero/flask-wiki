# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: BSD-3-Clause

"""This extension create a wiki from a tree directory."""

import re

from werkzeug.middleware.shared_data import SharedDataMiddleware

from . import config
from .views import blueprint

# a variable part of a URL rule: <name>, <converter:name> or <converter(arg):name>
VARIABLE_PART = re.compile(r"/?<(?:[^<>:]+:)?([^<>:]+)>")


class Wiki:
    """Flask extension that registers the wiki blueprint and middleware."""

    def __init__(self, app=None):
        """Initialize the extension, optionally binding it to an application.

        :param app: Flask application instance, or None for deferred initialization
        """
        self.app = app
        self.prefix_variables = []
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        prefix = app.config["WIKI_URL_PREFIX"]
        self.prefix_variables = VARIABLE_PART.findall(prefix)
        # the uploaded files hang from the static part of the prefix: a WSGI
        # mount point carries no variable, and neither does the URL of an image
        # written in a page
        files_prefix = VARIABLE_PART.sub("", prefix)
        app.register_blueprint(blueprint, url_prefix=prefix)
        app.add_url_rule(
            f"{files_prefix}/files/<filename>",
            "uploaded_files",
            build_only=True,
        )

        app.wsgi_app = SharedDataMiddleware(
            app.wsgi_app,
            {f"{files_prefix}/files": app.config["WIKI_UPLOAD_FOLDER"]},
        )
        app.extensions["flask-wiki"] = self

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith("WIKI_"):
                app.config.setdefault(k, getattr(config, k))
