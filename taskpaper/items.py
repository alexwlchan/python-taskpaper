#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
This file contains the TaskPaperItem class, and the associated setup code.
"""

import collections
import re

try:
    from collections.abc import MutableSequence
except ImportError:  # pragma: no cover
    from collections import MutableSequence


TaskPaperTag = collections.namedtuple('TaskPaperTag', 'name value')


# Regex for matching tags.  http://guide.taskpaper.com/getting_started.html:
#
#  > To create a tag, type the @ symbol followed by a name. Tags can
#  > optionally have a value in parentheses after the tag name:
#  >   @priority(1)
#
TAG_REGEX = re.compile(
    r'\B'                         # word boundary
    r'@'                          # literal @ character
    r'(?P<name>[a-z0-9\.\-_]+)'   # tag name
    r'(?:\((?P<value>[^)]*)\))?'  # tag value (optional)
    r'(?:\s|$)',                  # another word boundary or end-of-line
    flags=re.IGNORECASE
)


class TaskPaperItem(object):

    # Number of spaces per indentation level
    tab_size = 4

    def __init__(self, text):
        # Strip trailing whitespace from the name.
        self._text = text.rstrip()

        self.tags = _TagCollection()
        self.body_text = self._text

        self._parse()

    def _parse(self):
        # Separate the list of tags from the body text
        m = TAG_REGEX.findall(self._text)
        if m is not None:
            self.tags.extend(m)

        self.body_text = re.sub(TAG_REGEX, '', self.body_text).strip()

    def __repr__(self):
        return '%s(text=%r)' % (type(self).__name__, self._text)

    def __str__(self):
        components = [self.body_text]
        for tag in self.tags:
            if tag.value:
                components.append('@{tag.name}({tag.value})'.format(tag=tag))
            else:
                components.append('@{tag.name}'.format(tag=tag))
        return ' '.join(components)

    def add_tag(self, name, value=None):
        """
        Add a new tag with the given name and value.
        """
        if value is None:
            self.tags.append(name)
        else:
            self.tags.append((name, value))

    def remove_tag(self, name, value=None):
        """
        Remove all tags with the given name and value.  If 'value' is None,
        every tag with this name is removed.
        """
        for tag in self.tags:
            if (tag.name == name) and (value is None or tag.value == value):
                self.tags.remove(tag)


# Defining a collection of tags as an ABC is arguably overkill.  All I really
# want is the ability to search the list by name only, e.g. given the item
#
#    - Pick up dry cleaning @hello(world)
#
# I should be able to write `'hello' in item.tags`, and get True.
#
# This also pulls the work of coercing new tags to a TaskPaperTag object
# out of the TaskPaperDocument class.

class _TagCollection(MutableSequence):
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
            if ')' in value[1]:
                raise ValueError("Cannot have closing parens in tag value %r" %
                                 value[1])
            return TaskPaperTag(*value)
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
