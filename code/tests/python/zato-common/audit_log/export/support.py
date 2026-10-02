# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from threading import Lock
from time import monotonic, sleep, time_ns

# OpenTelemetry
from opentelemetry.proto.collector.logs.v1.logs_service_pb2 import ExportLogsServiceRequest
from opentelemetry.proto.common.v1.common_pb2 import InstrumentationScope
from opentelemetry.proto.resource.v1.resource_pb2 import Resource

# Zato
from zato.common.audit_log.api import AuditLog
from zato.common.audit_log.export.config import ExportConfig, ModuleCtx as ConfigCtx
from zato.common.audit_log.export.mapping import QueuedEvent, to_key_values
from zato.common.audit_log.export.queue import ExportQueue

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from opentelemetry.proto.common.v1.common_pb2 import AnyValue
    from opentelemetry.proto.logs.v1.logs_pb2 import LogRecord
    from zato.common.audit_log.buffer import PendingEvent
    from zato.common.typing_ import any_, anylist, callable_, intnone, stranydict

    log_record_list = list[LogRecord]
    pending_event_list = list[PendingEvent]

# ################################################################################################################################
# ################################################################################################################################

# The server every test event is written under
Server_Name = 'test-export-server'

# Where the fake collector is said to be
Endpoint = 'http://collector.test:4318/v1/logs'

# How long a test waits for the worker before giving up
Wait_Timeout = 5.0

# ################################################################################################################################
# ################################################################################################################################

class FakeSender:
    """ Keeps every body it was given and refuses them all while told to.
    """
    def __init__(self) -> 'None':
        self.bodies:'list[bytes]' = []
        self.attempts:'list[bytes]' = []
        self.is_refusing = False
        self.reason = 'HTTP 503 Service Unavailable'
        self.is_closed = False
        self.lock = Lock()

    def prepare(self, serialized:'bytes') -> 'bytes':
        return serialized

    def send(self, body:'bytes') -> 'str':
        with self.lock:
            self.attempts.append(body)
            if self.is_refusing:
                out = self.reason
            else:
                self.bodies.append(body)
                out = ''

        return out

    def close(self) -> 'None':
        self.is_closed = True

# ################################################################################################################################

    def get_records(self) -> 'log_record_list':
        """ Every record the collector accepted, in the order it arrived.
        """
        out:'log_record_list' = []

        with self.lock:
            bodies = list(self.bodies)

        for body in bodies:
            out.extend(decode_records(body))

        return out

# ################################################################################################################################
# ################################################################################################################################

def decode_records(body:'bytes') -> 'log_record_list':
    """ Parses one exported body back into its log records.
    """
    request = ExportLogsServiceRequest.FromString(body)

    out:'log_record_list' = []

    for resource_logs in request.resource_logs:
        for scope_logs in resource_logs.scope_logs:
            out.extend(scope_logs.log_records)

    return out

# ################################################################################################################################

def from_any_value(value:'AnyValue') -> 'any_':
    """ Turns an OTLP value back into a Python one.
    """
    kind = value.WhichOneof('value')

    if kind is None:
        return None

    if kind == 'array_value':
        out:'anylist' = []
        for item in value.array_value.values:
            out.append(from_any_value(item))
        return out

    out = getattr(value, kind)
    return out

# ################################################################################################################################

def attributes_of(record:'LogRecord') -> 'stranydict':
    """ The attributes of a record as a plain dict.
    """
    out:'stranydict' = {}

    for key_value in record.attributes:
        out[key_value.key] = from_any_value(key_value.value)

    return out

# ################################################################################################################################

def build_config(**overrides:'any_') -> 'ExportConfig':
    """ A configuration with the defaults, each test overriding what it is about.
    """
    out = ExportConfig()

    out.endpoint = Endpoint
    out.protocol = ConfigCtx.Protocol_HTTP
    out.headers = {}
    out.compression = ConfigCtx.Compression_None
    out.timeout_ms = ConfigCtx.Default_Timeout_Ms

    out.ssl_ca_file = ''
    out.ssl_cert_file = ''
    out.ssl_key_file = ''
    out.ssl_verify = ConfigCtx.Default_SSL_Verify

    out.batch_size = ConfigCtx.Default_Batch_Size
    out.max_batch_size = ConfigCtx.Default_Max_Batch_Size
    out.flush_interval_ms = ConfigCtx.Default_Flush_Interval_Ms
    out.queue_size = ConfigCtx.Default_Queue_Size

    out.sources = set()
    out.max_payload_size = ConfigCtx.Default_Max_Payload_Size

    out.environment = ''
    out.resource_attributes = {}

    for name, value in overrides.items():
        setattr(out, name, value)

    return out

