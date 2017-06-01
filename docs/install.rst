Installation
============

You will need `Python <http://python.org>`_ version 2.7 or better to
run :mod:`dataflake.docbuilder`.

It is advisable to install :mod:`dataflake.docbuilder` into a
:term:`virtualenv` in order to obtain isolation from any "system"
packages you've got installed in your Python version (and likewise, 
to prevent :mod:`dataflake.docbuilder` from globally installing 
versions of packages that are not compatible with your system Python).

After you've got the requisite dependencies installed, you may install
:mod:`dataflake.docbuilder` into your Python environment using the 
following command::

  $ easy_install dataflake.docbuilder

or...::

  $ pip install dataflake.docbuilder

If you use :mod:`zc.buildout` you can add :mod:`dataflake.docbuilder`
to the necessary ``eggs`` section to have it pulled in automatically.
