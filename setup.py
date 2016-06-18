#!/usr/bin/env python

# -----------------------------------------------------------------------------
# Copyright (c) 2013, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------
from setuptools import setup
from glob import glob

__version__ = "0.2.0-dev"


classes = """
    Development Status :: 3 - Alpha
    License :: OSI Approved :: BSD License
    Topic :: Scientific/Engineering :: Bio-Informatics
    Topic :: Software Development :: Libraries :: Application Frameworks
    Topic :: Software Development :: Libraries :: Python Modules
    Programming Language :: Python
    Programming Language :: Python :: 2.7
    Programming Language :: Python :: Implementation :: CPython
    Operating System :: POSIX :: Linux
    Operating System :: MacOS :: MacOS X
"""

long_description = ''

classifiers = [s.strip() for s in classes.split('\n') if s]

setup(name='qiime-scaling',
      version=__version__,
      long_description=long_description,
      license="BSD",
      description='qiime scaling',
      author="jose navas",
      author_email="",
      url='https://github.com/biocore/qiime-scaling',
      test_suite='nose.collector',
      packages=['scaling',
                'scaling/commands',
                'scaling/interfaces',
                'scaling/interfaces/optparse'
                ],
      include_package_data=True,
      package_data={
         },
      scripts=glob('scripts/*'),
      extras_require={'test': ["nose >= 0.10.1"]},
      install_requires=['pyqi', 'numpy'],
      classifiers=classifiers
      )
