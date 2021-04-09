# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#

import builtins
import glob
import inspect
import re
import shutil

import os
import sys
import sphinx_rtd_theme
import quickvision

PATH_HERE = os.path.abspath(os.path.dirname(__file__))
PATH_ROOT = os.path.join(PATH_HERE, '..', '..')
sys.path.insert(0, os.path.abspath(PATH_ROOT))


# -- Project information -----------------------------------------------------

project = 'quickvision'
copyright = '2020, Quick-AI'
author = 'Quick-AI'

# The full version, including alpha/beta/rc tags
release = '0.1.0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinx_rtd_theme", "sphinx.ext.autodoc", "sphinx_autodoc_typehints", "recommonmark",
              "sphinx_copybutton", "sphinx_togglebutton", "sphinx_paramlinks", "sphinx_autodoc_typehints"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

nbsphinx_execute = 'never'
nbsphinx_allow_errors = True
nbsphinx_requirejs_path = ''

source_suffix = {'.rst': 'restructuredtext', '.txt': 'markdown', '.md': 'markdown', '.ipynb': 'nbsphinx',}

# The master toctree document.
master_doc = 'index'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = None

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'pytorch_lightning': ('https://pytorch-lightning.readthedocs.io/en/stable/', None),
    'python': ('https://docs.python.org/3', None),
    'torch': ('https://pytorch.org/docs/stable/', None),
    'numpy': ('https://docs.scipy.org/doc/numpy/', None),
    'PIL': ('https://pillow.readthedocs.io/en/stable/', None),
}

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# define mapping from PyPI names to python imports
PACKAGE_MAPPING = {
    'pytorch-lightning': 'pytorch_lightning',
    'scikit-learn': 'sklearn',
    'Pillow': 'PIL',
    'opencv-python': 'cv2',
}

# only run doctests marked with a ".. doctest::" directive
doctest_test_doctest_blocks = ''
doctest_global_setup = """
import importlib
import os
import torch
import quickvision

"""
