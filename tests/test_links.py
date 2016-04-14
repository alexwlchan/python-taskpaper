#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
This file contains some methods for testing the way we handle links.
Compared to tags, this code is fairly simple.
"""

import pytest

from taskpaper import TaskPaperItem


@pytest.mark.parametrize('item_text,links', [
    # Example with no tags
    ['lorem ipsum', []],

    # Example with an email address at the end of the item
    ['hello example@example.org', ['example@example.org']],

    # Example with a web address at the end of the item
    ['foo http://google.co.uk', ['http://google.co.uk']],

    # Example with a web address in the middle of the item
    ['quick ftp://brownfox.com jumps', ['ftp://brownfox.com']],

    # Example with a local file path
    ['opening ./myfile.txt', ['./myfile.txt']],

    # Example with a web address and an email address
    ['send http://book.org to library@example.net', ['http://book.org', 'library@example.net']]
])
def test_link_parsing(item_text, links):
    """
    Create some items which contain links, and check the links are
    recognised correctly.
    """
    item = TaskPaperItem(item_text)
    assert item.links == links


@pytest.mark.parametrize('bad_link', [
    'notalink',
    'http//missingcolon.com',
    'example-at-example-dot-org',
    'http://example.org and some text'
])
def test_adding_bad_links_is_rejected(bad_link):
    """
    Trying to add something that isn't a link to the list of links is an
    error.
    """
    item = TaskPaperItem('An item without any links')
    with pytest.raises(ValueError):
        item.links.append(bad_link)


@pytest.mark.parametrize('good_link', [
    'http://google.co.uk',
    'ftp://sekrit.org',
    'john@smith.com',
])
def test_link_mutation(good_link):
    """
    Add a link to an item, check it's allowed, check it shows up correctly.
    """
    item = TaskPaperItem('Another item without any links')

    item.links.append(good_link)
    assert len(item.links) == 1
    assert item.links == [good_link]


# def test_tag_mutation():
#     """
#     Create an item, add some tags, remove some tags, check that the correct
#     state is preserved throughout.
#     """
#     item = TaskPaperItem('I am a test')
#
#     # Start by adding a series of tags
#     item.add_tag('hello')
#     item.add_tag(name='foo', value='bar')
#     item.add_tag(name='company', value='hogbay software')
#     item.add_tag(name='foo', value='baz')
#     print(item.tags)
#     assert item.tags == [
#         ('hello', ''),
#         ('foo', 'bar'),
#         ('company', 'hogbay software'),
#         ('foo', 'baz'),
#     ]
#
#     # Remove a tag by name only.  Check that all tags with this name are
#     # removed.
#     item.remove_tag(name='foo')
#     assert item.tags == [
#         ('hello', ''),
#         ('company', 'hogbay software'),
#     ]
#
#     # Remove a tag, specifying both the name and value.  Make sure that
#     # only this tag is removed.
#     item.add_tag(name='company', value='apple inc')
#     item.remove_tag(name='company', value='hogbay software')
#     assert item.tags == [
#         ('hello', ''),
#         ('company', 'apple inc'),
#     ]
#
#     # Using the set_tag method correctly updates the value of an
#     # existing tag
#     item.set_tag(name='hello', value='new_value')
#     assert item.tags == [
#         ('hello', 'new_value'),
#         ('company', 'apple inc'),
#     ]
#
#     # Using the set_tag method will create a new tag if the name doesn't
#     # already exist
#     item.set_tag(name='blue', value='aquamarine')
#     assert item.tags == [
#         ('hello', 'new_value'),
#         ('company', 'apple inc'),
#         ('blue', 'aquamarine'),
#     ]
#
# def test_tag_inclusion():
#     """
#     Create some tags, check they are correctly recognised as being part
#     of the tag list.
#     """
#     item = TaskPaperItem('I am a test @hello(world) @foo(bar) @baz')
#
#     # Check that if we only specify the name of the tag, we get the
#     # correct result.
#     for tag_name in ['hello', 'foo', 'baz']:
#         assert tag_name in item.tags
#     assert 'lorem' not in item.tags
#
#     # Check that if we specify a name and a value, we get the same
#     # result.
#     assert ('hello', 'world') in item.tags
#     assert ('foo', 'bar') in item.tags
#     assert ('lorem', 'ipsum') not in item.tags
#
#     # Check that nonsense objects are not in the list of tags
#     assert 47 not in item.tags
#     assert float('inf') not in item.tags
#     assert TaskPaperItem('tomato soup') not in item.tags
#
#
# def test_matching_tag_at_end_of_item_string():
#     """
#     Test that a tag at the end of an item is found correctly.
#     """
#     item = TaskPaperItem('Tag is right at the end @hello')
#     assert item.tags == [('hello', '')]
#
#     item2 = TaskPaperItem('Another item right at the end @hello(world)')
#     assert item2.tags == [('hello', 'world')]
#
#
# def test_matching_tag_at_start_of_item_string():
#     """
#     Test that a tag at the start of an item is found correctly.
#     """
#     item = TaskPaperItem('@hello Tag is at the very start')
#     assert item.tags == [('hello', '')]
#
#     item2 = TaskPaperItem('@hello(world) Another tag right at the start')
#     assert item2.tags == [('hello', 'world')]
#
#
# @pytest.mark.parametrize('bad_tag_name', [
#     47,
#     float('inf'),
#     TaskPaperItem('tomato soup'),
# ])
# def test_adding_bad_tag_names_is_rejected(bad_tag_name):
#     """
#     If we try to add a bad tag name to an item, we get a ValueError.
#     """
#     item = TaskPaperItem('I am a test @hello(world) @foo(bar) @baz')
#     with pytest.raises(ValueError):
#         item.add_tag(bad_tag_name)
#
#
# @pytest.mark.parametrize('bad_bool', [
#     42,
#     float('nan'),
#     'cabbage',
#     'strawberry custard',
#     1 + 2j,
# ])
# def test_setting_done_to_non_bool_is_error(bad_bool):
#     """
#     Trying to set the done status of an item to anything but True/False
#     is an error.
#     """
#     item = TaskPaperItem('I am an unfinished item.')
#     with pytest.raises(ValueError):
#         item.done = bad_bool
#
#
# @given(taglist_strategy())
# def test_creating_two_items_with_the_same_tags_gives_equal_tag_lists(taglist):
#     """
#     Two items given the same tags have equal tag lists.
#     """
#     item1 = TaskPaperItem('I am a test')
#     item2 = TaskPaperItem('A different test')
#
#     for t in taglist:
#         item1.add_tag(*t)
#         item2.add_tag(*t)
#
#     assert item1.tags == item2.tags
#
#
# @pytest.mark.parametrize('bad_item_string', [
#     'hello world @tag)',
#     'hello world @tag())',
#     'hello world @tag(value)a',
# ])
# def test_tag_followed_by_nonsense_char_is_ignored(bad_item_string):
#     """
#     A tag value followed by spurious parens isn't matched.  These examples
#     are obtained by experimenting with TaskPaper to see what it matches
#     as a tag.
#     """
#     item = TaskPaperItem(bad_item_string)
#     assert item.tags == []
#
#
# # TOOD: Swap this out for suppress_health_checks.
# @settings(perform_health_check=False)
# @given(taglist_strategy())
# def test_shuffling_tag_list_doesnt_affect_equality(taglist):
#     """
#     Tag lists are equal, modulo shuffling.
#     """
#     item1 = TaskPaperItem('I am a new test')
#     item2 = TaskPaperItem('Another different test')
#
#     for t in taglist:
#         item1.add_tag(*t)
#         item2.add_tag(*t)
#
#     # Shuffle the tags on item1, and check the tag lists remain equal.
#     random.shuffle(item1.tags)
#     assert item1.tags == item2.tags
#
#
# @given(taglist_strategy(), taglist_strategy())
# def test_different_taglists_of_different_lengths_are_unequal(list1, list2):
#     """
#     If two lists of tags have different length, they are never equal.
#     """
#     assume(len(list1) != len(list2))
#     item1 = TaskPaperItem('I am a new test')
#     item2 = TaskPaperItem('Another different test')
#
#     for t in list1:
#         item1.add_tag(*t)
#     for t in list2:
#         item2.add_tag(*t)
#
#     assert item1.tags != item2.tags
#
#
# @given(taglist_strategy())
# def test_round_trip_of_tag_items(taglist):
#     """
#     Casting an item with some tags to a string and back gets the same tags.
#     """
#     item = TaskPaperItem("I have no tags")
#     assert item.tags == []
#
#     for t in taglist:
#         item.add_tag(*t)
#
#     item_str = str(item)
#     new_item = TaskPaperItem(item_str)
#
#     assert new_item.tags == taglist
