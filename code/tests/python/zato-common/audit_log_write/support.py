# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import NamedTuple

# SQLAlchemy
from sqlalchemy import event as sa_event, select

# Zato
from zato.common.audit_log.api import event_attr_table, event_body_table, event_link_table, event_table, AuditBody, AuditEvent, \
    AuditLink, AuditOutcome, AuditSource
from zato.common.db_env.database import get_database_engine
from zato.common.audit_log.attachment import build_attachment
from zato.common.audit_log.common import event_count_table, event_dedup_table, event_open_table, event_payload_table
from zato.common.test.direct_sql.reset import reset_table_rows
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from sqlalchemy.engine import Engine
    from sqlalchemy.sql.schema import Table
    from zato.common.audit_log.api import AuditLog
    from zato.common.audit_log.pending import pending_event_list
    from zato.common.typing_ import any_, anylist, anytuple, stranydict, strlist

    any_ = any_
    anylist = anylist
    anytuple = anytuple
    AuditLog = AuditLog
    Engine = Engine
    pending_event_list = pending_event_list
    stranydict = stranydict
    strlist = strlist
    Table = Table

    recordergen = Iterator['StatementRecorder']

# ################################################################################################################################
# ################################################################################################################################

# The backend every test of this directory runs against
Backend_PostgreSQL = 'postgresql'

# The server all the test events are written under
Server_Name = 'test-audit-log-write-server'

# The channel all the test events belong to
Object_Name = 'audit.test.write-channel'

# The moment all the events of a comparison are stamped with
Event_Time = datetime(2026, 10, 29, 12, 0, 0, 123456, tzinfo=timezone.utc)

# The verbs of the statements that write or read rows
_row_verbs = ('INSERT', 'SELECT', 'COPY')

# The outgoing MLLP connection that a part of the value events belong to, whose sent messages open exchanges
MLLP_Object_Name = 'audit.test.write-mllp-outgoing'

# The minute of Event_Time, which the per-minute counts of the value events are kept under
Event_Minute = datetime(2026, 10, 29, 12, 0, 0, tzinfo=timezone.utc)

# The moment a part of the value events was published at
Pub_Time = datetime(2026, 10, 29, 11, 59, 30, 654321, tzinfo=timezone.utc)

# The bytes and the type of the attachment of every tenth value event
Attachment_File_Name    = 'invoice.pdf'
Attachment_Content_Type = 'application/pdf'
Attachment_Content      = b'%PDF-1.7 invoice for Maria Johnson'

# The text attribute that is longer than an attribute value may be, and how much of it is stored
Long_Note                = 'Order note for Jane Doe ' * 20
Stored_Attr_Value_Length = 255

# ################################################################################################################################
# ################################################################################################################################

class PayloadSpec(NamedTuple):
    """ A payload of the value events, with the digest it is stored under and the words of its search text.
    """
    text: str
    digest: str
    search_text: str

# A payload with characters outside of ASCII, one with none at all, one shared by many events,
# a JSON document and a payload of over 1 MB, which the value events cycle through by their index.
Payload_Non_ASCII = PayloadSpec('Zamówienie dla Marii Johnson – 5,50 € Jürgen', '487bceea365abfd65961332e0c256f5e',
    'zamówienie dla marii johnson jürgen')

Payload_Empty = PayloadSpec('', '', '')

Payload_Shared = PayloadSpec('Shared order of John Smith for 12.75 USD', 'db1e24bd91da65025027ea1458aed131',
    'shared order john smith for 12.75 usd')

Payload_JSON = PayloadSpec('{"order": "ORD-0042", "customer": "Anna Miller", "amount": 99.95}',
    'fd9f16cb3fd64b2da806917335aea3e4', 'order ord 0042 customer anna miller amount 99.95')

Payload_Large = PayloadSpec('Invoice line for Maria Johnson 42.50 USD\n' * 25_000, 'a11720082645484655eead3e50efe927',
    'invoice line for maria johnson 42.50 usd')

