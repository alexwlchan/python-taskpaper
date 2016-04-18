#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
This file contains the TaskPaperItem class, and the associated setup code.
"""

import re

from ._links import LINK_REGEX, LinkCollection
from ._tags import TagCollection


class TaskPaperItem(object):

    # Number of spaces per indentation level
    tab_size = 4

    def __init__(self, text):
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
    def type(self):
        content = self._content().lstrip()
        if any(content.startswith('%s ' % i) for i in '-*+'):
            return 'task'
        elif content.rstrip().endswith(':'):
            return 'project'
        else:
            return 'note'
