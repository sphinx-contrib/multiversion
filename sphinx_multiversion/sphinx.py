# -*- coding: utf-8 -*-
import json
import pathlib
import collections
import importlib.abc
import logging
import os
import posixpath

logger = logging.getLogger(__name__)

DEFAULT_TAG_WHITELIST = r'^.*$'
DEFAULT_BRANCH_WHITELIST = r'^.*$'
DEFAULT_REMOTE_WHITELIST = None
DEFAULT_RELEASED_PATTERN = r'^tags/.*$'
DEFAULT_OUTPUTDIR_FORMAT = r'{config.version}/{config.language}'

Version = collections.namedtuple('Version', [
    'name',
    'url',
    'version',
    'release',
    'is_released',
])


class VersionInfo:
    def __init__(self, app, context, metadata, current_version_name):
        self.app = app
        self.context = context
        self.metadata = metadata
        self.current_version_name = current_version_name

    def _dict_to_versionobj(self, v):
        return Version(
            name=v["name"],
            url=self.vpathto(v["name"]),
            version=v["version"],
            release=v["release"],
            is_released=v["is_released"],
        )

    @property
    def tags(self):
        return [self._dict_to_versionobj(v) for v in self.metadata.values()
                if v["source"] == "tags"]

    @property
    def branches(self):
        return [self._dict_to_versionobj(v) for v in self.metadata.values()
                if v["source"] != "tags"]

    @property
    def releases(self):
        return [self._dict_to_versionobj(v) for v in self.metadata.values()
                if v["is_released"]]

    @property
    def in_development(self):
        return [self._dict_to_versionobj(v) for v in self.metadata.values()
                if not v["is_released"]]

    def __iter__(self):
        for item in self.tags:
            yield item
        for item in self.branches:
            yield item

    def __getitem__(self, name):
        v = self.metadata.get(name)
        if v:
            return self._dict_to_versionobj(v)

    def vhasdoc(self, other_version_name):
        if self.current_version_name == other_version_name:
            return True

        other_version = self.metadata[other_version_name]
        return self.context["pagename"] in other_version["docnames"]

    def vpathto(self, other_version_name):
        if self.current_version_name == other_version_name:
            return '{}.html'.format(
                posixpath.split(self.context["pagename"])[-1])

        # Find output root
        current_version = self.metadata[self.current_version_name]
        relpath = pathlib.PurePath(current_version["outputdir"])
        outputroot = os.path.join(
            *('..' for x in relpath.joinpath(self.context["pagename"]).parent.parts)
        )

        # Find output dir of other version
        other_version = self.metadata[other_version_name]
        outputdir = posixpath.join(outputroot, other_version["outputdir"])

        if not self.vhasdoc(other_version_name):
            return posixpath.join(outputdir, 'index.html')

        return posixpath.join(outputdir, '{}.html'.format(self.context["pagename"]))


def parse_conf(config):
    module = {}
    code = importlib.abc.InspectLoader.source_to_code(config)
    exec(code, module)
    return module


def html_page_context(app, pagename, templatename, context, doctree):
    versioninfo = VersionInfo(
        app, context, app.config.smv_metadata, app.config.smv_current_version)
    context["versions"] = versioninfo
    context["vhasdoc"] = versioninfo.vhasdoc
    context["vpathto"] = versioninfo.vpathto

    context["current_version"] = versioninfo[app.config.smv_current_version]
    context["latest_version"] = versioninfo[app.config.smv_latest_version]
    context["html_theme"] = app.config.html_theme



def config_inited(app, config):
    """Update the Sphinx builder.
    :param sphinx.application.Sphinx app: Sphinx application object.
    """

    if not config.smv_metadata:
        if not config.smv_metadata_path:
            return

        with open(config.smv_metadata_path, mode="r") as f:
            metadata = json.load(f)

        config.smv_metadata = metadata

    if not config.smv_current_version:
        return

    app.connect("html-page-context", html_page_context)

    # Restore config values
    conf_path = os.path.join(app.srcdir, "conf.py")
    with open(conf_path, mode="r") as f:
        conf = parse_conf(f.read())
        config.version = conf['version']
        config.release = conf['release']


def setup(app):
    app.add_config_value("smv_metadata", {}, "html")
    app.add_config_value("smv_metadata_path", "", "html")
    app.add_config_value("smv_current_version", "", "html")
    app.add_config_value("smv_latest_version", "master", "html")
    app.add_config_value("smv_tag_whitelist", DEFAULT_TAG_WHITELIST, "html")
    app.add_config_value("smv_branch_whitelist", DEFAULT_BRANCH_WHITELIST, "html")
    app.add_config_value("smv_remote_whitelist", DEFAULT_REMOTE_WHITELIST, "html")
    app.add_config_value("smv_released_pattern", DEFAULT_RELEASED_PATTERN, "html")
    app.add_config_value("smv_outputdir_format", DEFAULT_OUTPUTDIR_FORMAT, "html")
    app.connect("config-inited", config_inited)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
