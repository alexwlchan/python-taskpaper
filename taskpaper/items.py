#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
This file contains the TaskPaperItem class, and the associated setup code.
"""

from datetime import datetime
import re

from .exceptions import TaskPaperError
from ._links import LINK_REGEX, LinkCollection
from ._tags import TAG_REGEX, TaskPaperTag, TagCollection


def _today():  # pragma: no cover
    """
    Returns a YYYY-MM-DD representation of today's date.
    """
    return str(datetime.today().date())


class TaskPaperItem(object):

    # Number of spaces per indentation level
    tab_size = 4

    def __init__(self, text):
        # Strip trailing whitespace from the name.
        self._text = text.rstrip()

        self.links = LinkCollection()
        self.tags = TagCollection()
        self.body_text = self._text

        self._parse()

    def _parse(self):
        # Separate the list of tags from the body text
        matches = TAG_REGEX.finditer(self._text)
        if matches is not None:
            for match in matches:
                self.tags.append(match.groups())

        # Separate the list of links from the body text
        matches = LINK_REGEX.findall(self._text)
        if matches is not None:
            self.links.extend(matches)

        self.body_text = re.sub(TAG_REGEX, '', self.body_text).strip()
        self.body_text = re.sub(LINK_REGEX, '', self.body_text).strip()

    def __repr__(self):
        return '%s(text=%r)' % (type(self).__name__, self._text)

    def __str__(self):
        components = [self.body_text]
        for link in self.links:
            components.append(link)
        for tag in self.tags:
            if tag.value:
                components.append('@{tag.name}({tag.value})'.format(tag=tag))
            else:
                components.append('@{tag.name}'.format(tag=tag))
        return ' '.join(components)

    def set_tag(self, name, value):
        """
        If there is already a tag with the given name, updates the value.
        If there isn't, creates a new tag.
        """
        for idx, tag in enumerate(self.tags):
            if tag.name == name:
                self.tags[idx] = (name, value)
                return
        else:
            self.add_tag(name, value)

    def add_tag(self, name, value=None):
        """
        Add a new tag with the given name and value.  Unlike set_tag,
        this won't overwrite an existing tag.
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
            self.remove_tag('done')
        elif value is True:
            self.set_tag('done', _today())
        else:
            raise ValueError("Expected True/False, got %r" % value)

    def done_date(self):
        """
        Returns the date on which an item was marked as completed.
        Throws a TaskPaperError if the task is unfinished.
        """
        try:
            done_tag = [tag for tag in self.tags if tag.name == 'done'].pop()
        except IndexError:
            raise TaskPaperError("Trying to get done date of an unfinished task")
        return done_tag.value

    def mark_done(self, date):
        """
        Mark an item as complete on a particular day.
        """
        self.done = True
        self.set_done_date(date)

    def set_done_date(self, date):
        """
        Set the date on which a task was marked as completed.
        """
        self.set_tag('done', date)
