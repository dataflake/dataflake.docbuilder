Installation
============


Prerequisites
-------------
For cloning remote software repositories the software uses the version control
system client directly, so you must have the respective client package like
`git` installed on your system.


Install with ``pip``
--------------------

.. code:: 

    $ pip install dataflake.docbuilder


Install with ``zc.buildout``
----------------------------
Just add :mod:`dataflake.docbuilder` to the ``eggs`` setting(s) in your
buildout configuration to have it pulled in automatically::

    ...
    eggs =
        dataflake.docbuilder
    ...
