# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.as2.outbound import SendResult
from zato.common.audit_log.api import event_table, get_audit_engine
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.typing_ import any_, dictlist, stranydict, strnone

# ################################################################################################################################
# ################################################################################################################################

# The topic reprocessed messages land on when the partner has no routing override.
Default_Topic = 'zato.as2.inbound'

# A short run of bytes no text decoding survives - byte 0x80 is not valid UTF-8 and 0x00 does not
# survive a round trip through a text field either. Real payloads that look like this are the PDFs
# and compressed archives that travel as attachments next to an EDI document.
Binary_Payload = b'%PDF-1.7\x00\x80\xff\xfe binary content \x01\x02\x03'

# ################################################################################################################################
# ################################################################################################################################

def use_tmp_audit_db(tmp_path:'os.PathLike') -> 'None':
    """ Points the audit database at a per-test SQLite file.
    """
    directory = str(tmp_path)
    database_path = os.path.join(directory, 'audit.db')

    os.environ[AuditLogCtx.Env_Type] = AuditLogCtx.Type_SQLite
    os.environ[AuditLogCtx.Env_Name] = database_path

# ################################################################################################################################

def cleanup_env() -> 'None':
    del os.environ[AuditLogCtx.Env_Type]
    del os.environ[AuditLogCtx.Env_Name]

# ################################################################################################################################

def get_last_event_id() -> 'int':
    """ Returns the id of the most recently written audit event.
    """
    newest_first = event_table.c.id.desc()
    statement = select(event_table.c.id).order_by(newest_first).limit(1)
    engine = get_audit_engine()

    with engine.connect() as connection:
        result = connection.execute(statement)
        row = result.first()

    out = row[0]
    return out

# ################################################################################################################################

def get_events(event_type:'str') -> 'dictlist':
    """ Returns all events of one type, oldest first, each as a dict.
    """
    statement = select(
        event_table.c.cid,
        event_table.c.correl_id,
        event_table.c.object_name,
        event_table.c.msg_id,
        event_table.c.data,
    ).where(event_table.c.event_type == event_type).order_by(event_table.c.id)

    engine = get_audit_engine()

    with engine.connect() as connection:
        result = connection.execute(statement)
        rows = result.fetchall()

    out:'dictlist' = []

    for cid, correl_id, object_name, msg_id, data in rows:
        out.append({'cid': cid, 'correl_id': correl_id, 'object_name': object_name, 'msg_id': msg_id, 'data': data})

    return out

# ################################################################################################################################
# ################################################################################################################################

class SendRecorder:
    """ A stand-in for an outgoing connection's send method, remembering what it was given
    and answering with a fresh delivery result the way the real pipeline would.
    """

    def __init__(self) -> 'None':
        self.payload:'any_' = None
        self.filename:'strnone' = None

# ################################################################################################################################

    def __call__(self, payload:'any_', filename:'strnone') -> 'SendResult':
        self.payload = payload
        self.filename = filename

        out = SendResult()
        out.is_ok = True
        out.message_id = '<resent-message@zato>'
        out.mic = 'UmVzZW50TUlDVmFsdWU=, sha-256'

        return out

# ################################################################################################################################

class RouteRecorder:
    """ A stand-in for a routing target, remembering where each message went.
    """

    def __init__(self) -> 'None':
        self.target_name = None
        self.message = None

        # Every message this target received, which is more than one for a delivery
        # that carried several documents.
        self.messages:'dictlist' = []

# ################################################################################################################################

    def __call__(self, target_name:'str', message:'stranydict') -> 'None':
        self.target_name = target_name
        self.message = message
        self.messages.append(message)

# ################################################################################################################################
# ################################################################################################################################
