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

import collections
import datetime
import logging
import os
import re
import subprocess
import tarfile
import tempfile

GitRef = collections.namedtuple(
    "VersionRef",
    [
        "name",
        "commit",
        "source",
        "is_remote",
        "refname",
        "creatordate",
    ],
)

logger = logging.getLogger(__name__)


def get_toplevel_path(cwd=None):
    cmd = (
        "git",
        "rev-parse",
        "--show-toplevel",
        "--show-superproject-working-tree",
    )
    output = subprocess.check_output(cmd, cwd=cwd).decode()
    # If this is a git submodule of a super project then we'll have two lines
    # of output, otherwise one. Since the superproject flag is second in the
    # command above the superproject will always be the last line if present.
    return output.split()[-1]


def get_all_refs(gitroot):
    cmd = (
        "git",
        "for-each-ref",
        "--format",
        "%(objectname)\t%(refname)\t%(creatordate:iso)",
        "refs",
    )
    output = subprocess.check_output(cmd, cwd=gitroot).decode()
    for line in output.splitlines():
        is_remote = False
        fields = line.strip().split("\t")
        if len(fields) != 3:
            continue

        commit = fields[0]
        refname = fields[1]
        creatordate = datetime.datetime.strptime(
            fields[2], "%Y-%m-%d %H:%M:%S %z"
        )

        # Parse refname
        matchobj = re.match(
            r"^refs/(heads|tags|remotes/[^/]+)/(\S+)$", refname
        )
        if not matchobj:
            continue
        source = matchobj.group(1)
        name = matchobj.group(2)

        if source.startswith("remotes/"):
            is_remote = True

        yield GitRef(name, commit, source, is_remote, refname, creatordate)


def get_refs(
    gitroot, tag_whitelist, branch_whitelist, remote_whitelist, files=()
):
    for ref in get_all_refs(gitroot):
        if ref.source == "tags":
            if tag_whitelist is None or not re.match(tag_whitelist, ref.name):
                logger.debug(
                    "Skipping '%s' because tag '%s' doesn't match the "
                    "whitelist pattern",
                    ref.refname,
                    ref.name,
                )
                continue
        elif ref.source == "heads":
            if branch_whitelist is None or not re.match(
                branch_whitelist, ref.name
            ):
                logger.debug(
                    "Skipping '%s' because branch '%s' doesn't match the "
                    "whitelist pattern",
                    ref.refname,
                    ref.name,
                )
                continue
        elif ref.is_remote and remote_whitelist is not None:
            remote_name = ref.source.partition("/")[2]
            if not re.match(remote_whitelist, remote_name):
                logger.debug(
                    "Skipping '%s' because remote '%s' doesn't match the "
                    "whitelist pattern",
                    ref.refname,
                    remote_name,
                )
                continue
            if branch_whitelist is None or not re.match(
                branch_whitelist, ref.name
            ):
                logger.debug(
                    "Skipping '%s' because branch '%s' doesn't match the "
                    "whitelist pattern",
                    ref.refname,
                    ref.name,
                )
                continue
        else:
            logger.debug(
                "Skipping '%s' because its not a branch or tag", ref.refname
            )
            continue

        missing_files = [
            filename
            for filename in files
            if filename != "."
            and not file_exists(gitroot, ref.refname, filename)
        ]
        if missing_files:
            logger.debug(
                "Skipping '%s' because it lacks required files: %r",
                ref.refname,
                missing_files,
            )
            continue

        yield ref


def file_exists(gitroot, refname, filename):
    if os.sep != "/":
        # Git requires / path sep, make sure we use that
        filename = filename.replace(os.sep, "/")

    cmd = (
        "git",
        "cat-file",
        "-e",
        "{}:{}".format(refname, filename),
    )
    proc = subprocess.run(
        cmd, cwd=gitroot, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    return proc.returncode == 0


def no_fs_traversal(member: tarfile.TarInfo):
    """
    Returns false for all members that are absolute paths or use the parent
    directory to protect against directory traversal attacks from malicious
    tarfiles.
    """
    return (
        not member.name.startswith("/")
        and not member.name.startswith("\\")
        and "../" not in member.name
        and "..\\" not in member.name
    )


def copy_tree(gitroot, src, dst, reference, sourcepath="."):
    with tempfile.SpooledTemporaryFile() as fp:
        cmd = (
            "git",
            "archive",
            "--format",
            "tar",
            reference.commit,
            "--",
            sourcepath,
        )
        subprocess.check_call(cmd, cwd=gitroot, stdout=fp)
        fp.seek(0)
        with tarfile.TarFile(fileobj=fp) as tarfp:
            # This should be safe, but still causes a warning with medium
            # severity due to <https://github.com/PyCQA/bandit/issues/1038>.
            # Therefore we'll silence the warning.
            tarfp.extractall(  # nosec
                dst,
                members=[
                    member
                    for member in tarfp.getmembers()
                    if no_fs_traversal(member)
                ],
            )
