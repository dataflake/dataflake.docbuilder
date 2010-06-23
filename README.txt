======================
 dataflake.docbuilder
======================

This package provides a set of scripts to automate building
Sprinx-based package documentation for packages hosted on a 
Subversion revision control server. They will...

- check out the current development trunk and all tagged versions

- build all Sphinx-based documentation in them, if it exists

- stitch together the trunk and release versions in a single 
  HTML file to provide a simple jump-off page for all package 
  versions

- rebuild the Sphinx documentation if there were any changes 
  since the last build

Documentation
=============
Full documentation for the last released version is at 
http://packages.python.org/dataflake.docbuilder. For  
documentation matching the current SVN trunk please visit 
http://docs.dataflake.org/dataflake.docbuilder.

Bug tracker
===========
A bug tracker is available at https://bugs.launchpad.net/dataflake.docbuilder

SVN version
===========
You can retrieve the latest code from Subversion using setuptools or
zc.buildout via this URL:

http://svn.dataflake.org/svn/dataflake.docbuilder/trunk#egg=dataflake.docbuilder

