# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads

# Zato
from zato.common.api import CHANNEL
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.resubmit import source_resubmit_actions, is_event_type_resubmittable
from zato.common.audit_log.service import get_resubmit_links, record_service_request, record_service_response, \
    Resubmit_Of_Cid_Key, Resubmit_Of_Event_Id_Key
from zato.common.ext.bunch import Bunch
from zato.common.json_internal import dumps
from zato.common.typing_ import cast_
from zato.server.service.internal.audit_log_service import ReprocessServiceRequest

# Test support
from audit_env import audit_db_env, events_of_type, get_events, get_parents, Server_Name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

# The name of the service the resubmit catalog points service requests at.
Reprocess_Service = 'zato.audit-log.service.reprocess'

# The cid the reprocess itself runs with.
Reprocess_Cid = 'cid-service-reprocess-1'

# The service whose request is repeated, and who called it the first time.
Target_Service = 'audit.test.service.target'
Original_Caller = 'audit.test.service.caller'
Original_Cid = 'cid-service-original-1'

# What the service was given the first time.
Request_Body = {'customer_id': 123, 'action': 'refresh'}

# What the failing target says.
Reprocess_Error = 'The target service is still down'

# ################################################################################################################################
# ################################################################################################################################

class ServerStub:
    """ Stands in for the server the reprocess service runs on - it remembers what the target
    service was invoked with and records the invocation the way the audit hook does.
    """

    def __init__(self, *, error_traceback:'str'='') -> 'None':
        self.name = Server_Name
        self.error_traceback = error_traceback
        self.invoked:'anylist' = []

    def invoke(self, service_name:'str', payload:'any_', **kwargs:'any_') -> 'None':
        self.invoked.append((service_name, payload, kwargs))

        # The hook records the request and the response under the cid and the request context given.
        audit_log = AuditLog(self.name)
        request_ctx = kwargs['request_ctx']
        cid = kwargs['cid']

        record_service_request(audit_log, service_name, cid, CHANNEL.INVOKE, '', payload, request_ctx)
        record_service_response(audit_log, service_name, cid, CHANNEL.INVOKE, '', {'ok': True}, 7,
            self.error_traceback, request_ctx)

        if self.error_traceback:
            raise Exception(Reprocess_Error)

# ################################################################################################################################
# ################################################################################################################################

def _seed_original_request() -> 'int':
    """ One recorded service request - what the reprocess reads back.
    """
    audit_log = AuditLog(Server_Name)

    record_service_request(audit_log, Target_Service, Original_Cid, CHANNEL.HTTP_SOAP, Original_Caller, Request_Body, {})
    record_service_response(audit_log, Target_Service, Original_Cid, CHANNEL.HTTP_SOAP, Original_Caller, None, 3,
        'Traceback (most recent call last):\nException: The first run failed', {})

    events = get_events()
    request_events = events_of_type(events, AuditEvent.Service_Request)
    out = request_events[0]['id']

    return out

# ################################################################################################################################

def _run_reprocess(event_id:'int', server:'ServerStub', *, actor:'str'='') -> 'stranydict':
    """ Runs the reprocess service over one stored event and returns the report it produced.
    """
    harness = Bunch()
    harness.cid = Reprocess_Cid
    harness.server = server
    harness.request = Bunch(input=Bunch(event_id=event_id, actor=actor))
    harness.response = Bunch(payload=Bunch())

    ReprocessServiceRequest.handle(cast_('any_', harness))

    out = loads(harness.response.payload.response_data)
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_the_catalog_offers_reprocess_for_service_requests() -> 'None':
    """ The catalog offers reprocess for service requests and not for responses.
    """
    actions = source_resubmit_actions[AuditSource.Service]

    assert actions[AuditEvent.Service_Request]['service'] == Reprocess_Service
    assert is_event_type_resubmittable(AuditSource.Service, AuditEvent.Service_Request)
    assert not is_event_type_resubmittable(AuditSource.Service, AuditEvent.Service_Response)

# ################################################################################################################################

def test_the_resubmit_links_come_from_the_request_context() -> 'None':
    """ An ordinary invocation carries no links, a resubmit carries the correlation id and the parent.
    """
    assert get_resubmit_links({}) == {}
    assert get_resubmit_links({'zato.request_ctx.async_msg': {}}) == {}

    links = get_resubmit_links({Resubmit_Of_Event_Id_Key: 42, Resubmit_Of_Cid_Key: 'cid-42'})

    assert links == {'correl_id': 'cid-42', 'parents': [42]}

# ################################################################################################################################

