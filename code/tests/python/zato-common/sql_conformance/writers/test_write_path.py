# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import time
from uuid import uuid4
from zlib import crc32

# gevent
import gevent

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import func, select

# Zato
from zato.common.audit_log.common import event_dedup_table
from zato.common.common_db.schema import shared_object_table
from zato.common.db_env.engine import execute_write
from zato.common.db_env.write_path import Mechanism, write_path, WritePathViolation
from zato.common.pubsub.sql.pending import new_pending_publication
from zato.common.pubsub.sql.schema import message_table
from zato.common.pubsub.sql.sqlite_write import write_items_sqlite
from zato.common.test.zato_database import file_database_engine
from zato.common.util.api import utcnow

# Zato - Rust
from zato_common_core.zato_common_core import SubscriptionList

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from sqlalchemy.engine import Engine
    from sqlalchemy.sql.dml import Insert
    from zato.common.pubsub.sql.pending import PendingPublication
    from zato.common.typing_ import anydict

    anydict = anydict
    Engine = Engine
    Insert = Insert
    Path = Path
    PendingPublication = PendingPublication

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The type of the shared objects that the tests insert
    Object_Type = 'write-path-test'

    # The outcome of a dedup row that the tests insert
    Dedup_Outcome = ''

    # The topic of the publications that the tests write, which has no subscribers
    Topic_Name = 'write-path-test.orders'

    # The priority and the expiration in seconds of those publications, and the time they are stamped with
    Priority = 5
    Expiration = 3600
    Time_ISO = '2026-11-19T10:00:00+00:00'

    # For how long the message IDs of those publications are recognized as repeats, in milliseconds
    Dedup_Window_Ms = 7 * 24 * 60 * 60 * 1000

# ################################################################################################################################
# ################################################################################################################################

def _new_shared_object_insert(name:'str') -> 'Insert':
    """ Returns an insert of one shared object, a table outside of the audit log.
    """
    out = shared_object_table.insert().values(
        object_type=ModuleCtx.Object_Type,
        name=name,
        data='{}',
        version=1,
        last_updated=utcnow(),
    )

    return out

# ################################################################################################################################

def _new_dedup_insert(dedup_key:'str') -> 'Insert':
    """ Returns an insert of one row of the dedup ledger, a table of the audit log.
    """
    out = event_dedup_table.insert().values(
        dedup_key=dedup_key,
        cid=dedup_key,
        action=ModuleCtx.Object_Type,
        actor=ModuleCtx.Object_Type,
        created_at=utcnow(),
        outcome=ModuleCtx.Dedup_Outcome,
        completed_at=None,
    )

    return out

# ################################################################################################################################

def _count_shared_objects(engine:'Engine', name:'str') -> 'int':
    statement = select(func.count()).select_from(shared_object_table).where(shared_object_table.c.name == name)

    with engine.connect() as connection:
        out = connection.execute(statement).scalar_one()

    return out

# ################################################################################################################################

def _insert_in_transaction(engine:'Engine', statement:'Insert') -> 'None':
    with engine.begin() as connection:
        _ = connection.execute(statement)

# ################################################################################################################################

def _new_publication(msg_id:'str') -> 'PendingPublication':
    """ Returns a publication of one message to a topic without subscribers.
    """
    payload = 'Order ORD-0042 for Maria Johnson'
    now_ms = int(time() * 1000)

    message_values:'anydict' = {
        'msg_id': msg_id,
        'topic_name': ModuleCtx.Topic_Name,
        'payload': payload,
        'payload_encrypted': False,
        'payload_crc32': crc32(payload.encode('utf8')),
        'data_class': None,
        'data_size': len(payload),
        'data_preview': payload,
        'priority': ModuleCtx.Priority,
        'expiration': ModuleCtx.Expiration,
        'pub_time_iso': ModuleCtx.Time_ISO,
        'recv_time_iso': ModuleCtx.Time_ISO,
        'expiration_time_iso': ModuleCtx.Time_ISO,
        'pub_time_ms': now_ms,
        'expiration_ms': now_ms + ModuleCtx.Expiration * 1000,
        'publisher': None,
        'cid': None,
        'correl_id': None,
        'in_reply_to': None,
        'ext_client_id': None,
        'max_retries': None,
        'retry_sleep_time': None,
        'retry_backoff_threshold': None,
        'retry_backoff_multiplier': None,
    }

    out = new_pending_publication(message_values, now_ms, ModuleCtx.Dedup_Window_Ms)
    return out

