# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: BSD-3-Clause

"""Forms class."""

from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired


class EditorForm(FlaskForm):
    """WTForms form for creating and editing wiki pages."""

    title = StringField(_("Title"), [InputRequired()])
    body = TextAreaField(_("Body"), [InputRequired()])
    tags = StringField(_("Tags"))