def test_the_records_are_linked_only_when_the_keys_are_present(tmp_path:'any_') -> 'None':
    """ The request and the response the hook records are linked to the event named in the request
    context, and left unlinked when nothing is named.
    """
    with audit_db_env(tmp_path):

        audit_log = AuditLog(Server_Name)

        # An ordinary pair ..
        record_service_request(audit_log, Target_Service, 'cid-plain', CHANNEL.INVOKE, '', 'abc', {})
        record_service_response(audit_log, Target_Service, 'cid-plain', CHANNEL.INVOKE, '', 'def', 1, '', {})

        plain_request, plain_response = get_events()

        assert plain_request['correl_id'] == ''
        assert plain_response['correl_id'] == ''
        assert get_parents(plain_request['id']) == []
        assert get_parents(plain_response['id']) == []

        # .. and a pair recorded on behalf of a resubmit.
        request_ctx = {
            Resubmit_Of_Event_Id_Key: plain_request['id'],
            Resubmit_Of_Cid_Key: 'cid-plain',
        }

        record_service_request(audit_log, Target_Service, 'cid-linked', CHANNEL.INVOKE, '', 'abc', request_ctx)
        record_service_response(audit_log, Target_Service, 'cid-linked', CHANNEL.INVOKE, '', 'def', 1, '', request_ctx)

        events = get_events()
        linked_request, linked_response = events[2:]

        assert linked_request['correl_id'] == 'cid-plain'
        assert linked_response['correl_id'] == 'cid-plain'
        assert get_parents(linked_request['id']) == [plain_request['id']]
        assert get_parents(linked_response['id']) == [plain_request['id']]

# ################################################################################################################################

def test_a_reprocess_reinvokes_the_service_with_the_stored_body(tmp_path:'any_') -> 'None':
    """ A reprocess hands the stored request body to the same service and names the original event
    in the request context - the service's own request and response events are the linked new attempt.
    """
    with audit_db_env(tmp_path):

        original_id = _seed_original_request()

        server = ServerStub()
        report = _run_reprocess(original_id, server, actor='audit.operator')

        assert report['is_ok'] is True
        assert report['is_duplicate'] is False
        assert report['cid'] == Reprocess_Cid
        assert report['action'] == 'reprocess'
        assert report['service_name'] == Target_Service

        # Nothing is inserted by the reprocess itself.
        assert report['event_id'] is None

        # The target service received the body as it was stored - text ..
        assert len(server.invoked) == 1

        service_name, payload, kwargs = server.invoked[0]

        assert service_name == Target_Service
        assert payload == dumps(Request_Body)
        assert kwargs['cid'] == Reprocess_Cid

        # .. and the request context named the event repeated.
        assert kwargs['request_ctx'] == {
            Resubmit_Of_Event_Id_Key: original_id,
            Resubmit_Of_Cid_Key: Original_Cid,
        }

        # The hook's own records are the new attempt - linked to the original by the correlation id
        # and the parent link, with the response saying it went through.
        events = get_events()

        request_events = events_of_type(events, AuditEvent.Service_Request)
        response_events = events_of_type(events, AuditEvent.Service_Response)

        new_request = request_events[1]
        new_response = response_events[1]

        for item in (new_request, new_response):
            assert item['source'] == AuditSource.Service
            assert item['object_name'] == Target_Service
            assert item['cid'] == Reprocess_Cid
            assert item['correl_id'] == Original_Cid
            assert get_parents(item['id']) == [original_id]

        assert new_response['outcome'] == AuditOutcome.OK

# ################################################################################################################################

def test_a_failed_reprocess_leaves_a_failed_response_on_record(tmp_path:'any_') -> 'None':
    """ A reprocess whose service raised comes back as a report with the error inside, and the
    response the hook recorded says the attempt failed.
    """
    with audit_db_env(tmp_path):

        original_id = _seed_original_request()

        server = ServerStub(error_traceback='Traceback (most recent call last):\nException: still down')
        report = _run_reprocess(original_id, server)

        assert report['is_ok'] is False
        assert report['is_duplicate'] is False
        assert Reprocess_Error in report['error']

        events = get_events()
        response_events = events_of_type(events, AuditEvent.Service_Response)
        new_response = response_events[1]

        assert new_response['cid'] == Reprocess_Cid
        assert new_response['correl_id'] == Original_Cid
        assert new_response['outcome'] == AuditOutcome.Error

        # A failed run released its key, so the request can be run again ..
        second_server = ServerStub()
        second_report = _run_reprocess(original_id, second_server)

        assert second_report['is_ok'] is True
        assert len(second_server.invoked) == 1

        # .. and one that went through is not run twice.
        third_report = _run_reprocess(original_id, second_server)

        assert third_report['is_ok'] is False
        assert third_report['is_duplicate'] is True
        assert len(second_server.invoked) == 1

# ################################################################################################################################

def test_only_requests_can_be_reprocessed(tmp_path:'any_') -> 'None':
    """ A response is not what a service was given - asking to run one again refuses.
    """
    with audit_db_env(tmp_path):

        _ = _seed_original_request()

        events = get_events()
        response_events = events_of_type(events, AuditEvent.Service_Response)
        response_id = response_events[0]['id']

        server = ServerStub()
        report = _run_reprocess(response_id, server)

        assert report['is_ok'] is False
        assert 'can be run again' in report['error']
        assert server.invoked == []

# ################################################################################################################################
# ################################################################################################################################