# ################################################################################################################################

def _write_publication(engine:'Engine', pending:'PendingPublication') -> 'None':
    """ Writes one publication through the Rust write path of pub/sub in a transaction of its own.
    """
    with engine.begin() as connection:
        _ = write_items_sqlite(connection, [pending], [], [], [], [], SubscriptionList())

# ################################################################################################################################

def _count_messages(engine:'Engine', msg_id:'str') -> 'int':
    with engine.connect() as connection:
        query = select(func.count()).select_from(message_table).where(message_table.c.msg_id == msg_id)
        out = connection.execute(query).scalar_one()
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_write_outside_mechanism_refused(tmp_path:'Path') -> 'None':
    """ An insert on an engine of the Zato database outside of every mechanism is refused before it reaches the database.
    """
    name = uuid4().hex

    with file_database_engine(tmp_path) as engine:

        with pytest.raises(WritePathViolation):
            _insert_in_transaction(engine, _new_shared_object_insert(name))

        assert _count_shared_objects(engine, name) == 0

# ################################################################################################################################

def test_serialized_write_accepted(tmp_path:'Path') -> 'None':
    """ The same insert through a serialized write is committed.
    """
    name = uuid4().hex

    with file_database_engine(tmp_path) as engine:
        _ = execute_write(engine, _new_shared_object_insert(name))

        assert _count_shared_objects(engine, name) == 1

# ################################################################################################################################

def test_audit_table_refused_to_serialized_write(tmp_path:'Path') -> 'None':
    """ A serialized write cannot insert into a table of the audit log, which only its group commit,
    maintenance, schema creation, a takeover and a seed write.
    """
    with file_database_engine(tmp_path) as engine:
        with pytest.raises(WritePathViolation):
            _ = execute_write(engine, _new_dedup_insert(uuid4().hex))

# ################################################################################################################################

def test_write_deferred_to_greenlet_refused(tmp_path:'Path') -> 'None':
    """ A greenlet that a mechanism starts begins without the mark of the mechanism, so a write handed over to it
    is refused rather than committed after the mechanism ended.
    """
    name = uuid4().hex

    with file_database_engine(tmp_path) as engine:

        with write_path(Mechanism.Serialized_Write):
            greenlet = gevent.spawn(_insert_in_transaction, engine, _new_shared_object_insert(name))

        with pytest.raises(WritePathViolation):
            greenlet.get()

        assert _count_shared_objects(engine, name) == 0

# ################################################################################################################################

def test_seed_cannot_change_rows(tmp_path:'Path') -> 'None':
    """ A seed inserts and removes rows, a table of the audit log included, and is refused when it changes one.
    """
    name = uuid4().hex

    with file_database_engine(tmp_path) as engine:

        with write_path(Mechanism.Seed):
            _insert_in_transaction(engine, _new_shared_object_insert(name))
            _insert_in_transaction(engine, _new_dedup_insert(name))

            update = shared_object_table.update().where(shared_object_table.c.name == name).values(version=2)

            with pytest.raises(WritePathViolation), engine.begin() as connection:
                _ = connection.execute(update)

        assert _count_shared_objects(engine, name) == 1

# ################################################################################################################################

def test_pubsub_rust_write_outside_mechanism_refused(tmp_path:'Path') -> 'None':
    """ A batch of pub/sub written in Rust outside of every mechanism is refused by the guard before Rust runs a statement.
    """
    msg_id = uuid4().hex

    with file_database_engine(tmp_path) as engine:

        with pytest.raises(WritePathViolation):
            _write_publication(engine, _new_publication(msg_id))

        assert _count_messages(engine, msg_id) == 0

# ################################################################################################################################

def test_pubsub_rust_write_in_group_commit_accepted(tmp_path:'Path') -> 'None':
    """ Every statement of the Rust write path of pub/sub passes the guard within the group commit,
    and the batch is committed.
    """
    msg_id = uuid4().hex

    with file_database_engine(tmp_path) as engine:

        with write_path(Mechanism.Group_Commit):
            _write_publication(engine, _new_publication(msg_id))

        assert _count_messages(engine, msg_id) == 1

# ################################################################################################################################
# ################################################################################################################################
