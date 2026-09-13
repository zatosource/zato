# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An outgoing REST connection carries alert settings of its own kind - the status codes it alerts on among them -
# stored, defaulted, validated and listed the way a channel's are, while its health check asks for how often
# to ping and nothing else, its outcome reaching people through those very alerts.

# pytest
import pytest

# Zato
from zato.common.alerting.object_config import alert_type_channels, alert_type_rest, get_defaults, get_field_names, \
    storage_name
from zato.common.api import CONNECTION, HTTP_SOAP, SchedulerLink, URL_TYPE
from zato.common.exception import BadRequest
from zato.common.ext.bunch import Bunch
from zato.common.json_internal import dumps, loads
from zato.common.odb.model import HTTPSOAP
from zato.common.util.sql import parse_instance_opaque_attr
from zato.server.service.internal.http_soap.create import Create
from zato.server.service.internal.http_soap.edit import Edit
from zato.server.service.internal.http_soap.health_check import has_health_check_config as _has_health_check_config

# Test support
from http_soap_stub import create as _create, get as _get, get_list as _get_list, new_service as _new_service, \
    outgoing_input as _outgoing_input, stored_opaque as _stored_opaque, Cluster_Id as _cluster_id, \
    Outgoing_Name as _outgoing_name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from unittest.mock import MagicMock
    from zato.common.typing_ import any_
    any_ = any_
    MagicMock = MagicMock

# ################################################################################################################################
# ################################################################################################################################

# The names an outgoing REST connection stores its settings under, in the order of the tab
_storage_names = [storage_name(name) for name in get_field_names(alert_type_rest)]

# The names a channel alone stores - none of them ever lands on an outgoing connection
_channel_only_names = [storage_name(name) for name in get_field_names(alert_type_channels)
    if name not in get_field_names(alert_type_rest)]

# The id the scheduler stand-in gives every job it is asked to create
_job_id = 1234

# ################################################################################################################################
# ################################################################################################################################

