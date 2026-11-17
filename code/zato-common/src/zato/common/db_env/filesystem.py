# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The file system that holds a database file, read from the mount table of the process. A file system held in memory
# never reaches a disk, so the commits of a database on it survive no loss of power, whatever its durability settings.

# stdlib
import os
from dataclasses import dataclass

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The mount table of the current process
    Mounts_Path = '/proc/self/mounts'

    # The file systems held in memory
    Memory_Types = ('tmpfs', 'ramfs')

    # The file system that layers directories over others, and the option with its directory of changes
    Overlay_Type = 'overlay'
    Overlay_Upper_Option = 'upperdir='

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Mount:

    # Where the file system is mounted
    mount_point: str

    # The type of the file system
    fs_type: str

    # The options of the mount
    options: 'list[str]'

# ################################################################################################################################
# ################################################################################################################################

def _unescape(value:'str') -> 'str':
    """ Returns a field of the mount table with its octal escapes of spaces, tabs and backslashes replaced.
    """
    out = value.replace('\\040', ' ').replace('\\011', '\t').replace('\\134', '\\')
    return out

# ################################################################################################################################

def get_mount(path:'str') -> 'Mount':
    """ Returns the mount that holds a path, which is the one with the longest mount point that contains it.
    """
    real_path = os.path.realpath(path)
    out = Mount()
    out.mount_point = ''

    with open(ModuleCtx.Mounts_Path) as mounts_file:
        for line in mounts_file:
            _, mount_point, fs_type, options = line.split()[:4]
            mount_point = _unescape(mount_point)

            if mount_point == '/':
                is_under = True
            else:
                is_under = real_path == mount_point or real_path.startswith(mount_point + '/')

            if is_under:
                if len(mount_point) >= len(out.mount_point):
                    out.mount_point = mount_point
                    out.fs_type = fs_type
                    out.options = options.split(',')

    return out

# ################################################################################################################################

def get_filesystem_type(path:'str') -> 'str':
    """ Returns the type of the file system that holds a path.
    """
    mount = get_mount(path)

    out = mount.fs_type
    return out

# ################################################################################################################################

def is_memory_filesystem(path:'str') -> 'bool':
    """ Returns whether a path is on a file system held in memory, including an overlay whose changes are kept
    on such a file system.
    """
    mount = get_mount(path)

    if mount.fs_type in ModuleCtx.Memory_Types:
        return True

    if mount.fs_type == ModuleCtx.Overlay_Type:
        for option in mount.options:
            if option.startswith(ModuleCtx.Overlay_Upper_Option):
                upper_dir = option.removeprefix(ModuleCtx.Overlay_Upper_Option)
                upper_dir = _unescape(upper_dir)
                if os.path.exists(upper_dir):
                    return is_memory_filesystem(upper_dir)

    return False

# ################################################################################################################################
# ################################################################################################################################
