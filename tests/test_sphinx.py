import os.path
import posixpath
import tempfile
import unittest

import sphinx_multiversion


class VersionInfoTestCase(unittest.TestCase):
    def setUp(self):
        root = tempfile.gettempdir()

        self.versioninfo = sphinx_multiversion.sphinx.VersionInfo(
            app=None,
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
