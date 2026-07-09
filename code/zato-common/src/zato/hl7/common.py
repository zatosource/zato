# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from threading import Lock

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# Directories HL7-FHIR mapping config names are resolved against, registered by the server at startup.
# This lives outside zato.hl7.mappings so that the server can register directories
# without importing the FHIR model.
_config_locations:'strlist' = []

# Serializes access to the location list
_config_lock = Lock()

# ################################################################################################################################

def add_config_location(dir_name:'str') -> 'None':
    """ Registers a directory that config names are resolved against, e.g. a server's user-conf directory.
    """
    with _config_lock:
        if dir_name not in _config_locations:
            _config_locations.append(dir_name)

# ################################################################################################################################

def get_config_locations() -> 'strlist':
    """ Returns all the directories a config name may resolve to a file in.
    """
    out:'strlist' = []

    with _config_lock:
        out.extend(_config_locations)

    # Extra directories may be pointed to by the same environment variable the server itself uses
    if env_locations := os.environ.get('ZATO_USER_CONF_DIR'):
        for dir_name in env_locations.split(os.pathsep):
            dir_name = dir_name.strip()
            if dir_name:
                out.append(dir_name)

    return out

# ################################################################################################################################
# ################################################################################################################################
