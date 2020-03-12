# -*- coding: utf-8 -*-
"""Sphinx configuration file."""
import time

author = "Jan Holthuis"
project = "sphinx-multiversion"
release = "0.1.1"
version = "0.1"
copyright = "{}, {}".format(time.strftime("%Y"), author)

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

mv_remote_whitelist = r"^origin$"
