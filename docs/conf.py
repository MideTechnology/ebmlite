# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'ebmlite'
copyright = '2025, Midé Technology Corp.'
author = 'David R. Stokes'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
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
