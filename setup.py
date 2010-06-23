##############################################################################
#
# Copyright (c) 2009-2010 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

__version__ = '1.3dev'

import os
import sys

from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

_boundary = '\n' + ('-' * 60) + '\n\n'
extra = {}

#if sys.version_info >= (3,):
#    # Python 3 support:
#    extra['use_2to3'] = True
#    extra['setup_requires'] = ['zope.fixers']
#    extra['use_2to3_fixers'] = ['zope.fixers']
#    extra['convert_2to3_doctests'] = ['docs/usage.rst']

setup(name='dataflake.docbuilder',
      version=__version__,
      description='Simple caching library',
      long_description=( read('README.txt') 
                       + _boundary 
                       + "Download\n========"
                       ),
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
#        "Programming Language :: Python :: 3",
#        "Programming Language :: Python :: 3.1",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Sphinx documentation',
      author="Jens Vagelpohl and contributors",
      author_email="jens@dataflake.org",
      url="http://pypi.python.org/pypi/dataflake.docbuilder",
      license="ZPL 2.1",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['dataflake'],
      install_requires=[
        'setuptools',
        'zope.interface',
        ],
      zip_safe=False,
      test_suite='dataflake.docbuilder.tests',
      **extra
      )

