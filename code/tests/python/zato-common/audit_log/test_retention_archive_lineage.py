# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The retention of the audit log archives the attributes and the lineage links of the events it deletes
# along with the events themselves.

# stdlib
import errno
import os
from datetime import timedelta
from json import loads

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import func, select

# Zato
from zato.common.audit_log.api import event_attr_table, event_link_table, event_table, get_source_env_suffix, AuditEvent, \
    AuditLink, AuditLog, AuditSource, Env_Retention_Days_Prefix
from zato.common.audit_log.attr_rows import build_attr_rows
from zato.common.audit_log.retention import Env_Archive_Dir
from zato.common.db_env.database import get_database_engine
from zato.common.test.direct_sql.seed import seed_audit_events
from zato.common.test.zato_database import zato_database_engine
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from pytest import MonkeyPatch
    from zato.common.typing_ import any_, anydict, anylist, stranydict, strdictnone

    # Dummy assignments to satisfy type checkers
    MonkeyPatch = MonkeyPatch
    any_ = any_
    anydict = anydict
    stranydict = stranydict
    strdictnone = strdictnone

    strgen = Iterator[str]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The server and the channel the events are written under
    Server_Name  = 'test-audit-archive-lineage-server'
    Channel_Name = 'audit.test.archive.lineage'

    # The directory of the archive, under the directory of the test
    Archive_Dir_Name = 'archive'

    # How many days of events the retention keeps and how old the expired events are
    Retention_Days   = 1
    Expired_Age_Days = 10

    # The kinds of the archive lines that hold attribute rows and lineage link rows
    Archive_Kind_Attr = 'attr'
    Archive_Kind_Link = 'link'

    # The columns of an archived attribute line that build_attr_rows does not produce
    Archive_Only_Attr_Columns = ['kind', 'id']

# The environment variable holding the retention of the source of the events
_env_source_retention_days = f'{Env_Retention_Days_Prefix}{get_source_env_suffix(AuditSource.MLLP_Channel)}'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def archive_dir(tmp_path:'os.PathLike', monkeypatch:'MonkeyPatch') -> 'strgen':
    """ A Zato database of the test and an archive directory in the directory of the test,
    with the retention of the source of the events set. Yields the archive directory.
    """
    out = os.path.join(str(tmp_path), ModuleCtx.Archive_Dir_Name)

    retention_days = f'{ModuleCtx.Retention_Days}'

    monkeypatch.setenv(Env_Archive_Dir, out)
    monkeypatch.setenv(_env_source_retention_days, retention_days)

    with zato_database_engine():
        yield out

# ################################################################################################################################
# ################################################################################################################################

def _insert_event(audit_log:'AuditLog', age_days:'int', cid:'str', attrs:'strdictnone'=None) -> 'int':
    """ Seeds one event that is the given number of days old and returns its id.
    """
    pending = audit_log.new_pending_event(AuditSource.MLLP_Channel, AuditEvent.Interchange_Received,
        ModuleCtx.Channel_Name, cid=cid, attrs=attrs)

    pending.values['event_time'] = utcnow() - timedelta(days=age_days)

    engine = get_database_engine()
    event_ids = seed_audit_events(engine, [pending])

    out = event_ids[0]
    return out

# ################################################################################################################################

def _count_rows(table:'any_', column:'any_', value:'int') -> 'int':
    """ Counts the rows of one table whose column has the given value.
    """
    engine = get_database_engine()

    query = select(func.count())
    query = query.select_from(table)
    query = query.where(column == value)

    with engine.connect() as connection:
        result = connection.execute(query)
        out = result.scalar_one()

    return out

# ################################################################################################################################

