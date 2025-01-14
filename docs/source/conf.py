# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

import geolab

project = "geolab"
copyright = "2023, geolab"
author = "Patrick Boateng"
release = geolab.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.doctest",
    "sphinxcontrib.bibtex",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx_copybutton",
    "sphinx_design",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = []

# -- References ------------------------------
# https://sphinxcontrib-bibtex.readthedocs.io/en/latest/quickstart.html

bibtex_bibfiles = ["refs.bib"]
bibtex_default_style = "unsrt"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_title = "geolab"
html_static_path = ["_static"]
html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/patrickboateng/geolab",
            "icon": "fab fa-github-square",
            "type": "fontawesome",
        },
    ],
}
