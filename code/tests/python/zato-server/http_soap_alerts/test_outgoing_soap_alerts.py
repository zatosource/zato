# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An outgoing SOAP connection carries the same alert settings an outgoing REST one does - the status codes it alerts on
# among them, a SOAP fault arriving as a 500 - stored, defaulted, validated and listed the same way, and its health
# check asks for how often to ping and nothing else, the check job naming the connection as a SOAP one.

# pytest
import pytest

# Zato
from zato.common.alerting.object_config import alert_type_channels, alert_type_rest, get_defaults, get_field_names, \
    storage_name
from zato.common.api import CONNECTION, HTTP_SOAP, SchedulerLink, URL_TYPE
from zato.common.exception import BadRequest
from zato.common.json_internal import loads
from zato.common.odb.model import HTTPSOAP
from zato.server.service.internal.http_soap.create import Create
from zato.server.service.internal.http_soap.edit import Edit

# Test support
from http_soap_stub import create as _create, get as _get, get_list as _get_list, new_service as _new_service, \
    soap_outgoing_input as _soap_outgoing_input, stored_opaque as _stored_opaque, Cluster_Id as _cluster_id, \
    Outgoing_Name as _outgoing_name, SOAP_Action as _soap_action, SOAP_Version as _soap_version

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# The names an outgoing connection stores its settings under, in the order of the tab
_storage_names = [storage_name(name) for name in get_field_names(alert_type_rest)]

# The names a channel alone stores - none of them ever lands on an outgoing connection
_channel_only_names = [storage_name(name) for name in get_field_names(alert_type_channels)
    if name not in get_field_names(alert_type_rest)]

# The id the scheduler stand-in gives every job it is asked to create
_job_id = 4321

# ################################################################################################################################
# ################################################################################################################################

def _create_outgoing(session_factory:'any_', **overrides:'any_') -> 'int':
    """ Creates one outgoing SOAP connection and returns its id.
    """
    out = _create(session_factory, **_soap_outgoing_input(**overrides))
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestCreate:

    def test_an_outgoing_soap_connection_stores_the_settings_it_was_sent(self, session_factory:'any_') -> 'None':
        item_id = _create_outgoing(session_factory,
            alert_status_codes='500, 5xx',
            alert_status_code_threshold=5,
            alert_connection_failures=2,
            alert_email_connection='smtp:ops.smtp',
        )

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_status_codes'] == '500, 5xx'
        assert opaque['alert_status_code_threshold'] == 5
        assert opaque['alert_connection_failures'] == 2
        assert opaque['alert_email_connection'] == 'smtp:ops.smtp'

        # The SOAP details stay what they were sent as
        item_dict = _get(session_factory, item_id)
        assert item_dict['soap_action'] == _soap_action
        assert item_dict['soap_version'] == _soap_version

    def test_an_outgoing_soap_connection_fills_in_the_defaults_for_what_it_was_not_sent(self,
        session_factory:'any_') -> 'None':
        item_id = _create_outgoing(session_factory, alert_max_latency=2500)

        opaque = _stored_opaque(session_factory, item_id)
        defaults = get_defaults(alert_type_rest)

        for name in _storage_names:
            assert name in opaque

        assert opaque['alert_max_latency'] == 2500
        assert opaque['alert_status_codes'] == defaults['status_codes']
        assert opaque['alert_status_codes'] == '401, 403, 5xx'
        assert opaque['alert_connection_failures'] == defaults['connection_failures']
        assert opaque['alert_is_active'] is True
        assert opaque['alert_use_llm'] is True

    def test_an_outgoing_soap_connection_stores_none_of_a_channels_own_settings(self, session_factory:'any_') -> 'None':
        item_id = _create_outgoing(session_factory, alert_traffic_expected=True, alert_auth_failures=3)

        opaque = _stored_opaque(session_factory, item_id)

        for name in _channel_only_names:
            assert name not in opaque, name

    def test_bad_status_codes_are_refused_before_anything_is_written(self, session_factory:'any_') -> 'None':

        with pytest.raises(BadRequest) as ctx:
            _ = _create_outgoing(session_factory, alert_status_codes='6xx')

        assert '6xx' in str(ctx.value)

        session = session_factory()
        assert session.query(HTTPSOAP).count() == 0
        session.close()

# ################################################################################################################################
# ################################################################################################################################

