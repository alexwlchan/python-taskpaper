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


def is_string_link(text):
    """Returns True if text contains a link, False otherwise."""
    return re.search('^' + LINK_REGEX.pattern + '$', text, flags=re.IGNORECASE)


class LinkCollection(MutableSequence):
    """
    Collection of links.  Acts like a list, but trying to add or remove
    anything that doesn't match LINK_REGEX will throw a ValueError.
    """
    def __init__(self, item):
        self.item = item

    def __str__(self):
        return str([x.group(1) for x in self._raw_links()])

    def __repr__(self):
        return str(self)

    def _raw_links(self):
        result = []
        for match in LINK_REGEX.finditer(self.item.text):
            link = {
                'type': 'link',
                'text': match.group(1),
            }
            if re.search(EMAIL_REGEX, match.group(1), flags=re.IGNORECASE):
                link['link_type'] = 'email'
                if not link['text'].startswith('mailto:'):
                    link['href'] = 'mailto:{email}'.format(email=link['text'])
            elif re.search(WEB_REGEX, match.group(1), flags=re.IGNORECASE):
                link['link_type'] = 'web'
                if not any(link['text'].startswith(h)
                           for h in ('http://', 'https://')):
                    link['href'] = 'http://{url}'.format(url=link['text'])
            # elif re.search(PATH_REGEX, match.group(1), flags=re.IGNORECASE):
            else:
                link['link_type'] = 'path'
                if not link['text'].startswith('file://'):
                    link['href'] = 'file://{path}'.format(path=link['text'])
            if 'href' not in link:
                link['href'] = link['text']
            result.append(link)
        return result

    def __len__(self):
        return len(self._raw_links())

    def __getitem__(self, position):
        return self._raw_links()[position].group(1)

    def __setitem__(self, position, value):
        if not is_string_link(value):
            raise ValueError("Tried to add non-link %s" % value)
        try:
            existing = self._raw_links()[position]
            start, stop = existing.span()
            self.item.text = (
                self.item.text[:start+1] +
                value +
                self.item.text[stop:]
            )
        except IndexError:
            self.item.text += ' %s' % value

    def __delitem__(self, key):
        del self._links[key]

    def insert(self, key, value):
        if not is_string_link(value):
            raise ValueError("Tried to add non-link %s" % value)
        self._links.insert(key, value)

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        else:
            return all(i == j for i, j in zip(self, other))

    def __neq__(self, other):
        return not (self == other)