Value_Payloads = (Payload_Non_ASCII, Payload_Empty, Payload_Shared, Payload_JSON, Payload_Large)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class EventSpec:
    """ What one value event is created with and what its row is expected to hold.
    """
    index: int
    source: str
    event_type: str
    object_name: str
    cid: str
    cid_sequence: int
    msg_id: str
    correl_id: str
    ext_client_id: str
    pub_time: 'datetime | None'
    endpoint: str
    sub_key: str
    size: int
    priority: int
    outcome: str
    application_outcome: str
    classification: str
    status: str
    duration_ms: int
    internal_data: str
    payload: PayloadSpec
    attrs: 'stranydict'
    bodies: 'stranydict'
    has_attachment: bool
    has_parent: bool
    is_export_payload_active: bool

# Type aliases
event_spec_list = list[EventSpec]

# ################################################################################################################################
# ################################################################################################################################

class StatementRecorder:
    """ The statements that write or read rows and the commits of an engine, each statement as its verb and its table.
    """

    def __init__(self) -> 'None':
        self.statements:'anylist' = []
        self.commit_count = 0

    def on_execute(
        self,
        conn:'any_',
        cursor:'any_',
        statement:'str',
        parameters:'any_',
        context:'any_',
        executemany:'bool',
        ) -> 'None':
        self.record(statement)

    def record(self, statement:'str') -> 'None':
        if verb_table := get_statement_verb_table(statement):
            self.statements.append(verb_table)

    def on_commit(self, conn:'any_') -> 'None':
        self.commit_count += 1

# ################################################################################################################################

def get_statement_verb_table(statement:'str') -> 'anytuple | None':
    """ Returns the verb and the table of a statement that writes or reads rows, or None for any other statement.
    """
    words = statement.split()
    verb = words[0]

    if verb not in _row_verbs:
        return None

    if verb == 'INSERT':
        table_name = words[2]
    elif verb == 'COPY':
        table_name = words[1]

    # A select of a function alone is recorded under the name of the function ..
    elif 'FROM' not in words:
        table_name = words[1].split('(')[0]

    else:
        from_index = words.index('FROM')
        table_name = words[from_index + 1]

        # .. and a select from a set-returning function is recorded under the name of the function as well.
        table_name = table_name.split('(')[0]

    out = (verb, table_name)
    return out

# ################################################################################################################################

@contextmanager
def record_statements(engine:'Engine') -> 'recordergen':
    """ Records the statements that SQLAlchemy sends and the commits of an engine for the duration of a block.
    """
    recorder = StatementRecorder()

    sa_event.listen(engine, 'before_cursor_execute', recorder.on_execute)
    sa_event.listen(engine, 'commit', recorder.on_commit)

    try:
        yield recorder
    finally:
        sa_event.remove(engine, 'before_cursor_execute', recorder.on_execute)
        sa_event.remove(engine, 'commit', recorder.on_commit)

# ################################################################################################################################
# ################################################################################################################################

def delete_all_rows() -> 'None':
    """ Starts a test from empty tables because the PostgreSQL container is shared by all the tests.
    """
    engine = get_database_engine()

    # The counts and the open exchanges are emptied last, after the triggers of the deleted events have written to them.
    reset_table_rows(engine, [event_attr_table, event_body_table, event_link_table, event_dedup_table, event_table,
        event_payload_table, event_count_table, event_open_table])

# ################################################################################################################################

def insert_seed_event(audit_log:'AuditLog') -> 'int':
    """ Writes the event the events of a batch link back to and returns its id.
    """
    event_id = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Message_Received, Object_Name,
        cid='cid-seed', msg_id='msg-seed', outcome=AuditOutcome.OK, data='Original order from John Smith')

    out = cast_('int', event_id)
    return out

# ################################################################################################################################

