# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: BSD-3-Clause

"""Views to respond to HTTP requests."""

from functools import wraps
from pathlib import Path

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

blueprint = Blueprint("wiki", __name__, template_folder="templates", static_folder="static")


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
    """Strip the wiki URL prefix and surrounding slashes from a path."""
    return path.replace(current_app.config.get("WIKI_URL_PREFIX"), "").strip("/")


@blueprint.app_template_filter()
def translate_ln(ln):
    """Return the localized display name for a language code."""
    return Locale(current_wiki.current_language).languages.get(ln)


@blueprint.app_template_filter()
def edit_path_list(path):
    """Return language-variant edit paths for a page, excluding the current one.

    :param str path: the current page path (URL slug, possibly with language suffix)
    :returns: list of dicts with ``ln`` and ``path`` keys for each other language variant
    :rtype: list[dict]
    """
    ln = path.split("_")[-1]
    base_path = path
    if ln in current_wiki.languages:
        base_path = path.rsplit("_", 1)[0]
    return list(
        filter(
            lambda v: v["path"] != path,
            [{"ln": ln, "path": f"{base_path}_{ln}"} for ln in current_wiki.languages],
        )
    )


@blueprint.app_template_filter()
def date_format(value):
    """Format a datetime as DD-MM-YYYY."""
    return value.strftime("%d-%m-%Y")


# PROCESSORS
# ==========
@blueprint.context_processor
def permission_processor():
    """Inject wiki edit and read permission flags into all templates."""
    return {
        "can_edit_wiki": current_app.config.get("WIKI_EDIT_UI_PERMISSION")(),
        "can_read_wiki": current_app.config.get("WIKI_READ_UI_PERMISSION")(),
    }


# MISCS
# =====
@blueprint.before_request
def set_wiki():
    """Ensure the wiki instance is initialised for the current request."""
    get_wiki()


def allowed_file(filename):
    """Return True if the filename has an extension allowed by the wiki configuration.

    :param str filename: the filename to check
    :rtype: bool
    """
    allowed_extensions = current_app.config.get("WIKI_ALLOWED_EXTENSIONS")
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


# ROUTES
# ======
@blueprint.route("/")
@can_read_permission
def index():
    """Redirect to the configured wiki home page."""
    return redirect(url_for("wiki.page", url=current_app.config.get("WIKI_HOME")))


@blueprint.route("/<path:url>/")
@can_read_permission
def page(url):
    """Display a wiki page.

    :param str url: URL slug of the page to display
    """
    page = current_wiki.get_or_404(url)
    return render_template(current_app.config.get("WIKI_PAGE_TEMPLATE"), page=page)


@blueprint.route("/edit/<path:url>/", methods=["GET", "POST"])
@can_edit_permission
def edit(url):
    """Display and handle the wiki page editor.

    On GET, renders the editor form pre-filled with existing page content.
    On POST, validates and saves the page, then redirects to the page view.

    :param str url: URL slug of the page to edit or create
    """
    page = current_wiki.get(url)
    form = EditorForm(obj=page)
    if form.validate_on_submit():
        if not page:
            page = current_wiki.get_bare(url)
        form.populate_obj(page)
        page.save()
        flash(_("Saved"), category="success")
        return redirect(url_for("wiki.page", url=url))
    return render_template(current_app.config.get("WIKI_EDITOR_TEMPLATE"), form=form, page=page, path=url)


@blueprint.route("/preview/", methods=["POST"])
@can_edit_permission
def preview():
    """Return rendered HTML for a markdown body submitted via POST."""
    data = {}
    processor = Processor(request.form["body"])
    data["html"], data["body"], data["meta"], data["toc"] = processor.process()
    return data["html"]


@blueprint.route("/page/delete/<path:url>")
@can_edit_permission
def delete_page(url):
    """Delete the wiki page at the given URL and redirect to the index.

    :param str url: URL slug of the page to delete
    """
    if current_wiki.delete(url):
        flash(_("Page deleted"), category="success")
    else:
        flash(_("Could not delete page as it does not exist."), category="error")
    return redirect(url_for("wiki.index"))


@blueprint.route("/file/delete/<path:filename>")
@can_edit_permission
def delete_file(filename):
    """Delete an uploaded file and redirect to the file management page.

    :param str filename: name of the file to delete
    """
    path = Path(current_app.config.get("WIKI_UPLOAD_FOLDER")) / filename
    try:
        path.unlink()
        flash(_("File deleted"), category="success")
    except OSError as e:
        flash(
            _("Something went wrong. Could not delete file. Error: {e}").format(e=e),
            category="error",
        )
    return redirect(url_for("wiki.files"))


@blueprint.route("/files", methods=["GET", "POST"])
@can_edit_permission
def files():
    """Display the file management page and handle file uploads."""
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
            output_filename = Path(current_app.config["WIKI_UPLOAD_FOLDER"]) / filename
            if output_filename.is_file():
                flash(_("File already exists"), category="danger")
            else:
                file.save(output_filename)
    if request.method == "POST" and not current_app.config["WIKI_EDIT_UI_PERMISSION"]():
        flash(_("You do not have the permission to add files."))
    upload_folder = Path(current_app.config.get("WIKI_UPLOAD_FOLDER"))
    files = [p.name for p in sorted(upload_folder.glob("*"), key=lambda p: p.stat().st_mtime)]
    return render_template(current_app.config.get("WIKI_FILES_TEMPLATE"), files=files)


@blueprint.route("/search", methods=["GET"])
def search():
    """Display search results for the given query."""
    query = request.args.get("q", "")
    with current_app.app_context():
        index_dir = whoosh_index.open_dir(current_app.config.get("WIKI_INDEX_DIR"))
    with index_dir.searcher() as searcher:
        results = current_wiki.search(query, index_dir, searcher)
        return render_template(current_app.config.get("WIKI_SEARCH_TEMPLATE"), results=results, query=query)


@blueprint.errorhandler(404)
def not_found(_error):
    """Render the 404 Not Found error page."""
    return render_template(current_app.config.get("WIKI_NOT_FOUND_TEMPLATE")), 404


@blueprint.errorhandler(403)
def forbidden(_error):
    """Render the 403 Forbidden error page."""
    return render_template(current_app.config.get("WIKI_FORBIDDEN_TEMPLATE")), 403
