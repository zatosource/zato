# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sqlite3

# local
import _audit
import _constants
import _enmasse
import _helpers
from _helpers import wait_until as _wait_until

# Zato
from zato.common.audit_log.api import AuditEvent

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# How many tool calls the audited middle phase of the toggle test makes
_toggle_call_count = 3

# What the server logs when an audit write fails and the event is dropped
_dropped_log_marker = 'Audit event dropped'

# The file mode that takes the write permissions away from the audit database
_read_only_mode = 0o444

# How many calls prove there is no crash loop while the audit file is unwritable
_unwritable_call_count = 3

# The companion files SQLite keeps next to the database in WAL mode
_sqlite_companion_suffixes = ('-wal', '-shm')

# ################################################################################################################################
# ################################################################################################################################

def _call_order_status(zato_server:'anydict', url_path:'str') -> 'anydict':
    """ One order status call through the given gateway on a fresh session,
    returning the whole response body.
    """

    client = _helpers.make_client(zato_server, url_path)
    session_id = _helpers.open_session(client)

    out = _helpers.call_tool(client, session_id, _constants.Service_Order_Status,
        {'order_id': _constants.Order_ID})

    return out

# ################################################################################################################################

def _prove_no_events(zato_server:'anydict', min_id:'int') -> 'None':
    """ Proves the audit-off gateway wrote nothing since the given id - a probe call
    on an audited gateway is waited for first, so the absence is not just a race.
    """

    audit_db_path = zato_server['audit_db_path']
    probe_min_id = _audit.last_event_id(audit_db_path)

    body = _call_order_status(zato_server, _constants.Path_Main)

    data = _helpers.get_result_data(body)
    assert data['status'] == _constants.Order_Status, body

    _ = _audit.wait_for_events(
        audit_db_path, 1,
        object_name=_constants.Gateway_Main,
        event_type=AuditEvent.MCP_Tools_Call,
        min_id=probe_min_id)

    events = _audit.read_events(audit_db_path, object_name=_constants.Gateway_Audit_Off, min_id=min_id)
    assert events == [], events

# ################################################################################################################################
# ################################################################################################################################

class TestAuditOptions:
    """ The audit flag itself - a gateway with the audit log off writes nothing,
    and flipping the flag by re-import starts and stops the writing at the call boundary.
    """

# ################################################################################################################################

    def test_audit_off_writes_nothing(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        # A whole conversation runs on the audit-off gateway and every call succeeds ..
        client = _helpers.make_client(zato_server, _constants.Path_Audit_Off)
        session_id = _helpers.open_session(client)

        tools = _helpers.list_tools(client, session_id)
        assert tools, tools

        for call_index in range(_toggle_call_count):

            arguments = {'order_id': f'{_constants.Order_ID}-{call_index}'}
            body = _helpers.call_tool(client, session_id, _constants.Service_Order_Status, arguments)

            data = _helpers.get_result_data(body)
            assert data['status'] == _constants.Order_Status, body

        # .. and not one of its events exists anywhere.
        _prove_no_events(zato_server, min_id)

# ################################################################################################################################

    def test_the_toggle_is_live(self, zato_server:'anydict') -> 'None':

        server_directory = zato_server['server_directory']
        audit_db_path = zato_server['audit_db_path']

        min_id = _audit.last_event_id(audit_db_path)

        # A call before the flip leaves no event ..
        body = _call_order_status(zato_server, _constants.Path_Audit_Off)

        data = _helpers.get_result_data(body)
        assert data['status'] == _constants.Order_Status, body

        _prove_no_events(zato_server, min_id)

        try:
            # .. one re-import turns the audit log on ..
            overrides = {_constants.Gateway_Audit_Off: {'is_audit_log_active': True}}
            config = _enmasse.build_suite_config(gateway_overrides=overrides)
            _enmasse.run_import(server_directory, config)

            # .. and once the flip reaches enforcement, events start at the call boundary ..
            def audit_is_on() -> 'bool':
                probe_min_id = _audit.last_event_id(audit_db_path)

                _ = _call_order_status(zato_server, _constants.Path_Audit_Off)

                events = _audit.read_events(
                    audit_db_path,
                    object_name=_constants.Gateway_Audit_Off,
                    event_type=AuditEvent.MCP_Tools_Call,
                    min_id=probe_min_id)

                out = len(events) > 0
                return out

            _wait_until(audit_is_on, 'the audit flag on reached enforcement')

            # .. with exactly one event per call from here on.
            on_min_id = _audit.last_event_id(audit_db_path)

            for _call_index in range(_toggle_call_count):
                _ = _call_order_status(zato_server, _constants.Path_Audit_Off)

            events = _audit.wait_for_events(
                audit_db_path, _toggle_call_count,
                object_name=_constants.Gateway_Audit_Off,
                event_type=AuditEvent.MCP_Tools_Call,
                min_id=on_min_id)

            assert len(events) == _toggle_call_count, events

        finally:
            # The baseline turns the audit log back off for the other tests.
            config = _enmasse.build_suite_config()
            _enmasse.run_import(server_directory, config)

            def audit_is_off() -> 'bool':
                probe_min_id = _audit.last_event_id(audit_db_path)

                _ = _call_order_status(zato_server, _constants.Path_Audit_Off)

                body = _call_order_status(zato_server, _constants.Path_Main)
                data = _helpers.get_result_data(body)
                assert data['status'] == _constants.Order_Status, body

                _ = _audit.wait_for_events(
                    audit_db_path, 1,
                    object_name=_constants.Gateway_Main,
                    event_type=AuditEvent.MCP_Tools_Call,
                    min_id=probe_min_id)

                events = _audit.read_events(
                    audit_db_path,
                    object_name=_constants.Gateway_Audit_Off,
                    min_id=probe_min_id)

                out = events == []
                return out

            _wait_until(audit_is_off, 'the audit flag off came back')

# ################################################################################################################################
# ################################################################################################################################

class TestAuditStorageFailure:
    """ The audit database failing underneath the gateway - a lock another writer holds,
    write permissions gone from the file and the file deleted outright - while every
    conversation keeps answering. A write the database refuses drops that one event
    with a logged warning, and a deleted database recreates on the next write.
    """

# ################################################################################################################################

    def _read_new_log_text(self, server_log_path:'str', log_offset:'int') -> 'str':
        """ Returns what the server logged since the given offset.
        """

        with open(server_log_path) as server_log:
            _ = server_log.seek(log_offset)
            out = server_log.read()

        return out

# ################################################################################################################################

    def _assert_writing_resumed(self, zato_server:'anydict') -> 'None':
        """ One call whose event lands in the audit database again proves the writing resumed.
        """

        audit_db_path = zato_server['audit_db_path']
        resumed_min_id = _audit.last_event_id(audit_db_path)

        body = _call_order_status(zato_server, _constants.Path_Main)

        data = _helpers.get_result_data(body)
        assert data['status'] == _constants.Order_Status, body

        _ = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Main,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=resumed_min_id)

