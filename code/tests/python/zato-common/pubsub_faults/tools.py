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

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

# The variable naming the directory of the libraries and the directory used unless it names another one.
_tools_dir_env = 'Zato_Test_Fault_Tools_Dir'
_default_tools_subdir = 'tools'

# The source of the library that delays and fails the file system calls.
_fsfault_source = os.path.join(os.path.dirname(__file__), 'native', 'fsfault.c')
_fsfault_name = 'fsfault.so'

# Where a PostgreSQL container finds the library, the list of the libraries that its dynamic linker preloads
# and the control file of the faults. The entrypoint of the image replaces and then unsets LD_PRELOAD
# when it runs under a user that is not in /etc/passwd, so the library is preloaded through /etc/ld.so.preload instead.
_container_fsfault_path = '/zato-fault/fsfault.so'
_container_preload_path = '/etc/ld.so.preload'
_container_control_dir = '/zato-fault-control'
_preload_list_name = 'ld.so.preload'

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
    """ Builds the library that delays and fails the file system calls unless it exists already and is newer
    than its source, and returns its path.
    """
    tools_dir = get_tools_dir()
    out = os.path.join(tools_dir, _fsfault_name)

    if os.path.exists(out):
        needs_build = os.path.getmtime(_fsfault_source) > os.path.getmtime(out)
    else:
        needs_build = True

    if needs_build:
        command = ['gcc', '-O2', '-Wall', '-Wextra', '-shared', '-fPIC', '-o', out, _fsfault_source, '-ldl', '-lpthread']
        _ = subprocess.run(command, check=True, capture_output=True, timeout=_build_timeout)

    return out

# ################################################################################################################################

def get_fsfault_docker_args(work_dir:'str', control_dir:'str', control_name:'str') -> 'strlist':
    """ Returns the arguments of docker run that make every process of a PostgreSQL container preload the library
    of the file system faults, which reads its settings from the file of the given name in the control directory.
    """
    fsfault_path = build_fsfault()

    preload_list_path = os.path.join(work_dir, _preload_list_name)

    with open(preload_list_path, 'w') as preload_list:
        _ = preload_list.write(_container_fsfault_path + '\n')

    out = [
        '-v', f'{fsfault_path}:{_container_fsfault_path}:ro',
        '-v', f'{preload_list_path}:{_container_preload_path}:ro',
        '-v', f'{control_dir}:{_container_control_dir}:ro',
        '-e', f'ZATO_FSFAULT_CONTROL={_container_control_dir}/{control_name}',
    ]

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
