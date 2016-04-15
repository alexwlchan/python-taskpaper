#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
This file contains code for handling tags in TaskPaper items.
"""

import collections
import re


TaskPaperTag = collections.namedtuple('TaskPaperTag', 'name value span')


# Regex for matching tags. http://guide.taskpaper.com/getting_started.html:
#
#  > To create a tag, type the @ symbol followed by a name. Tags can
#  > optionally have a value in parentheses after the tag name:
#  >   @priority(1)
#
# This regex is adapted from the birch.js variable tagRegexString.

TAG_REGEX = re.compile(
    r'(?:^|\s+)'                    # word boundary
    r'@'                            # literal @ character
    r'(?P<name>'                    # capturing group for tag name
    r'(?:[A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D'
        r'\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF'
        r'\uF900-\uFDCF\uFDF0-\uFFFD]|'
                                    # first char of the name.
                                    # taken directly from birch.js
    r'[\-.0-9\u00B7\u0300-\u036F\u203F-\u2040])*)'
                                    # other chars of the name/
                                    # taken directly from birch.js
    r'(?:\((?P<value>(?:\\\)|[^\)])*)\))?'
                                    # tag value
                                    # adapted from birch.js
    r'(?=\s|$)',                  # another word boundary or end-of-line
    flags=re.IGNORECASE
)


def stringify_tag(name, value):
    if value:
        return '@{name}({value})'.format(name=name, value=value)
    else:
        return '@{name}'.format(name=name)


class TagCollection(collections.OrderedDict):

    def __init__(self, item):
        self.item = item
        super(TagCollection, self).__init__()
        self._update()

    def __repr__(self):
        return repr(collections.OrderedDict(self.items()))

    def __str__(self):
        return str(collections.OrderedDict(self.items()))

    def _update(self):
        for key in list(self.keys()):
            super(TagCollection, self).__delitem__(key)
        for key, value in self._raw_tags().items():
            super(TagCollection, self).__setitem__(key, value)

    def _raw_tags(self):
        rc = collections.OrderedDict()
        for match in TAG_REGEX.finditer(self.item.text):
            name = match.group('name')
            value = match.group('value')
            span = slice(*match.span())
            rc[name] = TaskPaperTag(name, value, span)
        return rc

    def __setitem__(self, name, value=None):
        self._update()
        if value is None:
            value = ""
        raw_tags = self._raw_tags()
        tag_str = stringify_tag(name=name, value=value)

        # If the item already has a tag with this name, then we need to
        # update the existing tag.
        if name in raw_tags:

            # Get the existing tag, and find the bounds of the existing tag
            # within the item text.
            span = raw_tags[name].span

            self.item.text = (
                self.item.text[:span.start+1] +
                tag_str +
                self.item.text[span.stop:]
            )

        # If the item doesn't have this tag yet, then just append it
        # to the item.
        else:
            self.item.text += ' {tag_str}'.format(tag_str=tag_str)

        self._update()

    def __delitem__(self, name):
        self._update()
        if name in self.keys():
            value = self._raw_tags()[name]
            span = value.span

            self.item.text = (
                self.item.text[:span.start] +
                self.item.text[span.stop:]
            )
            super(TagCollection, self).__delitem__(name)
        else:
            raise KeyError("Item %s is not tagged with %s" % (self.item, name))

    def __getitem__(self, name):
        self._update()
        if name in self.keys():
            return super(TagCollection, self).__getitem__(name).value
        else:
            raise KeyError("Item %s is not tagged with %s" % (self.item, name))
