# -*- coding: utf-8 -*-
import collections
import subprocess
import re

from . import sphinx

VersionRef = collections.namedtuple('VersionRef', [
    'name',
    'commit',
    'source',
    'is_remote',
    'refname',
    'version',
    'release',
])


def get_refs(gitroot):
    cmd = ("git", "for-each-ref", "--format", "%(objectname) %(refname)", "refs")
    output = subprocess.check_output(cmd, cwd=gitroot).decode()
    for line in output.splitlines():
        line = line.strip()
        # Parse refname
        matchobj = re.match(r"^(\w+) refs/(heads|tags|remotes/[^/]+)/(\S+)$", line)
        if not matchobj:
            continue
        commit = matchobj.group(1)
        source = matchobj.group(2)
        name = matchobj.group(3)
        refname = line.partition(' ')[2]

        yield (name, commit, source, refname)


def get_conf(gitroot, refname, confpath):
    objectname = "{}:{}".format(refname, confpath)
    cmd = ("git", "show", objectname)
    return subprocess.check_output(cmd, cwd=gitroot).decode()


def find_versions(gitroot, confpath, tag_whitelist, branch_whitelist, remote_whitelist):
    for name, commit, source, refname in get_refs(gitroot):
        is_remote = False
        if source == 'tags':
            if tag_whitelist is None or not re.match(tag_whitelist, name):
                continue
        elif source == 'heads':
            if branch_whitelist is None or not re.match(branch_whitelist, name):
                continue
        elif source.startswith('remotes/') and remote_whitelist is not None:
            is_remote = True
            remote_name = source.partition('/')[2]
            if not re.match(remote_whitelist, remote_name):
                continue
            if branch_whitelist is None or not re.match(branch_whitelist, name):
                continue
        else:
            continue

        conf = get_conf(gitroot, refname, confpath)
        config = sphinx.parse_conf(conf)
        version = config['version']
        release = config['release']
        yield VersionRef(name, commit, source, is_remote, refname, version, release)


def shallow_clone(src, dst, branch):
    cmd = ("git", "clone", "--no-hardlinks", "--single-branch", "--depth", "1",
           "--branch", branch, src, dst)
    subprocess.check_call(cmd)
