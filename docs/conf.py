# -*- coding: utf-8 -*-
"""Sphinx configuration file."""
import time

author = "Jan Holthuis"
project = "sphinx-multiversion"
release = "1.0.0"
version = "1.0"
copyright = "{}, {}".format(time.strftime("%Y"), author)

html_last_updated_fmt = "%c"
master_doc = "index"
pygments_style = "friendly"
templates_path = ["_templates"]
extensions = []
