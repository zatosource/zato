# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.api import CHANNEL, DATA_FORMAT, URL_TYPE
from zato.common.audit_log.api import event_attr_table, get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.resubmit import source_resubmit_actions, is_event_type_resubmittable
from zato.common.ext.bunch import Bunch
from zato.common.typing_ import cast_
from zato.server.service.internal.audit_log_http_channel import ReprocessHTTPChannelRequest

# Test support
from audit_env import audit_db_env, get_events, get_parents, Server_Name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

# The name of the service the resubmit catalog points channel requests at.
Reprocess_Service = 'zato.audit-log.http-channel.reprocess'

# The cid the reprocess itself runs with.
Reprocess_Cid = 'cid-channel-reprocess-1'

# The data format a SOAP channel is configured with.
XML_Data_Format = 'xml'

# The two channels whose requests are repeated.
REST_Channel_Name = 'audit.test.rest.channel'
REST_Service = 'audit.test.rest.target'
REST_Body = '{"order_id": 77}'

SOAP_Channel_Name = 'audit.test.soap.channel'
SOAP_Service = 'audit.test.soap.target'
SOAP_Body = '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><order>77</order></soap:Body></soap:Envelope>'

# The request that is repeated.
Original_Cid = 'cid-channel-original-1'

# What the failing target says.
Reprocess_Error = 'The target service is still down'

# ################################################################################################################################
# ################################################################################################################################

class ServerStub:
    """ Stands in for the server the reprocess service runs on - it holds the channels
    live requests are dispatched through and remembers what their services were invoked with.
    """

    def __init__(self) -> 'None':
        self.name = Server_Name
        self.invoked:'anylist' = []

        channel_data = [
            {
                'name': 'audit.test.as4.channel',
                'transport': URL_TYPE.AS4,
                'service_name': 'audit.test.as4.target',
                'data_format': XML_Data_Format,
            },
            {
                'name': REST_Channel_Name,
                'transport': URL_TYPE.PLAIN_HTTP,
                'service_name': REST_Service,
                'data_format': DATA_FORMAT.JSON,
            },
            {
                'name': SOAP_Channel_Name,
                'transport': URL_TYPE.SOAP,
                'service_name': SOAP_Service,
                'data_format': XML_Data_Format,
            },
        ]

        url_data = Bunch(channel_data=channel_data)
        request_dispatcher = Bunch(url_data=url_data)
        self.config_manager = Bunch(request_dispatcher=request_dispatcher)

    def invoke(self, service_name:'str', payload:'any_', **kwargs:'any_') -> 'None':
        self.invoked.append((service_name, payload, kwargs))

# ################################################################################################################################

class FailingServerStub(ServerStub):
    """ A server whose channel services are still down - every invocation fails.
    """

    def invoke(self, service_name:'str', payload:'any_', **kwargs:'any_') -> 'None':
        raise Exception(Reprocess_Error)

# ################################################################################################################################
# ################################################################################################################################

def _seed_original_request(source:'str', channel_name:'str', service_name:'str', body:'str') -> 'int':
    """ One recorded channel request - the raw body in the data column.
    """
    audit_log = AuditLog(Server_Name)
    body_size = len(body)

    out = audit_log.insert(source, AuditEvent.Request_Received, channel_name, cid=Original_Cid,
        endpoint=service_name, size=body_size, data=body)

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

    ReprocessHTTPChannelRequest.handle(cast_('any_', harness))

    out = loads(harness.response.payload.response_data)
    return out

# ################################################################################################################################

def _get_attributes(event_id:'int') -> 'stranydict':
    """ The searchable attributes of one event, by name.
    """
    engine = get_audit_engine()

    query = select(event_attr_table.c.name, event_attr_table.c.value)
    query = query.where(event_attr_table.c.event_id == event_id)

    out:'stranydict' = {}

    with engine.connect() as connection:
        for row in connection.execute(query):
            out[row[0]] = row[1]

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_the_catalog_offers_reprocess_for_both_channel_kinds() -> 'None':
    """ The catalog offers reprocess for REST and SOAP channel requests through one and the same service.
    """
    rest_actions = source_resubmit_actions[AuditSource.REST_Channel]
    soap_actions = source_resubmit_actions[AuditSource.SOAP_Channel]

    assert rest_actions[AuditEvent.Request_Received]['service'] == Reprocess_Service
    assert soap_actions[AuditEvent.Request_Received]['service'] == Reprocess_Service

    assert is_event_type_resubmittable(AuditSource.REST_Channel, AuditEvent.Request_Received)
    assert is_event_type_resubmittable(AuditSource.SOAP_Channel, AuditEvent.Request_Received)

    assert not is_event_type_resubmittable(AuditSource.REST_Channel, AuditEvent.Response_Sent)
    assert not is_event_type_resubmittable(AuditSource.SOAP_Channel, AuditEvent.Response_Sent)

# ################################################################################################################################

