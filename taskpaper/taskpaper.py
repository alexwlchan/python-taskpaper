#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
This file contains the start of an API for dealing with TaskPaper documents.
"""

import collections
import re
import shutil
import tempfile

from .exceptions import TaskPaperError


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