# ################################################################################################################################

    def test_a_locked_audit_database_never_blocks_a_conversation(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        server_log_path = zato_server['server_log_path']

        min_id = _audit.last_event_id(audit_db_path)
        log_offset = os.path.getsize(server_log_path)

        # Another writer holds the database for the whole duration of the conversation ..
        lock_connection = sqlite3.connect(audit_db_path)

        try:
            _ = lock_connection.execute('begin immediate')

            # .. and the conversation still answers - the gateway's write waits out
            # the busy timeout, fails and drops the event, never the response.
            body = _call_order_status(zato_server, _constants.Path_Main)

            data = _helpers.get_result_data(body)
            assert data['status'] == _constants.Order_Status, body

        finally:
            lock_connection.rollback()
            lock_connection.close()

        # The writes are synchronous, so by response time the events were dropped for good ..
        events = _audit.read_events(audit_db_path, object_name=_constants.Gateway_Main, min_id=min_id)
        assert events == [], events

        # .. each drop left its warning in the server log ..
        new_log_text = self._read_new_log_text(server_log_path, log_offset)
        assert _dropped_log_marker in new_log_text, new_log_text

        # .. and with the lock gone, the very next call's event is written again.
        self._assert_writing_resumed(zato_server)

# ################################################################################################################################

    def test_an_unwritable_audit_file_has_one_defined_outcome(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        server_log_path = zato_server['server_log_path']

        min_id = _audit.last_event_id(audit_db_path)
        log_offset = os.path.getsize(server_log_path)

        original_mode = os.stat(audit_db_path).st_mode

        try:
            # The file loses its write permissions on disk ..
            os.chmod(audit_db_path, _read_only_mode)

            # .. yet call after call keeps answering - each event is dropped
            # on its own, so there is no crash loop to enter.
            for _call_index in range(_unwritable_call_count):

                body = _call_order_status(zato_server, _constants.Path_Main)

                data = _helpers.get_result_data(body)
                assert data['status'] == _constants.Order_Status, body

            events = _audit.read_events(audit_db_path, object_name=_constants.Gateway_Main, min_id=min_id)
            assert events == [], events

            # .. the failures were logged, not raised anywhere ..
            new_log_text = self._read_new_log_text(server_log_path, log_offset)
            assert _dropped_log_marker in new_log_text, new_log_text

        finally:
            os.chmod(audit_db_path, original_mode)

        # .. and restored permissions resume the writing with the very next call.
        self._assert_writing_resumed(zato_server)

# ################################################################################################################################

    def test_the_audit_database_recreates_after_deletion(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']

        # A probe proves the writing works before the deletion ..
        probe_min_id = _audit.last_event_id(audit_db_path)

        _ = _call_order_status(zato_server, _constants.Path_Main)

        _ = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Main,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=probe_min_id)

        # .. the whole database disappears from disk while the server runs ..
        os.remove(audit_db_path)

        for suffix in _sqlite_companion_suffixes:

            companion_path = audit_db_path + suffix

            # WAL mode decides on its own which companion files exist at any moment
            if os.path.exists(companion_path):
                os.remove(companion_path)

        # .. the very next call answers as always ..
        body = _call_order_status(zato_server, _constants.Path_Main)

        data = _helpers.get_result_data(body)
        assert data['status'] == _constants.Order_Status, body

        # .. and it is that call's own write that recreated the file, schema included,
        # with the call's events as the first thing written into the fresh database.
        assert os.path.isfile(audit_db_path), audit_db_path

        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Main,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=0)

        assert len(events) >= 1, events

# ################################################################################################################################
# ################################################################################################################################
