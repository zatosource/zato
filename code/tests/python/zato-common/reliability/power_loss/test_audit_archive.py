# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The retention of the audit log archives the events it deletes into a file on LazyFS, and every event
# that the retention deleted is in the archive after a loss of power. The PostgreSQL database keeps its data
# directory on LazyFS too, and both lose their power together.

# stdlib
import errno
import os
import shutil
from datetime import timedelta
from json import loads

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import select

# Zato
from checks import DatabaseReader
from zato.common.audit_log.api import event_table, get_source_env_suffix, AuditEvent, AuditLog, AuditSource, \
    Env_Retention_Days_Prefix
from zato.common.audit_log.retention import Env_Archive_Dir
from zato.common.db_env.database import dispose_database_engine, get_database_engine
from zato.common.test.direct_sql.seed import seed_audit_events
from zato.common.test.pubsub_database import connect, kill_container, pubsub_db_env, PubSubDBMode, start_container, \
    start_pubsub_database, stop_container, stop_pubsub_database
from zato.common.test.reliability.lazyfs import LazyFSMount
from zato.common.test.sql_conformance.disk import get_disk_dir
from zato.common.test.zato_database import zato_database_engine
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import pg8000.dbapi
    from pytest import MonkeyPatch
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import any_, anylist, intlist, intstrdict

    # Dummy assignments to satisfy type checkers
    MonkeyPatch = MonkeyPatch
    PubSubDatabase = PubSubDatabase

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The label of the database container, the tool container of the mount of its data directory
    # and the directory of its data
    Database_Label = 'power-loss-audit-archive'
    Database_Container_Name = 'zato-test-lazyfs-power-loss-audit-archive-postgresql'
    Data_Dir_Name = 'data'

    # The directory of the archive and the tool container of its mount
    Archive_Dir_Name = 'power-loss-audit-archive'
    Archive_Container_Name = 'zato-test-lazyfs-power-loss-audit-archive'

    # The server and the channel the events are written under
    Server_Name = 'test-audit-archive-server'
    Channel_Name = 'audit.test.archive'

    # The directory of the archive, under the directory of the test
    Archive_Subdir_Name = 'archive'

    # How many events are seeded, how old they are and how many days of them the retention keeps
    Event_Count = 3
    Event_Age_Days = 2
    Retention_Days = 1

    # The kind of the archive lines that hold full event rows
    Archive_Kind_Event = 'event'

# The environment variable holding the retention of the source of the events
_env_source_retention_days = f'{Env_Retention_Days_Prefix}{get_source_env_suffix(AuditSource.MLLP_Channel)}'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def database() -> 'any_':
    """ A PostgreSQL container whose data directory is on LazyFS. Yields the database and the mount of its data.
    """
    out = start_pubsub_database(ModuleCtx.Database_Label, PubSubDBMode.PostgreSQL)

    try:
        # The data that the container created at its start becomes the content of LazyFS ..
        stop_container(out)

        data_dir = os.path.join(out.work_dir, ModuleCtx.Data_Dir_Name)
        lazyfs_dir = os.path.join(out.work_dir, 'lazyfs')

        mount = LazyFSMount(ModuleCtx.Database_Container_Name, out.work_dir, lazyfs_dir, data_dir)
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
def archive_mount() -> 'any_':
    """ A LazyFS mount over the directory of the archive.
    """
    base_dir = get_disk_dir(ModuleCtx.Archive_Dir_Name)
    shutil.rmtree(base_dir)

    mount_dir = os.path.join(base_dir, 'files')
    lazyfs_dir = os.path.join(base_dir, 'lazyfs')
    os.makedirs(mount_dir)

    out = LazyFSMount(ModuleCtx.Archive_Container_Name, base_dir, lazyfs_dir, mount_dir)
    out.mount()

    try:
        yield out
    finally:
        out.unmount()
        shutil.rmtree(base_dir)

# ################################################################################################################################
# ################################################################################################################################

def _set_retention_env(monkeypatch:'MonkeyPatch', archive_dir:'str') -> 'None':
    """ Points the archive at its directory and sets the retention of the source of the events.
    """
    retention_days = f'{ModuleCtx.Retention_Days}'

    monkeypatch.setenv(Env_Archive_Dir, archive_dir)
    monkeypatch.setenv(_env_source_retention_days, retention_days)

# ################################################################################################################################

def _seed_expired_events(audit_log:'AuditLog') -> 'intstrdict':
    """ Seeds events older than the retention and returns the payload of each event by its id.
    """
    event_time = utcnow() - timedelta(days=ModuleCtx.Event_Age_Days)

    batch:'anylist' = []
    payloads:'anylist' = []

    for index in range(ModuleCtx.Event_Count):

        cid = f'cid-audit-archive-{index}'
        data = f'Payload of archived event {index}'

        pending = audit_log.new_pending_event(AuditSource.MLLP_Channel, AuditEvent.Interchange_Received,
            ModuleCtx.Channel_Name, cid=cid, data=data)

        pending.values['event_time'] = event_time

        batch.append(pending)
        payloads.append(data)

    engine = get_database_engine()
    event_ids = seed_audit_events(engine, batch)

    out:'intstrdict' = {}

    for event_id, data in zip(event_ids, payloads):
        out[event_id] = data

    return out

