# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The native libraries that the faults of single processes preload, built from source into the directory
# that Zato_Test_Fault_Tools_Dir names, and nowhere in the system.

# stdlib
import os
import shutil
import subprocess

# Zato
from zato.common.test.pubsub_database import get_runtime_dir

# ################################################################################################################################
# ################################################################################################################################

# The variable naming the directory of the libraries and the directory used unless it names another one.
_tools_dir_env = 'Zato_Test_Fault_Tools_Dir'
_default_tools_subdir = 'tools'

# The source of the library that delays and fails the file system calls.
_fsfault_source = os.path.join(os.path.dirname(__file__), 'native', 'fsfault.c')
_fsfault_name = 'fsfault.so'

# The release of libfaketime that is built and the file of the library it builds.
_faketime_repository = 'https://github.com/wolfcw/libfaketime.git'
_faketime_tag = 'v0.9.13'
_faketime_name = 'libfaketime.so.1'

# How long a build may take, in seconds.
_build_timeout = 600

# ################################################################################################################################
# ################################################################################################################################

def get_tools_dir() -> 'str':

    if tools_dir := os.environ.get(_tools_dir_env, ''):
        out = tools_dir
    else:
        runtime_dir = get_runtime_dir()
        out = os.path.join(runtime_dir, _default_tools_subdir)

    os.makedirs(out, exist_ok=True)
    return out

# ################################################################################################################################

def build_fsfault() -> 'str':
    """ Builds the library that delays and fails the file system calls unless it exists already and returns its path.
    """
    tools_dir = get_tools_dir()
    out = os.path.join(tools_dir, _fsfault_name)

    if not os.path.exists(out):
        command = ['gcc', '-O2', '-Wall', '-Wextra', '-shared', '-fPIC', '-o', out, _fsfault_source, '-ldl', '-lpthread']
        _ = subprocess.run(command, check=True, capture_output=True, timeout=_build_timeout)

    return out

# ################################################################################################################################

def build_faketime() -> 'str':
    """ Builds libfaketime unless it exists already and returns its path.
    """
    tools_dir = get_tools_dir()
    out = os.path.join(tools_dir, _faketime_name)

    if os.path.exists(out):
        return out

    # The release is cloned afresh ..
    source_dir = os.path.join(tools_dir, 'libfaketime-src')
    shutil.rmtree(source_dir, ignore_errors=True)

    clone = ['git', 'clone', '--quiet', '--depth', '1', '--branch', _faketime_tag, _faketime_repository, source_dir]
    _ = subprocess.run(clone, check=True, capture_output=True, timeout=_build_timeout)

    # .. built ..
    build_dir = os.path.join(source_dir, 'src')
    _ = subprocess.run(['make', _faketime_name], cwd=build_dir, check=True, capture_output=True, timeout=_build_timeout)

    # .. and its library is copied to the directory of the tools.
    library_path = os.path.join(build_dir, _faketime_name)
    _ = shutil.copy(library_path, out)

    return out

# ################################################################################################################################
# ################################################################################################################################
