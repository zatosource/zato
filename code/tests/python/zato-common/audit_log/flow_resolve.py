# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from common import delete_all_events
from zato.common.audit_log.api import get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.flow import resolve_seed, Resolved_Cid, Resolved_Event_Id, Resolved_Msg_Id

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-flow-resolve-server'

# The channel the test events belong to
_channel_name = 'audit.test.flow-resolve'

# ################################################################################################################################
# ################################################################################################################################

def run_flow_resolve_scenario() -> 'None':
    """ The search term resolver every backend must pass - a term is tried as an event id,
    then as a cid, then as a control id, the newest matching event winning within each
    meaning, and a term that names nothing resolves to nothing.
    """

    # Start from empty tables because containers can be reused between test runs ..
    engine = get_audit_engine()
    delete_all_events()

    audit_log = AuditLog(_server_name)

    # .. two events sharing one cid, so the cid must resolve to the newer of them ..
    older_id = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Request_Received, _channel_name,
        cid='flow-resolve-cid-1', msg_id='FLOW-MSG-100', outcome=AuditOutcome.OK,
        data='{"step": "older"}')

    newer_id = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Response_Sent, _channel_name,
        cid='flow-resolve-cid-1', msg_id='FLOW-MSG-100', outcome=AuditOutcome.OK,
        data='{"step": "newer"}')

    # .. and one event whose control id is all digits, so a numeric term that is no
    # event's own number can still fall through to the control id meaning.
    digits_id = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Request_Received, _channel_name,
        cid='flow-resolve-cid-2', msg_id='31337', outcome=AuditOutcome.OK,
        data='{"step": "digits"}')

    with engine.connect() as connection:

        # An event's own number is the most exact meaning, so it wins over everything else ..
        resolved = resolve_seed(connection, str(older_id))
        assert resolved.seed_id == older_id
        assert resolved.resolved_by == Resolved_Event_Id

        # .. a cid resolves to the newest event that travelled under it ..
        resolved = resolve_seed(connection, 'flow-resolve-cid-1')
        assert resolved.seed_id == newer_id
        assert resolved.resolved_by == Resolved_Cid

        # .. a control id resolves to the newest event carrying it ..
        resolved = resolve_seed(connection, 'FLOW-MSG-100')
        assert resolved.seed_id == newer_id
        assert resolved.resolved_by == Resolved_Msg_Id

        # .. a numeric term that is no event's own number still reaches the control ids ..
        resolved = resolve_seed(connection, '31337')
        assert resolved.seed_id == digits_id
        assert resolved.resolved_by == Resolved_Msg_Id

        # .. and a term that names nothing resolves to nothing.
        resolved = resolve_seed(connection, 'no-such-term-anywhere')
        assert resolved.seed_id == 0
        assert resolved.resolved_by == ''

# ################################################################################################################################
# ################################################################################################################################
