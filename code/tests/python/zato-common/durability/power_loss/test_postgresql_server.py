# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A server whose PostgreSQL database keeps its data directory on LazyFS. The database container loses its power
# under traffic and starts again, while the server keeps running.

# stdlib
import os
import shutil

# pytest
import pytest

# Zato
from checks import DatabaseReader
from scenario import new_server, PowerLoss, run_power_loss
from zato.common.test.durability.disk import get_disk_dir
from zato.common.test.durability.lazyfs import LazyFSMount
from zato.common.test.pubsub_database import connect, kill_container, PubSubDBMode, start_container, \
    start_pubsub_database, stop_container, stop_pubsub_database

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import pg8000.dbapi
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The label of the database container, the tool container of its mount and the directory of the server
    Database_Label = 'power-loss'
    Container_Name = 'zato-test-lazyfs-power-loss-postgresql'
    Dir_Name = 'power-loss-postgresql'

    # The name of the server
    Server_Name = 'postgresql'

    # The directory of the database container with its data
    Data_Dir_Name = 'data'

# ################################################################################################################################
# ################################################################################################################################

class DatabasePowerLoss(PowerLoss):
    """ The database container and the storage of its data lose their power together, and the container starts again.
    """

    def __init__(self, database:'PubSubDatabase', mount:'LazyFSMount') -> 'None':
        self.database = database
        self.mount = mount

    def cut(self) -> 'None':
        kill_container(self.database)
        self.mount.discard_unsynced()

    def restore(self) -> 'None':
        start_container(self.database)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def database() -> 'any_':
    """ A PostgreSQL container whose data directory is on LazyFS.
    """
    out = start_pubsub_database(ModuleCtx.Database_Label, PubSubDBMode.PostgreSQL)

    try:
        # The data that the container created at its start becomes the content of LazyFS ..
        stop_container(out)

        data_dir = os.path.join(out.work_dir, ModuleCtx.Data_Dir_Name)
        mount = LazyFSMount(ModuleCtx.Container_Name, out.work_dir, os.path.join(out.work_dir, 'lazyfs'), data_dir)
        mount.mount()

        # .. and the container works on LazyFS from now on.
        try:
            start_container(out)
            yield out, mount
        finally:
            stop_container(out)
            mount.unmount()

    finally:
        stop_pubsub_database(out)

# ################################################################################################################################

@pytest.fixture
def base_dir() -> 'any_':
    """ The directory with the quickstart environment of the server.
    """
    out = get_disk_dir(ModuleCtx.Dir_Name)
    shutil.rmtree(out)
    os.makedirs(out)

    try:
        yield out
    finally:
        shutil.rmtree(out)

# ################################################################################################################################
# ################################################################################################################################

def test_postgresql_server_power_loss(database:'any_', base_dir:'str') -> 'None':
    """ Every publication, acknowledgement, audit event that the server acknowledged before the database
    lost its power is stored once the database starts again, no acknowledged message is delivered again
    and no message is stored twice.
    """
    pubsub_database, mount = database

    server = new_server(ModuleCtx.Server_Name, base_dir, pubsub_database.env)

    def connect_database() -> 'pg8000.dbapi.Connection':
        out = connect(pubsub_database)
        return out

    reader = DatabaseReader(connect_database)

    try:
        server.create()
        server.start()

        power_loss = DatabasePowerLoss(pubsub_database, mount)
        run_power_loss(server, power_loss, reader)

    finally:
        server.remove()

# ################################################################################################################################
# ################################################################################################################################