def _read_archive_lines(archive_dir:'str', kind:'str') -> 'anylist':
    """ Returns the lines of one kind from every archive file in the directory.
    """
    out:'anylist' = []

    for file_name in sorted(os.listdir(archive_dir)):

        archive_path = os.path.join(archive_dir, file_name)

        with open(archive_path, encoding='utf-8') as archive_file:
            lines = archive_file.read().splitlines()

        for line in lines:
            entry = loads(line)

            if entry['kind'] == kind:
                out.append(entry)

    return out

# ################################################################################################################################

def _get_attr_name(row:'anydict') -> 'str':
    """ Returns the name of an attribute row, by which the rows of one event are ordered.
    """
    out = row['name']
    return out

# ################################################################################################################################

def _fail_fsync(fd:'int') -> 'None':
    """ Fails as fsync does when the device reports an I/O error.
    """
    raise OSError(errno.EIO, os.strerror(errno.EIO))

# ################################################################################################################################

def _run_retention(audit_log:'AuditLog') -> 'None':
    """ Runs the retention the way periodic inserts do.
    """
    now = utcnow()
    audit_log._run_retention(now)

# ################################################################################################################################
# ################################################################################################################################

def test_attributes_archived(archive_dir:'str') -> 'None':
    """ The attribute rows of a deleted event are in the archive exactly as they were written.
    """
    audit_log = AuditLog(ModuleCtx.Server_Name)

    attrs:'stranydict' = {
        'msg_type': 'ADT^A08',
        'segment_count': 7,
        'is_batch': True,
    }

    # An event older than the retention, with text, numeric and boolean attributes ..
    event_id = _insert_event(audit_log, ModuleCtx.Expired_Age_Days, 'cid-archive-lineage-attrs', attrs)

    # .. the retention archives and deletes it ..
    _run_retention(audit_log)

    # .. its attributes are no longer in the database ..
    assert _count_rows(event_table, event_table.c.id, event_id) == 0
    assert _count_rows(event_attr_table, event_attr_table.c.event_id, event_id) == 0

    # .. and the archive has every one of them, with the values that were written.
    archived:'anylist' = []

    for entry in _read_archive_lines(archive_dir, ModuleCtx.Archive_Kind_Attr):
        for column in ModuleCtx.Archive_Only_Attr_Columns:
            _ = entry.pop(column)
        archived.append(entry)

    expected = build_attr_rows(event_id, attrs)

    archived.sort(key=_get_attr_name)
    expected.sort(key=_get_attr_name)

    assert archived == expected

# ################################################################################################################################

def test_link_of_expired_child_archived(archive_dir:'str') -> 'None':
    """ The link of a deleted resubmission to its parent, which the retention keeps, is in the archive.
    """
    audit_log = AuditLog(ModuleCtx.Server_Name)

    # A recent original message and an expired resubmission of it ..
    parent_id = _insert_event(audit_log, 0, 'cid-archive-lineage-original')
    child_id = _insert_event(audit_log, ModuleCtx.Expired_Age_Days, 'cid-archive-lineage-resubmission')

    audit_log.add_links(child_id, [parent_id], AuditLink.Resubmit_Of)

    # .. the retention archives and deletes the resubmission ..
    _run_retention(audit_log)

    # .. the link is no longer in the database, while the original message is ..
    assert _count_rows(event_link_table, event_link_table.c.child_event_id, child_id) == 0
    assert _count_rows(event_table, event_table.c.id, parent_id) == 1

    # .. and the archive has the link.
    links = _read_archive_lines(archive_dir, ModuleCtx.Archive_Kind_Link)
    assert len(links) == 1, links

    link = links[0]
    assert link['child_event_id'] == child_id
    assert link['parent_event_id'] == parent_id
    assert link['link_type'] == AuditLink.Resubmit_Of

# ################################################################################################################################

