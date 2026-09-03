# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: BSD-3-Clause

"""Python-Markdown extensions."""

from xml.etree.ElementTree import Element, SubElement

from markdown import Extension
from markdown.treeprocessors import Treeprocessor


class BootstrapExtension(Extension):
    """Python-Markdown extension that adapts the rendered HTML to the wiki templates."""

    def extendMarkdown(self, md):  # noqa: N802
        """Register the wiki tree processors with the Markdown instance."""
        md.registerExtension(self)
        self.processor = BootstrapTreeprocessor()
        self.processor.md = md
        self.processor.config = self.getConfigs()
        md.treeprocessors.register(self.processor, "bootstrap", 1)
        md.treeprocessors.register(FigureTreeprocessor(md), "figure", 10)


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


class FigureTreeprocessor(Treeprocessor):
    """Tree processor that renders a captioned image as a figure."""

    def run(self, node):
        """Replace every paragraph made of a single titled image with a figure.

        :param node: the root element tree node
        :returns: the modified element tree node
        """
        for parent in node.iter():
            for index, child in enumerate(parent):
                if self.is_lone_titled_image(child):
                    parent[index] = self.figure(child)

        return node

    @staticmethod
    def is_lone_titled_image(element):
        """Return True if the element is a paragraph holding nothing but a titled image.

        A figure is a block element, so an image only becomes one when it stands alone
        in its paragraph; and its caption is the image title, so an image without one
        is left as it is.

        :param element: the element tree node to check
        :rtype: bool
        """
        return bool(
            element.tag == "p"
            and not (element.text or "").strip()
            and len(element) == 1
            and element[0].tag == "img"
            and not (element[0].tail or "").strip()
            and element[0].get("title")
        )

    @staticmethod
    def figure(paragraph):
        """Return the figure replacing a paragraph made of a single titled image.

        The title becomes the caption and is removed from the image, which would
        otherwise repeat it as a tooltip. The alt text is left untouched, as it
        describes the image for those who cannot see it.

        :param paragraph: the paragraph element tree node
        :returns: a figure element wrapping the image and its caption
        """
        image = paragraph[0]
        figure = Element("figure")
        figure.tail = paragraph.tail
        figure.append(image)
        SubElement(figure, "figcaption").text = image.attrib.pop("title")
        return figure
