# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What the delivery tests deliver through and read back afterwards - connections that remember
# what reached them and fail whichever of them a test needs to see fail, the destination list a
# channel stores, and the recorded rows the deliveries left behind.

# stdlib
from http.client import BAD_REQUEST, SERVICE_UNAVAILABLE

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_attr_table, event_table, get_audit_engine, AuditEvent, AuditLog
from zato.common.destination.constants import DestinationType
from zato.common.destination.coordinator import new_context, new_transports
from zato.common.destination.model import new_send_result

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.destination.coordinator import DeliveryContext, DeliveryTransports
    from zato.common.destination.model import DestinationEntry, HopSendResult
    from zato.common.typing_ import any_, anydict, anylist, stranydict, strintdict

    anydict = anydict
    anylist = anylist
    HopSendResult = HopSendResult
    stranydict = stranydict
    strintdict = strintdict

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
Server_Name = 'test-destination-server'

# The channel whose destinations the tests deliver to
Channel_Name = 'hl7.test.channel'

# The correlation id of the message that came in
CID = 'cid-destination-1'

# The connections the destinations point at
MLLP_Connection = 'hl7.forward.ehr'
REST_Connection = 'rest.billing'
FHIR_Connection = 'fhir.ehr'

# What arrived on the channel
Request_Payload = 'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FACILITY|20260101120000||ADT^A01|MSG00001|P|2.5'

# A failure another attempt can get past, and one it never can
Transient_Error = 'Connection refused by the receiver'
Permanent_Error = 'Message failed validation against the schema'

# What a destination that turned the message down answers with - one refusal another attempt
# can get past and one that is answered the same way however often it is repeated.
Rejected_Status = f'HTTP {SERVICE_UNAVAILABLE} Service Unavailable'
Permanently_Rejected_Status = f'HTTP {BAD_REQUEST} Bad Request'

# Two statuses whose wording says the opposite of what the adapter knows.
Reads_Transient_Status = 'The receiver is unavailable for now'
Reads_Permanent_Status = 'The message is invalid'

# How long the tests wait between two attempts at the same destination
Retry_Sleep_Seconds = 0.01

# ################################################################################################################################
# ################################################################################################################################

class ConnectionRecorder:
    """ A stand-in for the real connections, remembering what was delivered through each of
    them and failing whichever of them the test needs to see fail.
    """
    def __init__(self) -> 'None':

        # Every delivery that was attempted, as (destination name, payload)
        self.deliveries:'anylist' = []

        # How long the deliveries waited between attempts
        self.sleeps:'anylist' = []

        # How many times a spawned run was handed over
        self.spawn_count = 0

        # Destinations that always fail, by the error each of them fails with
        self.always_failing:'stranydict' = {}

        # Destinations that fail a number of times before going through
        self.failing_attempts:'strintdict' = {}

        # Destinations that answer every message by turning it down, by the status each
        # of them answers with.
        self.always_rejecting:'stranydict' = {}

# ################################################################################################################################

    def make(self) -> 'DeliveryTransports':
        out = new_transports(self.send, self.sleep, self.spawn)
        return out

# ################################################################################################################################

    def send(self, entry:'DestinationEntry', payload:'any_', cid:'str'='') -> 'HopSendResult':
        name = entry.name
        self.deliveries.append((name, payload))

        if error := self.always_failing.get(name):
            raise Exception(error)

        if remaining := self.failing_attempts.get(name):
            self.failing_attempts[name] = remaining - 1
            raise Exception(Transient_Error)

        # A destination that turned the message down still answered, so the refusal comes back
        # as data with the answer alongside it rather than as an exception.
        if status := self.always_rejecting.get(name):
            body = f'Refused by {name}'
            out = new_send_result(body, is_rejected=True, status=status, response_text=body)
            return out

        response = f'Accepted by {name}'

        out = new_send_result(response, response_text=response)
        return out

# ################################################################################################################################

    def sleep(self, seconds:'float') -> 'None':
        self.sleeps.append(seconds)

