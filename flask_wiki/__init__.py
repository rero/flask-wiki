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
        # the prefix stripped of its variable parts: the uploaded files hang from
        # it, as a WSGI mount point carries no variable, and neither does the URL
        # of an image written in a page
        static_prefix = VARIABLE_PART.sub("", prefix)
        app.register_blueprint(blueprint, url_prefix=prefix)
        self.init_prefix_defaults(app)
        app.add_url_rule(
            f"{static_prefix}/files/<filename>",
            "uploaded_files",
            build_only=True,
        )

        app.wsgi_app = SharedDataMiddleware(
            app.wsgi_app,
            {f"{static_prefix}/files": app.config["WIKI_UPLOAD_FOLDER"]},
        )
        app.extensions["flask-wiki"] = self

    def init_prefix_defaults(self, app):
        """Serve the default value of a prefix variable without it in the URL.

        ``WIKI_URL_PREFIX_DEFAULTS`` gives the value each variable of the prefix
        takes when a reader leaves it out. Registering every rule a second time
        under the prefix stripped of these variables, holding their values as
        Werkzeug defaults, is all it takes for the short URL to be served, to be
        the one the wiki builds for those values, and to receive a redirect from
        the spelled-out one. A variable the key does not name keeps its part of the
        prefix, as a rule still needs a value for it, and a value naming no
        variable of the prefix is dropped, as no rule would take it.

        :param app: Flask application instance
        """
        prefix = app.config["WIKI_URL_PREFIX"]
        defaults = {
            name: value
            for name, value in app.config["WIKI_URL_PREFIX_DEFAULTS"].items()
            if name in self.prefix_variables
        }
        if not defaults:
            return
        stripped = VARIABLE_PART.sub(lambda part: "" if part[1] in defaults else part[0], prefix)
        for rule in list(app.url_map.iter_rules()):
            if rule.endpoint.startswith(f"{blueprint.name}."):
                app.add_url_rule(
                    rule.rule.replace(prefix, stripped, 1),
                    endpoint=rule.endpoint,
                    view_func=app.view_functions[rule.endpoint],
                    defaults=defaults,
                    # Flask puts HEAD and OPTIONS back, as it did for the copied rule
                    methods=rule.methods - {"HEAD", "OPTIONS"},
                )

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith("WIKI_"):
                app.config.setdefault(k, getattr(config, k))
