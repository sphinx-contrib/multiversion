# -*- coding: utf-8 -*-
import collections
import subprocess
import re

from . import sphinx

VersionRef = collections.namedtuple('VersionRef', [
    'name',
    'source',
    'refname',
    'version',
    'release',
])


def get_refs(gitroot):
    cmd = ("git", "for-each-ref", "--format", "%(refname)", "refs")
    output = subprocess.check_output(cmd, cwd=gitroot).decode()
    for line in output.splitlines():
        refname = line.strip()

        # Parse refname
        matchobj = re.match(r"^refs/(heads|tags|remotes/[^/]+)/(\S+)$", refname)
        if not matchobj:
            continue
        source = matchobj.group(1)
        name = matchobj.group(2)
        yield (name, source, refname)


def get_conf(gitroot, refname, confpath):
    objectname = "{}:{}".format(refname, confpath)
    cmd = ("git", "show", objectname)
    return subprocess.check_output(cmd, cwd=gitroot).decode()


def find_versions(gitroot, confpath, tag_whitelist, branch_whitelist, remote_whitelist):
    for name, source, refname in get_refs(gitroot):
        if source == 'tags':
            if tag_whitelist is None or not re.match(tag_whitelist, name):
                continue
        elif source == 'heads':
            if branch_whitelist is None or not re.match(branch_whitelist, name):
                continue
        elif remote_whitelist is not None and re.match(remote_whitelist, source):
            if branch_whitelist is None or not re.match(branch_whitelist, name):
                continue
        else:
            continue

        conf = get_conf(gitroot, refname, confpath)
        config = sphinx.parse_conf(conf)
        version = config['version']
        release = config['release']
        yield VersionRef(name, source, refname, version, release)


def shallow_clone(src, dst, branch):
    cmd = ("git", "clone", "--no-hardlinks", "--single-branch", "--depth", "1",
           "--branch", branch, src, dst)
    subprocess.check_call(cmd)
