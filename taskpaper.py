#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
This file contains the start of an API for dealing with TaskPaper documents.
"""

import collections
import re
import shutil
import tempfile

try:
    from collections.abc import MutableSequence
except ImportError:  # Python 2
    from collections import MutableSequence


TaskPaperTag = collections.namedtuple('TaskPaperTag', 'name value')

TAG_REGEX = re.compile(
    r'\B'                          # non-word boundary
    r'@'                           # literal @ character
    r'(?P<name>[a-z0-9\.\-_]+)'    # tag name
    r'(?:\((?P<value>[^)]*)\))?',  # tag value (optional)
    flags=re.IGNORECASE
)


class TaskPaperError(Exception):
    pass


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
    def __init__(self, iterable=None):
        if iterable is None:
            self._tags = []
        else:
            self._tags = iterable

    def __repr__(self):
        return repr(self._tags)

    def __str__(self):
        return str(self._tags)

    @staticmethod
    def _coerce_value_to_tag(value):
        if isinstance(value, tuple) and len(value) == 2:
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
            return all(i == j for i, j in zip(self, other))


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



class TaskPaperDocument(object):

    def __init__(self, path):
        self.path = path
        self._text = self._read()
        self.items = [
            TaskPaperItem(line) for line in self._text.splitlines()
        ]

    def __repr__(self):
        return '%s(path=%r)' % (type(self).__name__, self.path)

    def _read(self):
        try:
            with open(self.path) as infile:
                return infile.read()
        except IOError as e:
            raise TaskPaperError("Unable to read document %s: %s" %
                                 (self.path, e))

    def write(self):
        """
        Write out the list of tasks.  Writes are atomic.
        """
        _, tmp_path = tempfile.mkstemp(prefix='taskpaper')
        with open(tmp_path, 'w') as outfile:
            outfile.write('\n'.join(str(item) for item in self.items))

        shutil.move(tmp_path, self.path)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.write()
