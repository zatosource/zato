# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
import tempfile
from shutil import rmtree
from typing import NamedTuple

# ################################################################################################################################
# ################################################################################################################################

# The zato binary of the checkout the tests run from
_zato_base = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
_zato_bin = os.path.join(_zato_base, 'bin', 'zato')

# How long quickstart create may take, in seconds
_create_timeout = 120

# ################################################################################################################################
# ################################################################################################################################

class TestEnvironment(NamedTuple):
    base_dir: str
    server_dir: str

# ################################################################################################################################
# ################################################################################################################################

def create_environment(prefix:'str') -> 'TestEnvironment':
    """ Creates a throwaway quickstart environment so tests never depend on any pre-existing one.
    Only the on-disk environment with its embedded ODB is needed - no server is started.
    """
    base_dir = tempfile.mkdtemp(prefix=prefix)

    command = [
        _zato_bin, 'quickstart', 'create', base_dir,
        '--servers', '1',
        '--no-scheduler',
    ]

    result = subprocess.run(command, capture_output=True, text=True, timeout=_create_timeout)
    if result.returncode != 0:
        rmtree(base_dir, ignore_errors=True)
        raise Exception(f'quickstart create failed:\n{result.stdout}\n{result.stderr}')

    out = TestEnvironment(base_dir=base_dir, server_dir=os.path.join(base_dir, 'server1'))
    return out

# ################################################################################################################################

def delete_environment(environment:'TestEnvironment') -> 'None':
    """ Removes a throwaway environment along with its embedded ODB.
    """
    rmtree(environment.base_dir, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################
