# -*- coding: utf-8 -*-
#
# This file is part of Flask-Wiki
# Copyright (C) 2023 RERO
#
# Flask-Wiki is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Core classes."""

import os
import re
from collections import OrderedDict
from datetime import datetime
from io import open
from pathlib import Path

import markdown
from flask import abort, current_app, g
from werkzeug.local import LocalProxy

from .markdown_ext import BootstrapExtension
from .utils import clean_url, wikilink


class Processor(object):
    """Processing file content into metadata and rendering.

    The processor handles the processing of file content intometadata and
    markdown and takes care of the rendering. It also offers some helper
    methods that can be used for various cases.
    """

    preprocessors = []
    postprocessors = [wikilink]

    def __init__(self, text):
        """Initialize the processor.

        :param str text: the text to process
        """
        markdown_ext = current_app.config['WIKI_MARKDOWN_EXTENSIONS']

        self.md = markdown.Markdown(extensions={
            BootstrapExtension(),
            'codehilite', 'fenced_code', 'toc', 'meta', 'tables'
            }.union(markdown_ext))

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
        self.meta_raw, self.markdown = self.pre.split('\n\n', 1)

    def process_meta(self):
        """Get metadata.

        .. warning:: Can only be called after :meta:`html` was
        called.
        """
        # the markdown meta plugin does not retain the order of the
        # entries, so we have to loop over the meta values a second
        # time to put them into a dictionary in the correct order
        self.meta = OrderedDict()
        for line in self.meta_raw.split('\n'):
            key = line.split(':', 1)[0]
            # markdown metadata always returns a list of lines, we will
            # reverse that here
            self.meta[key.lower()] = \
                '\n'.join(self.md.Meta[key.lower()])

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

        return self.final, self.markdown, self.meta, TOC(
            self.toc, self.md.toc_tokens
            )


class TOC(object):
    """Table of contents."""

    def __init__(self, toc, tokens=None):
        """Initialize the table of contents."""
        if tokens is None:
            tokens = []
        self._toc = toc
        self.tokens = tokens

    def __bool__(self):
        """."""
        return bool(self.tokens)

    def __html__(self):
        """."""
        return self._toc


class Page(object):
    """A page of the wiki."""

    def __init__(self, path, url, new=False):
        """."""
        self.path = path
        self.url = url
        self._meta = OrderedDict()
        self.toc = None
        if not new:
            self.load()
            self.render()

    def __repr__(self):
        """."""
        return f"<Page: {self.url}@{self.path}>"

    def load(self):
        """Load a page."""
        with open(self.path, 'r', encoding='utf-8') as f:
            self.content = f.read()

    def render(self):
        """Process and render a page."""
        processor = Processor(self.content)
        self._html, self.body, self._meta, self.toc = processor.process()

        # Get creation and update times from file
        self.creation_datetime = datetime.fromtimestamp(
            os.path.getctime(self.path))
        self.modification_datetime = datetime.fromtimestamp(
            os.path.getmtime(self.path))

    def save(self, update=True):
        """Save a page."""
        folder = os.path.dirname(self.path)
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(self.path, 'w', encoding='utf-8') as f:
            for key, value in self._meta.items():
                line = u'%s: %s\n' % (key, value)
                f.write(line)
            f.write(u'\n')
            f.write(self.body.replace(u'\r\n', u'\n'))
        if update:
            self.load()
            self.render()

    @property
    def meta(self):
        """."""
        return self._meta

    def __getitem__(self, name):
        """."""
        return self._meta[name]

    def __setitem__(self, name, value):
        """."""
        self._meta[name] = value

    @property
    def html(self):
        """."""
        return self._html

    def __html__(self):
        """."""
        return self.html

    @property
    def title(self):
        """Return page title."""
        try:
            return self['title']
        except KeyError:
            return self.url

    @title.setter
    def title(self, value):
        """."""
        self['title'] = value

    @property
    def tags(self):
        """Return page tags."""
        try:
            return self['tags']
        except KeyError:
            return ""

    @tags.setter
    def tags(self, value):
        """."""
        self['tags'] = value

    @property
    def language(self):
        """Return page language.

        Returns the language in which a page has been saved
        or returns default wiki language if page doesn't have a language.
        """
        filename = Path(self.path).stem
        return filename.split('_')[-1] if '_' in filename\
            else current_wiki.languages[0]


