# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

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