# ################################################################################################################################

    def spawn(self, function:'any_', *args:'any_') -> 'None':
        self.spawn_count += 1
        function(*args)

# ################################################################################################################################

    def get_delivered_names(self) -> 'anylist':
        out = []

        for name, _ in self.deliveries:
            out.append(name)

        return out

# ################################################################################################################################
# ################################################################################################################################

class RejectThenFailRecorder(ConnectionRecorder):
    """ A connection whose first attempt is turned down and whose every later attempt gets
    no answer at all.
    """
    def __init__(self, name:'str') -> 'None':
        super().__init__()
        self.name = name

    def send(self, entry:'DestinationEntry', payload:'any_', cid:'str'='') -> 'HopSendResult':
        self.deliveries.append((entry.name, payload))
        delivery_count = len(self.deliveries)

        if delivery_count == 1:
            body = f'Refused by {self.name}'
            out = new_send_result(body, is_rejected=True, status=Rejected_Status, response_text=body)
            return out

        raise Exception(Transient_Error)

# ################################################################################################################################
# ################################################################################################################################

class ClassifyingRecorder(ConnectionRecorder):
    """ A connection whose every refusal carries the classification the adapter made of it,
    with a status whose wording says the opposite.
    """
    def __init__(self, name:'str', classification:'str', status:'str') -> 'None':
        super().__init__()
        self.name = name
        self.classification = classification
        self.status = status

    def send(self, entry:'DestinationEntry', payload:'any_', cid:'str'='') -> 'HopSendResult':
        self.deliveries.append((entry.name, payload))

        body = f'Refused by {self.name}'

        out = new_send_result(body, is_rejected=True, status=self.status, response_text=body,
            classification=self.classification)
        return out

# ################################################################################################################################
# ################################################################################################################################

def get_stored_list() -> 'anylist':
    """ Returns three destinations, one of each type the tests deliver through.
    """
    out = [
        {
            'name': MLLP_Connection,
            'type': DestinationType.MLLP,
            'connection': MLLP_Connection,
            'is_active': True,
            'options': {},
        },
        {
            'name': REST_Connection,
            'type': DestinationType.REST,
            'connection': REST_Connection,
            'is_active': True,
            'options': {'method': 'PUT'},
        },
        {
            'name': FHIR_Connection,
            'type': DestinationType.FHIR,
            'connection': FHIR_Connection,
            'is_active': True,
            'options': {'method': 'POST', 'path': '/Patient'},
        },
    ]

    return out

# ################################################################################################################################

def new_test_context(recorder:'ConnectionRecorder', *, retry_count:'int'=0) -> 'DeliveryContext':
    """ Returns the context one delivery run shares, with the retries the test allows.
    """
    audit_log = AuditLog(Server_Name)
    transports = recorder.make()

    out = new_context(Channel_Name, CID, transports, audit_log,
        retry_count=retry_count, retry_sleep_seconds=Retry_Sleep_Seconds)

    return out

# ################################################################################################################################

def get_hop_rows() -> 'anylist':
    """ Returns every delivery recorded for the message, oldest first.
    """
    engine = get_audit_engine()

    query = select(event_table)
    query = query.where(event_table.c.event_type == AuditEvent.Request_Sent)
    query = query.where(event_table.c.cid == CID)
    query = query.order_by(event_table.c.id)

    with engine.connect() as connection:
        result = connection.execute(query).fetchall()

    out = []

    for row in result:
        out.append(dict(row._mapping))

    return out

# ################################################################################################################################

def get_attr_map(event_id:'int') -> 'anydict':
    """ Returns the attributes of one recorded delivery as a dict of name to value.
    """
    engine = get_audit_engine()

    query = select(event_attr_table.c.name, event_attr_table.c.value)
    query = query.where(event_attr_table.c.event_id == event_id)

    with engine.connect() as connection:
        result = connection.execute(query).fetchall()

    out = {}

    for row in result:
        out[row.name] = row.value

    return out

# ################################################################################################################################
# ################################################################################################################################
