=============
 Development
=============

Getting the source code
=======================
The source code is maintained on GitHub. To check out the trunk:

.. code-block:: sh

  $ git clone https://github.com/dataflake/dataflake.docbuilder.git

You can also browse the code online at
https://github.com/dataflake/dataflake.docbuilder


Bug tracker
===========
For bug reports, suggestions or questions please use the 
GitHub bug tracker at 
https://github.com/dataflake/dataflake.docbuilder/issues.


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
by the buildout. The `twine` package is required for uploading the
release packages.

.. code-block:: sh

  $ bin/buildout -o
  $ bin/python setup.py sdist bdist_wheel
  $ gpg --detach-sign -a dist/dataflake.docbuilder-NNN.tar.gz
  $ gpg --detach-sign -a dist/dataflake.docbuilder-NNN-py2.py3-none-any.whl
  $ twine upload dist/dataflake.docbuilder-NNN.tar.gz dist/dataflake.docbuilder-NNN.tar.gz.asc
  $ twine upload dist/dataflake.docbuilder-NNN-py2.py3-none-any.whl dist/dataflake.docbuilder-NNN-py2.py3-none-any.whl.asc

The ``bin/buildout`` step will make sure the correct package information 
is used.

