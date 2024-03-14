##############################################################################
#
# Copyright (c) 2010-2023 Jens Vagelpohl and Contributors. All Rights Reserved.
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

from setuptools import setup


def read(*rnames):
    with open(os.path.join(os.path.dirname(__file__), *rnames)) as f:
        return f.read()


setup(name='dataflake.docbuilder',
      version='2.5.dev0',
      description='Automated Sphinx documentation builder',
      long_description=read('README.rst'),
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='sphinx documentation',
      author="Jens Vagelpohl and contributors",
      author_email="jens@dataflake.org",
      url="https://github.com/dataflake/dataflake.docbuilder",
      project_urls={
        'Documentation': 'https://dataflakedocbuilder.readthedocs.io/',
        'Sources': 'https://github.com/dataflake/dataflake.docbuilder',
        'Issue Tracker': ('https://github.com/dataflake/'
                          'dataflake.docbuilder/issues'),
      },
      license="ZPL 2.1",
      packages=['dataflake.docbuilder'],
      package_dir={'': 'src'},
      include_package_data=True,
      python_requires='>=3.7',
      install_requires=[
        'setuptools',
        'sphinx',
        'zc.buildout',
        'zc.recipe.egg',
        ],
      extras_require={
        'docs': ['pkginfo',
                 'sphinx_rtd_theme',
                 ],
        },
      zip_safe=False,
      entry_points={
        'console_scripts': ['docbuilder = dataflake.docbuilder:run_builder'],
        'zc.buildout': ['default=dataflake.docbuilder:BuildoutScript']
        },
      )
