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
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

import datetime
import os
import sys

top = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, top)

if True:  # Keep linters happy
    import pyodc


# -- Project information -----------------------------------------------------

project = "pyodc"
author = "ECMWF"

year = datetime.datetime.now().year
if year == 2021:
    years = "2021"
else:
    years = "2021-%s" % (year,)

copyright = "%s, %s" % (years, author)

# Get the current version directly from the package.
release = pyodc.__version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx_rtd_theme",
    "nbsphinx",
    "IPython.sphinxext.ipython_directive",
    "IPython.sphinxext.ipython_console_highlighting",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "'**.ipynb_checkpoints'"]

source_suffix = ".rst"
master_doc = "index"
pygments_style = "sphinx"

# https://www.notion.so/Deepnote-Launch-Buttons-63c642a5e875463495ed2341e83a4b2a

nbsphinx_prolog = """
{% set docname = env.doc2path(env.docname, base=None) %}

|Binder| |Colab| |Deepnote| |Kaggle|

.. |Binder| image:: https://mybinder.org/badge.svg
   :target: https://mybinder.org/v2/gh/ecmwf/pyodc/{{ env.config.release|e }}?urlpath=lab/tree/docs/{{ docname|e }}
   :alt: Binder
   :class: badge

.. |Colab| image:: https://colab.research.google.com/assets/colab-badge.svg
   :target: https://colab.research.google.com/github/ecmwf/pyodc/blob/{{ env.config.release|e }}/docs/{{ docname|e }}
   :alt: Colab
   :class: badge

.. |Deepnote| image:: https://img.shields.io/badge/launch%20in-deepnote-blue.svg
   :target: https://beta.deepnote.org/launch?template=deepnote&url=https://github.com/ecmwf/pyodc/blob/{{ env.config.release|e }}/docs/{{ docname|e }}
   :alt: Deepnote
   :class: badge

.. |Kaggle| image:: https://kaggle.com/static/images/open-in-kaggle.svg
   :target: https://kaggle.com/kernels/welcome?src=https://github.com/ecmwf/pyodc/blob/{{ env.config.release|e }}/docs/{{ docname|e }}
   :alt: Kaggle
   :class: badge

"""  # noqa

# ipython_warning_is_error = False


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_context = {"css_files": ["_static/style.css"]}

# Remove links to the reST sources from the page headers.
html_show_sourcelink = False

# Remove "Created using Sphinx" from the HTML footer.
html_show_sphinx = False

# html_theme_options = {'logo_only': True}
# html_logo = '_static/logo.png'


# -- Options for the autodoc  extension --------------------------------------

autodoc_member_order = "bysource"


# -- Options for the todo extension ------------------------------------------

# To disable output of `todo` blocks, just set the `NO_INCLUDE_TODOS` environment variable to any value, i.e:
#
#   NO_INCLUDE_TODOS=1
#
#   Unfortunately, this cannot be done via the configuration file for the Read the Docs service, you must use their web
#   interface instead. More information here: https://github.com/readthedocs/readthedocs.org/issues/6311
todo_include_todos = False if os.environ.get("NO_INCLUDE_TODOS") else True


# -- Options for the intersphinx extension ------------------------------------------

# Target the latest version when interlinking the projects
intersphinx_mapping = {
    "odc": ("https://odc.readthedocs.io/en/latest/", None),
}
