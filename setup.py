#!/usr/bin/env python
# encoding: utf-8
"""
This file contains the setup for setuptools to distribute everything as a
(PyPI) package.

This is a modernized version of madmom for Python 3.11+ and NumPy 2.x+.
"""

from setuptools import setup, Extension
from Cython.Build import cythonize

import numpy as np

# define version
version = '0.17.0'

# define which extensions to compile
include_dirs = [np.get_include()]

# Cython compiler directives for modern compatibility
compiler_directives = {
    'language_level': 3,
    'boundscheck': False,
    'wraparound': False,
}

extensions = [
    Extension(
        'madmom.audio.comb_filters',
        ['madmom/audio/comb_filters.pyx'],
        include_dirs=include_dirs,
    ),
    Extension(
        'madmom.features.beats_crf',
        ['madmom/features/beats_crf.pyx'],
        include_dirs=include_dirs,
    ),
    Extension(
        'madmom.ml.hmm',
        ['madmom/ml/hmm.pyx'],
        include_dirs=include_dirs,
    ),
]

# the actual setup routine
# Most configuration is now in pyproject.toml
# This file is retained for Cython extension compilation
setup(
    ext_modules=cythonize(
        extensions,
        compiler_directives=compiler_directives,
    ),
)
