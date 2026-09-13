# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An outgoing FHIR connection carries the alert settings an outgoing REST one does plus the operation outcomes it alerts
# on - the issue codes, their threshold and window - stored, defaulted, validated and listed under the fhir type through the
# generic connection services, and its health check asks for how often to ping, the check job naming the connection as a
# FHIR one and the check itself reading the connection's own wrapper.

# stdlib
from types import SimpleNamespace

# pytest
import pytest

# Zato
from zato.common.alerting.object_config import alert_type_fhir, alert_type_rest, get_defaults, get_field_names, storage_name
from zato.common.api import HTTP_SOAP, SchedulerLink
from zato.common.exception import BadRequest
from zato.common.json_internal import loads
from zato.server.service.internal.connection import HealthCheckRun
from zato.server.service.internal.generic.connection import Create, Delete, Edit

# Test support
from generic_stub import add_job as _add_job, count_connections as _count_connections, create as _create, \
    fhir_input as _fhir_input, get_list as _get_list, new_service as _new_service, stored_opaque as _stored_opaque, \
    FHIR_Address as _fhir_address, FHIR_Name as _fhir_name, Job_Id as _job_id

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_health_check = HTTP_SOAP.HealthCheck

# The names an outgoing FHIR connection stores its settings under, in the order of the tab
_storage_names = [storage_name(name) for name in get_field_names(alert_type_fhir)]

# The names a FHIR connection alone stores - the outcomes, which never land on a REST one
_fhir_only_names = [storage_name(name) for name in get_field_names(alert_type_fhir)
    if name not in get_field_names(alert_type_rest)]

# ################################################################################################################################
# ################################################################################################################################

def _create_calls(service:'any_') -> 'list':
    """ The scheduler job creations a service asked for.
    """
    out = [call for call in service.invoke.call_args_list if call[0][0] == 'zato.scheduler.job.create']
    return out

# ################################################################################################################################

def _invoked_names(service:'any_') -> 'list':
    """ The names of every service a service invoked, in order.
    """
    out = [call[0][0] for call in service.invoke.call_args_list]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestCreate:

    def test_an_outgoing_fhir_connection_stores_the_settings_it_was_sent(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory,
            alert_status_codes='500, 5xx',
            alert_status_code_threshold=5,
            alert_outcome_codes='exception, not-found',
            alert_outcome_threshold=2,
            alert_outcomes_window=600,
            alert_connection_failures=2,
            alert_email_connection='smtp:ops.smtp',
        )

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_status_codes'] == '500, 5xx'
        assert opaque['alert_status_code_threshold'] == 5
        assert opaque['alert_outcome_codes'] == 'exception, not-found'
        assert opaque['alert_outcome_threshold'] == 2
        assert opaque['alert_outcomes_window'] == 600
        assert opaque['alert_connection_failures'] == 2
        assert opaque['alert_email_connection'] == 'smtp:ops.smtp'

        # The FHIR details stay what they were sent as
        assert opaque['is_audit_log_active'] is True
        assert opaque['auth_type'] == 'no-auth'

    def test_a_status_codes_text_of_one_code_stays_text(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, alert_status_codes='500')

        opaque = _stored_opaque(session_factory, item_id)
        assert opaque['alert_status_codes'] == '500'

    def test_an_outgoing_fhir_connection_fills_in_the_defaults_for_what_it_was_not_sent(self,
        session_factory:'any_') -> 'None':
        item_id = _create(session_factory, alert_max_latency=2500)

        opaque = _stored_opaque(session_factory, item_id)
        defaults = get_defaults(alert_type_fhir)

        for name in _storage_names:
            assert name in opaque

        assert opaque['alert_max_latency'] == 2500
        assert opaque['alert_status_codes'] == defaults['status_codes']
        assert opaque['alert_status_codes'] == '401, 403, 5xx'
        assert opaque['alert_outcome_codes'] == defaults['outcome_codes']
        assert opaque['alert_outcome_codes'] == 'exception, transient, timeout, throttled, lock-error, no-store, too-costly'
        assert opaque['alert_outcome_threshold'] == defaults['outcome_threshold']
        assert opaque['alert_connection_failures'] == defaults['connection_failures']
        assert opaque['alert_is_active'] is True
        assert opaque['alert_use_llm'] is True

    def test_the_outcomes_are_the_fhir_connections_own_settings(self) -> 'None':
        assert _fhir_only_names == ['alert_outcome_codes', 'alert_outcome_threshold', 'alert_outcomes_window']

    def test_bad_status_codes_are_refused_before_anything_is_written(self, session_factory:'any_') -> 'None':

        with pytest.raises(BadRequest) as ctx:
            _ = _create(session_factory, alert_status_codes='6xx')

        assert '6xx' in str(ctx.value)
        assert _count_connections(session_factory) == 0

    def test_bad_outcome_codes_are_refused_before_anything_is_written(self, session_factory:'any_') -> 'None':

        # A SOAP fault code is not a FHIR issue code
        with pytest.raises(BadRequest) as ctx:
            _ = _create(session_factory, alert_outcome_codes='Receiver')

        assert 'Receiver' in str(ctx.value)
        assert _count_connections(session_factory) == 0

    def test_the_settings_ride_in_the_config_message(self, session_factory:'any_') -> 'None':
        service = _new_service(Create, session_factory, _fhir_input(alert_outcome_codes='not-found', alert_connection_failures=7))
        service.handle()

        message = service.config_dispatcher.publish.call_args[0][0]

        assert message['alert_outcome_codes'] == 'not-found'
        assert message['alert_connection_failures'] == 7
        assert message['alert_status_codes'] == '401, 403, 5xx'

