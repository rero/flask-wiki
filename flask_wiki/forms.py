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
from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, Form
from wtforms.validators import InputRequired


class EditorForm(FlaskForm):
    class Meta:
        locales = ['en', 'fr', 'de', 'it']

    def get_translations(self, form):
            return super(FlaskForm.Meta, self).get_translations(form)

    title = StringField(_('Title'), [InputRequired()])
    body = TextAreaField(_('Body'), [InputRequired()])
    tags = StringField(_('Tags'))