def test_a_rest_request_reaches_the_channel_service_with_the_channel_data_format(tmp_path:'any_') -> 'None':
    """ A reprocess hands the raw body to the REST channel's service in the channel's data format
    and leaves the new attempt as its own event under the channel, linked to the original one.
    """
    with audit_db_env(tmp_path):

        original_id = _seed_original_request(AuditSource.REST_Channel, REST_Channel_Name, REST_Service, REST_Body)

        server = ServerStub()
        report = _run_reprocess(original_id, server, actor='audit.operator')

        assert report['is_ok'] is True
        assert report['is_duplicate'] is False
        assert report['cid'] == Reprocess_Cid
        assert report['action'] == 'reprocess'
        assert report['service_name'] == REST_Service

        # The channel's service received the body as it arrived the first time, in the channel's data format.
        assert len(server.invoked) == 1

        service_name, payload, kwargs = server.invoked[0]

        assert service_name == REST_Service
        assert payload == REST_Body
        assert kwargs['channel'] == CHANNEL.INVOKE
        assert kwargs['data_format'] == DATA_FORMAT.JSON
        assert kwargs['cid'] == Reprocess_Cid

        # The new attempt is its own event under the channel, sharing the original's correlation id
        # and naming the original event as its parent ..
        events = get_events()

        assert len(events) == 2

        new_event = events[1]

        assert new_event['id'] == report['event_id']
        assert new_event['source'] == AuditSource.REST_Channel
        assert new_event['event_type'] == AuditEvent.Request_Received
        assert new_event['object_name'] == REST_Channel_Name
        assert new_event['endpoint'] == REST_Service
        assert new_event['cid'] == Reprocess_Cid
        assert new_event['correl_id'] == Original_Cid
        assert new_event['outcome'] == AuditOutcome.OK
        assert new_event['data'] == REST_Body
        assert new_event['size'] == len(REST_Body)

        assert get_parents(new_event['id']) == [original_id]

        # .. and it says who asked for the run.
        assert _get_attributes(new_event['id']) == {'actor': 'audit.operator'}

# ################################################################################################################################

def test_a_soap_request_reaches_the_channel_service_as_xml(tmp_path:'any_') -> 'None':
    """ A SOAP channel's envelope is not JSON - it is read raw and reaches the service as XML,
    recorded under the SOAP channel source.
    """
    with audit_db_env(tmp_path):

        original_id = _seed_original_request(AuditSource.SOAP_Channel, SOAP_Channel_Name, SOAP_Service, SOAP_Body)

        server = ServerStub()
        report = _run_reprocess(original_id, server)

        assert report['is_ok'] is True
        assert report['service_name'] == SOAP_Service

        service_name, payload, kwargs = server.invoked[0]

        assert service_name == SOAP_Service
        assert payload == SOAP_Body
        assert kwargs['data_format'] == XML_Data_Format

        events = get_events()
        new_event = events[1]

        assert new_event['source'] == AuditSource.SOAP_Channel
        assert new_event['object_name'] == SOAP_Channel_Name
        assert new_event['correl_id'] == Original_Cid
        assert new_event['outcome'] == AuditOutcome.OK

        # Nothing was asked for by name, so nothing is recorded about who asked.
        assert _get_attributes(new_event['id']) == {}

        assert get_parents(new_event['id']) == [original_id]

# ################################################################################################################################

def test_a_failed_reprocess_is_recorded_too(tmp_path:'any_') -> 'None':
    """ A reprocess whose service is still down comes back as a report with the error inside,
    and the failed attempt is on record with the same links and the error as its status.
    """
    with audit_db_env(tmp_path):

        original_id = _seed_original_request(AuditSource.REST_Channel, REST_Channel_Name, REST_Service, REST_Body)

        report = _run_reprocess(original_id, FailingServerStub())

        assert report['is_ok'] is False
        assert report['is_duplicate'] is False
        assert Reprocess_Error in report['error']

        events = get_events()
        failed = events[1]

        assert failed['source'] == AuditSource.REST_Channel
        assert failed['event_type'] == AuditEvent.Request_Received
        assert failed['cid'] == Reprocess_Cid
        assert failed['correl_id'] == Original_Cid
        assert failed['outcome'] == AuditOutcome.Error
        assert failed['status'] == Reprocess_Error
        assert failed['data'] == REST_Body

        assert get_parents(failed['id']) == [original_id]

        # A failed run released its key, so the request can be run again ..
        server = ServerStub()
        second_report = _run_reprocess(original_id, server)

        assert second_report['is_ok'] is True
        assert len(server.invoked) == 1

        # .. and one that went through is not run twice.
        third_report = _run_reprocess(original_id, server)

        assert third_report['is_ok'] is False
        assert third_report['is_duplicate'] is True
        assert len(server.invoked) == 1

# ################################################################################################################################

def test_a_channel_that_no_longer_exists_refuses(tmp_path:'any_') -> 'None':
    """ A request of a channel that was deleted since cannot reach a service and the report says so.
    """
    with audit_db_env(tmp_path):

        original_id = _seed_original_request(AuditSource.REST_Channel, 'audit.test.gone.channel', REST_Service, REST_Body)

        server = ServerStub()
        report = _run_reprocess(original_id, server)

        assert report['is_ok'] is False
        assert 'No REST or SOAP channel matches the name' in report['error']
        assert server.invoked == []

        # Nothing was recorded either.
        events = get_events()
        assert len(events) == 1

# ################################################################################################################################

def test_only_received_requests_can_be_reprocessed(tmp_path:'any_') -> 'None':
    """ A response the channel sent is not a request - asking to run one again refuses.
    """
    with audit_db_env(tmp_path):

        audit_log = AuditLog(Server_Name)
        response_id = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Response_Sent, REST_Channel_Name,
            cid=Original_Cid, endpoint=REST_Service, data='{"ok": true}')

        server = ServerStub()
        report = _run_reprocess(response_id, server)

        assert report['is_ok'] is False
        assert 'can be run again' in report['error']
        assert server.invoked == []

# ################################################################################################################################
# ################################################################################################################################