# ################################################################################################################################
# ################################################################################################################################

class TestEdit:

    def test_an_edit_without_the_settings_keeps_the_stored_ones(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, alert_outcome_codes='not-found', alert_email_connection='smtp:ops.smtp')

        service = _new_service(Edit, session_factory, _fhir_input(id=item_id, is_audit_log_active=False))
        service.handle()

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_outcome_codes'] == 'not-found'
        assert opaque['alert_email_connection'] == 'smtp:ops.smtp'
        assert opaque['is_audit_log_active'] is False

        for name in _storage_names:
            assert name in opaque

    def test_an_edit_with_the_settings_replaces_them(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, alert_outcome_codes='not-found')

        service = _new_service(Edit, session_factory,
            _fhir_input(id=item_id, alert_outcome_codes='exception', alert_is_active=False))
        service.handle()

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_outcome_codes'] == 'exception'
        assert opaque['alert_is_active'] is False

    def test_an_edit_refuses_bad_outcome_codes_and_keeps_the_stored_ones(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, alert_outcome_codes='not-found')

        service = _new_service(Edit, session_factory, _fhir_input(id=item_id, alert_outcome_codes='500'))

        with pytest.raises(BadRequest):
            service.handle()

        opaque = _stored_opaque(session_factory, item_id)
        assert opaque['alert_outcome_codes'] == 'not-found'

# ################################################################################################################################
# ################################################################################################################################

class TestGetList:

    def test_an_outgoing_fhir_connection_lists_every_setting_with_the_defaults_filled_in(self,
        session_factory:'any_') -> 'None':
        _ = _create(session_factory, alert_outcome_codes='not-found')

        rows = _get_list(session_factory)
        assert len(rows) == 1

        row = rows[0]
        defaults = get_defaults(alert_type_fhir)

        for name in _storage_names:
            assert name in row

        assert row['name'] == _fhir_name
        assert row['address'] == _fhir_address
        assert row['alert_outcome_codes'] == 'not-found'
        assert row['alert_status_codes'] == defaults['status_codes']
        assert row['alert_outcome_threshold'] == defaults['outcome_threshold']
        assert row['alert_connection_failures'] == defaults['connection_failures']

        # The secret never leaves the server
        assert 'secret' not in row

