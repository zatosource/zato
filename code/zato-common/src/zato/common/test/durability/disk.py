# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The directories in which the tests keep their databases. Each one is on a file system that reaches a disk,
# so that a database of a test syncs its commits as a database of a production system does.

# stdlib
import os

# Zato
from zato.common.db_env.filesystem import get_filesystem_type, is_memory_filesystem

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The environment variable with the base directory of the databases of the tests
    Env_Base_Dir = 'Zato_Test_Disk_Dir'

    # The base directory under the home directory of the user, unless the variable names another one
    Default_Base_Dir = os.path.join(os.path.expanduser('~'), '.cache', 'zato-test')

# ################################################################################################################################
# ################################################################################################################################

class MemoryFilesystemError(Exception):
    """ Raised when a directory for the databases of a test is on a file system held in memory.
    """

# ################################################################################################################################
# ################################################################################################################################

def verify_disk_dir(path:'str') -> 'None':
    """ Raises MemoryFilesystemError if a directory is on a file system held in memory.
    """
    if is_memory_filesystem(path):
        fs_type = get_filesystem_type(path)
        raise MemoryFilesystemError(f'Directory `{path}` is on `{fs_type}`, which keeps its data in memory')

# ################################################################################################################################

def get_disk_dir(name:'str') -> 'str':
    """ Returns a directory of the given name for the databases of a test, on a file system that reaches a disk,
    creating it if needed.
    """
    base_dir = os.environ.get(ModuleCtx.Env_Base_Dir)

    if base_dir is None:
        base_dir = ModuleCtx.Default_Base_Dir

    out = os.path.join(base_dir, name)
    os.makedirs(out, exist_ok=True)

    verify_disk_dir(out)

    return out

# ################################################################################################################################
# ################################################################################################################################
