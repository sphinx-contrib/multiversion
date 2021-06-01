import os.path
import posixpath
import tempfile
import unittest
from unittest.mock import Mock

import sphinx_multiversion

mock = Mock()
myapp = mock.config
myapp.config.project = "example"


class VersionInfoTestCase(unittest.TestCase):
    def setUp(self):
        root = tempfile.gettempdir()

        self.versioninfo = sphinx_multiversion.sphinx.VersionInfo(
            app=myapp,
            context={"pagename": "testpage"},
            metadata={
                "master": {
                    "name": "master",
                    "version": "",
                    "release": "0.2",
                    "is_released": False,
                    "source": "heads",
                    "creatordate": "2020-08-07 07:45:20 -0700",
                    "basedir": os.path.join(root, "master"),
                    "sourcedir": os.path.join(root, "master", "docs"),
                    "outputdir": os.path.join(root, "build", "html", "master"),
                    "confdir": os.path.join(root, "master", "docs"),
                    "docnames": ["testpage", "appendix/faq"],
                    "build_targets": {
                        "HTML": {
                            "builder": "html",
                            "downloadable": True,
                            "download_format": "zip",
                        },
                    },
                },
                "v0.1.0": {
                    "name": "v0.1.0",
                    "version": "",
                    "release": "0.1.0",
                    "is_released": True,
                    "source": "tags",
                    "creatordate": "2020-07-16 08:45:20 -0100",
                    "basedir": os.path.join(root, "v0.1.0"),
                    "sourcedir": os.path.join(root, "v0.1.0", "docs"),
                    "outputdir": os.path.join(root, "build", "html", "v0.1.0"),
                    "confdir": os.path.join(root, "v0.1.0", "docs"),
                    "docnames": ["old_testpage", "appendix/faq"],
                    "build_targets": {
                        "HTML": {
                            "builder": "html",
                            "downloadable": True,
                            "download_format": "zip",
                        },
                    },
                },
                "branch-with/slash": {
                    "name": "branch-with/slash",
                    "version": "",
                    "release": "0.1.1",
                    "is_released": False,
                    "source": "heads",
                    "creatordate": "2020-08-06 11:53:06 -0400",
                    "basedir": os.path.join(root, "branch-with/slash"),
                    "sourcedir": os.path.join(
                        root, "branch-with/slash", "docs"
                    ),
                    "outputdir": os.path.join(
                        root, "build", "html", "branch-with/slash"
                    ),
                    "confdir": os.path.join(root, "branch-with/slash", "docs"),
                    "docnames": ["testpage"],
                    "build_targets": {
                        "HTML": {
                            "builder": "html",
                            "downloadable": True,
                            "download_format": "zip",
                        },
                    },
                },
            },
            current_version_name="master",
        )

    def test_tags_property(self):
        versions = self.versioninfo.tags
        self.assertEqual([version.name for version in versions], ["v0.1.0"])

    def test_branches_property(self):
        versions = self.versioninfo.branches
        self.assertEqual(
            [version.name for version in versions],
            ["master", "branch-with/slash"],
        )

    def test_releases_property(self):
        versions = self.versioninfo.releases
        self.assertEqual([version.name for version in versions], ["v0.1.0"])

    def test_in_development_property(self):
        versions = self.versioninfo.in_development
        self.assertEqual(
            [version.name for version in versions],
            ["master", "branch-with/slash"],
        )

    def test_vhasdoc(self):
        self.assertTrue(self.versioninfo.vhasdoc("master"))
        self.assertFalse(self.versioninfo.vhasdoc("v0.1.0"))
        self.assertTrue(self.versioninfo.vhasdoc("branch-with/slash"))

        self.versioninfo.context["pagename"] = "appendix/faq"
        self.assertTrue(self.versioninfo.vhasdoc("master"))
        self.assertTrue(self.versioninfo.vhasdoc("v0.1.0"))
        self.assertFalse(self.versioninfo.vhasdoc("branch-with/slash"))

    def test_vpathto(self):
        self.assertEqual(self.versioninfo.vpathto("master"), "testpage.html")
        self.assertEqual(
            self.versioninfo.vpathto("v0.1.0"),
            posixpath.join("..", "v0.1.0", "index.html"),
        )
        self.assertEqual(
            self.versioninfo.vpathto("branch-with/slash"),
            posixpath.join("..", "branch-with/slash", "testpage.html"),
        )

        self.versioninfo.context["pagename"] = "appendix/faq"
        self.assertEqual(self.versioninfo.vpathto("master"), "faq.html")
        self.assertEqual(
            self.versioninfo.vpathto("v0.1.0"),
            posixpath.join("..", "..", "v0.1.0", "appendix", "faq.html"),
        )
        self.assertEqual(
            self.versioninfo.vpathto("branch-with/slash"),
            posixpath.join("..", "..", "branch-with/slash", "index.html"),
        )

    def test_apathto(self):
        build_targets = {
            "HTML": {
                "builder": "html",
                "downloadable": True,
                "download_format": "zip",
            },
            "PDF": {
                "builder": "latexpdf",
                "downloadable": True,
                "download_format": "pdf",
            },
        }
        self.assertEqual(
            self.versioninfo.apathto("HTML", build_targets["HTML"]),
            posixpath.join("artefacts", "example_docs-master-HTML.zip"),
        )
        self.assertEqual(
            self.versioninfo.apathto("PDF", build_targets["PDF"]),
            "artefacts/example_docs-master.pdf",
        )

        mock_versioninfo = self.versioninfo
        mock_versioninfo.current_version_name = "branch-with/slash"

        self.versioninfo = Mock()
        self.versioninfo = mock_versioninfo
        self.assertEqual(
            self.versioninfo.apathto("PDF", build_targets["PDF"]),
            "artefacts/example_docs-branch-with-slash.pdf",
        )
