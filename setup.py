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

import os

from setuptools import find_packages
from setuptools import setup


NAME = 'dataflake.docbuilder'


def read(*rnames):
    with open(os.path.join(os.path.dirname(__file__), *rnames)) as f:
        return f.read()


setup(name=NAME,
      version=read('version.txt').strip(),
      description='Automated Sphinx documentation builder',
      long_description=read('README.rst'),
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='sphinx documentation',
      author="Jens Vagelpohl and contributors",
      author_email="jens@dataflake.org",
      url="https://github.com/dataflake/%s" % NAME,
      license="ZPL 2.1",
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
        'setuptools',
        'Sphinx',
        'docutils',
        'zc.buildout',
        'zc.recipe.egg',
        ],
      zip_safe=False,
      entry_points={
        'console_scripts': ['docbuilder = %s:run_builder' % NAME],
        'zc.buildout': ['default=%s:BuildoutScript' % NAME]
        },
      )
