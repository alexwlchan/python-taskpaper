# -*- encoding: utf-8 -*-

from hypothesis.strategies import builds, text

from taskpaper import TaskPaperItem


def taskpaper_item_strategy():
    return builds(
        TaskPaperItem,
        text=text()
    )
