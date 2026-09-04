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

    def process(self, *, postprocess=True):
        """Run the full processing suite.

        Runs the full suite of processing on the given text, all
        pre and post processing, markdown rendering and meta data
        handling.

        :param bool postprocess: if False, skip the postprocessors. They build
            the URL of the wikilinks, which needs a request; the metadata and
            the raw body, all the search index stores, do not.
        """
        self.process_pre()
        self.process_markdown()
        self.split_raw()
        self.process_meta()
        if postprocess:
            self.process_post()
        else:
            self.final = self.html

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

    def __init__(self, path, url, *, new=False, fallback_language=None, postprocess=True):
        """Initialize a wiki page.

        :param path: filesystem path to the page file
        :param str url: URL slug identifying the page
        :param bool new: if True, skip loading and rendering (page does not exist yet)
        :param str fallback_language: language code of the variant served when the
            page does not exist in the current language, None otherwise
        :param bool postprocess: if False, render without the postprocessors. Use it
            outside a request, where the URL of a wikilink cannot be built.
        """
        self.path = path
        self.url = url
        self.fallback_language = fallback_language
        self._meta = OrderedDict()
        self.toc = None
        if not new:
            self.load()
            self.render(postprocess=postprocess)

    def __repr__(self):
        """Return a developer-readable string representation."""
        return f"<Page: {self.url}@{self.path}>"

    def load(self):
        """Load a page."""
        with Path(self.path).open(encoding="utf-8") as f:
            self.content = f.read()

    def render(self, *, postprocess=True):
        """Process and render a page.

        :param bool postprocess: if False, skip the postprocessors of the markdown
        """
        processor = Processor(self.content)
        self._html, self.body, self._meta, self.toc = processor.process(postprocess=postprocess)

        # Get creation and update times from file
        stat = Path(self.path).stat()
        self.creation_datetime = datetime.fromtimestamp(stat.st_ctime)  # noqa: DTZ006
        self.modification_datetime = datetime.fromtimestamp(stat.st_mtime)  # noqa: DTZ006

    def index(self):
        """Index page data for whoosh search engine."""
        index_dir = index.open_dir(current_app.config.get("WIKI_INDEX_DIR"))
        writer = AsyncWriter(index_dir)
        writer.update_document(
            url=current_wiki.url_of(self.path),
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
    def tag_list(self):
        """Return the page tags as a list, blank entries left out.

        :rtype: list
        """
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]

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

        Returns the language code carried by the file name, or the first
        configured language for a legacy file that does not carry one.
        """
        _, language = current_wiki.split_url(Path(self.path).stem)
        return language or next(iter(current_wiki.languages))


class WikiBase:
    """Utility class for wiki management methods."""

    def __init__(self, root):
        """Initialize the wiki.

        :param str root: filesystem path to the wiki content directory
        """
        self.root = root

    def split_url(self, url):
        """Split a page URL into its slug and its language code.

        The language code is None when the URL does not carry a configured one,
        as for a legacy page saved before language codes became mandatory.

        :param str url: the page URL slug, with or without a language code
        :returns: the slug and the language code
        :rtype: tuple
        """
        slug, _, language = url.rpartition("_")
        return (slug, language) if slug and language in self.languages else (url, None)

    def ln_url(self, url, language=None):
        """Return the page URL carrying a language code.

        The language code already carried by the URL wins over the given one,
        which defaults to the current language.

        :param str url: the page URL slug, with or without a language code
        :param str language: the language code to add, defaults to the current one
        :rtype: str
        """
        slug, url_language = self.split_url(url)
        return f"{slug}_{url_language or language or self.current_language}"

    def path(self, url, language=None):
        """Return the filesystem path for a given page URL.

        Every page belongs to a language, so the language code is added to URLs
        that do not carry one: ``page`` becomes ``page_en.md``.

        :param str url: the page URL slug, with or without a language code
        :param str language: the language code, defaults to the current language
        :returns: path to the corresponding .md file
        :rtype: pathlib.Path
        """
        return Path(self.root) / f"{self.ln_url(url, language)}.md"

    def legacy_path(self, url):
        """Return the filesystem path of a page saved without a language code.

        Such pages are only kept readable for wikis created before language codes
        became mandatory, they are never written to.

        :param str url: the page URL slug
        :rtype: pathlib.Path
        """
        return Path(self.root) / f"{url}.md"

    def url_of(self, path):
        """Return the page URL of a page file.

        The URL is the path of the file relative to the content directory,
        without its extension, and is the identifier used by the search index.

        :param path: filesystem path to a page file
        :rtype: str
        """
        relative = Path(path).resolve().relative_to(Path(self.root).resolve())
        return clean_url(str(relative.with_suffix("")))

    def exists(self, url):
        """Return True if a page with the given URL exists on disk.

        :param str url: the page URL slug
        :rtype: bool
        """
        return self.path(url).exists()

    def get(self, url, *, fallback=True):
        """Return the page for the given URL, in the current language if available.

        Looks for the current language variant (e.g. ``page_it.md``), then, unless
        ``fallback`` is False, for each language of ``WIKI_FALLBACK_LANGUAGES`` in
        turn (e.g. ``page_en.md``, then ``page_fr.md``). A URL that carries its own
        language code is never served in another language. A legacy page without a
        language code (e.g. ``page.md``) is used as a last resort, as a fallback in
        the language it is assumed to be in.

        :param str url: the page URL slug, with or without a language code
        :param bool fallback: if False, skip the fallback languages. Use it when the
            page is meant to be written to, as saving a page served in another
            language would overwrite that language variant.
        :returns: the page instance, or None if not found
        :rtype: Page or None
        """
        path = self.path(url)
        if path.is_file():
            return Page(path, url)
        if fallback and not self.split_url(url)[1]:
            for language in self.fallback_languages:
                if language == self.current_language:
                    continue
                path = self.path(url, language)
                if path.is_file():
                    return Page(path, url, fallback_language=language)
        path = self.legacy_path(url)
        if not path.is_file():
            return None
        page = Page(path, url)
        # a legacy page carries no language code, it is assumed to be written in
        # the first configured language
        if page.language != self.current_language:
            page.fallback_language = page.language
        return page

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

        Renames the current language variant, or the legacy page without a language
        code when there is no such variant, in which case the page is renamed to the
        current language variant. Creates any intermediate folders as needed. Raises
        RuntimeError if the target path would escape the content directory.

        :param str url: current URL slug of the page
        :param str newurl: new URL slug for the page
        :raises RuntimeError: if the target path escapes the content directory
        """
        source = self.path(url)
        if not source.is_file():
            source = self.legacy_path(url)
        target = self.path(newurl)
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

        Deletes the current language variant of the page, or the legacy page
        without a language code when there is no such variant.

        :param str url: URL slug of the page to delete
        :returns: True if deleted, False if the page did not exist
        :rtype: bool
        """
        path = self.path(url)
        if not path.is_file():
            path = self.legacy_path(url)
        if not path.is_file():
            return False
        path.unlink()
        index_dir = index.open_dir(current_app.config.get("WIKI_INDEX_DIR"))
        writer = AsyncWriter(index_dir)
        writer.delete_by_term("url", self.url_of(path))
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

        A page matching in several languages is returned once, in the current
        language when it matches, otherwise in the first language of the fallback
        cascade that matches. Every match is returned, as the search page lists
        them all rather than paginating them.

        :param str query: the search query
        :param whoosh.index ix: the whoosh index to use
        :param whoosh.searcher searcher: an active whoosh searcher instance

        :returns: a list of whoosh.searching.Hit instances
        """
        # parse the query to search all fields present in the schema
        fields = ix.schema.names()
        query_parser = qparser.MultifieldParser(fields, schema=ix.schema, group=qparser.OrGroup)
        parsed_query = query_parser.parse(query)
        # score every match: the whoosh default only scores the first ten, which
        # the language variants collapsed below would shrink further
        results = searcher.search(parsed_query, limit=None)
        # set highlights fragment size to 50 words
        results.fragmenter.surround = 50
        # set highlights separator for display
        results.formatter.between = "<strong> [...] </strong>"
        # keep the best language variant of each page, in relevance order
        languages = [self.current_language, *self.fallback_languages]
        hits = {}
        for hit in results:
            slug, language = self.split_url(hit["url"])
            rank = languages.index(language) if language in languages else len(languages)
            if slug not in hits or rank < hits[slug][0]:
                hits[slug] = (rank, hit)
        return [hit for _, hit in hits.values()]

    def list_files(self):
        """Build up a list of every page file, language variants included.

        The URL is carried along the path it was built from, as :meth:`url_of`
        cleans it and is therefore not reversible.

        :returns: a list of (path, URL) pairs, each URL carrying its language code
            except for legacy pages saved before language codes became mandatory
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
                    pages.append((path, self.url_of(path)))
        return pages

    def list_all_pages(self):
        """Build up a list of all the pages, one per file, language variants included.

        The pages are rendered without the postprocessors, so their ``html`` carries
        no wikilink: they are meant for indexing, not for display.

        :returns: a list of all the wiki pages
        :rtype: list
        """
        pages = [Page(path, url, postprocess=False) for path, url in self.list_files()]
        return sorted(pages, key=lambda x: x.title.lower())

    def list_pages(self):
        """Build up a list of all the available pages, one per page slug.

        Each page is listed in the current language, or in the first language of
        the fallback cascade it has been translated into.

        :returns: a list of all the wiki pages
        :rtype: list
        """
        slugs = {self.split_url(url)[0] for _, url in self.list_files()}
        pages = [page for page in map(self.get, slugs) if page]
        return sorted(pages, key=lambda x: x.title.lower())

    def index_all_pages(self):
        """Index all the pages for the current wiki."""
        for page in self.list_all_pages():
            page.index()

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
        for page in self.list_pages():
            pages.setdefault(getattr(page, key), []).append(page)
        return pages

    def get_by_title(self, title):
        """Get the page carrying the given title, None if no page does.

        :param str title: the title to look for
        :rtype: Page
        """
        return next((page for page in self.list_pages() if page.title == title), None)

    def get_tags(self):
        """Get all tags."""
        tags = {}
        for page in self.list_pages():
            for tag in page.tag_list:
                tags.setdefault(tag, []).append(page)
        return tags

    def list_tagged_pages(self, tag):
        """Get a list of all pages that carry the given tag."""
        tagged = [page for page in self.list_pages() if tag in page.tag_list]
        return sorted(tagged, key=lambda x: x.title.lower())

    @property
    def current_language(self):
        """Return the current language code from the application configuration."""
        return current_app.config.get("WIKI_CURRENT_LANGUAGE")()

    @property
    def fallback_languages(self):
        """Return the language codes tried, in order, when a page has no current variant.

        Defaults to every configured language when ``WIKI_FALLBACK_LANGUAGES`` is
        left unset; an empty list disables the cascade.
        """
        languages = current_app.config.get("WIKI_FALLBACK_LANGUAGES")
        return list(self.languages) if languages is None else languages

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
