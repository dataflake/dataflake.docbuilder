=============
 Development
=============

Getting the source code
=======================
The source code is maintained in the Dataflake Git 
repository. To check out the trunk:

.. code-block:: sh

  $ git clone https://git.dataflake.org/git/dataflake.docbuilder

You can also browse the code online at 
http://git.dataflake.org/cgit


Bug tracker
===========
For bug reports, suggestions or questions please use the 
Launchpad bug tracker at 
`https://bugs.launchpad.net/dataflake.docbuilder 
<https://bugs.launchpad.net/dataflake.docbuilder>`_.


Sharing Your Changes
====================

If you got a read-only checkout from the Git repository, and you
have made a change you would like to share, the best route is to let
Git help you make a patch file:

.. code-block:: sh

   $ git diff > dataflake.docbuilder-cool_feature.patch

You can then upload that patch file as an attachment to a Launchpad bug
report.


Building the documentation in a ``virtualenv``
==============================================

:mod:`dataflake.docbuilder` uses the nifty :mod:`Sphinx` documentation system
for building its docs. If you use the ``virtualenv`` package to create 
lightweight Python development environments, you can build the documentation 
using nothing more than the ``python`` binary in a virtualenv.  First, create 
a scratch environment:

.. code-block:: sh

   $ /path/to/virtualenv --no-site-packages /tmp/virtualpy

Next, get this package registered as a "development egg" in the
environment:

.. code-block:: sh

   $ /tmp/virtualpy/bin/python setup.py develop

Now you can build the documentation:

.. code-block:: sh

   $ cd docs
   $ PATH=/tmp/virtualpy/bin:$PATH make html
   sphinx-build -b html -d _build/doctrees   . _build/html
   ...
   build succeeded.

   Build finished. The HTML pages are in _build/html.


Building the documentation using :mod:`zc.buildout`
===================================================

:mod:`dataflake.docbuilder` ships with its own :file:`buildout.cfg` file and
:file:`bootstrap.py` for setting up a development buildout:

.. code-block:: sh

  $ python bootstrap.py
  ...
  Generated script '.../bin/buildout'
  $ bin/buildout
  ...
  Generated script '...bin/docbuilder'.
  ...
  Generated script '...bin/docbuilderdocs'.

The :mod:`dataflake.docbuilder` buildout installs the Sphinx scripts required 
to build the documentation, including testing its code snippets:

.. code-block:: sh

   $ cd docs
   $ PATH=../bin:$PATH make html
   sphinx-build -b html -d _build/doctrees   . _build/html
   ...
   build succeeded.

   Build finished. The HTML pages are in _build/html.


Making a release
================

These instructions assume that you have a development sandbox set 
up using :mod:`zc.buildout` as the scripts used here are generated 
by the buildout.

The first thing to do when making a release is to check that the ReST
to be uploaded to PyPI is valid:

.. code-block:: sh

  $ bin/docpy setup.py --long-description | bin/rst2 html \
    --link-stylesheet \
    --stylesheet=http://www.python.org/styles/styles.css > build/desc.html

Once you're certain everything is as it should be, the following will
build the distribution, upload it to PyPI, register the metadata with
PyPI and upload the Sphinx documentation to PyPI:

.. code-block:: sh

  $ bin/buildout -o
  $ bin/docpy setup.py sdist register upload upload_sphinx --upload-dir=docs/_build/html

The ``bin/buildout`` step will make sure the correct package information 
is used.