def _create_outgoing(session_factory:'any_', **overrides:'any_') -> 'int':
    """ Creates one outgoing REST connection and returns its id.
    """
    out = _create(session_factory, **_outgoing_input(**overrides))
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestCreate:

    def test_an_outgoing_rest_connection_stores_the_settings_it_was_sent(self, session_factory:'any_') -> 'None':
        item_id = _create_outgoing(session_factory,
            alert_status_codes='404, 4xx',
            alert_status_code_threshold=5,
            alert_connection_failures=2,
            alert_email_connection='smtp:ops.smtp',
        )

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_status_codes'] == '404, 4xx'
        assert opaque['alert_status_code_threshold'] == 5
        assert opaque['alert_connection_failures'] == 2
        assert opaque['alert_email_connection'] == 'smtp:ops.smtp'

    def test_an_outgoing_rest_connection_fills_in_the_defaults_for_what_it_was_not_sent(self,
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

    def test_an_outgoing_rest_connection_stores_none_of_a_channels_own_settings(self, session_factory:'any_') -> 'None':
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

    def test_good_status_codes_are_stored_as_the_string_they_arrived_as(self, session_factory:'any_') -> 'None':
        item_id = _create_outgoing(session_factory, alert_status_codes='401,403 , 5xx')

        opaque = _stored_opaque(session_factory, item_id)
        assert opaque['alert_status_codes'] == '401,403 , 5xx'

# ################################################################################################################################
# ################################################################################################################################

class TestEdit:

    def test_an_edit_without_the_settings_keeps_the_stored_ones(self, session_factory:'any_') -> 'None':
        item_id = _create_outgoing(session_factory, alert_status_codes='404', alert_email_connection='smtp:ops.smtp')

        service = _new_service(Edit, session_factory, _outgoing_input(id=item_id, data_format='xml'))
        service.handle()

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_status_codes'] == '404'
        assert opaque['alert_email_connection'] == 'smtp:ops.smtp'

        for name in _storage_names:
            assert name in opaque

    def test_an_edit_with_the_settings_replaces_them(self, session_factory:'any_') -> 'None':
        item_id = _create_outgoing(session_factory, alert_status_codes='404')

        service = _new_service(Edit, session_factory,
            _outgoing_input(id=item_id, alert_status_codes='5xx', alert_is_active=False))
        service.handle()

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_status_codes'] == '5xx'
        assert opaque['alert_is_active'] is False

    def test_an_edit_refuses_bad_status_codes_and_keeps_the_stored_ones(self, session_factory:'any_') -> 'None':
        item_id = _create_outgoing(session_factory, alert_status_codes='404')

        service = _new_service(Edit, session_factory, _outgoing_input(id=item_id, alert_status_codes='40'))

        with pytest.raises(BadRequest):
            service.handle()

        opaque = _stored_opaque(session_factory, item_id)
        assert opaque['alert_status_codes'] == '404'

    def test_the_settings_ride_in_the_config_message(self, session_factory:'any_') -> 'None':
        item_id = _create_outgoing(session_factory, alert_status_codes='404', alert_connection_failures=7)

        service = _new_service(Edit, session_factory, _outgoing_input(id=item_id))
        service.handle()

        message = service.config_dispatcher.publish.call_args[0][0]
        assert message['alert_status_codes'] == '404'
        assert message['alert_connection_failures'] == 7

    def test_a_get_then_edit_round_trip_keeps_the_settings(self, session_factory:'any_') -> 'None':
        item_id = _create_outgoing(session_factory, alert_status_codes='404, 5xx', alert_llm_connection='ops.llm')

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

        assert opaque['alert_status_codes'] == '404, 5xx'
        assert opaque['alert_llm_connection'] == 'ops.llm'

# ################################################################################################################################
# ################################################################################################################################

class TestGetList:

    def test_an_outgoing_rest_connection_lists_every_setting_with_the_defaults_filled_in(self,
        session_factory:'any_') -> 'None':
        _ = _create_outgoing(session_factory, alert_status_codes='404')

        # A connection stored before a setting existed has nothing under that name
        session = session_factory()
        item = session.query(HTTPSOAP).filter(HTTPSOAP.name==_outgoing_name).one()
        opaque = parse_instance_opaque_attr(item)
        del opaque['alert_connection_failures']
        item.opaque1 = dumps(opaque)
        session.commit()
        session.close()

        rows = _get_list(session_factory, CONNECTION.OUTGOING, URL_TYPE.PLAIN_HTTP)
        row = rows[0]

        defaults = get_defaults(alert_type_rest)

        for name in _storage_names:
            assert name in row

        assert row['alert_status_codes'] == '404'
        assert row['alert_connection_failures'] == defaults['connection_failures']

        for name in _channel_only_names:
            assert name not in row, name

# ################################################################################################################################
# ################################################################################################################################

class TestHealthCheck:

    def test_a_run_every_alone_is_what_asks_for_a_check(self) -> 'None':
        assert _has_health_check_config(Bunch(health_check_run_every=5)) is True
        assert _has_health_check_config(Bunch(health_check_run_every=None)) is False
        assert _has_health_check_config(Bunch(health_check_run_every=0)) is False

    def test_the_health_check_field_list_asks_for_run_every_and_its_unit_alone(self) -> 'None':
        health_check = HTTP_SOAP.HealthCheck

        assert health_check.FieldList == (health_check.Field_Run_Every, health_check.Field_Run_Unit, health_check.Field_Job_ID)

        for name in health_check.FieldList:
            assert 'callback' not in name
            assert 'notify' not in name

    def test_a_create_with_a_run_every_creates_the_check_job(self, session_factory:'any_') -> 'None':
        service = _new_service(Create, session_factory,
            _outgoing_input(health_check_run_every=5, health_check_run_unit='minutes'))
        service.invoke.return_value = {'id': _job_id}
        service.handle()

        # The one job created is the health check's, pointing back at the connection ..
        create_calls = [call for call in service.invoke.call_args_list if call[0][0] == 'zato.scheduler.job.create']
        assert len(create_calls) == 1

        request = create_calls[0][0][1]
        assert request[SchedulerLink.Kind] == SchedulerLink.KindType.HealthCheck
        assert request[SchedulerLink.Conn_Type] == SchedulerLink.ConnType.REST_Outgoing
        assert request['service'] == HTTP_SOAP.HealthCheck.Dispatch_Service
        assert request['minutes'] == 5

        # .. its extra names the connection and nothing about where to deliver the outcome ..
        extra = loads(request['extra'])
        assert extra == {
            HTTP_SOAP.HealthCheck.Extra_Conn_ID: service.response.payload.id,
            HTTP_SOAP.HealthCheck.Extra_Conn_Name: _outgoing_name,
            HTTP_SOAP.HealthCheck.Extra_Conn_Type: SchedulerLink.ConnType.REST_Outgoing,
        }

        # .. and the connection remembers the job and how often it runs.
        opaque = _stored_opaque(session_factory, service.response.payload.id)

        assert opaque['health_check_run_every'] == 5
        assert opaque['health_check_run_unit'] == 'minutes'
        assert opaque['health_check_job_id'] == _job_id

    def test_a_create_without_a_run_every_creates_no_check_job(self, session_factory:'any_') -> 'None':
        service = _new_service(Create, session_factory, _outgoing_input())
        service.handle()

        for call in service.invoke.call_args_list:
            assert call[0][0] != 'zato.scheduler.job.create'

# ################################################################################################################################
# ################################################################################################################################
