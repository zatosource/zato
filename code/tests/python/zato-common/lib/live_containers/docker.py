# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import subprocess

# ################################################################################################################################
# ################################################################################################################################

def has_docker() -> 'bool':
    """ True when docker compose answers on this machine.
    """
    try:
        result = subprocess.run(['docker', 'compose', 'version'], capture_output=True, check=False)
    except FileNotFoundError:
        return False

    out = result.returncode == 0
    return out

# ################################################################################################################################
# ################################################################################################################################
