# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: BSD-3-Clause

"""Core classes."""

import os
from collections import OrderedDict
from datetime import datetime
from pathlib import Path

import markdown
from bs4 import BeautifulSoup
from flask import abort, current_app, g
from werkzeug.local import LocalProxy
from whoosh import index, qparser
from whoosh.analysis import LanguageAnalyzer
from whoosh.fields import ID, TEXT, Schema
from whoosh.writing import AsyncWriter

from .markdown_ext import BootstrapExtension
from .utils import clean_url, wikilink


class Processor:
    """Processing file content into metadata and rendering.

    The processor handles the processing of file content intometadata and
    markdown and takes care of the rendering. It also offers some helper
    methods that can be used for various cases.
    """

    def __init__(self, text):
        """Initialize the processor.

        :param str text: the text to process
        """
        markdown_ext = current_app.config["WIKI_MARKDOWN_EXTENSIONS"]

        self.preprocessors = []
        self.postprocessors = [wikilink]

        self.md = markdown.Markdown(
            extensions={
                BootstrapExtension(),
                "codehilite",
                "fenced_code",
                "toc",
                "meta",
                "tables",
            }.union(markdown_ext)
        )

        self.input = text
        self.markdown = None
        self.meta_raw = None

        self.pre = None
        self.html = None
        self.final = None
        self.meta = None
        self.toc = None

    def process_pre(self):
        """Content preprocessor."""
        current = self.input
        for processor in self.preprocessors:
            current = processor(current)
        self.pre = current

    def process_markdown(self):
        """Convert to HTML."""
        self.html = self.md.convert(self.pre)
        self.toc = self.md.toc

    def split_raw(self):
        """Split text into raw meta and content."""
        self.meta_raw, self.markdown = self.pre.split("\n\n", 1)

    def process_meta(self):
        """Get metadata.

        .. warning:: Can only be called after :meta:`html` was
        called.
        """
        # the markdown meta plugin does not retain the order of the
        # entries, so we have to loop over the meta values a second
        # time to put them into a dictionary in the correct order
        self.meta = OrderedDict()
        for line in self.meta_raw.split("\n"):
            key = line.split(":", 1)[0]
            # markdown metadata always returns a list of lines, we will
            # reverse that here
            self.meta[key.lower()] = "\n".join(self.md.Meta[key.lower()])

    def process_post(self):
        """Content postprocessor."""
        current = self.html
        for processor in self.postprocessors:
            current = processor(current)
        self.final = current

    def process(self):
        """Run the full processing suite.

        Runs the full suite of processing on the given text, all
        pre and post processing, markdown rendering and meta data
        handling.
        """
        self.process_pre()
        self.process_markdown()
        self.split_raw()
        self.process_meta()
        self.process_post()

        return self.final, self.markdown, self.meta, TOC(self.toc, self.md.toc_tokens)


class TOC:
    """Table of contents."""

    def __init__(self, toc, tokens=None):
        """Initialize the table of contents."""
        if tokens is None:
            tokens = []
        self._toc = toc
        self.tokens = tokens

    def __bool__(self):
        """Return True if the table of contents has at least one section."""
        return bool(self.tokens)

    def __html__(self):
        """Return the HTML string for use in Jinja2 templates."""
        return self._toc


