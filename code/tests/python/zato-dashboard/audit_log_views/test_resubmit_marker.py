# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What a row of the listing says about resubmitting - whether it was already sent again,
# and whether it carries anything to send again at all.

# stdlib
import os
from contextlib import contextmanager

# Zato
from zato.admin.web.views.audit_log.query import _mark_resubmittable, _mark_resubmitted
from zato.admin.web.views.audit_log.resubmit import resubmit
from zato.common.audit_log.api import get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource, \
    ModuleCtx as AuditLogCtx
from zato.common.audit_log.request_context import Key_Payload, Key_Payload_Kind, Payload_Kind_Described
from zato.common.ext.bunch import Bunch
from zato.common.json_internal import dumps, loads

# Test support
from live_sql.env import database_env

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import any_, anydict, anylist
    any_ = any_
    anydict = anydict
    anylist = anylist

    envgen = Iterator[AuditLog]

# ################################################################################################################################
# ################################################################################################################################

# The server and connection the events of these tests are written under
_server_name = 'test-resubmit-marker-server'
_connection_name = 'test.resubmit.marker.conn'

# The prefix all the audit log database environment variables share
_env_prefix = 'Zato_Audit_Log_DB_'

# What a call that can be repeated recorded
_stored_call = dumps({Key_Payload: '{"order": 1}', 'method': 'POST', 'address': 'https://crm.example.com/orders'})

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def _audit_log(tmp_path:'any_') -> 'envgen':
    """ Points the audit log at a throwaway SQLite database and hands back a log writing to it.
    """
    db_path = os.path.join(str(tmp_path), 'audit.db')

    details_config = {
        'type': AuditLogCtx.Type_SQLite,
        'name': db_path,
    }

    with database_env(_env_prefix, details_config):
        yield AuditLog(_server_name)

# ################################################################################################################################

def _new_row(event_id:'int', cid:'str', data:'str'='') -> 'anydict':
    """ One page row of the shape the listing hands to the markers.
    """
    out = {
        'id': event_id,
        'cid': cid,
        'event_type': AuditEvent.Request_Sent,
        'data': data,
    }

    return out

# ################################################################################################################################

def _mark(rows:'anylist') -> 'None':
    """ Runs the resubmitted marker over a page of REST outgoing rows.
    """
    engine = get_audit_engine()

    with engine.connect() as connection:
        _mark_resubmitted(connection, AuditSource.REST_Outgoing, rows)

# ################################################################################################################################
# ################################################################################################################################

class TestResubmittedMarker:

    def test_a_successful_attempt_badges_the_row_it_repeated(self, tmp_path:'any_') -> 'None':
        with _audit_log(tmp_path) as audit_log:

            original_id = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _connection_name,
                cid='marker-ok', outcome=AuditOutcome.Error, data=_stored_call)

            _ = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _connection_name,
                cid='marker-ok-attempt', correl_id='marker-ok', outcome=AuditOutcome.OK, data=_stored_call)

            rows = [_new_row(original_id, 'marker-ok', _stored_call)]
            _mark(rows)

            assert rows[0]['is_resubmitted'] is True

# ################################################################################################################################

    def test_a_failed_attempt_leaves_the_row_unbadged(self, tmp_path:'any_') -> 'None':
        with _audit_log(tmp_path) as audit_log:

            original_id = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _connection_name,
                cid='marker-error', outcome=AuditOutcome.Error, data=_stored_call)

            # An attempt that did not go through is no resubmit.
            _ = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _connection_name,
                cid='marker-error-attempt', correl_id='marker-error', outcome=AuditOutcome.Error,
                status='Connection timeout', data=_stored_call)

            rows = [_new_row(original_id, 'marker-error', _stored_call)]
            _mark(rows)

            assert rows[0]['is_resubmitted'] is False

# ################################################################################################################################

    def test_a_row_nothing_repeated_is_unbadged(self, tmp_path:'any_') -> 'None':
        with _audit_log(tmp_path) as audit_log:

            original_id = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _connection_name,
                cid='marker-alone', outcome=AuditOutcome.Error, data=_stored_call)

            rows = [_new_row(original_id, 'marker-alone', _stored_call)]
            _mark(rows)

            assert rows[0]['is_resubmitted'] is False

# ################################################################################################################################
# ################################################################################################################################

class TestMissingRow:

    def test_a_row_that_is_gone_answers_that_it_was_not_found(self, tmp_path:'any_') -> 'None':
        with _audit_log(tmp_path):

            request = Bunch()
            request.method = 'POST'
            request.POST = {'id': '4242'}

            # Retention deletes old events, so the page may be older than the row it shows.
            response = resubmit(request)
            body = loads(response.content)

            assert body['is_success'] is False
            assert body['message'] == 'Audit event 4242 was not found'

# ################################################################################################################################
# ################################################################################################################################

class TestResubmittableFlag:

    def test_a_row_carrying_its_call_offers_the_action(self) -> 'None':
        rows = [_new_row(1, 'flag-1', _stored_call)]
        _mark_resubmittable(AuditSource.REST_Outgoing, rows)

        assert rows[0]['is_resubmittable'] is True

# ################################################################################################################################

    def test_a_row_with_no_stored_call_offers_nothing(self) -> 'None':

        # An SMTP ping wrote a row of this very type, with nothing in it to send anywhere.
        rows = [_new_row(2, 'flag-2')]
        _mark_resubmittable(AuditSource.Email_SMTP, rows)

        assert rows[0]['is_resubmittable'] is False

# ################################################################################################################################

    def test_a_described_body_offers_nothing_either(self) -> 'None':

        # What would go out is the description of the body rather than the body.
        described = dumps({
            Key_Payload: '<MultipartEncoder object at 0x1>',
            Key_Payload_Kind: Payload_Kind_Described,
        })

        rows = [_new_row(3, 'flag-3', described)]
        _mark_resubmittable(AuditSource.REST_Outgoing, rows)

        assert rows[0]['is_resubmittable'] is False

# ################################################################################################################################

    def test_an_undeclared_event_type_offers_nothing(self) -> 'None':
        rows = [_new_row(4, 'flag-4', _stored_call)]
        rows[0]['event_type'] = AuditEvent.Response_Received

        _mark_resubmittable(AuditSource.REST_Outgoing, rows)

        assert rows[0]['is_resubmittable'] is False

# ################################################################################################################################

    def test_an_smtp_message_is_offered_without_a_payload_of_its_own(self) -> 'None':

        # An e-mail is rebuilt from the whole document rather than from a payload key.
        rows = [_new_row(5, 'flag-5', dumps({'subject': 'Invoice', 'body': 'Please find it attached'}))]
        rows[0]['event_type'] = AuditEvent.Message_Sent

        _mark_resubmittable(AuditSource.Email_SMTP, rows)

        assert rows[0]['is_resubmittable'] is True

# ################################################################################################################################
# ################################################################################################################################
