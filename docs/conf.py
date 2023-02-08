# -*- coding: utf-8 -*-
"""Sphinx configuration file."""
import time

author = "Jan Holthuis"
project = "sphinx-multiversion"
release = "0.2.12"
version = "0.2"
copyright = "{}, {}".format(time.strftime("%Y"), author)

html_theme = "alabaster"
html_theme_options = {
    "github_repo": "sphinx-multiversion",
    "github_user": "Holzhaus",
    "github_banner": True,
    "github_button": True,
    "travis_button": True,
    "show_relbar_bottom": True,
}
html_last_updated_fmt = "%c"
master_doc = "index"
pygments_style = "friendly"
templates_path = ["_templates"]
extensions = [
    "sphinx_multiversion",
]

templates_path = [
    "_templates",
]

html_sidebars = {
    "**": [
        "about.html",
        "navigation.html",
        "relations.html",
        "searchbox.html",
        "versioning.html",
    ],
}

smv_remote_whitelist = r"^origin$"
smv_branch_whitelist = r"^master$"
