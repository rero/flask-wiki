title: Editing a page
tags: guide, markdown

A page is a Markdown file preceded by a few metadata lines. The *Edit* button opens the editor, which writes the file of the language announced in the tab bar.

## Metadata

The lines before the first empty line describe the page:

| Key | Purpose |
|-----|---------|
| `title` | Title shown at the top of the page, in the index and in search results |
| `tags` | Keywords separated by commas |

```markdown
title: Editing a page
tags: guide, markdown

The content starts here.
```

## Links

An internal link is written the wiki way, `[[home|Home]]`, or as a plain Markdown link to [another page](/help/guides/languages/). In both cases the address carries no language code: the wiki serves the variant matching the reader's language.

## Images

Images are uploaded from the *Files* page, then referenced by their URL:

![The Flask logo](/help/files/flask-logo.png "The Flask logo")

## Table of contents

Level 2 and 3 headings feed the table of contents displayed on the right of the page.
