# -*- coding: utf-8 -*-
#
# This file is part of Flask-Wiki
# Copyright (C) 2023 RERO
#
# Flask-Wiki is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Misc utils functions."""

import re

from flask import url_for


def clean_url(url):
    """Clean the url and correct various errors.

    Removes multiple spaces and all leading and trailing spaces. Changes
    spaces to underscores. Also takes care of Windows style folders use.

    :param str url: the url to clean
    :returns: the cleaned url
    :rtype: str
    """
    url = re.sub("[ ]{2,}", " ", url).strip()
    url = url.replace("\\\\", "/").replace("\\", "/")
    return url


def wikilink(text, url_formatter=None):
    """Process Wikilink syntax "[[Link]]" within the html body.

    This is intended to be run after content has been processed
    by markdown and is already HTML.

    :param str text: the html to highlight wiki links in.
    :param function url_formatter: which URL formatter to use,
        will by default use the flask url formatter

    Syntax:
        This accepts Wikilink syntax in the form of [[WikiLink]] or
        [[url/location|LinkName]]. Everything is referenced from the
        base location "/", therefore sub-pages need to use the
        [[page/subpage|Subpage]].

    :returns: the processed html
    :rtype: str
    """
    if url_formatter is None:
        url_formatter = url_for
    link_regex = re.compile(
        r"((?<!\<code\>)\[\[([^<].+?) \s*([|] \s* (.+?) \s*)?]])", re.X | re.U
    )
    for i in link_regex.findall(text):
        title = [i[-1] or i[1]][0]
        url = clean_url(i[1])
        html_url = "<a href='{0}'>{1}</a>".format(
            url_formatter("display", url=url), title
        )
        text = re.sub(link_regex, html_url, text, count=1)
    return text
