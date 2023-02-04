Development
===========

Bug tracker
-----------
For bug reports, suggestions or questions please use the 
GitHub issue tracker at 
https://github.com/dataflake/dataflake.docbuilder/issues.


Getting the source code
-----------------------
The source code is maintained on GitHub. To check out the main branch:

.. code-block:: console

  $ git clone https://github.com/dataflake/dataflake.docbuilder.git

You can also browse the code online at
https://github.com/dataflake/dataflake.docbuilder


Preparing the development sandbox
---------------------------------
The following steps only need to be done once to install all the tools and
scripts needed for building, packaging and testing. First, create a
:term:`Virtual environment`. The example here uses Python 3.11, but any Python
version supported by this package will work. Then install all the required
tools:

.. code-block:: console

    $ cd dataflake.docbuilder
    $ python3.11 -m venv .
    $ bin/pip install -U pip wheel
    $ bin/pip install -U setuptools zc.buildout tox twine


Building the documentation
--------------------------
``tox`` is also used to build the :term:`Sphinx`-based documentation. The
input files are in the `docs` subfolder and the documentation build step will
compile them to HTML. The output is stored in `docs/_build/html/`:

.. code-block:: console

    $ bin/tox -edocs

If the documentation contains doctests they are run as well.