# ################################################################################################################################

def build_queue(config:'ExportConfig', sender:'FakeSender') -> 'ExportQueue':
    """ A queue over a fake sender with a minimal resource and scope.
    """
    resource = Resource(attributes=to_key_values({'service.name': 'zato-server'}))
    scope = InstrumentationScope(name='zato.audit_log', version='test')

    out = ExportQueue(config=config, sender=sender, resource=resource, scope=scope, address=Endpoint)
    return out

# ################################################################################################################################

def build_stopped_queue(config:'ExportConfig', sender:'FakeSender') -> 'ExportQueue':
    """ A queue whose worker exits as soon as it starts, so a test drives the batches itself, the way flush_and_stop does.
    """
    out = build_queue(config, sender)
    out._stop.set()

    return out

# ################################################################################################################################

def wait_until(check:'callable_', timeout:'float'=Wait_Timeout) -> 'bool':
    """ Waits for a condition the worker thread is about to satisfy.
    """
    deadline = monotonic() + timeout

    while monotonic() < deadline:
        if check():
            return True
        sleep(0.01)

    out = check()
    return out

# ################################################################################################################################

def wait_for_attempts(sender:'FakeSender', count:'int') -> 'bool':
    """ Waits until the sender was asked at least this many times.
    """
    def check() -> 'bool':
        return len(sender.attempts) >= count

    out = wait_until(check)
    return out

# ################################################################################################################################

def wait_for_bodies(sender:'FakeSender', count:'int') -> 'bool':
    """ Waits until the sender accepted this many bodies.
    """
    def check() -> 'bool':
        return len(sender.bodies) == count

    out = wait_until(check)
    return out

# ################################################################################################################################

def wait_for_exported(queue:'ExportQueue', count:'int') -> 'bool':
    """ Waits until the queue counts this many exported events.
    """
    def check() -> 'bool':
        return queue.get_stats()['exported'] == count

    out = wait_until(check)
    return out

# ################################################################################################################################

def wait_for_paused(queue:'ExportQueue') -> 'bool':
    """ Waits until the queue reports an outage.
    """
    def check() -> 'bool':
        return queue.get_stats()['is_paused']

    out = wait_until(check)
    return out

# ################################################################################################################################
# ################################################################################################################################

class CapturingAuditLog(AuditLog):
    """ An audit log that keeps the events it would have written, giving each one the id the database would.
    """
    def __init__(self, server_name:'str'=Server_Name) -> 'None':
        super().__init__(server_name, flush_max_size=1, flush_max_wait_ms=1)
        self.pending:'pending_event_list' = []
        self.next_id = 1

    def _write_batch(self, batch:'pending_event_list') -> 'intnone':
        out = None

        for pending in batch:
            pending.event_id = self.next_id
            out = self.next_id
            self.next_id += 1
            self.pending.append(pending)

        return out

# ################################################################################################################################

    def last(self) -> 'PendingEvent':
        out = self.pending[-1]
        return out

# ################################################################################################################################
# ################################################################################################################################

def to_queued(pending:'PendingEvent', *, is_payload_active:'bool'=False) -> 'QueuedEvent':
    """ What the export queues for one written event.
    """
    out = QueuedEvent()
    out.event_id = pending.event_id
    out.values = pending.values
    out.attrs = pending.attrs
    out.bodies = pending.bodies
    out.observed_ns = time_ns()
    out.is_payload_active = is_payload_active

    return out

# ################################################################################################################################

def build_queued(**overrides:'any_') -> 'QueuedEvent':
    """ A queued event with every column set to something, each test overriding what it is about.
    """
    values:'stranydict' = {
        'cid': 'cid-1',
        'cid_sequence': 1,
        'source': 'rest-channel',
        'event_type': 'request-received',
        'object_name': 'test.channel',
        'msg_id': '',
        'correl_id': '',
        'ext_client_id': '',
        'pub_time_iso': '',
        'event_time_iso': '2026-03-01T10:20:30.123456+00:00',
        'server_name': Server_Name,
        'endpoint': 'test.service',
        'sub_key': '',
        'size': 12,
        'priority': 0,
        'outcome': 'ok',
        'application_outcome': '',
        'classification': '',
        'status': '',
        'duration_ms': 0,
        'data': '',
    }

    out = QueuedEvent()
    out.event_id = overrides.pop('event_id', 1)
    out.attrs = overrides.pop('attrs', {})
    out.bodies = overrides.pop('bodies', {})
    out.observed_ns = overrides.pop('observed_ns', time_ns())
    out.is_payload_active = overrides.pop('is_payload_active', False)

    values.update(overrides)
    out.values = values

    return out

# ################################################################################################################################
# ################################################################################################################################
