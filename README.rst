.. image:: https://readthedocs.org/projects/dataflakedocbuilder/badge/?version=latest
   :target: https://dataflakedocbuilder.readthedocs.io
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/dataflake.docbuilder.svg
   :target: https://pypi.python.org/pypi/dataflake.docbuilder
   :alt: PyPI

.. image:: https://img.shields.io/pypi/pyversions/dataflake.docbuilder.svg
   :target: https://pypi.python.org/pypi/dataflake.docbuilder
   :alt: Python versions


======================
 dataflake.docbuilder
======================

This package provides a set of scripts to automate building
Sphinx-based package documentation for packages hosted on a 
source code revision control server such as Subversion, 
Git or Mercurial. They will...

  * check out the current development trunk and all tagged versions
  * build all Sphinx-based documentation in them, if it exists
  * stitch together the trunk and release versions in a single 
    HTML file to provide a simple jump-off page for all package 
    versions
  * rebuild the Sphinx documentation if there were any changes 
    since the last build
