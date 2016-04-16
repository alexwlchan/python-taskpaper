#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
This file contains some tests for the way items are marked with the
'done' state.
"""

from hypothesis import given, strategies as st
import pytest

import taskpaper
from taskpaper import TaskPaperItem, TaskPaperError


# Mock out the function that produces the date string for a new @done tag.
MOCK_DATE_STR = '2016-04-09'
taskpaper.items._today = lambda: MOCK_DATE_STR


completed_item_examples = [
    ['Register to vote @done', ''],
    ['Do the laundry @done(2016-04-03)', '2016-04-03'],
    ['But some groceries @done()', ''],
    ['Wash the car @done @home', ''],
    ['Make some coffee @done(yesterday)', 'yesterday'],
]


uncompleted_item_examples = [
    'Clean the bathroom @domestic',
    'Read "Fluent Python"',
    'Write more unit tests',
    'Cook dinner',
]


@pytest.mark.parametrize('item_text,completion_date', completed_item_examples)
def test_completed_item_strings_are_done(item_text, completion_date):
    """
    Create some items from strings that include the @done tag.
    Test that they all register as completed.
    """
    assert TaskPaperItem(item_text).done


@pytest.mark.parametrize('item_text', uncompleted_item_examples)
def test_uncompleted_item_strings_are_not_done(item_text):
    """
    Create some items from strings that don't include the @done tag.
    Test that they register as incomplete.
    """
    assert not TaskPaperItem(item_text).done


@pytest.mark.parametrize('item_text,completion_date', completed_item_examples)
def test_marking_as_undone_uncompletes_an_item(item_text, completion_date):
    """
    Unsetting the 'done' attribute marks an item as incomplete.
    """
    item = TaskPaperItem(item_text)
    item.done = False
    assert not item.done


@pytest.mark.parametrize('item_text', uncompleted_item_examples)
def test_marking_an_undone_item_as_undone_is_a_noop(item_text):
    """
    If an item is already incomplete, setting the 'done' attribute to
    False has no effect.
    """
    item = TaskPaperItem(item_text)
    item.done = False
    assert not item.done


@pytest.mark.parametrize('item_text,completion_date', completed_item_examples)
def test_marking_a_done_item_as_done_is_a_noop(item_text, completion_date):
    """
    If an item is already done, setting the 'done' attribute to
    True has no effect.
    """
    item = TaskPaperItem(item_text)
    item.done = True
    assert item.done


@pytest.mark.parametrize('item_text,completion_date', completed_item_examples)
def test_setting_done_state_of_completed_item(item_text, completion_date):
    """
    Create some items with the done tag, and test we can toggle their state
    with the done setter.
    """
    item = TaskPaperItem(item_text)

    item.done = False
    assert not item.done

    item.done = True
    assert item.done


@pytest.mark.parametrize('item_text', uncompleted_item_examples)
def test_setting_done_state_of_uncompleted_item(item_text):
    """
    Create some items with the undone tag, and test we can toggle their state
    with the done setter.
    """
    item = TaskPaperItem(item_text)

    item.done = True
    assert item.done

    item.done = False
    assert not item.done


@given(st.text(), st.booleans())
def test_setting_done_state_on_arbitrary_items(item_text, state):
    item = TaskPaperItem(item_text)
    item.done = state
    assert (state == item.done)


@pytest.mark.parametrize('bad_state', [
    'cabbage',
    'truey false',
    'maybe',
    42,
])
def test_setting_bad_done_state_is_error(bad_state):
    item = TaskPaperItem("hello world")
    with pytest.raises(ValueError):
        item.done = bad_state
