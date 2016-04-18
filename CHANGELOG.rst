Release history
===============

0.3 (2016-04-18)
****************

*  Drop the ``done_date()``, ``mark_done()`` and ``set_done_date()`` methods,
   in favour of just looking up ``done`` as a regular tag.
*  Add the ability to get an item's ``type`` (either ``project``, ``task`` or
   ``note``).
*  Make the ``links`` and ``tags`` attributes editable in a more sensible way.
   Docs to follow.

0.2 (2016-04-09)
****************

*  In 0.1a, you set the completion state of a task with ``mark_done()`` and
   ``mark_undone()``.  Move to using attributes only, which is more Pythonic.
*  Rudimentary support for handling links on items with the ``links``
   attribute.

0.1a  (2016-04-05)
******************

*  Initial PyPI release.  Supports viewing/editing the tags of a task, and
   viewing/setting the done status.
*  Should have been 0.1, but I screwed up trying to upload 0.1 to PyPI, so
   I called it 0.1a instead.