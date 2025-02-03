# -*- coding: utf-8 -*-
#
# This file is part of Flask-Wiki
# Copyright (C) 2023 RERO
#
# Flask-Wiki is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Views to respond to HTTP requests."""

import glob
import os
from functools import wraps

from babel import Locale
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_babel import gettext as _
from werkzeug.utils import secure_filename
from whoosh import index as whoosh_index

from .api import Processor, current_wiki, get_wiki
from .forms import EditorForm

blueprint = Blueprint(
    "wiki", __name__, template_folder="templates", static_folder="static"
)


# PERMISSIONS
# ===========
def can_read_permission(func):
    """Check Reading Permission."""

    @wraps(func)
    def decorated_view(*args, **kwargs):
        permission = current_app.config.get("WIKI_READ_VIEW_PERMISSION")()
        if isinstance(permission, bool):
            if not permission:
                abort(403)
            return func(*args, **kwargs)
        return permission

    return decorated_view


def can_edit_permission(func):
    """Check Edition Permission."""

    @wraps(func)
    def decorated_view(*args, **kwargs):
        permission = current_app.config.get("WIKI_EDIT_VIEW_PERMISSION")()
        if isinstance(permission, bool):
            if not permission:
                abort(403)
            return func(*args, **kwargs)
        return permission

    return decorated_view


# FILTERS
# =======
@blueprint.app_template_filter()
def prune_url(path):
    """."""
    return path.replace(current_app.config.get("WIKI_URL_PREFIX"), "").strip("/")


@blueprint.app_template_filter()
def translate_ln(ln):
    """."""
    return Locale(current_wiki.current_language).languages.get(ln)


@blueprint.app_template_filter()
def edit_path_list(path):
    """."""
    ln = path.split("_")[-1]
    base_path = path
    if ln in current_wiki.languages:
        base_path = path.rsplit("_", 1)[0]
    return list(
        filter(
            lambda v: v["path"] != path,
            [
                dict(ln=ln, path="_".join((base_path, ln)))
                for ln in current_wiki.languages
            ],
        )
    )


@blueprint.app_template_filter()
def date_format(value, format=None):
    """."""
    return value.strftime("%d-%m-%Y")


# PROCESSORS
# ==========
@blueprint.context_processor
def permission_processor():
    """."""
    return dict(
        can_edit_wiki=current_app.config.get("WIKI_EDIT_UI_PERMISSION")(),
        can_read_wiki=current_app.config.get("WIKI_READ_UI_PERMISSION")(),
    )


# MISCS
# =====
@blueprint.before_request
def setWiki():
    """."""
    get_wiki()


def allowed_file(filename):
    """."""
    ALLOWED_EXTENSIONS = current_app.config.get("WIKI_ALLOWED_EXTENSIONS")
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ROUTES
# ======
@blueprint.route("/")
@can_read_permission
def index():
    """."""
    return redirect(url_for("wiki.page", url=current_app.config.get("WIKI_HOME")))


@blueprint.route("/<path:url>/")
@can_read_permission
def page(url):
    """."""
    page = current_wiki.get_or_404(url)
    return render_template(current_app.config.get("WIKI_PAGE_TEMPLATE"), page=page)


@blueprint.route("/edit/<path:url>/", methods=["GET", "POST"])
@can_edit_permission
def edit(url):
    """."""
    page = current_wiki.get(url)
    form = EditorForm(obj=page)
    if form.validate_on_submit():
        if not page:
            page = current_wiki.get_bare(url)
        form.populate_obj(page)
        page.save()
        flash(_("Saved"), category="success")
        return redirect(url_for("wiki.page", url=url))
    return render_template(
        current_app.config.get("WIKI_EDITOR_TEMPLATE"), form=form, page=page, path=url
    )


@blueprint.route("/preview/", methods=["POST"])
@can_edit_permission
def preview():
    """."""
    data = {}
    processor = Processor(request.form["body"])
    data["html"], data["body"], data["meta"], data["toc"] = processor.process()
    return data["html"]


@blueprint.route("/page/delete/<path:url>")
@can_edit_permission
def delete_page(url):
    """."""
    if current_wiki.delete(url):
        flash(_("Page deleted"), category="success")
    else:
        flash(_("Could not delete page as it does not exist."), category="error")
    return redirect(url_for("wiki.index"))


@blueprint.route("/file/delete/<path:filename>")
@can_edit_permission
def delete_file(filename):
    """."""
    path = os.path.join(current_app.config.get("WIKI_UPLOAD_FOLDER"), filename)
    try:
        os.remove(path)
        flash(_("File deleted"), category="success")
    except Exception as e:
        flash(
            _(f"Something went wrong. Could not delete file. Error: {e}"),
            category="error",
        )
    return redirect(url_for("wiki.files"))


@blueprint.route("/files", methods=["GET", "POST"])
@can_edit_permission
def files():
    """."""
    if request.method == "POST" and current_app.config["WIKI_EDIT_UI_PERMISSION"]():
        # check if the post request has the file part
        if "file" not in request.files:
            flash(_("No file part"))
            return redirect(request.url)
        file = request.files["file"]
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == "":
            flash(_("No selected file"))
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            output_filename = os.path.join(
                current_app.config["WIKI_UPLOAD_FOLDER"], filename
            )
            if os.path.isfile(output_filename):
                flash(_("File already exists"), category="danger")
            else:
                file.save(output_filename)
    if request.method == "POST" and not current_app.config["WIKI_EDIT_UI_PERMISSION"]():
        flash(_("You do not have the permission to add files."))
    files = [
        os.path.basename(f)
        for f in sorted(
            glob.glob("/".join([current_app.config.get("WIKI_UPLOAD_FOLDER"), "*"])),
            key=os.path.getmtime,
        )
    ]
    return render_template(current_app.config.get("WIKI_FILES_TEMPLATE"), files=files)


@blueprint.route("/search", methods=["GET"])
def search():
    """."""
    query = request.args.get("q", "")
    with current_app.app_context():
        index_dir = whoosh_index.open_dir(current_app.config.get("WIKI_INDEX_DIR"))
    with index_dir.searcher() as searcher:
        results = current_wiki.search(query, index_dir, searcher)
        return render_template(
            current_app.config.get("WIKI_SEARCH_TEMPLATE"), results=results, query=query
        )


@blueprint.errorhandler(404)
def not_found(error):
    """."""
    return render_template(current_app.config.get("WIKI_NOT_FOUND_TEMPLATE")), 404


@blueprint.errorhandler(403)
def forbidden(error):
    """."""
    return render_template(current_app.config.get("WIKI_FORBIDDEN_TEMPLATE")), 403
