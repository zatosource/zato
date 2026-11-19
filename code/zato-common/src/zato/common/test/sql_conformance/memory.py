# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The ways in which a database can be placed in memory or on a file system that is held in memory. A database placed
# in either way never reaches a disk, so its commits survive no loss of power, whatever its durability settings.

# stdlib
import os
import re
from dataclasses import dataclass

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class MemoryPattern:

    # The name under which an exemption refers to the pattern
    name: str

    # The pattern itself
    pattern: 're.Pattern[str]'

memory_pattern_list = list[MemoryPattern]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # This module, which is the only file that holds the patterns themselves
    Definition_Path = os.path.abspath(__file__)

    # The name of each pattern and its source
    Patterns = (
        ('sqlite_memory_url',    r'sqlite(?:\+\w+)?:/{2}(?:/:memory:)?[\'"]'),
        ('sqlite_memory_file',   r'[\'"]:memory:[\'"]'),
        ('sqlite_memory_uri',    r'\bmode\s*=\s*memory\b'),
        ('rust_memory',          r'\bopen_in_memory\b'),
        ('docker_tmpfs_option',  r'-{2}tmpfs\b'),
        ('mount_type_tmpfs',     r'\btype\s*=\s*(?:tmpfs|ramfs)\b'),
        ('mount_command_tmpfs',  r'\bmount\s+-t\s+(?:tmpfs|ramfs)\b'),
        ('compose_tmpfs',        r'^\s*tmpfs\s*:'),
        ('shared_memory_dir',    r'/dev/shm/(?![\w.-]+\.html\b)\w'),
        ('in_memory_container',  r'\bis_in_memory\s*=\s*True\b'),
    )

# ################################################################################################################################
# ################################################################################################################################

def get_memory_patterns() -> 'memory_pattern_list':
    """ Returns every pattern of a database placed in memory, compiled without regard to case.
    """
    out:'memory_pattern_list' = []

    for name, source in ModuleCtx.Patterns:
        item = MemoryPattern()
        item.name = name
        item.pattern = re.compile(source, re.IGNORECASE | re.MULTILINE)
        out.append(item)

    return out

# ################################################################################################################################
# ################################################################################################################################