class WikiBase(object):
    """."""

    def __init__(self, root):
        """."""
        self.root = root

    def path(self, url):
        """."""
        return os.path.join(self.root, f'{url}.md')

    def ln_path(self, url):
        """."""
        return os.path.join(self.root, f'{url}_{self.current_language}.md')

    def exists(self, url):
        """."""
        path = self.path(url)
        return os.path.exists(path)

    def get(self, url):
        """."""
        path = self.ln_path(url)
        if os.path.isfile(path):
            return Page(path, url)
        path = self.path(url)
        return Page(path, url) if os.path.isfile(path) else None

    def get_or_404(self, url):
        """."""
        if page := self.get(url):
            return page
        abort(404)

    def get_bare(self, url):
        """."""
        path = self.path(url)
        return False if self.exists(url) else Page(path, url, new=True)

    def move(self, url, newurl):
        """."""
        source = f'{os.path.join(self.root, url)}.md'
        target = f'{os.path.join(self.root, newurl)}.md'
        # normalize root path (just in case somebody defined it absolute,
        # having some '../' inside) to correctly compare it to the target
        root = os.path.normpath(self.root)
        # get root path longest common prefix with normalized target path
        common = os.path.commonprefix((root, os.path.normpath(target)))
        # common prefix length must be at least as root length is
        # otherwise there are probably some '..' links in target path leading
        # us outside defined root directory
        if len(common) < len(root):
            raise RuntimeError(
                'Possible write attempt outside content directory: '
                '%s' % newurl)
        # create folder if it does not exists yet
        folder = os.path.dirname(target)
        if not os.path.exists(folder):
            os.makedirs(folder)
        os.rename(source, target)

    def delete(self, url):
        """."""
        path = self.path(url)
        if not self.exists(url):
            return False
        os.remove(path)
        return True

    def index(self):
        """Build up a list of all the available pages.

        :returns: a list of all the wiki pages
        :rtype: list
        """
        # make sure we always have the absolute path for fixing the
        # walk path
        pages = []
        root = os.path.abspath(self.root)
        for cur_dir, _, files in os.walk(root):
            # get the url of the current directory
            cur_dir_url = cur_dir[len(root)+1:]
            for cur_file in files:
                path = os.path.join(cur_dir, cur_file)
                if cur_file.endswith('.md'):
                    url = clean_url(os.path.join(cur_dir_url, cur_file[:-3]))
                    page = Page(path, url)
                    pages.append(page)
        return sorted(pages, key=lambda x: x.title.lower())

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
        """."""
        pages = self.index(attr='title')
        return pages.get(title)

    def get_tags(self):
        """."""
        pages = self.index()
        tags = {}
        for page in pages:
            pagetags = page.tags.split(',')
            for tag in pagetags:
                tag = tag.strip()
                if tag == '':
                    continue
                elif tags.get(tag):
                    tags[tag].append(page)
                else:
                    tags[tag] = [page]
        return tags

    def index_by_tag(self, tag):
        """."""
        pages = self.index()
        tagged = [page for page in pages if tag in page.tags]
        return sorted(tagged, key=lambda x: x.title.lower())

    @property
    def current_language(self):
        """."""
        return current_app.config.get('WIKI_CURRENT_LANGUAGE')()

    @property
    def languages(self):
        """."""
        return current_app.config.get('WIKI_LANGUAGES')

    def search(self, term, ignore_case=True, attrs=None):
        """."""
        if attrs is None:
            attrs = ['title', 'tags', 'body']
        pages = self.index()

        for page in pages:
            page["score"] = 0

        # When searching for "*", return ALL pages
        if term == "*":
            return pages

        current_language_pages = [
            p for p in pages if p.language == self.current_language]

        # If no query term, return all current language pages
        if not term:
            return current_language_pages

        regex = re.compile(
            re.escape(term), re.IGNORECASE if ignore_case else 0)

        matched = []
        for page in current_language_pages:
            for attr in attrs:
                if found := re.findall(regex, getattr(page, attr)):
                    page["score"] += len(found)
                    if page not in matched:
                        matched.append(page)
        # Sort results by score
        return sorted(matched, key=lambda x: x["score"], reverse=True)


def get_wiki():
    """."""
    wiki = getattr(g, '_wiki', None)
    if wiki is None:
        wiki = g._wiki = WikiBase(current_app.config['WIKI_CONTENT_DIR'])
    return wiki


current_wiki = LocalProxy(get_wiki)
