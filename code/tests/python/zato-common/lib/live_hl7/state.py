# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strlist

# ################################################################################################################################
# ################################################################################################################################

# Where a standalone system records what it runs as
State_Dir = os.path.expanduser('~/.zato/hl7-live')

# Where fetched artifacts such as module jars and source archives are kept between runs
Cache_Dir = os.path.join(State_Dir, 'cache')

# ################################################################################################################################
# ################################################################################################################################

def _state_path(system:'str') -> 'str':
    out = os.path.join(State_Dir, f'{system}.json')
    return out

# ################################################################################################################################

def ensure_directories() -> 'None':
    os.makedirs(State_Dir, exist_ok=True)
    os.makedirs(Cache_Dir, exist_ok=True)

# ################################################################################################################################

def write_state(system:'str', data:'stranydict') -> 'None':
    """ Records a running standalone system.
    """
    ensure_directories()
    path = _state_path(system)

    with open(path, 'w', encoding='utf8') as state_file:
        json.dump(data, state_file, indent=2)

# ################################################################################################################################

def read_state(system:'str') -> 'stranydict':
    """ Returns what a standalone system was started with, failing when it is not running.
    """
    path = _state_path(system)

    if not os.path.exists(path):
        raise Exception(f'{system} is not running standalone - no state file under {path}')

    with open(path, encoding='utf8') as state_file:
        out = json.load(state_file)

    return out

# ################################################################################################################################

def has_state(system:'str') -> 'bool':
    path = _state_path(system)
    out = os.path.exists(path)

    return out

# ################################################################################################################################

def remove_state(system:'str') -> 'None':
    path = _state_path(system)

    if os.path.exists(path):
        os.remove(path)

# ################################################################################################################################

def _kept_path(system:'str') -> 'str':
    out = os.path.join(State_Dir, f'{system}.kept')
    return out

# ################################################################################################################################

def read_kept_digest(system:'str') -> 'str':
    """ The digest of the password a system's kept volumes were installed with, empty when there is none recorded.
    """
    path = _kept_path(system)

    if not os.path.exists(path):
        return ''

    with open(path, encoding='utf8') as kept_file:
        out = kept_file.read().strip()

    return out

# ################################################################################################################################

def write_kept_digest(system:'str', digest:'str') -> 'None':
    ensure_directories()
    path = _kept_path(system)

    with open(path, 'w', encoding='utf8') as kept_file:
        _ = kept_file.write(digest)

# ################################################################################################################################

def list_states() -> 'strlist':
    """ Names of every standalone system with a state file, sorted.
    """
    out:'strlist' = []

    if os.path.isdir(State_Dir):
        for name in sorted(os.listdir(State_Dir)):
            if name.endswith('.json'):
                system = name[:-len('.json')]
                out.append(system)

    return out

# ################################################################################################################################
# ################################################################################################################################