# ################################################################################################################################
# ################################################################################################################################

class TestHealthCheck:

    def test_a_create_with_a_run_every_creates_the_check_job_as_a_fhir_one(self, session_factory:'any_') -> 'None':
        service = _new_service(Create, session_factory,
            _fhir_input(health_check_run_every=1, health_check_run_unit='minutes'))
        service.handle()

        # The one job created is the health check's, naming the connection as a FHIR one ..
        create_calls = _create_calls(service)
        assert len(create_calls) == 1

        request = create_calls[0][0][1]
        assert request[SchedulerLink.Kind] == SchedulerLink.KindType.HealthCheck
        assert request[SchedulerLink.Conn_Type] == SchedulerLink.ConnType.FHIR_Outgoing
        assert request[SchedulerLink.Conn_ID] == service.response.payload.id
        assert request['service'] == _health_check.Dispatch_Service
        assert request['name'] == _health_check.Job_Prefix + _fhir_name
        assert request['minutes'] == 1

        extra = loads(request['extra'])
        assert extra == {
            _health_check.Extra_Conn_ID: service.response.payload.id,
            _health_check.Extra_Conn_Name: _fhir_name,
            _health_check.Extra_Conn_Type: SchedulerLink.ConnType.FHIR_Outgoing,
        }

        # .. and the connection remembers the job and how often it runs.
        opaque = _stored_opaque(session_factory, service.response.payload.id)

        assert opaque[_health_check.Field_Run_Every] == 1
        assert opaque[_health_check.Field_Run_Unit] == 'minutes'
        assert opaque[_health_check.Field_Job_ID] == _job_id

    def test_a_create_without_a_run_every_creates_no_check_job(self, session_factory:'any_') -> 'None':
        service = _new_service(Create, session_factory, _fhir_input())
        service.handle()

        assert _create_calls(service) == []

    def test_a_bad_run_every_is_refused_before_anything_is_written(self, session_factory:'any_') -> 'None':
        service = _new_service(Create, session_factory,
            _fhir_input(health_check_run_every=1, health_check_run_unit='fortnights'))

        with pytest.raises(BadRequest) as ctx:
            service.handle()

        assert 'fortnights' in str(ctx.value)
        assert _count_connections(session_factory) == 0

    def test_an_edit_with_a_new_run_every_edits_the_existing_job(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, health_check_run_every=1, health_check_run_unit='minutes')
        _add_job(session_factory, _job_id, _health_check.Job_Prefix + _fhir_name)

        # The edit form sends the job id back along with the new schedule
        service = _new_service(Edit, session_factory, _fhir_input(id=item_id,
            health_check_run_every=30, health_check_run_unit='seconds', health_check_job_id=_job_id))
        service.handle()

        assert _invoked_names(service) == ['zato.scheduler.job.edit']

        request = service.invoke.call_args[0][1]
        assert request['id'] == _job_id
        assert request['seconds'] == 30
        assert request[SchedulerLink.Conn_Type] == SchedulerLink.ConnType.FHIR_Outgoing

        opaque = _stored_opaque(session_factory, item_id)
        assert opaque[_health_check.Field_Run_Every] == 30
        assert opaque[_health_check.Field_Run_Unit] == 'seconds'
        assert opaque[_health_check.Field_Job_ID] == _job_id

    def test_an_edit_that_does_not_carry_the_job_id_keeps_it(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, health_check_run_every=1, health_check_run_unit='minutes')
        _add_job(session_factory, _job_id, _health_check.Job_Prefix + _fhir_name)

        # What enmasse sends - the schedule without the job id it never knew
        service = _new_service(Edit, session_factory, _fhir_input(id=item_id,
            health_check_run_every=2, health_check_run_unit='minutes'))
        service.handle()

        assert _invoked_names(service) == ['zato.scheduler.job.edit']

        opaque = _stored_opaque(session_factory, item_id)
        assert opaque[_health_check.Field_Job_ID] == _job_id
        assert opaque[_health_check.Field_Run_Every] == 2

    def test_an_edit_without_a_run_every_deletes_the_job(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, health_check_run_every=1, health_check_run_unit='minutes')
        _add_job(session_factory, _job_id, _health_check.Job_Prefix + _fhir_name)

        service = _new_service(Edit, session_factory, _fhir_input(id=item_id, health_check_job_id=_job_id))
        service.handle()

        assert _invoked_names(service) == ['zato.scheduler.job.delete']
        assert service.invoke.call_args[0][1] == {'id': _job_id}

    def test_a_delete_of_the_connection_deletes_its_job(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, health_check_run_every=1, health_check_run_unit='minutes')
        _add_job(session_factory, _job_id, _health_check.Job_Prefix + _fhir_name)

        service = _new_service(Delete, session_factory, {'id': item_id})
        service.handle()

        assert _count_connections(session_factory) == 0
        assert _invoked_names(service) == ['zato.scheduler.job.delete']
        assert service.invoke.call_args[0][1] == {'id': _job_id}

    def test_a_delete_of_a_connection_without_a_check_deletes_no_job(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory)

        service = _new_service(Delete, session_factory, {'id': item_id})
        service.handle()

        assert _count_connections(session_factory) == 0
        assert _invoked_names(service) == []