class Page:
    """A page of the wiki."""

    def __init__(self, path, url, *, new=False):
        """Initialize a wiki page.

        :param path: filesystem path to the page file
        :param str url: URL slug identifying the page
        :param bool new: if True, skip loading and rendering (page does not exist yet)
        """
        self.path = path
        self.url = url
        self._meta = OrderedDict()
        self.toc = None
        if not new:
            self.load()
            self.render()

    def __repr__(self):
        """Return a developer-readable string representation."""
        return f"<Page: {self.url}@{self.path}>"

    def load(self):
        """Load a page."""
        with Path(self.path).open(encoding="utf-8") as f:
            self.content = f.read()

    def render(self):
        """Process and render a page."""
        processor = Processor(self.content)
        self._html, self.body, self._meta, self.toc = processor.process()

        # Get creation and update times from file
        stat = Path(self.path).stat()
        self.creation_datetime = datetime.fromtimestamp(stat.st_ctime)  # noqa: DTZ006
        self.modification_datetime = datetime.fromtimestamp(stat.st_mtime)  # noqa: DTZ006

    def index(self):
        """Index page data for whoosh search engine."""
        index_dir = index.open_dir(current_app.config.get("WIKI_INDEX_DIR"))
        writer = AsyncWriter(index_dir)
        writer.update_document(
            url=self.url,
            title=self.title,
            body=self.raw_body,
            tags=self.tags,
            language=self.language,
        )
        writer.commit()

    def save(self, *, update=True):
        """Save a page to disk and update the search index.

        :param bool update: if True, reload and re-render the page after saving
        """
        folder = Path(self.path).parent
        if not folder.exists():
            folder.mkdir(parents=True)
        with Path(self.path).open("w", encoding="utf-8") as f:
            for key, value in self._meta.items():
                line = f"{key}: {value}\n"
                f.write(line)
            f.write("\n")
            f.write(self.body.replace("\r\n", "\n"))
        self.index()
        if update:
            self.load()
            self.render()

    @property
    def meta(self):
        """Return the page metadata as an ordered dictionary."""
        return self._meta

    def __getitem__(self, name):
        """Return the metadata value for the given key.

        :param str name: metadata key
        :raises KeyError: if the key does not exist
        """
        return self._meta[name]

    def __setitem__(self, name, value):
        """Set a metadata value.

        :param str name: metadata key
        :param str value: metadata value
        """
        self._meta[name] = value

    @property
    def html(self):
        """Return the rendered HTML of the page body."""
        return self._html

    def __html__(self):
        """Return the rendered HTML for use in Jinja2 templates."""
        return self.html

    @property
    def title(self):
        """Return page title."""
        try:
            return self["title"]
        except KeyError:
            return self.url

    @title.setter
    def title(self, value):
        self["title"] = value

    @property
    def tags(self):
        """Return page tags."""
        try:
            return self["tags"]
        except KeyError:
            return ""

    @tags.setter
    def tags(self, value):
        self["tags"] = value

    @property
    def raw_body(self):
        """Return raw text of the body.

        Returns the raw text of the body without markdown or html markup,
        used for indexing and search results display.
        """
        html = markdown.markdown(self.body)
        html = BeautifulSoup(html, "html.parser")
        return html.get_text(separator=" ")

    @raw_body.setter
    def raw_body(self, value):
        self["raw_body"] = value

    @property
    def language(self):
        """Return page language.

        Returns the language in which a page has been saved
        or returns default wiki language if page doesn't have a language.
        """
        filename = Path(self.path).stem
        return filename.split("_")[-1] if "_" in filename else next(iter(current_wiki.languages.keys()))


