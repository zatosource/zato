# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A server whose SQLite database is on LazyFS loses its power under traffic and starts again.

# stdlib
import os
import shutil
import sqlite3

# pytest
import pytest

# Zato
from checks import DatabaseReader
from scenario import new_server, PowerLoss, run_power_loss
from zato.common.db_env.database_env import DatabaseEnv
from zato.common.test.reliability.lazyfs import LazyFSMount
from zato.common.test.sql_conformance.disk import get_disk_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.reliability.power_loss import PowerLossServer
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The directory of the test and the tool container of its mount
    Dir_Name = 'power-loss-sqlite'
    Container_Name = 'zato-test-lazyfs-power-loss-sqlite'

    # The name of the server
    Server_Name = 'sqlite'

# ################################################################################################################################
# ################################################################################################################################

class ServerPowerLoss(PowerLoss):
    """ The server and the storage of its database lose their power together, and the server starts again.
    """

    def __init__(self, server:'PowerLossServer', mount:'LazyFSMount') -> 'None':
        self.server = server
        self.mount = mount

    def cut(self) -> 'None':
        self.server.kill()
        self.mount.discard_unsynced()

    def restore(self) -> 'None':
        self.server.start()

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def base_dir() -> 'any_':
    """ The directory with the quickstart environment of the server and the LazyFS mount of its database.
    """
    out = get_disk_dir(ModuleCtx.Dir_Name)
    shutil.rmtree(out)
    os.makedirs(out)

    try:
        yield out
    finally:
        shutil.rmtree(out)

# ################################################################################################################################

@pytest.fixture
def mount(base_dir:'str') -> 'any_':
    """ LazyFS over the directory of the database of the server.
    """
    database_dir = os.path.join(base_dir, 'database')
    os.makedirs(database_dir)

    out = LazyFSMount(ModuleCtx.Container_Name, base_dir, os.path.join(base_dir, 'lazyfs'), database_dir)
    out.mount()

    try:
        yield out
    finally:
        out.unmount()

# ################################################################################################################################
# ################################################################################################################################

def test_sqlite_server_power_loss(base_dir:'str', mount:'LazyFSMount') -> 'None':
    """ Every publication, acknowledgement, receipt of a fenced acknowledgement and audit event
    that the server acknowledged before the loss of power is stored once it starts again, no acknowledged message
    is delivered again, no message is stored twice and every acknowledged publication to the pushed topic is pushed.
    """
    db_path = os.path.join(mount.mount_dir, DatabaseEnv.File_Name)

    database_env = {
        DatabaseEnv.Env_Type: DatabaseEnv.Type_SQLite,
        DatabaseEnv.Env_Path: db_path,
    }

    server = new_server(ModuleCtx.Server_Name, base_dir, database_env)

    def connect() -> 'sqlite3.Connection':
        out = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
        return out

    reader = DatabaseReader(connect)

    try:
        server.create()
        server.start()

        power_loss = ServerPowerLoss(server, mount)
        run_power_loss(server, power_loss, reader)

    finally:
        server.remove()

# ################################################################################################################################
# ################################################################################################################################
