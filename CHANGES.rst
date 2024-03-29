Change log
==========

2.6 (unreleased)
----------------


2.5 (2024-03-14)
----------------

- Switch to PEP 420 implicit namespace support.

- Add support for Python 3.13.


2.4 (2024-01-03)
----------------

- Add support for Python 3.12.


2.3 (2023-02-06)
----------------

- Fix index page link creation


2.2 (2023-02-06)
----------------

- Fix breakage attempting to activate invalid distributions


2.1 (2022-02-06)
----------------

- Add support for older Git versions.


2.0 (2023-02-06)
----------------

- Drop support for documentation generated with ``z3c.recipe.sphinx``.

- Drop support for Subversion and Mercurial.

- Drop option ``copy-output``. Always copy HTML output to HTML output folder.

- Add support for Python 3.8, 3.9, 3.10, 3.11.

- Drop support for Python 2.7, 3.5, 3.6.


1.23 (2018-10-16)
-----------------
- make sure to convert shell output to unicode on Python 3 and 2.
- before invoking ``setup.py`` commands in a subshell, make sure
  it is present.


1.22 (2018-07-22)
-----------------
- add option ``-n`` to skip checkout and build of software packages


1.21 (2018-06-29)
-----------------
- test and declare support for Python 3.7


1.20 (2017-06-01)
-----------------
- use pkgutil-style namespace declaration
- package cleanup (``.gitignore``, ``MANIFEST.in``, ``README.rst``)
- docs cleanup (``Makefile``, ``conf.py``)
- tests cleanup (``tox.ini``)
- remove unsupported documentation bits


1.19 (2017-05-29)
-----------------
- Python 3 compatibility


1.18 (2017-05-29)
-----------------
- added tox configuration to do PEP-8 checking with ``flake8``
- PEP 8 code cleanup


1.17 (2017-05-27)
-----------------
- If output folders don't exist yet create them instead of failing.
- Use the name ``development`` instead of ``trunk`` or ``head`` to
  designate the current development version in the rendered index page.
- If a version control URL does not specify which version control
  system is used, `Git` is now used as default instead of `Subversion`.
- Moved the repository to GitHub and its documentation to ReadTheDocs


1.16 (2014-11-25)
-----------------
- added flag ``-c``/``--copy-output`` which will copy instead of link
  all HTML output into the folder designated as HTML output folder.


1.15 (2014-11-21)
-----------------
- switched documentation to point to the new Git repository
- use new bootstrap.py script


1.14 (2011-11-29)
-----------------
- Add a flag ``-m``/``--max-tags`` to set the number of package
  versions (tags) to be shown on the generated main page. If more
  tags exist, a link to a separate page is provided that shows all
  versions.


1.13 (2011-10-31)
-----------------
- Catch additional errors upon building
- Ignoring empty tag lists when asking Git for tags


1.12 (2011-08-30)
-----------------
- Be more resilient when simple ReST text compilation or 
  Sphinx building fails. Now the whole documentation build 
  process won't just fail at that point.
- provide more meaningful log messages when running with 
  the ``-v`` option.


1.11 (2011-08-09)
-----------------
- Now you can use ``Git`` alongside ``Mercurial`` and 
  ``Subversion`` to use as version control system.


1.10 (2011-08-09)
-----------------
- Taking more control of logging by defining our own logger and
  suppressing standard Sphinx log output. The new script flag 
  ``-v`` or ``--verbose`` enables the user to determine what to 
  show. Without it, only serious warnings are shown. With ``-v``
  specified once you will see script progress output and notes 
  about Sphinx build warnings. With ``-vv`` all Sphinx output 
  is shown as well.


1.9 (2011-08-09)
----------------
- Now using pkg_resources.parse_version to parse the tag names and 
  produce correct release ordering for each package
- Instead of using a flag to set the revision control system 
  across all packages you now specify the revision control system 
  per package with a simple prefix::

    [hg]http://myserver/hg/mypackage
    [svn]https://myservr/svnmypackage

  For backwards compatibility, all URLs without prefix are assumed 
  to point to a Subversion repository.


1.8 (2011-08-05)
----------------
- Feature: You can now use either ``Subversion`` or ``Mercurial``
  to check out documented packages.


1.7 (2010-08-03)
----------------
- Feature: If no standard package documentation can be found, 
  the setuptools ``long_description`` settings is used as a 
  last fallback to at least generate a single page for a package.

- Feature: To style the ``long_description`` fallback ReST 
  documentation, a new parameter ``fallback-css`` can be used to 
  provide a path to a CSS file.


1.6 (2010-07-31)
----------------
- Bug: If the ``z3csphinx-output-directory`` was set, all its 
  contained packages ended up on the index document. Now this 
  only happens if no SVN source URLs are otherwise provided.
  If they are, only packages from those source URLs are 
  considered for linking on the index document.


1.5 (2010-07-31)
----------------
- Feature: If you generate some documentation via 
  `z3c.recipe.sphinxdoc` and want to stitch links to it 
  into the generated index file, you can use the new 
  ``z3csphinx-output-directory`` parameter to point the script 
  to the generated package documentation root folder.


1.4 (2010-07-31)
----------------
- Bug: Don't clean up intermediate files, otherwise it is not 
  possible to re-use a template folder for creating several
  separate pages into an output folder.

- Bug: Clean up group header creation to avoid header level
  mixups.

- Bug: When creating a missing required index.rst, use a 
  template file if it exists.


1.3 (2010-07-30)
----------------
- Feature: Added a script and buildout option ``index-name`` to 
  specify the file name (without extension) for the index page.
  With this option you can safely build the index page into an 
  existing `Sphinx` documentation folder without overwriting 
  or changing the existing ``index.rst`` file and its HTML 
  equivalent. The default continues to be ``index.rst``, though.

- Feature removed: It is no longer possible to create a simple HTML
  index page without using `Sphinx` and a minimal `Sphinx` 
  configuration.


1.2 (2010-07-29)
----------------
- Feature: Add new script option ``-g``/``--grouping`` and zc.buildout 
  option ``grouping`` to group packages.

- Miscellaneous: Renamed the zc.buildout option `source` to `sources`
  since it contains one or more elements.

- Miscellaneous: Removed the version pinning on the Sphinx dependency 
  since our other dependency (repoze.sphinx.autointerface) is now 
  compatible with Sphinx 1.0.

- Bug: If pkg_resources.find_distributions cannot find valid
  Egg distributions we still force the tag folder itself into the 
  pkg_resources.working_set as a fallback.


1.1 (2010-07-25)
----------------
- Feature: The user can now provide a Sphinx configuration folder 
  path that will be used to generate additional content for the 
  documentation root folder.

- Factoring: Moved the DocsBuilder class into its own module.

- Factoring: Save run state on the documentation builder class 
  instead of handing it around

- Cosmetic: Use a flat hierarchy when creating the HTML output links
  instead of a folder per package. Only a single index page needs to 
  be created that way.


1.0 (2010-07-23)
----------------
- Initial release
