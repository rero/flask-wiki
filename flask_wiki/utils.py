# -*- coding: utf-8 -*-
#
# Copyright (c) 2013, Alexander Jung-Loddenkemper
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:

#   Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.

#   Redistributions in binary form must reproduce the above copyright notice, this
#   list of conditions and the following disclaimer in the documentation and/or
#   other materials provided with the distribution.

#   Neither the name of this project nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# This file is part of Flask-Wiki
# Copyright (C) 2020 RERO
#
# Flask-Wiki is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Misc utils functions."""

import re

from flask import url_for


def clean_url(url):
    """Cleans the url and corrects various errors.

        Removes multiple spaces and all leading and trailing spaces. Changes
        spaces to underscores and makes all characters lowercase. Also takes
        care of Windows style folders use.

        :param str url: the url to clean
        :returns: the cleaned url
        :rtype: str
    """
    url = re.sub('[ ]{2,}', ' ', url).strip()
    url = url.lower().replace(' ', '_')
    url = url.replace('\\\\', '/').replace('\\', '/')
    return url


def wikilink(text, url_formatter=None):
    """Processes Wikilink syntax "[[Link]]" within the html body.

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
        r"((?<!\<code\>)\[\[([^<].+?) \s*([|] \s* (.+?) \s*)?]])",
        re.X | re.U
    )
    for i in link_regex.findall(text):
        title = [i[-1] if i[-1] else i[1]][0]
        url = clean_url(i[1])
        html_url = u"<a href='{0}'>{1}</a>".format(
            url_formatter('display', url=url),
            title
        )
        text = re.sub(link_regex, html_url, text, count=1)
    return text
