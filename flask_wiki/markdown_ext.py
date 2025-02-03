# -*- coding: utf-8 -*-
#
# This file is part of Flask-Wiki
# Copyright (C) 2023 RERO
#
# Flask-Wiki is free software; you can redistribute it and/or modify
# it under the terms

"""Python-Markdown extensions."""

from markdown import Extension
from markdown.treeprocessors import Treeprocessor


class BootstrapExtension(Extension):
    """."""

    def extendMarkdown(self, md, md_globals):
        """."""
        md.registerExtension(self)
        self.processor = BootstrapTreeprocessor()
        self.processor.md = md
        self.processor.config = self.getConfigs()
        md.treeprocessors.add("bootstrap", self.processor, "_end")


class BootstrapTreeprocessor(Treeprocessor):
    """."""

    def run(self, node):
        """."""
        for child in node.iter():
            if child.tag == "img":
                child.set("class", "img-fluid mx-auto d-block")
            elif child.tag == "table":
                child.set("class", "table table-striped")

        return node
