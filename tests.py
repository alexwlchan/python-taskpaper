#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import pytest

from taskpaper import TaskPaperItem


tag_examples = [
    # Example with no tags
    ['lorem ipsum', []],

    # Example with one tag, name-only
    ['hello @world', [('world', '')]],

    # Example with one tag, both name and value
    ['foo @bar(baz)', [('bar', 'baz')]],

    # Example with two tags, one name-only, one name and value
    ['quick @brown(fox) @jumps', [('brown', 'fox'), ('jumps', '')]]
]

@pytest.mark.parametrize('item_text,tags', tag_examples)
def test_tag_parsing(item_text, tags):
    """
    Create some items which contain tags, and check the tags are
    recognised correctly.
    """
    item = TaskPaperItem(item_text)
    assert item.tags == tags


def test_tag_mutation():
    """
    Create an item, add some tags, remove some tags, check that the correct
    state is preserved throughout.
    """
    item = TaskPaperItem('I am a test')

    # Start by adding a series of tags
    item.add_tag('hello')
    item.add_tag(name='foo', value='bar')
    item.add_tag(name='company', value='hogbay software')
    item.add_tag(name='foo', value='baz')
    print(item.tags)
    assert item.tags == [
        ('hello', ''),
        ('foo', 'bar'),
        ('company', 'hogbay software'),
        ('foo', 'baz'),
    ]

    # Remove a tag by name only.  Check that all tags with this name are
    # removed.
    item.remove_tag(name='foo')
    assert item.tags == [
        ('hello', ''),
        ('company', 'hogbay software'),
    ]

    # Remove a tag, specifying both the name and value.  Make sure that
    # only this tag is removed.
    item.add_tag(name='company', value='apple inc')
    item.remove_tag(name='company', value='hogbay software')
    assert item.tags == [
        ('hello', ''),
        ('company', 'apple inc'),
    ]


def test_tag_inclusion():
    """
    Create some tags, check they are correctly recognised as being part
    of the tag list.
    """
    item = TaskPaperItem('I am a test @hello(world) @foo(bar) @baz')

    # Check that if we only specify the name of the tag, we get the
    # correct result.
    for tag_name in ['hello', 'foo', 'baz']:
        assert tag_name in item.tags
    assert 'lorem' not in item.tags

    # Check that if we specify a name and a value, we get the same
    # result.
    assert ('hello', 'world') in item.tags
    assert ('foo', 'bar') in item.tags
    assert ('lorem', 'ipsum') not in item.tags

    # Check that nonsense objects are not in the list of tags
    assert 47 not in item.tags
    assert float('inf') not in item.tags
    assert TaskPaperItem('tomato soup') not in item.tags



@pytest.mark.parametrize('bad_tag', [
    47,
    float('inf'),
    TaskPaperItem('tomato soup'),
])
def test_adding_bad_tags_is_rejected(bad_tag):
    """
    If we try to add a bad tag to an item, we get a ValueError.
    """
    item = TaskPaperItem('I am a test @hello(world) @foo(bar) @baz')
    with pytest.raises(ValueError):
        item.add_tag(bad_tag)


