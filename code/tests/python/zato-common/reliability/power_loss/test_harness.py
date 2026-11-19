# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The verification of the LazyFS harness, which the power loss tests rely on to detect a write that was not synced.
# The files belong to no database.

# stdlib
import os
import shutil

# pytest
import pytest

# Zato
from zato.common.test.reliability.lazyfs import LazyFSMount
from zato.common.test.sql_conformance.disk import get_disk_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The directory of the test and the tool container of its mount
    Dir_Name = 'power-loss-harness'
    Container_Name = 'zato-test-lazyfs-power-loss-harness'

    # How large each file is, in bytes
    File_Size = 65536

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def mount() -> 'any_':
    """ A LazyFS mount over an empty directory.
    """
    base_dir = get_disk_dir(ModuleCtx.Dir_Name)
    shutil.rmtree(base_dir)

    mount_dir = os.path.join(base_dir, 'files')
    os.makedirs(mount_dir)

    out = LazyFSMount(ModuleCtx.Container_Name, base_dir, os.path.join(base_dir, 'lazyfs'), mount_dir)
    out.mount()

    try:
        yield out
    finally:
        out.unmount()
        shutil.rmtree(base_dir)

# ################################################################################################################################
# ################################################################################################################################

def _write_file(path:'str', data:'bytes') -> 'None':
    with open(path, 'wb') as output_file:
        _ = output_file.write(data)

# ################################################################################################################################

def _write_synced_file(path:'str', data:'bytes') -> 'None':
    with open(path, 'wb') as output_file:
        _ = output_file.write(data)
        output_file.flush()
        os.fsync(output_file.fileno())

# ################################################################################################################################

def _read_file(path:'str') -> 'bytes':
    """ Returns the content of a file, which is empty if the loss of power took the file itself.
    """
    if not os.path.exists(path):
        return b''

    with open(path, 'rb') as input_file:
        out = input_file.read()

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_unsynced_write_is_lost(mount:'LazyFSMount') -> 'None':
    """ A file written without fsync loses its content when the cache is cleared, and a file written with fsync keeps it.
    """
    unsynced_data = os.urandom(ModuleCtx.File_Size)
    synced_data = os.urandom(ModuleCtx.File_Size)

    unsynced_path = os.path.join(mount.mount_dir, 'unsynced.bin')
    synced_path = os.path.join(mount.mount_dir, 'synced.bin')

    _write_file(unsynced_path, unsynced_data)
    _write_synced_file(synced_path, synced_data)

    # Both files are complete before the loss of power ..
    assert _read_file(unsynced_path) == unsynced_data
    assert _read_file(synced_path) == synced_data

    mount.discard_unsynced()

    # .. and only the synced one is complete afterwards.
    assert _read_file(unsynced_path) != unsynced_data
    assert _read_file(synced_path) == synced_data

# ################################################################################################################################
# ################################################################################################################################
