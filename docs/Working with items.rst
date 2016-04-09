Working with items
==================

The ``TaskPaperItem`` class lets you interact with an item.  It is
instantiated from a single line of a TaskPaper document.

For example::

   >>> from taskpaper import TaskPaperItem
   >>> item = TaskPaperItem('- Buy some apples')

You can manipulate the tags and completion status of an item, or get
it back as a string at any time::

   >>> str(item)
   '- Buy some apples'

Working with tags
*****************

In TaskPaper, tags are an ``@`` symbol followed by a name.  A tag can have
a value in parentheses after the tag name.  For example::

   - Buy some apples @food @priority(2)

This item has two tags:

*  a ``food`` tag
*  the ``priority`` tag with value ``2``

Here are some ways you can work with tags:

*  **View the tags on an item.**  Use the ``tags`` attribute::

      >>> item = TaskPaperItem('- Buy some apples @food @priority(2)')
      >>> item.tags
      [('food', ''), ('priority', '2')

   Each of these tags has a ``name`` and a ``value`` attribute.  For example::

      >>> for tag in item.tags:
      ...     print(tag.name, tag.value)
      ...
      food
      priority 2

   In general, you can treat the ``tags`` attribute like a regular list.  Any
   methods that work on a regular list will work here.  Note that a tag can
   either be a *name* string, or a 2-tuple (*name*, *value*).

*  **Check if an item has a particular tag.**  You can use ``in`` to check
   if an item has a tag.  This supports either a *name* string, or a 2-tuple
   (*name*, *value*).  For example::

      >>> 'food' in item.tags
      True
      >>> ('priority', '2') in item.tags
      True
      >>> 'work' in item.tags
      False

*  **Set a tag on an item.**  You can set a tag with the ``set_tag`` method,
   by providing a name and a value.

   If there's an existing tag with the same name, it gets overriden.
   Otherwise, a new tag is created::

      >>> item.set_tag('priority', '3')
      >>> item.set_tag('shopping', 'groceries')
      >>> str(item)
      '- Buy some apples @food @priority(3) @shopping(groceries)'

   The value of the ``priority`` tag has been changed to ``3``, and the
   ``shopping`` tag has been created with value ``groceries``.

*  **Add a new tag.**  The ``add_tag`` method is like the ``set_tag`` method,
   but it won't overwrite an existing tag::

      >>> item.add_tag('priority', '4')
      >>> str(item)
      '- Buy some apples @food @priority(3) @shopping(groceries) @priority(4)'

   There's a new ``priority`` tag with value ``4``, but the existing tag has
   been unaffected.

   .. note:: This method might go away in a future version.  TaskPaper doesn't
             recognise two tags with the same name on a single item.

*  **Remove a tag.**  The ``remove_tag`` method lets you remove a tag.  You
   can specify a *name*, which removes any tag with that name, or both a name
   and a value, in which case only tags that match both will be removed::

      >>> item.remove_tag('priority')
      >>> str(item)
      '- Buy some apples @food @shopping(groceries)'

      >>> item.remove_tag('shopping', 'petrol')
      >>> str(item)
      '- Buy some apples @food @shopping(groceries)'

      >>> item.remove_tag('shopping', 'groceries')
      >>> str(item)
      '- Buy some apples @food'

Setting the completion state of a task
**************************************

The ``@done`` tag has special meaning in TaskPaper.  In the Mac app, any items
marked with ``@done`` will be struck through, to indicate that they're complete.

You can query and set the completion state of a task with the ``done``
attribute::

   >>> item.done
   False
   >>> item.done = True
   >>> item.done
   True

The ``done_date`` method will let you look up the date when a task was
completed.  This throws a ``TaskPaperError`` if the task isn't done yet.

::

   >>> item.done_date()
   '2016-04-09'

You can set the done date explicitly with the ``set_done_date()`` method.
If you set it with ``item.done = True``, it will default to the current day's
date.

::

   >>> item.set_done_date('2015-03-08')
   >>> item.done_date()
   '2015-03-08'