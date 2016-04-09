#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
This file contains some tests for the way items are marked with the
'done' state.
"""

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


@pytest.mark.parametrize('item_text,done_date', completed_item_examples)
def test_getting_done_date_of_completed_item_strings(item_text, done_date):
    """
    Create some items from strings that include the @done tag and a date.
    Check that the correct date is recognised.
    """
    assert TaskPaperItem(item_text).done_date() == done_date


@pytest.mark.parametrize('item_text', uncompleted_item_examples)
def test_getting_done_date_of_uncompleted_is_error(item_text):
    """
    Trying to get the done date of a task which isn't completed throws
    a TaskPaperError error.
    """
    with pytest.raises(TaskPaperError):
        TaskPaperItem(item_text).done_date()


@pytest.mark.parametrize('item_text', uncompleted_item_examples)
def test_marking_as_done_completes_an_item(item_text):
    """
    Setting the 'done' attribute marks an item as complete with
    today's date.
    """
    item = TaskPaperItem(item_text)

    item.done = True
    assert item.done
    assert item.done_date() == MOCK_DATE_STR


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


@pytest.mark.parametrize('item_text', uncompleted_item_examples)
def test_setting_custom_done_date(item_text):
    """
    Mark an item as done, then check we can set the done date to another
    string.
    """
    item = TaskPaperItem(item_text)

    item.done = True
    assert item.done_date() == MOCK_DATE_STR

    item.set_done_date('yesterday')
    assert item.done_date() == 'yesterday'


@pytest.mark.parametrize('item_text', uncompleted_item_examples)
def test_setting_custom_done_date(item_text):
    """
    Check that we can mark an item as done on a particular date.
    """
    item = TaskPaperItem(item_text)

    item.mark_done(date='tomorrow')
    assert item.done_date() == 'tomorrow'


def test_we_can_only_set_done_once():
    """
    Test that an item can only ever have one 'done' tag.
    """
    item = TaskPaperItem('hello world')

    item.add_tag(name='done', value='now')
    assert str(item) == 'hello world @done(now)'

    # If we try to add a second done tag, we can only update the
    # existing done tag.
    item.add_tag(name='done', value='tomorrow')
    assert str(item) == 'hello world @done(tomorrow)'

    # Call the base methods on the tag list, just to be sure.
    item.tags.insert(0, value=('done', 'maybe'))
    assert str(item) == 'hello world @done(maybe)'

    # Add an extra tag, and then try to overwrite it.
    item.add_tag(name='foo', value='bar')
    item.tags[0] = ('done', 'nope')
    assert str(item) == 'hello world @done(nope)'


def test_done_tag_is_always_at_the_end():
    """
    Test that the 'done' tag is always forced to the end.
    """
    item = TaskPaperItem('hello world')

    item.add_tag(name='done', value='now')
    assert str(item) == 'hello world @done(now)'

    # Although we added this tag *after* the done tag, the done tag should
    # be moved to the end -- it has special significance.
    item.add_tag(name='foo', value='bar')
    assert str(item) == 'hello world @foo(bar) @done(now)'

    # If we now add a third tag, it maintains that final spot
    item.add_tag(name='baz')
    assert str(item) == 'hello world @foo(bar) @baz @done(now)'
