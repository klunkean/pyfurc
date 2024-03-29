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
import os
import sys

sys.path.insert(0, os.path.abspath("../../pyfurc/"))


# -- Project information -----------------------------------------------------

project = "pyfurc"
copyright = "2021, klunkean"
author = "klunkean"

# The full version, including alpha/beta/rc tags
release = "0.2.3"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosectionlabel",
    "sphinxcontrib.bibtex",
    # "sphinx_lesson.directives",
    # "jupyter_sphinx"
]

bibtex_bibfiles = ["_static/pyfurcbib.bib"]

napoleon_google_docstring = False
napoleon_use_param = False
napoleon_use_ivar = True

intersphinx_mapping = {
    "sympy": ("https://docs.sympy.org/latest/", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

autoclass_content = "class"
autodoc_dumb_docstring = True

# -- Options for HTML output -------------------------------------------------
html_theme = "pydata_sphinx_theme"
html_sidebars = {
    "**": [
        "globaltoc.html",
        "searchbox.html",
        # "sidebar-nav-bs.html",
    ]
}
html_theme_options = {
    "show_toc_level": 2,
    # "page_sidebar_items": ["page-toc"],
}

html_logo = "_static/logo.png"

html_favicon = "_static/favicon.png"

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]


# From Stackoverflow to omit listing object as a class's base.
# ClassDocumenter.add_directive_header uses ClassDocumenter.add_line to
#   write the class documentation.
# We'll monkeypatch the add_line method and intercept lines that begin
#   with "Bases:".
# In order to minimize the risk of accidentally intercepting a wrong line,
#   we'll apply this patch inside of the add_directive_header method.

from sphinx.ext.autodoc import ClassDocumenter, _

add_line = ClassDocumenter.add_line
line_to_delete = _("Bases: %s") % ":class:`object`"


def add_line_no_object_base(self, text, *args, **kwargs):
    if text.strip() == line_to_delete:
        return

    add_line(self, text, *args, **kwargs)


add_directive_header = ClassDocumenter.add_directive_header


def add_directive_header_no_object_base(self, *args, **kwargs):
    self.add_line = add_line_no_object_base.__get__(self)

    result = add_directive_header(self, *args, **kwargs)

    del self.add_line

    return result


ClassDocumenter.add_directive_header = add_directive_header_no_object_base