def test_link_of_expired_parent_archived(archive_dir:'str') -> 'None':
    """ The link of a recent batch item to its deleted batch is in the archive, and the item stays intact.
    """
    audit_log = AuditLog(ModuleCtx.Server_Name)

    item_attrs:'stranydict' = {
        'msg_type': 'ORU^R01',
    }

    # An expired HL7 batch and a recent item of it ..
    batch_id = _insert_event(audit_log, ModuleCtx.Expired_Age_Days, 'cid-archive-lineage-batch')
    item_id = _insert_event(audit_log, 0, 'cid-archive-lineage-batch-item', item_attrs)

    audit_log.add_links(item_id, [batch_id], AuditLink.Batch_Item_Of)

    # .. the retention archives and deletes the batch ..
    _run_retention(audit_log)

    # .. the link is no longer in the database, while the item and its attributes are ..
    assert _count_rows(event_link_table, event_link_table.c.parent_event_id, batch_id) == 0
    assert _count_rows(event_table, event_table.c.id, item_id) == 1
    assert _count_rows(event_attr_table, event_attr_table.c.event_id, item_id) == 1

    # .. and the archive has the link.
    links = _read_archive_lines(archive_dir, ModuleCtx.Archive_Kind_Link)
    assert len(links) == 1, links

    link = links[0]
    assert link['child_event_id'] == item_id
    assert link['parent_event_id'] == batch_id
    assert link['link_type'] == AuditLink.Batch_Item_Of

# ################################################################################################################################

def test_link_within_one_chunk_archived_once(archive_dir:'str') -> 'None':
    """ A link whose child and parent are both deleted in the same chunk is in the archive exactly once.
    """
    audit_log = AuditLog(ModuleCtx.Server_Name)

    # An expired original message and an expired resubmission of it ..
    parent_id = _insert_event(audit_log, ModuleCtx.Expired_Age_Days, 'cid-archive-lineage-chunk-original')
    child_id = _insert_event(audit_log, ModuleCtx.Expired_Age_Days, 'cid-archive-lineage-chunk-resubmission')

    audit_log.add_links(child_id, [parent_id], AuditLink.Resubmit_Of)

    # .. the retention archives and deletes both ..
    _run_retention(audit_log)

    assert _count_rows(event_table, event_table.c.id, parent_id) == 0
    assert _count_rows(event_table, event_table.c.id, child_id) == 0

    # .. and the archive has the link once.
    links = _read_archive_lines(archive_dir, ModuleCtx.Archive_Kind_Link)
    assert len(links) == 1, links

    link = links[0]
    assert link['child_event_id'] == child_id
    assert link['parent_event_id'] == parent_id

# ################################################################################################################################

def test_failed_archive_sync_keeps_attributes_and_links(archive_dir:'str', monkeypatch:'MonkeyPatch') -> 'None':
    """ A retention whose archive cannot be synced to stable storage deletes no event, attribute or link.
    """
    audit_log = AuditLog(ModuleCtx.Server_Name)

    attrs:'stranydict' = {
        'msg_type': 'ADT^A01',
    }

    # An expired event with an attribute and an expired resubmission of it ..
    parent_id = _insert_event(audit_log, ModuleCtx.Expired_Age_Days, 'cid-archive-lineage-sync-original', attrs)
    child_id = _insert_event(audit_log, ModuleCtx.Expired_Age_Days, 'cid-archive-lineage-sync-resubmission')

    audit_log.add_links(child_id, [parent_id], AuditLink.Resubmit_Of)

    # .. the device fails every fsync of the archive and the retention stops with the error ..
    with monkeypatch.context() as fsync_patch:

        fsync_patch.setattr(os, 'fsync', _fail_fsync)

        with pytest.raises(OSError):
            _run_retention(audit_log)

    # .. and the events, the attribute and the link are all still in the database.
    assert _count_rows(event_table, event_table.c.id, parent_id) == 1
    assert _count_rows(event_table, event_table.c.id, child_id) == 1
    assert _count_rows(event_attr_table, event_attr_table.c.event_id, parent_id) == 1
    assert _count_rows(event_link_table, event_link_table.c.child_event_id, child_id) == 1

# ################################################################################################################################
# ################################################################################################################################
