=============
 Development
=============

Getting the source code
=======================
The source code is maintained in the Dataflake Subversion 
repository. To check out the trunk:

.. code-block:: sh

  $ svn co http://svn.dataflake.org/svn/dataflake.docbuilder/trunk/

You can also browse the code online at 
`http://svn.dataflake.org/viewvc/dataflake.docbuilder
<http://svn.dataflake.org/viewvc/dataflake.docbuilder/>`_.

When using setuptools or zc.buildout you can use the following 
URL to retrieve the latest development code as Python egg:

.. code-block:: sh

  $ http://svn.dataflake.org/svn/dataflake.docbuilder/trunk#egg=dataflake.docbuilder


Bug tracker
===========
For bug reports, suggestions or questions please use the 
Launchpad bug tracker at 
`https://bugs.launchpad.net/dataflake.docbuilder 
<https://bugs.launchpad.net/dataflake.docbuilder>`_.


Sharing Your Changes
====================

.. note::

   Please ensure that all tests are passing before you submit your code.
   If possible, your submission should include new tests for new features
   or bug fixes, although it is possible that you may have tested your
   new code by updating existing tests.

If you got a read-only checkout from the Subversion repository, and you
have made a change you would like to share, the best route is to let
Subversion help you make a patch file:

.. code-block:: sh

   $ svn diff > dataflake.docbuilder-cool_feature.patch

You can then upload that patch file as an attachment to a Launchpad bug
report.

Running the tests in a ``virtualenv``
=====================================
If you use the ``virtualenv`` package to create lightweight Python
development environments, you can run the tests using nothing more
than the ``python`` binary in a virtualenv.  First, create a scratch
environment:

.. code-block:: sh

   $ /path/to/virtualenv --no-site-packages /tmp/virtualpy

Next, get this package registered as a "development egg" in the
environment:

.. code-block:: sh

   $ /tmp/virtualpy/bin/python setup.py develop

Finally, run the tests using the build-in ``setuptools`` testrunner:

.. code-block:: sh

   $ /tmp/virtualpy/bin/python setup.py test
   running test
   ...
   test_timeout (dataflake.docbuilder.tests.test_timeout.TestTimeoutCache) ... ok
   
   ----------------------------------------------------------------------
   Ran 22 tests in 0.619s
   
   OK

If you have the :mod:`nose` package installed in the virtualenv, you can
use its testrunner too:

.. code-block:: sh

   $ /tmp/virtualpy/bin/easy_install nose
   ...
   $ /tmp/virtualpy/bin/python setup.py nosetests
   running nosetests
   .........................
   ----------------------------------------------------------------------
   Ran 25 tests in 0.647s

   OK

or:

.. code-block:: sh

   $ /tmp/virtualpy/bin/nosetests
   .........................
   ----------------------------------------------------------------------
   Ran 25 tests in 0.649s

   OK

If you have the :mod:`coverage` package installed in the virtualenv,
you can see how well the tests cover the code:

.. code-block:: sh

   $ /tmp/virtualpy/bin/easy_install nose coverage
   ...
   $ /tmp/virtualpy/bin/python setup.py nosetests \
       --with-coverage --cover-package=dataflake.docbuilder
   running nosetests
   ...
   Name                         Stmts   Exec  Cover   Missing
   ----------------------------------------------------------
   dataflake.docbuilder                  1      1   100%   
   dataflake.docbuilder.interfaces      12     12   100%   
   dataflake.docbuilder.simple          39     39   100%   
   dataflake.docbuilder.timeout         61     61   100%   
   dataflake.docbuilder.utils           25     10    40%   20-37
   ----------------------------------------------------------
   TOTAL                          138    123    89%   
   ----------------------------------------------------------------------
   Ran 25 tests in 0.668s

   OK

Building the documentation in a ``virtualenv``
==============================================

:mod:`dataflake.docbuilder` uses the nifty :mod:`Sphinx` documentation system
for building its docs.  Using the same virtualenv you set up to run the
tests, you can build the docs:

.. code-block:: sh

   $ cd docs
   $ PATH=/tmp/virtualpy/bin:$PATH make html
   sphinx-build -b html -d _build/doctrees   . _build/html
   ...
   build succeeded.

   Build finished. The HTML pages are in _build/html.

You can also test the code snippets in the documentation:

.. code-block:: sh

   $ PATH=/tmp/virtualpy/bin:$PATH make doctest
   sphinx-build -b doctest -d _build/doctrees   . _build/doctest
   ...
   running tests...

   Document: usage
   ---------------
   1 items passed all tests:
     14 tests in default
   14 tests in 1 items.
   14 passed and 0 failed.
   Test passed.
   
   Doctest summary
   ===============
      14 tests
       0 failures in tests
       0 failures in setup code
   build succeeded.
   Testing of doctests in the sources finished, look at the \
        results in _build/doctest/output.txt.


Running the tests using  :mod:`zc.buildout`
===========================================

:mod:`dataflake.docbuilder` ships with its own :file:`buildout.cfg` file and
:file:`bootstrap.py` for setting up a development buildout:

.. code-block:: sh

  $ python bootstrap.py
  ...
  Generated script '.../bin/buildout'
  $ bin/buildout
  ...
  Generated script '/usr/local/py26/dataflake.docbuilder/bin/pkginfo'.
  Generated interpreter '/usr/local/py26/dataflake.docbuilder/bin/docpy'.

Once you have a buildout, the tests can be run as follows:

.. code-block:: sh

   Running tests at all levels
   Running zope.testing.testrunner.layer.UnitTests tests:
     Set up zope.testing.testrunner.layer.UnitTests in 0.000 seconds.
     Running:
   .......................
     Ran 23 tests with 0 failures and 0 errors in 1.615 seconds.
   Tearing down left over layers:
     Tear down zope.testing.testrunner.layer.UnitTests in 0.000 seconds.


Building the documentation using :mod:`zc.buildout`
===================================================

The :mod:`dataflake.docbuilder` buildout installs the Sphinx scripts required 
to build the documentation, including testing its code snippets:

.. code-block:: sh

   $ cd docs
   $ PATH=../bin:$PATH make doctest html
   .../bin/sphinx-build -b doctest -d .../docs/_build/doctrees   \
        .../docs .../docs/_build/doctest
   ...
   running tests...

   Document: usage
   ---------------
   1 items passed all tests:
     14 tests in default
   14 tests in 1 items.
   14 passed and 0 failed.
   Test passed.
   
   Doctest summary
   ===============
      14 tests
       0 failures in tests
       0 failures in setup code
   build succeeded.
   Testing of doctests in the sources finished, look at the  results in \
        .../docs/_build/doctest/output.txt.
   .../bin/sphinx-build -b html -d .../docs/_build/doctrees   \
        .../docs .../docs/_build/html
   ...
   build succeeded.

   Build finished. The HTML pages are in .../docs/_build/html.


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

