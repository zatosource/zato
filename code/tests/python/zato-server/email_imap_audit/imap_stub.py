# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What reading a mailbox reaches for when it is exercised offline - a fabricated message
# where a live server would have answered, the connection built around it and the
# environment that points the audit log at a throwaway database.

# stdlib
import os
from base64 import b64encode
from contextlib import contextmanager
from io import BytesIO

# Zato
from live_sql.env import database_env
from zato.common.audit_log.api import AuditLog, ModuleCtx as AuditLogCtx
from zato.common.ext.bunch import Bunch
from zato.common.ext.imbox.parser import Struct
from zato.server.connection.email import GenericIMAPConnection

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import any_

    envgen = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

# The server the audit events are written under
Server_Name = 'test-imap-audit-server'

# The name the connection under test goes by
Connection_Name = 'test.imap.audit'

# The uid the fabricated message arrives under
Message_UID = b'4211'

# What the fabricated message says
Subject = 'Lab results ready'
Body_Text = 'The body of the message the mailbox holds'

# The file that travels with it
Attachment_Name = 'results.pdf'
Attachment_Type = 'application/pdf'
Attachment_Content = b'%PDF-1.4 lab results'

# The prefix all the audit log database environment variables share
_env_prefix = 'Zato_Audit_Log_DB_'

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def imap_audit_env(tmp_path:'any_') -> 'envgen':
    """ Points the audit log at a throwaway SQLite database for the duration of a test.
    """
    db_path = os.path.join(str(tmp_path), 'audit.db')

    details = {
        'type': AuditLogCtx.Type_SQLite,
        'name': db_path,
    }

    with database_env(_env_prefix, details):
        yield

# ################################################################################################################################
# ################################################################################################################################

def new_message_struct() -> 'Struct':
    """ Builds the struct the imbox parser would have built out of one message
    with a subject, a body and one attachment.
    """
    out = Struct(**{
        'subject': Subject,
        'sent_from': [{'name': 'Lab', 'email': 'lab@example.com'}],
        'sent_to': [{'name': 'Ward', 'email': 'ward@example.com'}],
        'body': {'plain': [Body_Text], 'html': []},
        'attachments': [{
            'filename': Attachment_Name,
            'content-type': Attachment_Type,
            'content': BytesIO(Attachment_Content),
            'size': len(Attachment_Content),
        }],
    })

    return out

# ################################################################################################################################
# ################################################################################################################################

class _ImapSocketStub:
    def close(self) -> 'None':
        pass

class _ImapServerStub:
    sock = _ImapSocketStub()

class _ImapTransportStub:
    server = _ImapServerStub()

# ################################################################################################################################

class ImboxStub:
    """ Stands in for the imbox client - it hands over the fabricated message where a live
    server would have answered a fetch.
    """

    class _Connection:
        def select(self, folder:'any_') -> 'any_':
            return ('OK', [])

    def __init__(self, message:'Struct') -> 'None':
        self.message = message
        self.connection = self._Connection()
        self.server = _ImapTransportStub()

    def fetch_list(self, criteria:'any_') -> 'any_':
        yield (Message_UID, self.message)

    def close(self) -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################

class StubbedIMAPConnection(GenericIMAPConnection):
    """ The connection under test - real except for the client, which never touches
    the network.
    """

    # The message the stubbed client answers a fetch with
    message:'Struct'

    @contextmanager
    def get_connection(self) -> 'any_':
        yield ImboxStub(self.message)

# ################################################################################################################################

def new_imap_connection(message:'Struct', *, is_audit_log_active:'bool'=True) -> 'StubbedIMAPConnection':
    """ Builds the connection under test around one fabricated message.
    """
    config = Bunch()

    config.name = Connection_Name
    config.is_audit_log_active = is_audit_log_active
    config.get_criteria = 'UNSEEN'

    audit_log = AuditLog(Server_Name)

    out = StubbedIMAPConnection(config, config, audit_log)
    out.message = message

    return out

# ################################################################################################################################
# ################################################################################################################################

def new_native_ms365_message() -> 'Bunch':
    """ Builds what the Microsoft 365 client would have handed over for one message
    with a subject, an HTML body and one attachment, its content base64-encoded
    the way the Graph API sends it.
    """
    attachment = Bunch()
    attachment.name = Attachment_Name
    attachment.content = b64encode(Attachment_Content).decode('ascii')

    sender = Bunch()
    sender.name = 'Lab'
    sender.address = 'lab@example.com'

    recipient = Bunch()
    recipient.name = 'Ward'
    recipient.address = 'ward@example.com'

    out = Bunch()

    out.subject = Subject
    out.body = f'<p>{Body_Text}</p>'
    out.sender = sender
    out.to = [recipient]
    out.cc = []
    out.attachments = [attachment]

    return out

# ################################################################################################################################
# ################################################################################################################################
