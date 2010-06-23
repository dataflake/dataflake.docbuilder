Using dataflake.docbuilder
==========================

:mod:`dataflake.docbuilder` provides several cache implementations 
with a shared simplified API.

Using a SimpleCache object:

.. doctest::

    >>> from dataflake.docbuilder.simple import SimpleCache
    >>> cache = SimpleCache()
    >>> cache.set('key1', 'value1')
    >>> cache.get('key1')
    'value1'
    >>> cache.invalidate('key1')
    >>> cache.get('key1', default='not available')
    'not available'

To attach a specific lifetime to cached items, a cache 
implementation with built-in timeout is provided as well:

.. doctest::

    >>> import time
    >>> from dataflake.docbuilder.timeout import TimeoutCache
    >>> cache = TimeoutCache()
    >>> cache.setTimeout(1)
    >>> cache.set('key1', 'value1')
    >>> cache.get('key1')
    'value1'
    >>> time.sleep(1)
    >>> cache.get('key1', default='not available')
    'not available'

Both the simple and timeout caches are available as thread-safe 
implementations using locks, see the :ref:`simple_cache_module` 
and :ref:`timeout_cache_module` documentation.

The :ref:`api_interfaces_section` page contains more
information about the cache APIs.

