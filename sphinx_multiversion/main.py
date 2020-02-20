# -*- coding: utf-8 -*-
import os
import json
import pathlib
import subprocess
import sys
import tempfile

from sphinx.cmd import build as sphinx_build
from sphinx import project as sphinx_project

from . import sphinx
from . import git


def main(argv=None):
    if not argv:
        argv = sys.argv[1:]

    parser = sphinx_build.get_parser()
    args = parser.parse_args(argv)

    # Find the indices
    srcdir_index = None
    outdir_index = None
    for i, value in enumerate(argv):
        if value == args.sourcedir:
            argv[i] = '{{{SOURCEDIR}}}'
            test_args = parser.parse_args(argv)
            if test_args.sourcedir == argv[i]:
                srcdir_index = i
            argv[i] = args.sourcedir

        if value == args.outputdir:
            argv[i] = '{{{OUTPUTDIR}}}'
            test_args = parser.parse_args(argv)
            if test_args.outputdir == argv[i]:
                outdir_index = i
            argv[i] = args.outputdir

    if srcdir_index is None:
        raise ValueError("Failed to find srcdir index")
    if outdir_index is None:
        raise ValueError("Failed to find outdir index")

    # Parse config
    confpath = os.path.join(args.confdir, 'conf.py')
    with open(confpath, mode='r') as f:
        config = sphinx.parse_conf(f.read())

    for d in args.define:
        key, _, value = d.partition('=')
        config[key] = value

    tag_whitelist = config.get('smv_tag_whitelist', sphinx.DEFAULT_TAG_WHITELIST)
    branch_whitelist = config.get('smv_branch_whitelist', sphinx.DEFAULT_BRANCH_WHITELIST)
    remote_whitelist = config.get('smv_remote_whitelist', sphinx.DEFAULT_REMOTE_WHITELIST)
    outputdir_format = config.get('smv_outputdir_format', sphinx.DEFAULT_OUTPUTDIR_FORMAT)

    gitroot = pathlib.Path('.').resolve()
    versions = git.find_versions(str(gitroot), 'source/conf.py', tag_whitelist, branch_whitelist, remote_whitelist)

    with tempfile.TemporaryDirectory() as tmp:
        # Generate Metadata
        metadata = {}
        outputdirs = set()
        sourcedir = os.path.relpath(args.sourcedir, str(gitroot))
        for versionref in versions:
            # Ensure that there are not duplicate output dirs
            outputdir = sphinx.format_outputdir(
                outputdir_format, versionref, language=config["language"])
            if outputdir in outputdirs:
                print("outputdir '%s' of version %r conflicts with other versions!"
                      % (outputdir, versionref))
                continue
            outputdirs.add(outputdir)

            # Clone Git repo
            repopath = os.path.join(tmp, str(hash(versionref)))
            srcdir = os.path.join(repopath, sourcedir)
            try:
                git.shallow_clone(gitroot.as_uri(), repopath, versionref.name)
            except subprocess.CalledProcessError:
                outputdirs.remove(outputdir)
                continue

            # Get List of files
            source_suffixes = config.get("source_suffix", "")
            if isinstance(source_suffixes, str):
                source_suffixes = [source_suffixes]
            project = sphinx_project.Project(srcdir, source_suffixes)
            metadata[versionref.name] = {
                "name": versionref.name,
                "version": versionref.version,
                "release": versionref.release,
                "source": versionref.source,
                "sourcedir": srcdir,
                "outputdir": outputdir,
                "docnames": list(project.discover())
            }
        metadata_path = os.path.abspath(os.path.join(tmp, "versions.json"))
        with open(metadata_path, mode='w') as fp:
            json.dump(metadata, fp, indent=2)

        # Run Sphinx
        argv.extend(["-D", "smv_metadata_path={}".format(metadata_path)])
        for version_name, data in metadata.items():
            current_argv = argv.copy()
            current_argv.extend([
                "-D", "smv_current_version={}".format(version_name),
            ])

            outdir = os.path.join(args.outputdir, data["outputdir"])
            current_argv[srcdir_index] = data["sourcedir"]
            current_argv[outdir_index] = outdir
            os.makedirs(outdir, exist_ok=True)
            status = sphinx_build.build_main(current_argv)
            if status not in (0, None):
                break
