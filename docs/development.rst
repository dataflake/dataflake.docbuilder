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
GitHub issue tracker at 
https://github.com/dataflake/dataflake.docbuilder/issues.


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

.. code-block:: sh

  $ bin/buildout -o
  $ python setup.py sdist bdist_wheel upload --sign

The ``bin/buildout`` step will make sure the correct package information 
is used.
