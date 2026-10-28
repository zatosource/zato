# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import ssl
from dataclasses import dataclass
from datetime import timedelta
from http.client import BAD_GATEWAY, GATEWAY_TIMEOUT, SERVICE_UNAVAILABLE
from threading import RLock
from urllib.error import HTTPError, URLError

# SQLAlchemy
from sqlalchemy import insert, select, update

# Zato
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditOutcome
from zato.common.b2b.common.commit_group import TransactionResult
from zato.common.b2b.common.commit_sql import EventWrite, write_events
from zato.common.b2b.common.schema import address_state_table
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Connection
    from zato.common.b2b.common.clock import Clock
    from zato.common.b2b.common.commit_group import GroupCommitWriter
    from zato.common.typing_ import callable_, strlist
    callable_ = callable_
    Clock = Clock
    Connection = Connection
    datetime = datetime
    GroupCommitWriter = GroupCommitWriter
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The environment variables with the number of consecutive transport failures that suspend an address,
# and with how often a suspended address is probed, in seconds.
Env_Suspend_After_Failures = 'Zato_B2B_Suspend_After_Failures'
Env_Probe_Interval_Seconds = 'Zato_B2B_Probe_Interval_Seconds'

Default_Suspend_After_Failures = 5
Default_Probe_Interval_Seconds = 60

# The HTTP statuses of a gateway in front of a partner that cannot reach it.
_transport_failure_statuses = (BAD_GATEWAY, SERVICE_UNAVAILABLE, GATEWAY_TIMEOUT)

# ################################################################################################################################
# ################################################################################################################################

class AddressState:
    """ Whether messages are sent to an address, or held until it is resumed.
    """
    Active    = 'active'
    Suspended = 'suspended'

# ################################################################################################################################

class SuspensionReason:
    """ Why the state of an address changed, unless an operator gave a reason of their own.
    """
    Transport_Failures = 'transport-failures'
    Probe_Answered     = 'probe-answered'

# ################################################################################################################################

class _Data:
    """ The keys of the data document of the events of an address.
    """
    Reason               = 'reason'
    Consecutive_Failures = 'consecutive_failures'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class AddressRecord:
    """ The delivery state of one address as its row has it.
    """
    address:              str
    state:                str
    consecutive_failures: int
    changed_at:           'datetime'
    reason:               str

# ################################################################################################################################
# ################################################################################################################################

def get_suspend_after_failures() -> 'int':
    """ Returns after how many consecutive transport failures an address is suspended.
    """
    if value := os.environ.get(Env_Suspend_After_Failures, ''):
        out = int(value)
    else:
        out = Default_Suspend_After_Failures

    return out

# ################################################################################################################################

def get_probe_interval() -> 'timedelta':
    """ Returns how often a suspended address is probed.
    """
    if value := os.environ.get(Env_Probe_Interval_Seconds, ''):
        seconds = int(value)
    else:
        seconds = Default_Probe_Interval_Seconds

    out = timedelta(seconds=seconds)
    return out

# ################################################################################################################################

def is_transport_failure_status(status_code:'int') -> 'bool':
    """ Says whether an HTTP response means that the partner behind a gateway could not be reached.
    """
    out = status_code in _transport_failure_statuses
    return out

# ################################################################################################################################

def is_transport_error(error:'BaseException') -> 'bool':
    """ Says whether an exception raised by a delivery means that no response was received - a connection error,
    a TLS error or a timeout. An HTTP error carries a response, which its status classifies.
    """
    if isinstance(error, HTTPError):
        out = is_transport_failure_status(error.code)

    else:
        out = isinstance(error, (ConnectionError, ssl.SSLError, TimeoutError, URLError))

    return out

# ################################################################################################################################
# ################################################################################################################################

class AddressRegistry:
    """ The delivery state of the addresses a server sends messages to, kept in the database. An address is suspended
    after a run of consecutive transport failures or by an operator, and resumed by an operator or once a probe
    is answered. Each change records an event in the audit log in the same transaction as the new state.
    """

    def __init__(self, writer:'GroupCommitWriter', source:'str', server_name:'str', clock:'Clock') -> 'None':

        self.writer = writer
        self.source = source
        self.server_name = server_name
        self.clock = clock

        self.suspend_after = get_suspend_after_failures()
        self.probe_interval = get_probe_interval()

        # Builds the events that the writer commits.
        self.audit_log = AuditLog(server_name, flush_max_size=1)

        # The state of each address that has a row, read once on start and kept up to date by every change.
        self._records:'dict[str, AddressRecord]' = {}
        self._lock = RLock()

        # Called with each address that is resumed, so that its held messages become due at once.
        self.resume_callbacks:'list[callable_]' = []

        self.writer.add_event_source(source)

# ################################################################################################################################

    def _read_all(self) -> 'list[AddressRecord]':

        out:'list[AddressRecord]' = []

        with self.writer.engine.connect() as connection:
            for row in connection.execute(select(address_state_table)):
                record = AddressRecord()
                record.address = row.address
                record.state = row.state
                record.consecutive_failures = row.consecutive_failures
                record.changed_at = row.changed_at
                record.reason = row.reason
                out.append(record)

        return out

