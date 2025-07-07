# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import codecs
import os.path
import sys

# go up a dir and include that guy =
p = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, p)


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

def get_version(rel_path):
    """ Read the version number directly from the source. """
    with codecs.open(rel_path, 'r') as fp:
        for line in fp:
            if line.startswith('__version__'):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
        else:
            raise RuntimeError("Unable to find version string.")


project = 'ebmlite'
copyright = '2025, Midé Technology Corp.'
author = 'David R. Stokes'

# The full version, including alpha/beta/rc tags
release = get_version(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ebmlite', '__init__.py')))
# The short X.Y version
version = '.'.join(release.split(".")[:2])


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.githubpages',
    'sphinx_autodoc_typehints',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'venv', 'Thumbs.db', '.DS_Store']


# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

html_theme = 'pydata_sphinx_theme'
html_logo = '_static/endaq-logo-300x121.svg'
html_favicon = '_static/endaq-favicon.ico'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    "logo": {
        "link": "index"
    },
    "github_url": "https://github.com/MideTechnology/ebmlite",
    "twitter_url": "https://twitter.com/enDAQ_sensors",
    "collapse_navigation": True,
    "analytics": {
        "google_analytics_id": "G-E9QXH4H5LP",
    }
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Appends custom .css file
# https://docs.readthedocs.io/en/stable/guides/adding-custom-css.html#overriding-or-replacing-a-theme-s-stylesheet
html_style = "https://info.endaq.com/hubfs/docs/css/endaq-docs-style.css"

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}