def new_batch(audit_log:'AuditLog', event_count:'int', seed_event_id:'int') -> 'pending_event_list':
    """ Returns events with attributes of every kind, two bodies each, an attachment on every tenth event
    and a link to the seed event on every second one, all stamped with the same moment.
    """
    out:'pending_event_list' = []

    for index in range(event_count):

        attachments:'anylist' = []
        parents:'anylist' = []

        if index % 10 == 0:
            attachment = build_attachment('invoice.pdf', 'application/pdf', b'%PDF-1.7 invoice for Maria Johnson')
            attachments.append(attachment)

        if index % 2 == 0:
            parents.append(seed_event_id)

        attrs = {
            'partner': 'Maria Johnson',
            'order_id': f'ORD-{index:04d}',
            'amount': index * 10.25,
            'quantity': index,
            'is_priority': index % 3 == 0,
        }

        bodies = {
            AuditBody.Request: f'{{"order": {index}, "customer": "John Smith"}}',
            AuditBody.Response: f'{{"order": {index}, "status": "accepted"}}',
        }

        pending = audit_log.new_pending_event(AuditSource.REST_Channel, AuditEvent.Message_Received, Object_Name,
            cid=f'cid-{index}', msg_id=f'msg-{index}', outcome=AuditOutcome.OK, data=f'Order {index} from John Smith',
            internal_data=f'{{"digest": "sha256-{index}"}}', attrs=attrs, bodies=bodies, attachments=attachments,
            parents=parents, parent_link_type=AuditLink.Resubmit_Of)

        pending.values['event_time'] = Event_Time
        out.append(pending)

    return out

# ################################################################################################################################

def read_rows(table:'Table') -> 'anylist':
    """ Returns all the rows of a table as dicts, in the order of their ids.
    """
    engine = get_database_engine()

    query = select(table)
    query = query.order_by(table.c.id)

    out:'anylist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            values = dict(row._mapping)
            out.append(values)

    return out

# ################################################################################################################################

def _set_outcome(spec:'EventSpec') -> 'None':
    """ Gives every sixth event a transient failure, every sixth one from the fourth on a permanent one
    and all the others success, with the classification that each of them is expected to receive.
    """
    spec.application_outcome = ''
    spec.status = ''

    if spec.index % 6 == 5:
        spec.outcome = AuditOutcome.Error
        spec.status = 'connection timeout'
        spec.classification = 'transient'

    elif spec.index % 6 == 3:
        spec.outcome = AuditOutcome.Error
        spec.application_outcome = 'validation failed'
        spec.classification = 'permanent'

    else:
        spec.outcome = AuditOutcome.OK
        spec.classification = ''

# ################################################################################################################################

def _set_kind(spec:'EventSpec', event_count:'int') -> 'None':
    """ Makes the even events messages sent over MLLP and the odd ones messages received by a REST channel,
    except that the last event of a batch of more than one acknowledges the message of the first one.
    """
    index = spec.index

    if index > 0 and index == event_count - 1:
        spec.source = AuditSource.MLLP_Outgoing
        spec.event_type = AuditEvent.Ack_Received
        spec.object_name = MLLP_Object_Name
        spec.msg_id = 'msg-0000'

    elif index % 2 == 0:
        spec.source = AuditSource.MLLP_Outgoing
        spec.event_type = AuditEvent.Message_Sent
        spec.object_name = MLLP_Object_Name
        spec.msg_id = f'msg-{index:04d}'

    else:
        spec.source = AuditSource.REST_Channel
        spec.event_type = AuditEvent.Message_Received
        spec.object_name = Object_Name
        spec.msg_id = f'msg-{index:04d}'

# ################################################################################################################################

def _set_companions(spec:'EventSpec') -> 'None':
    """ Gives the MLLP events numeric, boolean and non-ASCII attributes, the REST events text attributes with one
    longer than a stored value and two bodies, every seventh event no attributes, every tenth one an attachment
    and every second one from the third on a link to the seed event.
    """
    index = spec.index

    if index % 7 == 6:
        spec.attrs = {}

    elif index % 2 == 0:
        spec.attrs = {
            'mrn': f'MRN-{index:04d}',
            'msg_type': 'ADT^A01',
            'facility': 'Szpital Świętej Marii',
            'quantity': index,
            'amount': index * 10.25,
            'is_priority': index % 3 == 0,
        }

    else:
        spec.attrs = {
            'partner': 'Maria Johnson',
            'order_id': f'ORD-{index:04d}',
            'note': Long_Note,
        }

    if index % 2 == 1:
        spec.bodies = {
            AuditBody.Request: f'{{"order": {index}, "customer": "Jürgen Müller"}}',
            AuditBody.Response: f'{{"order": {index}, "status": "przyjęte"}}',
        }
    else:
        spec.bodies = {}

    spec.has_attachment = index % 10 == 0
    spec.has_parent = index > 0 and index % 2 == 0

