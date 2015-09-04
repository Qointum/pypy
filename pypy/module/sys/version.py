"""
Version numbers exposed by PyPy through the 'sys' module.
"""
import os
from rpython.rlib import compilerinfo
from pypy.interpreter import gateway

#XXX # the release serial 42 is not in range(16)
CPYTHON_VERSION            = (3, 2, 5, "final", 0)
#XXX # sync CPYTHON_VERSION with patchlevel.h, package.py
CPYTHON_API_VERSION        = 1013   #XXX # sync with include/modsupport.h

PYPY_VERSION               = (2, 7, 0, "alpha", 0)    #XXX # sync patchlevel.h


import pypy
pypydir = os.path.dirname(os.path.abspath(pypy.__file__))
pypyroot = os.path.dirname(pypydir)
del pypy
from rpython.tool.version import get_repo_version_info

import time as t
gmtime = t.gmtime()
date = t.strftime("%b %d %Y", gmtime)
time = t.strftime("%H:%M:%S", gmtime)
del t

# ____________________________________________________________

app = gateway.applevel('''
"NOT_RPYTHON"
from _structseq import structseqtype, structseqfield
class version_info(metaclass=structseqtype):

    major        = structseqfield(0, "Major release number")
    minor        = structseqfield(1, "Minor release number")
    micro        = structseqfield(2, "Patch release number")
    releaselevel = structseqfield(3,
                       "'alpha', 'beta', 'candidate', or 'release'")
    serial       = structseqfield(4, "Serial release number")
''')

def get_api_version(space):
    return space.wrap(CPYTHON_API_VERSION)

def get_version_info(space):
    w_version_info = app.wget(space, "version_info")
    return space.call_function(w_version_info, space.wrap(CPYTHON_VERSION))

def _make_version_template(PYPY_VERSION=PYPY_VERSION):
    ver = "%d.%d.%d" % (PYPY_VERSION[0], PYPY_VERSION[1], PYPY_VERSION[2])
    if PYPY_VERSION[3] != "final":
        ver = ver + "-%s%d" %(PYPY_VERSION[3], PYPY_VERSION[4])
    template = "%d.%d.%d (%s, %s, %s)\n[PyPy %s with %%s]" % (
        CPYTHON_VERSION[0],
        CPYTHON_VERSION[1],
        CPYTHON_VERSION[2],
        get_repo_version_info(root=pypyroot)[1],
        date,
        time,
        ver)
    assert template.count('%') == 1     # only for the "%s" near the end
    return template
_VERSION_TEMPLATE = _make_version_template()

def get_version(space):
    return space.wrap(_VERSION_TEMPLATE % compilerinfo.get_compiler_info())

def get_winver(space):
    return space.wrap("%d.%d" % (
        CPYTHON_VERSION[0],
        CPYTHON_VERSION[1]))

def get_hexversion(space):
    return space.wrap(tuple2hex(CPYTHON_VERSION))

def get_pypy_version_info(space):
    ver = PYPY_VERSION
    w_version_info = app.wget(space, "version_info")
    return space.call_function(w_version_info, space.wrap(ver))

def get_subversion_info(space):
    return space.wrap(('PyPy', '', ''))

def get_repo_info(space):
    info = get_repo_version_info(root=pypyroot)
    if info:
        repo_tag, repo_version = info
        return space.newtuple([space.wrap('PyPy'),
                               space.wrap(repo_tag),
                               space.wrap(repo_version)])
    else:
        return space.w_None

def tuple2hex(ver):
    d = {'alpha':     0xA,
         'beta':      0xB,
         'candidate': 0xC,
         'final':     0xF,
         }
    subver = ver[4]
    if not (0 <= subver <= 9):
        subver = 0
    return (ver[0] << 24   |
            ver[1] << 16   |
            ver[2] << 8    |
            d[ver[3]] << 4 |
            subver)