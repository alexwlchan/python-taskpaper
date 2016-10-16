# -*- encoding: utf-8 -*-

from .exceptions import TaskPaperError


class TaskPaperItem(object):

    def __init__(self, text, tab_size=4, parent=None):
        """
        :param tab_size: Number of spaces used per indentation level.
        :param parent: Parent task.
        """
        self.tab_size = tab_size
        self.children = []
        self.parent = parent

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, new_parent):
        # If we've never had a parent, default to None before proceeding
        if not hasattr(self, '_parent'):
            self._parent = None

        # If this is the same as our old parent, this is a no-op
        if self._parent is new_parent:
            return

        # Check that we aren't about to form a circular cycle of parents --
        # in particular, that we aren't our new parent's parent, or any of
        # its ancestors.
        if new_parent is not None:
            for ancestor in new_parent.ancestors:
                if ancestor is self:
                    raise TaskPaperError(
                        'Making %s a parent of %s would create a circular '
                        'family tree' % (self, new_parent)
                    )

        # If we already had a parent, remove ourselves from its children
        if self._parent is not None:
            self._parent.children.remove(self)

        # If the new parent is not None, add ourselves to its children
        if new_parent is not None:
            new_parent.children.append(self)

        self._parent = new_parent

    @property
    def ancestors(self):
        current = self
        while current.parent is not None:
            yield current.parent
            current = current.parent
