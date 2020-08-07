import os
import re
import runpy
import subprocess
import sys

import docutils.nodes
import docutils.parsers.rst
import docutils.utils
import docutils.frontend


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

    changelog_pattern = re.compile(r"^Version (\S+)((?: \(unreleased\)))?$")

    matchobj = changelog_pattern(visitor.sectiontitles_found[1])
    assert matchobj
    version = matchobj.group(1)
    version_unreleased = matchobj.group(2)

    matchobj = changelog_pattern(visitor.sectiontitles_found[2])
    assert matchobj
    release = matchobj.group(1)
    release_unreleased = matchobj.group(2)

    if version_unreleased:
        assert release_unreleased

    return version, release


def get_sphinxconfpy_version(rootdir):
    """Get version from Sphinx' conf.py."""
    sphinx_conf = runpy.run_path(os.path.join(rootdir, "docs", "conf.py"))
    version, sep, bugfix = sphinx_conf["release"].rpartition(".")
    assert sep == "."
    assert bugfix
    assert version == sphinx_conf["version"]
    return sphinx_conf["version"], sphinx_conf["release"]


def get_setuppy_version(rootdir):
    """Get version from setup.py."""
    setupfile = os.path.join(rootdir, "setup.py")
    cmd = (sys.executable, setupfile, "--version")
    release = subprocess.check_output(cmd, text=True).rstrip("\n")
    version = release.rpartition(".")[0]
    return version, release


def main():
    rootdir = os.path.join(os.path.dirname(__file__), "..")

    setuppy_version, setuppy_release = get_setuppy_version(rootdir)
    confpy_version, confpy_release = get_setuppy_version(rootdir)
    changelog_version, changelog_release = get_setuppy_version(rootdir)

    version_head = "Version"
    version_width = max(
        [
            len(version_head),
            len(setuppy_version),
            len(confpy_version),
            len(changelog_version),
        ]
    )

    release_head = "Release"
    release_width = max(
        [
            len(release_head),
            len(setuppy_release),
            len(confpy_release),
            len(changelog_release),
        ]
    )

    print(
        f"File                            {version_head} {release_head}\n"
        f"------------------------------- {'-' * version_width}"
        f" {'-' * release_width}\n"
        f"setup.py                        {setuppy_version:>{version_width}}"
        f" {setuppy_release:>{release_width}}\n"
        f"docs/conf.py                    {confpy_version:>{version_width}}"
        f" {confpy_release:>{release_width}}\n"
        f"docs/changelog.rst              {changelog_version:>{version_width}}"
        f" {changelog_release:>{release_width}}\n"
    )

    assert setuppy_version == confpy_version
    assert setuppy_version == changelog_version

    assert setuppy_release == confpy_release
    assert setuppy_release == changelog_release


if __name__ == "__main__":
    main()
