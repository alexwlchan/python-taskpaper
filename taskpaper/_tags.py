#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
This file contains code for handling tags in TaskPaper items.
"""

import collections

import re

try:
    from collections.abc import MutableSequence
except ImportError:  # pragma: no cover
    from collections import MutableSequence


TaskPaperTag = collections.namedtuple('TaskPaperTag', 'name value')


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


# Defining a collection of tags as an ABC is arguably overkill.  All I really
# want is the ability to search the list by name only, e.g. given the item
#
#    - Pick up dry cleaning @hello(world)
#
# I should be able to write `'hello' in item.tags`, and get True.
#
# This also pulls the work of coercing new tags to a TaskPaperTag object
# out of the TaskPaperDocument class.

class TagCollection(MutableSequence):
    """
    Collection of tags that lets you search for inclusion by tag name
    or tag value.
    """
    def __init__(self):
        self._tags = []

    def __repr__(self):
        return repr(self._tags)

    def __str__(self):
        return str(self._tags)

    @staticmethod
    def _coerce_value_to_tag(value):
        if isinstance(value, tuple) and len(value) == 2:
            if isinstance(value[1], str) and (')' in value[1]):
                raise ValueError("Cannot have closing parens in tag value %r" %
                                 value[1])
            return TaskPaperTag(value[0], value[1] or '')
        elif isinstance(value, str):
            return TaskPaperTag(value, '')
        else:
            raise ValueError("Cannot coerce %r to TaskPaperTag." % value)

    def __len__(self):
        return len(self._tags)

    def __getitem__(self, position):
        return self._tags[position]

    def __setitem__(self, position, value):
        self._tags[position] = self._coerce_value_to_tag(value)

    def __delitem__(self, position):
        del self._tags[position]

    def insert(self, position, value):
        self._tags.insert(position, self._coerce_value_to_tag(value))

    def __contains__(self, value):
        # If we get a 2-tuple, assume that they're searching for an exact
        # tag, and search accordingly.
        if isinstance(value, tuple) and len(value) == 2:
            return value in self._tags

        # If we get a name, assume that they're searching for a tag with
        # a given name, but don't care about the value.
        elif isinstance(value, str):
            return any(tag.name == value for tag in self._tags)

        # No other search terms are acceptable.
        else:
            return False

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        else:
            return all(i == j for i, j in zip(sorted(self), sorted(other)))

    def __ne__(self, other):
        return not (self == other)
