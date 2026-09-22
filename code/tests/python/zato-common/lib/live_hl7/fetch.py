# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
from urllib.request import urlopen

# Live HL7
from live_hl7.state import Cache_Dir, ensure_directories

# ################################################################################################################################
# ################################################################################################################################

# How long one download may stall before it fails, in seconds
Download_Timeout = 120

# ################################################################################################################################
# ################################################################################################################################

def cached_path(name:'str') -> 'str':
    out = os.path.join(Cache_Dir, name)
    return out

# ################################################################################################################################

def fetch_once(url:'str', name:'str') -> 'str':
    """ Downloads a URL into the cache under the given name unless it is already there, returns the cached path.
    A failed download leaves nothing behind, so the next run tries again.
    """
    ensure_directories()
    path = cached_path(name)

    if os.path.exists(path):
        return path

    partial = path + '.partial'

    with urlopen(url, timeout=Download_Timeout) as response, open(partial, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

    os.replace(partial, path)

    return path

# ################################################################################################################################

def work_directory(name:'str') -> 'str':
    """ A directory under the cache a system mounts or renders into - kept between runs.
    """
    ensure_directories()
    out = cached_path(name)
    os.makedirs(out, exist_ok=True)

    return out

# ################################################################################################################################
# ################################################################################################################################