# ################################################################################################################################

def get_event_spec(index:'int', event_count:'int') -> 'EventSpec':
    """ Returns what the value event at the given position of a batch of the given size is created with.
    Each pair of events from the second one on shares a cid, and the first event has none.
    """
    out = EventSpec()
    out.index = index

    _set_kind(out, event_count)
    _set_outcome(out)
    _set_companions(out)

    if index == 0:
        out.cid = ''
        out.cid_sequence = 0
    else:
        pair_index = (index + 1) // 2
        out.cid = f'cid-{pair_index:04d}'
        out.cid_sequence = 2 - index % 2

    if index % 3 == 0:
        out.correl_id = f'correl-{index:04d}'
    else:
        out.correl_id = ''

    if index % 4 == 1:
        out.ext_client_id = 'client-maria-johnson'
    else:
        out.ext_client_id = ''

    if index % 2 == 0:
        out.pub_time = None
    else:
        out.pub_time = Pub_Time

    if index % 2 == 1:
        out.endpoint = '/api/orders/submit'
    else:
        out.endpoint = '10.0.0.7:2575'

    if index % 5 == 2:
        out.sub_key = 'zpsk.test.write.1'
    else:
        out.sub_key = ''

    if index % 2 == 0:
        out.internal_data = f'{{"digest": "sha256-{index}"}}'
    else:
        out.internal_data = ''

    out.size = index * 100
    out.priority = index % 10
    out.duration_ms = index * 3
    out.payload = Value_Payloads[index % len(Value_Payloads)]
    out.is_export_payload_active = index % 3 == 1

    return out

# ################################################################################################################################

def get_event_specs(event_count:'int') -> 'event_spec_list':
    """ Returns what each value event of a batch of the given size is created with, in the order of the batch.
    """
    out:'event_spec_list' = []

    for index in range(event_count):
        spec = get_event_spec(index, event_count)
        out.append(spec)

    return out

# ################################################################################################################################

def new_value_batch(audit_log:'AuditLog', specs:'event_spec_list', seed_event_id:'int') -> 'pending_event_list':
    """ Returns the events of the given specs, all stamped with Event_Time.
    """
    out:'pending_event_list' = []

    for spec in specs:

        attachments:'anylist' = []
        parents:'anylist' = []

        if spec.has_attachment:
            attachment = build_attachment(Attachment_File_Name, Attachment_Content_Type, Attachment_Content)
            attachments.append(attachment)

        if spec.has_parent:
            parents.append(seed_event_id)

        pending = audit_log.new_pending_event(spec.source, spec.event_type, spec.object_name,
            cid=spec.cid, msg_id=spec.msg_id, correl_id=spec.correl_id, ext_client_id=spec.ext_client_id,
            pub_time=spec.pub_time, endpoint=spec.endpoint, sub_key=spec.sub_key, size=spec.size, priority=spec.priority,
            outcome=spec.outcome, application_outcome=spec.application_outcome, status=spec.status,
            duration_ms=spec.duration_ms, data=spec.payload.text, internal_data=spec.internal_data, attrs=spec.attrs,
            bodies=spec.bodies, attachments=attachments, parents=parents, parent_link_type=AuditLink.Batch_Item_Of,
            is_export_payload_active=spec.is_export_payload_active)

        pending.values['event_time'] = Event_Time
        out.append(pending)

    return out

# ################################################################################################################################

def read_value_events() -> 'anylist':
    """ Returns the rows of the value events, without the seed event, in the order of their ids.
    """
    out:'anylist' = []

    for row in read_rows(event_table):
        if row['cid'] != 'cid-seed':
            out.append(row)

    return out

# ################################################################################################################################
# ################################################################################################################################