class WikiBase:
    """Utility class for wiki management methods."""

    def __init__(self, root):
        """Initialize the wiki.

        :param str root: filesystem path to the wiki content directory
        """
        self.root = root

    def path(self, url):
        """Return the filesystem path for a given page URL.

        :param str url: the page URL slug
        :returns: path to the corresponding .md file
        :rtype: pathlib.Path
        """
        return Path(self.root) / f"{url}.md"

    def ln_path(self, url):
        """Return the language-specific filesystem path for a given page URL.

        :param str url: the page URL slug
        :returns: path to the language-variant .md file
        :rtype: pathlib.Path
        """
        return Path(self.root) / f"{url}_{self.current_language}.md"

    def exists(self, url):
        """Return True if a page with the given URL exists on disk.

        :param str url: the page URL slug
        :rtype: bool
        """
        return self.path(url).exists()

    def get(self, url):
        """Return the page for the given URL, preferring a language variant if available.

        Returns the language-specific file (e.g. ``page_fr.md``) when it exists,
        otherwise falls back to the base file (e.g. ``page.md``).
        Returns None if neither file exists.

        :param str url: the page URL slug
        :returns: the page instance, or None if not found
        :rtype: Page or None
        """
        path = self.ln_path(url)
        if path.is_file():
            return Page(path, url)
        path = self.path(url)
        return Page(path, url) if path.is_file() else None

    def get_or_404(self, url):
        """Return the page for the given URL, or abort with a 404 error.

        :param str url: the page URL slug
        :returns: the page instance
        :rtype: Page
        """
        if page := self.get(url):
            return page
        abort(404)
        return None

    def get_bare(self, url):
        """Return a new, unsaved Page for a URL that does not yet exist.

        Returns False if the URL already exists on disk.

        :param str url: the page URL slug
        :returns: a new Page instance, or False if the page already exists
        :rtype: Page or bool
        """
        path = self.path(url)
        return False if self.exists(url) else Page(path, url, new=True)

    def move(self, url, newurl):
        """Rename a page from one URL to another.

        Creates any intermediate folders as needed. Raises RuntimeError if
        the target path would escape the content directory.

        :param str url: current URL slug of the page
        :param str newurl: new URL slug for the page
        :raises RuntimeError: if the target path escapes the content directory
        """
        source = Path(self.root) / f"{url}.md"
        target = Path(self.root) / f"{newurl}.md"
        # resolve root to normalize any '../' in the configured path
        root = Path(self.root).resolve()
        # ensure target does not escape the root directory (path traversal guard)
        # is_relative_to() checks path components, unlike the string-prefix approach
        if not target.resolve().is_relative_to(root):
            msg = f"Possible write attempt outside content directory: {newurl}"
            raise RuntimeError(msg)
        # create folder if it does not exist yet
        folder = target.parent
        if not folder.exists():
            folder.mkdir(parents=True)
        source.rename(target)

    def delete(self, url):
        """Delete a page and remove it from the search index.

        :param str url: URL slug of the page to delete
        :returns: True if deleted, False if the page did not exist
        :rtype: bool
        """
        path = self.path(url)
        if not self.exists(url):
            return False
        path.unlink()
        index_dir = index.open_dir(current_app.config.get("WIKI_INDEX_DIR"))
        writer = AsyncWriter(index_dir)
        writer.delete_by_term("url", url)
        writer.commit()
        return True

    def init_search_index(self):
        """Create a new whoosh search index for the wiki."""
        index_dir = current_app.config.get("WIKI_INDEX_DIR")
        # initialize whoosh index schema
        schema = Schema(
            url=ID(stored=True, unique=True),
            title=TEXT(stored=True, analyzer=LanguageAnalyzer("fr")),
            tags=TEXT(stored=True),
            body=TEXT(stored=True, analyzer=LanguageAnalyzer("fr")),
            language=ID(stored=True),
        )
        index_path = Path(index_dir)
        if not index_path.exists():
            index_path.mkdir()
        index.create_in(index_dir, schema)

    def search(self, query, ix, searcher):
        """Search the whoosh index for a given query.

        :param str query: the search query
        :param whoosh.index ix: the whoosh index to use
        :param whoosh.searcher searcher: an active whoosh searcher instance

        :returns: a whoosh.results object instance
        """
        # parse the query to search all fields present in the schema
        fields = ix.schema.names()
        query_parser = qparser.MultifieldParser(fields, schema=ix.schema, group=qparser.OrGroup)
        parsed_query = query_parser.parse(query)
        # return a whoosh Results object to treat results
        results = searcher.search(parsed_query)
        # set highlights fragment size to 50 words
        results.fragmenter.surround = 50
        # set highlights separator for display
        results.formatter.between = "<strong> [...] </strong>"
        # return the modified Results object
        return results

    def list_pages(self):
        """Build up a list of all the available pages.

        :returns: a list of all the wiki pages
        :rtype: list
        """
        # make sure we always have the absolute path for fixing the
        # walk path
        pages = []
        root = Path(self.root).resolve()
        for cur_dir, _, files in os.walk(root):
            cur_dir_path = Path(cur_dir)
            for cur_file in files:
                if cur_file.endswith(".md"):
                    path = cur_dir_path / cur_file
                    url = clean_url(str(cur_dir_path.relative_to(root) / cur_file[:-3]))
                    page = Page(path, url)
                    pages.append(page)
        return sorted(pages, key=lambda x: x.title.lower())

    def index_all_pages(self):
        """Index all the pages for the current wiki."""
        for page in self.list_pages():
            Page.index(page)

    def index_by(self, key):
        """Get an index based on the given key.

        Will use the metadata value of the given key to group
        the existing pages.

        :param str key: the attribute to group the index on.

        :returns: Will return a dictionary where each entry holds
            a list of pages that share the given attribute.
        :rtype: dict
        """
        pages = {}
        for page in self.index():
            value = getattr(page, key)
            pre = pages.get(value, [])
            pages[value] = pre.append(page)
        return pages

    def get_by_title(self, title):
        """Get all page titles."""
        pages = self.list_pages(attr="title")
        return pages.get(title)

    def get_tags(self):
        """Get all tags."""
        pages = self.list_pages()
        tags = {}
        for page in pages:
            pagetags = page.tags.split(",")
            for tag in pagetags:
                tag = tag.strip()  # noqa: PLW2901
                if tag == "":
                    continue
                if tags.get(tag):
                    tags[tag].append(page)
                else:
                    tags[tag] = [page]
        return tags

    def list_tagged_pages(self, tag):
        """Get a list of all pages that have a tag."""
        pages = self.list_pages()
        tagged = [page for page in pages if tag in page.tags]
        return sorted(tagged, key=lambda x: x.title.lower())

    @property
    def current_language(self):
        """Return the current language code from the application configuration."""
        return current_app.config.get("WIKI_CURRENT_LANGUAGE")()

    @property
    def languages(self):
        """Return the configured language mapping (code to display name)."""
        return current_app.config.get("WIKI_LANGUAGES")


def get_wiki():
    """Return the wiki instance for the current request context, creating it if needed."""
    wiki = getattr(g, "_wiki", None)
    if wiki is None:
        wiki = g._wiki = WikiBase(current_app.config["WIKI_CONTENT_DIR"])  # noqa: SLF001
    return wiki


current_wiki = LocalProxy(get_wiki)
