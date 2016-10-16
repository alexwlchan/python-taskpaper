# -*- encoding: utf-8 -*-

from hypothesis import given
from hypothesis.strategies import integers, lists
import pytest

from taskpaper import TaskPaperItem, TaskPaperError

from utils import taskpaper_item_strategy


@given(integers())
def test_setting_tab_size(tab_size):
    """We can set the tab size on TaskPaperItem."""
    item = TaskPaperItem('hello world', tab_size=tab_size)
    assert item.tab_size == tab_size


class TestParentChildRelationship(object):
    """
    Tests of the parent-child relationship between items.
    """

    def test_default_parent_is_none(self):
        """By default, a task does not have a parent."""
        item = TaskPaperItem('hello world')
        assert item.parent is None

    def test_default_task_has_no_children(self):
        """By default, a task has no children."""
        item = TaskPaperItem('hello world')
        assert item.children == []

    def test_setting_a_parent(self):
        """Test we can initialize an item with a parent."""
        item_p = TaskPaperItem('parent')
        item_c = TaskPaperItem('child', parent=item_p)
        assert item_c.parent == item_p
        assert item_p.children == [item_c]

    def test_updating_a_parent(self):
        """Test we can create an item with a parent, then change the parent."""
        item_p1 = TaskPaperItem('parent1')
        item_p2 = TaskPaperItem('parent2')
        item_c = TaskPaperItem('child', parent=item_p1)

        item_c.parent = item_p2
        assert item_c.parent == item_p2
        assert item_p2.children == [item_c]
        assert item_p1.children == []

    def test_updating_to_same_parent(self):
        """
        Create an item with a parent, change the parent to existing parent,
        check nothing happens.
        """
        item_p = TaskPaperItem('parent')
        item_c = TaskPaperItem('child', parent=item_p)

        item_c.parent == item_p
        assert item_c.parent == item_p
        assert item_p.children == [item_c]

    def test_removing_a_parent(self):
        """
        Create an item with a parent, then set the parent to None.  Check the
        child is removed from the list of its previous parents' children.
        """
        item_p = TaskPaperItem('parent')
        item_c = TaskPaperItem('child', parent=item_p)

        item_c.parent = None
        assert item_c.parent is None
        assert item_p.children == []

    def test_detect_item_cannot_be_its_parents_parent(self):
        """
        An item cannot be the parent of its own parent.
        """
        item_p = TaskPaperItem('parent')
        item_c = TaskPaperItem('child', parent=item_p)

        with pytest.raises(TaskPaperError):
            item_p.parent = item_c

    @given(lists(taskpaper_item_strategy(), min_size=2))
    def test_detecting_circular_chain(self, items):
        """
        We detect an arbitrarily long circular parent chain.
        """
        # Create a chain of parent-child relationships
        #    items[0] -> items[1] -> ... -> items[n]
        for idx, alt_item in enumerate(items[1:], start=1):
            items[idx-1].parent = alt_item

        # Now make the first item the parent of the last, and check we
        # get an exception.
        with pytest.raises(TaskPaperError):
            items[-1].parent = items[0]
