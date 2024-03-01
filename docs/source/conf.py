# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import sphinx_rtd_theme


project = 'motormongo'
copyright = '2024, Patrick Prunty'
author = 'Patrick Prunty'
release = '0.1.13'
html_theme = 'sphinx_rtd_theme'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx_rtd_theme',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = []

# import os
# import sys
# sys.path.insert(0, os.path.abspath('../..'))
#
# # Set the path to your package's modules
# import motormongo


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ['_static']
numfig = True
html_secnumber_suffix = '. '
# html_theme = 'alabaster'
