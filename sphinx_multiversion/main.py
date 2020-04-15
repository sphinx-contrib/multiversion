# -*- coding: utf-8 -*-
import itertools
import argparse
import json
import logging
import os
import pathlib
import re
import string
import subprocess
import sys
import tempfile

from sphinx.cmd import build as sphinx_build
from sphinx import config as sphinx_config
from sphinx import project as sphinx_project

from . import sphinx
from . import git


def main(argv=None):
    if not argv:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser()
    parser.add_argument("sourcedir", help="path to documentation source files")
    parser.add_argument("outputdir", help="path to output directory")
    parser.add_argument(
        "filenames",
        nargs="*",
        help="a list of specific files to rebuild. Ignored if -a is specified",
    )
    parser.add_argument(
        "-c",
        metavar="PATH",
        dest="confdir",
        help=(
            "path where configuration file (conf.py) is located "
            "(default: same as SOURCEDIR)"
        ),
    )
    parser.add_argument(
        "-C",
        action="store_true",
        dest="noconfig",
        help="use no config file at all, only -D options",
    )
    parser.add_argument(
        "-D",
        metavar="setting=value",
        action="append",
        dest="define",
        default=[],
        help="override a setting in configuration file",
    )
    parser.add_argument(
        "--dump-metadata",
        action="store_true",
        help="dump generated metadata and exit",
    )
    args, argv = parser.parse_known_args(argv)
    if args.noconfig:
        return 1

    # Conf-overrides
    confoverrides = {}
    for d in args.define:
        key, _, value = d.partition("=")
        confoverrides[key] = value

    # Parse config
    config = sphinx_config.Config.read(
        os.path.abspath(args.confdir if args.confdir else args.sourcedir),
        confoverrides,
    )
    config.add("smv_tag_whitelist", sphinx.DEFAULT_TAG_WHITELIST, "html", str)
    config.add(
        "smv_branch_whitelist", sphinx.DEFAULT_TAG_WHITELIST, "html", str
    )
    config.add(
        "smv_remote_whitelist", sphinx.DEFAULT_REMOTE_WHITELIST, "html", str
    )
    config.add(
        "smv_released_pattern", sphinx.DEFAULT_RELEASED_PATTERN, "html", str
    )
    config.add(
        "smv_outputdir_format", sphinx.DEFAULT_OUTPUTDIR_FORMAT, "html", str
    )
    config.add("smv_prefer_remote_refs", False, "html", bool)
    config.pre_init_values()
    config.init_values()

    # Get git references
    gitroot = pathlib.Path(".").resolve()
    gitrefs = git.get_refs(
        str(gitroot),
        config.smv_tag_whitelist,
        config.smv_branch_whitelist,
        config.smv_remote_whitelist,
    )

    # Order git refs
    if config.smv_prefer_remote_refs:
        gitrefs = sorted(gitrefs, key=lambda x: (not x.is_remote, *x))
    else:
        gitrefs = sorted(gitrefs, key=lambda x: (x.is_remote, *x))

    logger = logging.getLogger(__name__)

    # Get Sourcedir
    sourcedir = os.path.relpath(args.sourcedir, str(gitroot))
    if args.confdir:
        confdir = os.path.relpath(args.confdir, str(gitroot))
    else:
        confdir = sourcedir

    with tempfile.TemporaryDirectory() as tmp:
        # Generate Metadata
        metadata = {}
        outputdirs = set()
        for gitref in gitrefs:
            # Clone Git repo
            repopath = os.path.join(tmp, gitref.commit)
            try:
                git.copy_tree(gitroot.as_uri(), repopath, gitref)
            except (OSError, subprocess.CalledProcessError):
                logger.error(
                    "Failed to copy git tree for %s to %s",
                    gitref.refname,
                    repopath,
                )
                continue

            # Find config
            confpath = os.path.join(repopath, confdir)
            try:
                current_config = sphinx_config.Config.read(
                    confpath, confoverrides,
                )
            except (OSError, sphinx_config.ConfigError):
                logger.error(
                    "Failed load config for %s from %s",
                    gitref.refname,
                    confpath,
                )
                continue
            current_config.pre_init_values()
            current_config.init_values()

            # Ensure that there are not duplicate output dirs
            outputdir = config.smv_outputdir_format.format(
                ref=gitref, config=current_config,
            )
            if outputdir in outputdirs:
                logger.warning(
                    "outputdir '%s' for %s conflicts with other versions",
                    outputdir,
                    gitref.refname,
                )
                continue
            outputdirs.add(outputdir)

            # Get List of files
            source_suffixes = current_config.source_suffix
            if isinstance(source_suffixes, str):
                source_suffixes = [current_config.source_suffix]

            current_sourcedir = os.path.join(repopath, sourcedir)
            project = sphinx_project.Project(
                current_sourcedir, source_suffixes
            )
            metadata[gitref.name] = {
                "name": gitref.name,
                "version": current_config.version,
                "release": current_config.release,
                "is_released": bool(
                    re.match(config.smv_released_pattern, gitref.refname)
                ),
                "source": gitref.source,
                "creatordate": gitref.creatordate.strftime(sphinx.DATE_FMT),
                "sourcedir": current_sourcedir,
                "outputdir": os.path.join(
                    os.path.abspath(args.outputdir), outputdir
                ),
                "confdir": os.path.abspath(confdir),
                "docnames": list(project.discover()),
            }

        if args.dump_metadata:
            print(json.dumps(metadata, indent=2))
            return

        if not metadata:
            logger.error("No matching refs found!")
            return

        # Write Metadata
        metadata_path = os.path.abspath(os.path.join(tmp, "versions.json"))
        with open(metadata_path, mode="w") as fp:
            json.dump(metadata, fp, indent=2)

        # Run Sphinx
        argv.extend(["-D", "smv_metadata_path={}".format(metadata_path)])
        for version_name, data in metadata.items():
            os.makedirs(data["outputdir"], exist_ok=True)

            defines = itertools.chain(
                *(
                    ("-D", string.Template(d).safe_substitute(data))
                    for d in args.define
                )
            )

            current_argv = argv.copy()
            current_argv.extend(
                [
                    *defines,
                    "-D",
                    "smv_current_version={}".format(version_name),
                    "-c",
                    data["confdir"],
                    data["sourcedir"],
                    data["outputdir"],
                    *args.filenames,
                ]
            )
            logger.debug("Running sphinx-build with args: %r", current_argv)
            status = sphinx_build.build_main(current_argv)
            if status not in (0, None):
                break
