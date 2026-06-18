# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: BSD-3-Clause

"""Python-Markdown extensions."""

from markdown import Extension
from markdown.treeprocessors import Treeprocessor


class BootstrapExtension(Extension):
    """Python-Markdown extension that adds Bootstrap CSS classes to HTML elements."""

    def extendMarkdown(self, md):  # noqa: N802
        """Register the Bootstrap tree processor with the Markdown instance."""
        md.registerExtension(self)
        self.processor = BootstrapTreeprocessor()
        self.processor.md = md
        self.processor.config = self.getConfigs()
        md.treeprocessors.register(self.processor, "bootstrap", 1)


class BootstrapTreeprocessor(Treeprocessor):
    """Tree processor that applies Bootstrap CSS classes to images and tables."""

    def run(self, node):
        """Apply Bootstrap classes to all img and table elements in the parse tree.

        :param node: the root element tree node
        :returns: the modified element tree node
        """
        for child in node.iter():
            if child.tag == "img":
                child.set("class", "img-fluid mx-auto d-block")
            elif child.tag == "table":
                child.set("class", "table table-striped")

        return node
