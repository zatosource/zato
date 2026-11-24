# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What a live suite reads back from the audit trail the server under test wrote - the Zato database that
# the Zato_Database_* variables of the quickstart environment select.

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_attr_table, event_table
from zato.common.db_env.database import new_odb_engine
from zato.common.test.pubsub_database import pubsub_db_env

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import anydict, anylist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

def new_database_engine(database_env:'strstrdict') -> 'Engine':
    """ An engine of the Zato database that the Zato_Database_* variables given select, which its caller disposes.
    """
    with pubsub_db_env(database_env):
        out = new_odb_engine()

    return out

# ################################################################################################################################

def events(
    database_env:'strstrdict',
    *,
    event_type:'str',
    object_name:'str'='',
    msg_id:'str'='',
    cid:'str'='',
    ) -> 'anylist':
    """ The events of one type the trail holds, oldest first, each as a dict of its columns, narrowed by
    whichever of the object, the message id and the correlation id is given.
    """
    out:'anylist' = []

    engine = new_database_engine(database_env)

    query = select(event_table)
    query = query.where(event_table.c.event_type == event_type)

    if object_name:
        query = query.where(event_table.c.object_name == object_name)

    if msg_id:
        query = query.where(event_table.c.msg_id == msg_id)

    if cid:
        query = query.where(event_table.c.cid == cid)

    query = query.order_by(event_table.c.id)

    with engine.connect() as connection:
        for row in connection.execute(query):
            out.append(dict(row._mapping))

    engine.dispose()

    return out

# ################################################################################################################################

def attributes(database_env:'strstrdict', event_id:'int') -> 'strstrdict':
    """ The attributes of one event, name to value.
    """
    engine = new_database_engine(database_env)

    query = select(event_attr_table)
    query = query.where(event_attr_table.c.event_id == event_id)

    out:'strstrdict' = {}

    with engine.connect() as connection:
        for row in connection.execute(query):
            mapping = row._mapping
            out[mapping['name']] = mapping['value']

    engine.dispose()

    return out

# ################################################################################################################################

def attribute_of(database_env:'strstrdict', event:'anydict', name:'str') -> 'str':
    """ One attribute of one event.
    """
    event_attributes = attributes(database_env, event['id'])

    out = event_attributes[name]
    return out

# ################################################################################################################################
# ################################################################################################################################