# ################################################################################################################################

def _read_stored_ids(database:'PubSubDatabase') -> 'intlist':
    """ Returns the ids of the events in the database, read outside of the engine of the test.
    """
    def connect_database() -> 'pg8000.dbapi.Connection':
        out = connect(database)
        return out

    reader = DatabaseReader(connect_database)
    rows = reader.read_rows(f'select id from {event_table.name}')

    out:'intlist' = []

    for row in rows:
        out.append(row[0])

    return out

# ################################################################################################################################

def _read_archived_events(archive_dir:'str') -> 'intstrdict':
    """ Returns the payload of each event in the archive files by its id.
    """
    out:'intstrdict' = {}

    # The loss of power may take the directory itself ..
    if not os.path.isdir(archive_dir):
        return out

    # .. and each file in it may have lost its content.
    for file_name in sorted(os.listdir(archive_dir)):

        archive_path = os.path.join(archive_dir, file_name)

        with open(archive_path, encoding='utf-8', errors='replace') as archive_file:
            lines = archive_file.read().splitlines()

        for line in lines:

            # A line that the loss of power damaged holds no event ..
            try:
                entry = loads(line)
            except ValueError:
                continue

            # .. and only full event rows are of interest here.
            if entry['kind'] == ModuleCtx.Archive_Kind_Event:
                out[entry['id']] = entry['data']

    return out

# ################################################################################################################################

def _fail_fsync(fd:'int') -> 'None':
    """ Fails as fsync does when the device reports an I/O error.
    """
    raise OSError(errno.EIO, os.strerror(errno.EIO))

# ################################################################################################################################
# ################################################################################################################################

def test_archive_survives_power_loss(database:'any_', archive_mount:'LazyFSMount', monkeypatch:'MonkeyPatch') -> 'None':
    """ Every event that the retention deleted before the loss of power is in the archive afterwards.
    """
    pubsub_database, data_mount = database

    archive_dir = os.path.join(archive_mount.mount_dir, ModuleCtx.Archive_Subdir_Name)
    _set_retention_env(monkeypatch, archive_dir)

    with pubsub_db_env(pubsub_database.env):

        try:

            # The events are older than the retention ..
            audit_log = AuditLog(ModuleCtx.Server_Name)
            payloads = _seed_expired_events(audit_log)

            # .. the retention archives and deletes them ..
            now = utcnow()
            audit_log._run_retention(now)

        # .. the engine of the test is closed ..
        finally:
            dispose_database_engine()

    # .. the database and the archive lose their power together ..
    kill_container(pubsub_database)
    data_mount.discard_unsynced()
    archive_mount.discard_unsynced()

    # .. and the database starts again on what its storage kept.
    start_container(pubsub_database)

    stored_ids = _read_stored_ids(pubsub_database)
    archived = _read_archived_events(archive_dir)

    deleted_ids:'intlist' = []

    for event_id in payloads:
        if event_id not in stored_ids:
            deleted_ids.append(event_id)

    assert deleted_ids, f'No events were deleted, stored: {stored_ids}'

    for event_id in deleted_ids:
        assert event_id in archived, f'Event {event_id} was deleted and is not in the archive: {archived}'
        assert archived[event_id] == payloads[event_id]

# ################################################################################################################################

def test_failed_archive_sync_keeps_chunk(tmp_path:'os.PathLike', monkeypatch:'MonkeyPatch') -> 'None':
    """ A retention whose archive cannot be synced to stable storage deletes no events.
    """
    archive_dir = os.path.join(str(tmp_path), ModuleCtx.Archive_Subdir_Name)
    _set_retention_env(monkeypatch, archive_dir)

    with zato_database_engine() as engine:

        # The events are older than the retention ..
        audit_log = AuditLog(ModuleCtx.Server_Name)
        payloads = _seed_expired_events(audit_log)

        now = utcnow()

        # .. the device fails every fsync of the archive and the retention stops with the error ..
        with monkeypatch.context() as fsync_patch:

            fsync_patch.setattr(os, 'fsync', _fail_fsync)

            with pytest.raises(OSError):
                audit_log._run_retention(now)

        # .. and every event is still in the database.
        query = select(event_table.c.id)

        stored_ids:'intlist' = []

        with engine.connect() as connection:
            for row in connection.execute(query):
                stored_ids.append(row[0])

    for event_id in payloads:
        assert event_id in stored_ids, f'Event {event_id} was deleted without an archive, stored: {stored_ids}'

# ################################################################################################################################
# ################################################################################################################################
