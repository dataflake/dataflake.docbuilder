##############################################################################
#
# Copyright (c) 2010 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

__version__ = '1.4'

import os
import sys

from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

_boundary = '\n' + ('-' * 60) + '\n\n'
extra = {}
NAME = 'dataflake.docbuilder'

setup(name=NAME,
      version=__version__,
      description='Automated Sphix documentation builder',
      long_description=( read('README.txt') 
                       + _boundary 
                       + "Download\n========"
                       ),
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='sphinx documentation',
      author="Jens Vagelpohl and contributors",
      author_email="jens@dataflake.org",
      url="http://pypi.python.org/pypi/%s" % NAME,
      license="ZPL 2.1",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['dataflake'],
      install_requires=[
        'setuptools',
        'Sphinx',
        'docutils',
        'pkginfo',
        'zc.recipe.egg',
        ],
      zip_safe=False,
      test_suite='%s.tests' % NAME,
      entry_points = {
          'console_scripts': ['docbuilder = %s:run_builder' % NAME],
          'zc.buildout': ['default=%s:BuildoutScript' % NAME]
        },
      **extra
      )

