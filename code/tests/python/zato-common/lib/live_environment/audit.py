# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What a live suite reads back from the audit trail the server under test wrote - the SQLite file the
# quickstart environment points its server at.

# stdlib
import os

# SQLAlchemy
from sqlalchemy import create_engine, select

# Zato
from zato.common.audit_log.api import event_attr_table, event_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

def events(
    audit_db_path:'str',
    *,
    event_type:'str',
    object_name:'str'='',
    msg_id:'str'='',
    cid:'str'='',
    ) -> 'anylist':
    """ The events of one type the trail holds, oldest first, each as a dict of its columns, narrowed by
    whichever of the object, the message id and the correlation id is given. A trail not written yet has none.
    """
    out:'anylist' = []

    if not os.path.exists(audit_db_path):
        return out

    engine = create_engine(f'sqlite:///{audit_db_path}')

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

def attributes(audit_db_path:'str', event_id:'int') -> 'strstrdict':
    """ The attributes of one event, name to value.
    """
    engine = create_engine(f'sqlite:///{audit_db_path}')

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

def attribute_of(audit_db_path:'str', event:'anydict', name:'str') -> 'str':
    """ One attribute of one event.
    """
    event_attributes = attributes(audit_db_path, event['id'])

    out = event_attributes[name]
    return out

# ################################################################################################################################
# ################################################################################################################################
