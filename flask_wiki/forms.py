# -*- coding: utf-8 -*-
#
# This file is part of Flask-Wiki
# Copyright (C) 2020 RERO
#
# Flask-Wiki is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Forms class."""

from flask_babelex import gettext as _
from flask_wtf import Form
from wtforms import TextAreaField, TextField
from wtforms.validators import InputRequired


class EditorForm(Form):
    title = TextField(_('title'), [InputRequired()])
    body = TextAreaField(_('body'), [InputRequired()])
    tags = TextField(_('tags'))