# ################################################################################################################################
# ################################################################################################################################

class _FHIRWrapperStub:
    """ Stands in for the wrapper of one outgoing FHIR connection - answers a ping with the response it is given
    or raises the error it is given, remembering how it was asked.
    """
    def __init__(self, response:'any_'=None, error:'Exception | None'=None) -> 'None':
        self.response = response
        self.error = error
        self.calls = []

    def ping(self, cid:'str', *, return_response:'bool'=False, needs_audit:'bool'=False) -> 'any_':
        self.calls.append((cid, return_response, needs_audit))

        if self.error:
            raise self.error

        return self.response

# ################################################################################################################################

def _run_health_check(session_factory:'any_', wrapper:'_FHIRWrapperStub') -> 'any_':
    """ Runs HealthCheckRun the way the scheduler does for a FHIR connection, against the given wrapper.
    """
    service = _new_service(HealthCheckRun, session_factory, {})
    service.request.payload = {
        _health_check.Extra_Conn_ID: 1,
        _health_check.Extra_Conn_Name: _fhir_name,
        _health_check.Extra_Conn_Type: SchedulerLink.ConnType.FHIR_Outgoing,
    }
    service._config_manager = SimpleNamespace(outconn_hl7_fhir={_fhir_name: SimpleNamespace(conn=wrapper)})

    service.handle()

    return service

# ################################################################################################################################
# ################################################################################################################################

class TestHealthCheckRun:

    def test_a_fhir_connection_is_pinged_through_its_own_wrapper_for_the_response(self, session_factory:'any_') -> 'None':
        wrapper = _FHIRWrapperStub(response=SimpleNamespace(ok=True, status_code=200, reason='OK'))

        service = _run_health_check(session_factory, wrapper)

        # One ping, asking for the response and for the pair to be written under the health source
        assert wrapper.calls == [(service.cid, True, True)]

    def test_a_failing_ping_is_a_check_that_ran(self, session_factory:'any_') -> 'None':
        wrapper = _FHIRWrapperStub(response=SimpleNamespace(ok=False, status_code=503, reason='Service Unavailable'))

        _ = _run_health_check(session_factory, wrapper)

        assert len(wrapper.calls) == 1

    def test_a_ping_that_raises_is_a_check_that_ran(self, session_factory:'any_') -> 'None':
        wrapper = _FHIRWrapperStub(error=Exception('Connection refused'))

        _ = _run_health_check(session_factory, wrapper)

        assert len(wrapper.calls) == 1

# ################################################################################################################################
# ################################################################################################################################
