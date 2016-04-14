#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
This file contains the code for working with links.
"""

import re

try:
    from collections.abc import MutableSequence
except ImportError:  # pragma: no cover
    from collections import MutableSequence


# Regex for matching email addresses.  This is taken from birch.js.
EMAIL_REGEX = (
    r'\b'                   # Word boundary
    r'[A-Z0-9\._%+\-]+'     # Username
    r'@'                    # Literal @ character
    r'[A-Z0-9\.\-]+'        # Hostname
    r'\.'                   # Literal . character
    r'[A-Z]{2,4}'           # TLD e.g .com, .org
    r'\b'                   # Another word boundary
)


# Regex for matching paths.  This is adapted from birch.js
PATH_REGEX = (
    r'\.?\/'                # Slash and dot (optional) for start of path
    r'(?:\\\s|[^\0 ]+)'     # Either an escaped space ('\ ') or any char
                            # which isn't a space
)


# Regex for matching web addresses.  This is adapted from birch.js
WEB_REGEX = (
    r'\b'                           # Word boundary

    r'(?:'                          # one of two possibilities:
        r'[a-z][\w\-]+'             # scheme, e.g. 'http', 'ftp'
        r':'                        # literal : character
        r'(?:\/{1,3}|[a-z0-9%.])'   # 1-3 slashes or other chars
    r'|'
        r'www\d{0,3}[.]'            # literal 'www' folowed by digits and a .
    r')'

    r'(?:'                          # one or more of two possibilities:
        r'[^\s()<>]+'               # anything except whitespace, () or <>
    r'|'
        r'\([^\s()<>]+\)'           # literal parens () around anything
                                    # but whitespace, () or <>
    r')+'

    r'(?:'                          # one or more of two possibilities
        r'\([^\s()<>]+\)'           # literal parens around anything but
                                    # whitespace, () or <>
    r'|'
        r'[^`!()\[\]{};:\'".,<>?«»“”‘’\s]'
                                    # anything except whitespace or these chars
    r')'
)


LINK_REGEX = re.compile(
    '(?:^|\s)(%s|%s|%s)' % (EMAIL_REGEX, PATH_REGEX, WEB_REGEX),
    flags=re.IGNORECASE
)


class LinkCollection(MutableSequence):
    """
    Collection of links.  Acts like a list, but trying to add or remove
    anything that doesn't match LINK_REGEX will throw a ValueError.
    """
    def __init__(self):
        self.__links = []

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.__links)

    def __len__(self):
        return len(self.__links)

    def __getitem__(self, position):
        return self.__links[position]

    def __setitem__(self, position, value):
        if not re.search('^' + LINK_REGEX.pattern + '$', value, flags=re.IGNORECASE):
            raise ValueError("Tried to add non-link %s" % value)
        self.__links[position] = value

    def __delitem__(self, position, value):
        if not re.search('^' + LINK_REGEX.pattern + '$', value, flags=re.IGNORECASE):
            raise ValueError("Tried to delete non-link %s" % value)
        del self.__links[position]

    def insert(self, position, value):
        if not re.search('^' + LINK_REGEX.pattern + '$', value, flags=re.IGNORECASE):
            raise ValueError("Tried to insert non-link %s" % value)
        self.__links.insert(position, value)

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        else:
            return all(i == j for i, j in zip(self, other))

    def __neq__(self, other):
        return not (self == other)