class TestEdit:

    def test_an_edit_without_the_settings_keeps_the_stored_ones(self, session_factory:'any_') -> 'None':
        item_id = _create_outgoing(session_factory, alert_status_codes='500', alert_email_connection='smtp:ops.smtp')

        service = _new_service(Edit, session_factory, _soap_outgoing_input(id=item_id, soap_version='1.2'))
        service.handle()

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_status_codes'] == '500'
        assert opaque['alert_email_connection'] == 'smtp:ops.smtp'

        for name in _storage_names:
            assert name in opaque

        item_dict = _get(session_factory, item_id)
        assert item_dict['soap_version'] == '1.2'

    def test_an_edit_with_the_settings_replaces_them(self, session_factory:'any_') -> 'None':
        item_id = _create_outgoing(session_factory, alert_status_codes='500')

        service = _new_service(Edit, session_factory,
            _soap_outgoing_input(id=item_id, alert_status_codes='5xx', alert_is_active=False))
        service.handle()

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_status_codes'] == '5xx'
        assert opaque['alert_is_active'] is False

    def test_an_edit_refuses_bad_status_codes_and_keeps_the_stored_ones(self, session_factory:'any_') -> 'None':
        item_id = _create_outgoing(session_factory, alert_status_codes='500')

        service = _new_service(Edit, session_factory, _soap_outgoing_input(id=item_id, alert_status_codes='50'))

        with pytest.raises(BadRequest):
            service.handle()

        opaque = _stored_opaque(session_factory, item_id)
        assert opaque['alert_status_codes'] == '500'

    def test_the_settings_ride_in_the_config_message(self, session_factory:'any_') -> 'None':
        item_id = _create_outgoing(session_factory, alert_status_codes='500', alert_connection_failures=7)

        service = _new_service(Edit, session_factory, _soap_outgoing_input(id=item_id))
        service.handle()

        message = service.config_dispatcher.publish.call_args[0][0]
        assert message['alert_status_codes'] == '500'
        assert message['alert_connection_failures'] == 7

    def test_a_get_then_edit_round_trip_keeps_the_settings(self, session_factory:'any_') -> 'None':
        item_id = _create_outgoing(session_factory, alert_status_codes='500, 5xx', alert_llm_connection='ops.llm')

        # What the listing's inline edit does - read the object, change one field, save it whole
        item_dict = _get(session_factory, item_id)
        item_dict['id'] = item_id
        item_dict['cluster_id'] = _cluster_id
        item_dict['service'] = None
        item_dict['is_active'] = False
        item_dict['security_groups'] = None

        service = _new_service(Edit, session_factory, item_dict)
        service.handle()

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_status_codes'] == '500, 5xx'
        assert opaque['alert_llm_connection'] == 'ops.llm'

# ################################################################################################################################
# ################################################################################################################################

class TestGetList:

    def test_an_outgoing_soap_connection_lists_every_setting_with_the_defaults_filled_in(self,
        session_factory:'any_') -> 'None':
        _ = _create_outgoing(session_factory, alert_status_codes='500')

        rows = _get_list(session_factory, CONNECTION.OUTGOING, URL_TYPE.SOAP)
        row = rows[0]

        defaults = get_defaults(alert_type_rest)

        for name in _storage_names:
            assert name in row

        assert row['alert_status_codes'] == '500'
        assert row['alert_connection_failures'] == defaults['connection_failures']
        assert row['soap_action'] == _soap_action

        for name in _channel_only_names:
            assert name not in row, name

    def test_the_rest_listing_never_carries_a_soap_connection(self, session_factory:'any_') -> 'None':
        _ = _create_outgoing(session_factory, alert_status_codes='500')

        rows = _get_list(session_factory, CONNECTION.OUTGOING, URL_TYPE.PLAIN_HTTP)
        assert rows == []

# ################################################################################################################################
# ################################################################################################################################

class TestHealthCheck:

    def test_a_create_with_a_run_every_creates_the_check_job_as_a_soap_one(self, session_factory:'any_') -> 'None':
        service = _new_service(Create, session_factory,
            _soap_outgoing_input(health_check_run_every=1, health_check_run_unit='seconds'))
        service.invoke.return_value = {'id': _job_id}
        service.handle()

        # The one job created is the health check's, naming the connection as a SOAP one ..
        create_calls = [call for call in service.invoke.call_args_list if call[0][0] == 'zato.scheduler.job.create']
        assert len(create_calls) == 1

        request = create_calls[0][0][1]
        assert request[SchedulerLink.Kind] == SchedulerLink.KindType.HealthCheck
        assert request[SchedulerLink.Conn_Type] == SchedulerLink.ConnType.SOAP_Outgoing
        assert request['service'] == HTTP_SOAP.HealthCheck.Dispatch_Service
        assert request['seconds'] == 1

        extra = loads(request['extra'])
        assert extra == {
            HTTP_SOAP.HealthCheck.Extra_Conn_ID: service.response.payload.id,
            HTTP_SOAP.HealthCheck.Extra_Conn_Name: _outgoing_name,
            HTTP_SOAP.HealthCheck.Extra_Conn_Type: SchedulerLink.ConnType.SOAP_Outgoing,
        }

        # .. and the connection remembers the job and how often it runs.
        opaque = _stored_opaque(session_factory, service.response.payload.id)

        assert opaque['health_check_run_every'] == 1
        assert opaque['health_check_run_unit'] == 'seconds'
        assert opaque['health_check_job_id'] == _job_id

    def test_a_create_without_a_run_every_creates_no_check_job(self, session_factory:'any_') -> 'None':
        service = _new_service(Create, session_factory, _soap_outgoing_input())
        service.handle()

        for call in service.invoke.call_args_list:
            assert call[0][0] != 'zato.scheduler.job.create'

# ################################################################################################################################
# ################################################################################################################################
