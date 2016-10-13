# -*- encoding: utf-8 -*-

from hypothesis import given
from hypothesis.strategies import integers

from taskpaper import TaskPaperItem


@given(integers())
def test_setting_tab_size(tab_size):
    item = TaskPaperItem(tab_size=tab_size)
    assert item.tab_size == tab_size
