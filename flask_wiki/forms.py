# -*- coding: utf-8 -*-
#
# This file is part of Flask-Wiki
# Copyright (C) 2023 RERO
#
# Flask-Wiki is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Forms class."""

from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired


class EditorForm(FlaskForm):
    """."""

    title = StringField(_("Title"), [InputRequired()])
    body = TextAreaField(_("Body"), [InputRequired()])
    tags = StringField(_("Tags"))
