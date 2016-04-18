#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
This file contains the TaskPaperItem class, and the associated setup code.
"""

import re

from ._links import LINK_REGEX, LinkCollection
from ._tags import TagCollection, stringify_tag


class TaskPaperItem(object):

    # Number of spaces per indentation level
    tab_size = 4

    def __init__(self, text, parent=None):
        self.text = text.rstrip()

        self.links = LinkCollection(item=self)
        self.tags = TagCollection(item=self)

    def __repr__(self):
        return '%s(text=%r)' % (type(self).__name__, self.text)

    def __str__(self):
        return self.text

    def add_tag(self, name, value=""):
        self.tags[name] = value

    def raw_tags(self):
        return self.tags._raw_tags()

    def raw_links(self):
        return self.links._raw_links()

    @property
    def done(self):
        """
        Returns True if an item is marked as 'done'; that is, whether it
        has the @done tag.
        """
        return 'done' in self.tags

    @done.setter
    def done(self, value):
        if value is False:
            try:
                del self.tags['done']
            except KeyError:
                pass
        elif value is True:
            self.tags['done'] = ''
        else:
            raise ValueError("Expected True/False, got %r" % value)

    def _content(self):
        content = self.text
        for tag in reversed(self.raw_tags().values()):
            content = content[:tag['span'].start] + content[tag['span'].stop:]
        for link in LINK_REGEX.findall(content):
            content = content.replace(link, '')
        return content

    @property
    def depth(self):
        try:
            return self.parent.depth + 1
        except AttributeError:
            return 1

    @property
    def type(self):
        content = self._content().lstrip()
        if any(content.startswith('%s ' % i) for i in '-*+'):
            return 'task'
        elif content.rstrip().endswith(':'):
            return 'project'
        else:
            return 'note'

    def to_html(self):
        if self.type == 'project':
            rc = '<h{self.depth}>{self.text}</h{self.depth}>'.format(self=self)
        elif self.type == 'task':
            rc = '<li>{text}</li>'.format(text=self.text.lstrip('-*+').lstrip())
        else:
            rc = self.text

        # TODO: This should handle file paths and emails correctly
        for link in self.raw_links():
            rc = rc.replace(link['text'],
                '<a href="{href}">{text}</a>'.format(href=link['href'],
                                                     text=link['text']))

        for tag in self.tags.values():
            tag_str = stringify_tag(tag['name'], tag['value'])
            rc = rc.replace(
                tag_str,
                '<span class="tag tag-{tag}">{tag_str}</span>'.format(
                    tag=tag['name'], tag_str=tag_str)
            )

        rc = rc.replace(
            '<li>',
            '<li class="%s">' % ''.join('tagged-%s' % name for name in self.tags)
        )
        return rc
