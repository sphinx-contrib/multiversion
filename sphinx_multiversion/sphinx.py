# -*- coding: utf-8 -*-
# Copyright (c) 2025 Jan Holthuis <jan.holthuis@rub.de>
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

import datetime
import json
import collections
import logging
import os
import posixpath

from sphinx import config as sphinx_config
from sphinx.util import i18n as sphinx_i18n
from sphinx.locale import _

logger = logging.getLogger(__name__)

DATE_FMT = "%Y-%m-%d %H:%M:%S %z"
DEFAULT_TAG_WHITELIST = r"^.*$"
DEFAULT_BRANCH_WHITELIST = r"^.*$"
DEFAULT_REMOTE_WHITELIST = None
DEFAULT_RELEASED_PATTERN = r"^tags/.*$"
DEFAULT_OUTPUTDIR_FORMAT = r"{ref.name}"
DEFAULT_TOPLEVELREF = None

Version = collections.namedtuple(
    "Version",
    [
        "name",
        "url",
        "version",
        "release",
        "is_released",
        "creatordate",
    ],
)


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
            creatordate=v["creatordate"],
        )

    @property
    def tags(self):
        return [
            self._dict_to_versionobj(v)
            for v in self.metadata.values()
            if v["source"] == "tags"
        ]

    @property
    def branches(self):
        return [
            self._dict_to_versionobj(v)
            for v in self.metadata.values()
            if v["source"] != "tags"
        ]

    @property
    def releases(self):
        return [
            self._dict_to_versionobj(v)
            for v in self.metadata.values()
            if v["is_released"]
        ]

    @property
    def in_development(self):
        return [
            self._dict_to_versionobj(v)
            for v in self.metadata.values()
            if not v["is_released"]
        ]

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
            return "{}.html".format(
                posixpath.split(self.context["pagename"])[-1]
            )

        # Find relative outputdir paths from common output root
        current_version = self.metadata[self.current_version_name]
        other_version = self.metadata[other_version_name]

        current_outputroot = os.path.abspath(current_version["outputdir"])
        other_outputroot = os.path.abspath(other_version["outputdir"])
        outputroot = os.path.commonpath((current_outputroot, other_outputroot))

        current_outputroot = os.path.relpath(
            current_outputroot, start=outputroot
        )
        other_outputroot = os.path.relpath(other_outputroot, start=outputroot)

        # Ensure that we use POSIX separators in the path (for the HTML code)
        if os.sep != posixpath.sep:
            current_outputroot = posixpath.join(
                *os.path.split(current_outputroot)
            )
            other_outputroot = posixpath.join(*os.path.split(other_outputroot))

        # Find relative path to root of other_version's outputdir
        current_outputdir = posixpath.dirname(
            posixpath.join(current_outputroot, self.context["pagename"])
        )
        other_outputdir = posixpath.relpath(
            other_outputroot, start=current_outputdir
        )

        if not self.vhasdoc(other_version_name):
            return posixpath.join(other_outputdir, "index.html")

        return posixpath.join(
            other_outputdir, "{}.html".format(self.context["pagename"])
        )


def format_date(value, format="%Y-%m-%d"):
    date_obj = datetime.datetime.strptime(
        value, DATE_FMT
    )  # Convert the date string to a datetime object
    return date_obj.strftime(format)  # Format to desired output


def html_page_context(app, pagename, templatename, context, doctree):
    versioninfo = VersionInfo(
        app, context, app.config.smv_metadata, app.config.smv_current_version
    )
    context["versions"] = versioninfo
    context["vhasdoc"] = versioninfo.vhasdoc
    context["vpathto"] = versioninfo.vpathto

    context["current_version"] = versioninfo[app.config.smv_current_version]
    context["latest_version"] = versioninfo[app.config.smv_latest_version]
    context["html_theme"] = app.config.html_theme

    # Add a filter to format the date
    app.builder.templates.environment.filters["format_date"] = format_date


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

    try:
        data = app.config.smv_metadata[config.smv_current_version]
    except KeyError:
        return

    app.connect("html-page-context", html_page_context)

    # Restore config values
    old_config = sphinx_config.Config.read(data["confdir"])
    old_config.pre_init_values()
    old_config.init_values()
    config.version = data["version"]
    config.release = data["release"]
    config.rst_prolog = data["rst_prolog"]
    config.today = old_config.today
    if not config.today:
        config.today = sphinx_i18n.format_date(
            format=config.today_fmt or _("%b %d, %Y"),
            date=datetime.datetime.strptime(data["creatordate"], DATE_FMT),
            language=config.language,
        )


def setup(app):
    app.add_config_value("smv_metadata", {}, "html")
    app.add_config_value("smv_metadata_path", "", "html")
    app.add_config_value("smv_current_version", "", "html")
    app.add_config_value("smv_latest_version", "master", "html")
    app.add_config_value("smv_tag_whitelist", DEFAULT_TAG_WHITELIST, "html")
    app.add_config_value(
        "smv_branch_whitelist", DEFAULT_BRANCH_WHITELIST, "html"
    )
    app.add_config_value(
        "smv_remote_whitelist", DEFAULT_REMOTE_WHITELIST, "html"
    )
    app.add_config_value(
        "smv_released_pattern", DEFAULT_RELEASED_PATTERN, "html"
    )
    app.add_config_value(
        "smv_outputdir_format", DEFAULT_OUTPUTDIR_FORMAT, "html"
    )
    app.add_config_value("smv_toplevelref", DEFAULT_TOPLEVELREF, "html")
    app.connect("config-inited", config_inited)

    return {
        "version": "0.2",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
