#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2024 Jan Holthuis <jan.holthuis@rub.de>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# SPDX-License-Identifier: BSD-2-Clause

import importlib.util
import os
import pkgutil
import re
import runpy
import sys

import docutils.nodes
import docutils.parsers.rst
import docutils.utils
import docutils.frontend

CHANGELOG_PATTERN = re.compile(r"^Version (\S+)((?: \(.+\)))?$")


def parse_rst(text: str) -> docutils.nodes.document:
    parser = docutils.parsers.rst.Parser()
    components = (docutils.parsers.rst.Parser,)
    settings = docutils.frontend.OptionParser(
        components=components
    ).get_default_values()
    document = docutils.utils.new_document("<rst-doc>", settings=settings)
    parser.parse(text, document)
    return document


class SectionVisitor(docutils.nodes.NodeVisitor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sectiontitles_found = []

    def visit_section(self, node: docutils.nodes.section) -> None:
        """Called for "section" nodes."""
        title = node[0]
        assert isinstance(title, docutils.nodes.title)
        self.sectiontitles_found.append(title.astext())

    def unknown_visit(self, node: docutils.nodes.Node) -> None:
        """Called for all other node types."""
        pass


def get_sphinxchangelog_version(rootdir):
    with open(os.path.join(rootdir, "docs", "changelog.rst"), mode="r") as f:
        doc = parse_rst(f.read())

    visitor = SectionVisitor(doc)
    doc.walk(visitor)

    unique_sectiontitles = set(visitor.sectiontitles_found)
    assert len(visitor.sectiontitles_found) == len(unique_sectiontitles)
    assert visitor.sectiontitles_found[0] == "Changelog"

    matchobj = CHANGELOG_PATTERN.match(visitor.sectiontitles_found[1])
    assert matchobj
    version = matchobj.group(1)
    version_date = matchobj.group(2)

    matchobj = CHANGELOG_PATTERN.match(visitor.sectiontitles_found[2])
    assert matchobj
    release = matchobj.group(1)
    release_date = matchobj.group(2)

    if version_date:
        assert version_date == release_date

    return version, release


def get_sphinxconfpy_version(rootdir):
    """Get version from Sphinx' conf.py."""
    sphinx_conf = runpy.run_path(os.path.join(rootdir, "docs", "conf.py"))
    version, sep, bugfix = sphinx_conf["release"].rpartition(".")
    assert sep == "."
    assert bugfix
    assert version == sphinx_conf["version"]
    return sphinx_conf["version"], sphinx_conf["release"]


def get_package_version(rootdir):
    """Get version from package __init__.py."""
    sys.path.insert(0, os.path.join(rootdir))
    for modinfo in pkgutil.walk_packages(path=[rootdir]):
        if modinfo.ispkg and modinfo.name == "sphinx_multiversion":
            break
    else:
        raise FileNotFoundError("package not found")

    spec = modinfo.module_finder.find_spec(modinfo.name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    release = mod.__version__
    version = release.rpartition(".")[0]

    return version, release


def main():
    rootdir = os.path.join(os.path.dirname(__file__), "..")

    package_version, package_release = get_package_version(rootdir)
    confpy_version, confpy_release = get_sphinxconfpy_version(rootdir)
    changelog_version, changelog_release = get_sphinxchangelog_version(rootdir)

    version_head = "Version"
    version_width = max(
        (
            len(repr(x))
            for x in (
                version_head,
                package_version,
                confpy_version,
                changelog_version,
            )
        )
    )

    release_head = "Release"
    release_width = max(
        (
            len(repr(x))
            for x in (
                release_head,
                package_release,
                confpy_release,
                changelog_release,
            )
        )
    )

    print(
        f"File                            {version_head} {release_head}\n"
        f"------------------------------- {'-' * version_width}"
        f" {'-' * release_width}\n"
        f"sphinx_multiversion/__init__.py"
        f" {package_version!r:>{version_width}}"
        f" {package_release!r:>{release_width}}\n"
        f"docs/conf.py                   "
        f" {confpy_version!r:>{version_width}}"
        f" {confpy_release!r:>{release_width}}\n"
        f"docs/changelog.rst             "
        f" {changelog_version!r:>{version_width}}"
        f" {changelog_release!r:>{release_width}}\n"
    )

    assert package_version == confpy_version
    assert package_version == changelog_version

    assert package_release == confpy_release
    assert package_release == changelog_release


if __name__ == "__main__":
    main()