# ################################################################################################################################

    def load(self) -> 'int':
        """ Reads the state of every address from the database, as on start, and returns how many addresses have one.
        """
        records = self.writer.call(self._read_all)

        with self._lock:
            self._records = {}
            for record in records:
                self._records[record.address] = record

        out = len(records)
        return out

# ################################################################################################################################

    def get(self, address:'str') -> 'AddressRecord':
        """ Returns the state of an address, which is active with no failures when it has no row.
        """
        with self._lock:
            if address in self._records:
                out = self._records[address]
            else:
                out = AddressRecord()
                out.address = address
                out.state = AddressState.Active
                out.consecutive_failures = 0
                out.changed_at = self.clock.now()
                out.reason = ''

        return out

# ################################################################################################################################

    def is_suspended(self, address:'str') -> 'bool':
        record = self.get(address)

        out = record.state == AddressState.Suspended
        return out

# ################################################################################################################################

    def suspended(self) -> 'strlist':
        """ Returns the suspended addresses, which the probes are sent to.
        """
        out:'strlist' = []

        with self._lock:
            for record in self._records.values():
                if record.state == AddressState.Suspended:
                    out.append(record.address)

        out.sort()
        return out

# ################################################################################################################################

    def _new_event(self, event_type:'str', record:'AddressRecord') -> 'EventWrite':

        data = dumps({
            _Data.Reason: record.reason,
            _Data.Consecutive_Failures: record.consecutive_failures,
        })

        out = EventWrite()
        out.pending = self.audit_log.new_pending_event(self.source, event_type, record.address, endpoint=record.address,
            outcome=AuditOutcome.OK, data=data)

        return out

# ################################################################################################################################

    def _save(
        self,
        connection:'Connection',
        commit_id:'str',
        record:'AddressRecord',
        event_type:'str',
        ) -> 'TransactionResult':
        """ Saves the state of an address and, if the state changed, the event that records the change.
        """
        values = {
            'state': record.state,
            'consecutive_failures': record.consecutive_failures,
            'changed_at': record.changed_at,
            'reason': record.reason,
        }

        statement = update(address_state_table).where(address_state_table.c.address == record.address).values(values)
        result = connection.execute(statement)

        # An address that has no row yet receives it.
        if not result.rowcount:
            _ = connection.execute(insert(address_state_table).values(address=record.address, **values))

        out = TransactionResult()

        if event_type:
            event = self._new_event(event_type, record)
            _ = write_events(connection, [event], commit_id)
            out.event_writes.append(event)

        return out

# ################################################################################################################################

    def _change(self, address:'str', state:'str', failures:'int', reason:'str', event_type:'str') -> 'AddressRecord':
        """ Commits the new state of an address with the event of the change, if any, and keeps it once committed.
        """
        out = AddressRecord()
        out.address = address
        out.state = state
        out.consecutive_failures = failures
        out.changed_at = self.clock.now()
        out.reason = reason

        with self._lock:
            _ = self.writer.run_transaction(self._save, out, event_type)
            self._records[address] = out

        return out

# ################################################################################################################################

    def _resumed(self, address:'str') -> 'None':
        for callback in self.resume_callbacks:
            callback(address)

# ################################################################################################################################

    def record_failure(self, address:'str') -> 'bool':
        """ Records a transport failure of a delivery to an address, and returns True if this failure suspended it.
        """
        with self._lock:
            record = self.get(address)

            # A suspended address stays suspended until it is resumed.
            if record.state == AddressState.Suspended:
                return False

            failures = record.consecutive_failures + 1

            if failures >= self.suspend_after:
                _ = self._change(address, AddressState.Suspended, failures, SuspensionReason.Transport_Failures,
                    AuditEvent.Delivery_Suspended)
                out = True

            else:
                _ = self._change(address, AddressState.Active, failures, record.reason, '')
                out = False

        return out

# ################################################################################################################################

    def record_success(self, address:'str') -> 'None':
        """ Records a delivery to an address that received a response other than a transport failure,
        which ends a run of failures.
        """
        with self._lock:
            record = self.get(address)

            if record.state == AddressState.Active:
                if record.consecutive_failures:
                    _ = self._change(address, AddressState.Active, 0, record.reason, '')

# ################################################################################################################################

    def suspend(self, address:'str', reason:'str') -> 'None':
        """ Suspends an address on behalf of an operator.
        """
        with self._lock:
            record = self.get(address)
            _ = self._change(address, AddressState.Suspended, record.consecutive_failures, reason,
                AuditEvent.Delivery_Suspended)

# ################################################################################################################################

    def resume(self, address:'str', reason:'str') -> 'None':
        """ Resumes an address, after which its held messages are due at once.
        """
        with self._lock:
            _ = self._change(address, AddressState.Active, 0, reason, AuditEvent.Delivery_Resumed)

        self._resumed(address)

# ################################################################################################################################

    def record_probe(self, address:'str', is_answered:'bool') -> 'bool':
        """ Records the result of a probe of a suspended address. An address whose probe was answered with a Pong
        is resumed, and True is returned.
        """
        if is_answered:
            self.resume(address, SuspensionReason.Probe_Answered)

        return is_answered

# ################################################################################################################################
# ################################################################################################################################
