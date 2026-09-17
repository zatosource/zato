# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.alerting.object_config import alert_type_channels, alert_type_rest, get_defaults, get_field_names, storage_name
from zato.common.alerting.time_slots import TimeSlotsError
from zato.common.api import CONNECTION, URL_TYPE
from zato.common.json_internal import dumps
from zato.common.odb.model import HTTPSOAP
from zato.common.util.sql import parse_instance_opaque_attr
from zato.server.service.internal.http_soap.edit import Edit

# Test support
from http_soap_stub import base_input as _base_input, create as _create, get as _get, get_list as _get_list, \
    new_service as _new_service, soap_input as _soap_input, soap_outgoing_input as _soap_outgoing_input, \
    stored_opaque as _stored_opaque, Channel_Name as _channel_name, Cluster_Id as _cluster_id

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# The names the settings are stored under, in the order of the tab
_storage_names = [storage_name(name) for name in get_field_names(alert_type_channels)]
_rest_storage_names = [storage_name(name) for name in get_field_names(alert_type_rest)]

# ################################################################################################################################
# ################################################################################################################################

class TestCreate:

    def test_a_rest_channel_stores_the_settings_it_was_sent(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory,
            alert_max_latency=2500,
            alert_traffic_expected=True,
            alert_silence_window=1800,
            alert_email_connection='smtp:ops.smtp',
        )

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_max_latency'] == 2500
        assert opaque['alert_traffic_expected'] is True
        assert opaque['alert_silence_window'] == 1800
        assert opaque['alert_email_connection'] == 'smtp:ops.smtp'

    def test_a_rest_channel_fills_in_the_defaults_for_what_it_was_not_sent(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, alert_max_latency=2500)

        opaque = _stored_opaque(session_factory, item_id)
        defaults = get_defaults(alert_type_channels)

        for name in get_field_names(alert_type_channels):
            assert storage_name(name) in opaque

        assert opaque['alert_consecutive_failures'] == defaults['consecutive_failures']
        assert opaque['alert_silence_slots'] == '[]'
        assert opaque['alert_is_active'] is True
        assert opaque['alert_use_llm'] is True

    def test_a_soap_outgoing_connection_stores_settings(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, **_soap_outgoing_input(alert_max_latency=2500, alert_status_code_threshold=7))

        opaque = _stored_opaque(session_factory, item_id)
        defaults = get_defaults(alert_type_rest)

        # The settings follow the rest type, as an outgoing REST connection's do ..
        assert opaque['alert_max_latency'] == 2500
        assert opaque['alert_status_code_threshold'] == 7
        assert opaque['alert_status_codes'] == defaults['status_codes']

        # .. and none of the channel-only ones is stored
        for name in _storage_names:
            if name not in _rest_storage_names:
                assert name not in opaque, name

    def test_a_soap_channel_stores_the_settings_it_was_sent(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, **_soap_input(alert_max_latency=2500, alert_auth_failures=3))

        opaque = _stored_opaque(session_factory, item_id)
        defaults = get_defaults(alert_type_channels)

        assert opaque['alert_max_latency'] == 2500
        assert opaque['alert_auth_failures'] == 3
        assert opaque['alert_is_active'] is True

        # What it was not sent is at its default, as with a REST channel
        for name in _storage_names:
            assert name in opaque

        assert opaque['alert_consecutive_failures'] == defaults['consecutive_failures']

    def test_bad_silence_slots_are_refused_before_anything_is_written(self, session_factory:'any_') -> 'None':
        bad_slots = dumps([{'time_from': '09:00', 'is_on': True, 'silence_seconds': 900}])

        with pytest.raises(TimeSlotsError) as ctx:
            _ = _create(session_factory, alert_silence_slots=bad_slots)

        assert 'Time slot 1 has no time_to' in str(ctx.value)

        session = session_factory()
        assert session.query(HTTPSOAP).count() == 0
        session.close()

    def test_good_silence_slots_are_stored_as_the_string_they_arrived_as(self, session_factory:'any_') -> 'None':
        slots = dumps([{'time_from': '09:00', 'time_to': '17:00', 'is_on': True, 'silence_seconds': 900}])

        item_id = _create(session_factory, alert_silence_slots=slots)

        opaque = _stored_opaque(session_factory, item_id)
        assert opaque['alert_silence_slots'] == slots

# ################################################################################################################################
# ################################################################################################################################

class TestEdit:

    def test_an_edit_without_the_settings_keeps_the_stored_ones(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, alert_max_latency=2500, alert_email_connection='smtp:ops.smtp')

        service = _new_service(Edit, session_factory, _base_input(id=item_id, data_format='xml'))
        service.handle()

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_max_latency'] == 2500
        assert opaque['alert_email_connection'] == 'smtp:ops.smtp'

        for name in _storage_names:
            assert name in opaque

    def test_an_edit_with_the_settings_replaces_them(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, alert_max_latency=2500)

        service = _new_service(Edit, session_factory, _base_input(id=item_id, alert_max_latency=750, alert_is_active=False))
        service.handle()

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_max_latency'] == 750
        assert opaque['alert_is_active'] is False

    def test_a_soap_channel_edit_without_the_settings_keeps_the_stored_ones(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, **_soap_input(alert_max_latency=2500, alert_email_connection='smtp:ops.smtp'))

        service = _new_service(Edit, session_factory, _soap_input(id=item_id, soap_version='1.2'))
        service.handle()

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_max_latency'] == 2500
        assert opaque['alert_email_connection'] == 'smtp:ops.smtp'

        for name in _storage_names:
            assert name in opaque

    def test_a_soap_channel_edit_with_the_settings_replaces_them(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, **_soap_input(alert_max_latency=2500))

        service = _new_service(Edit, session_factory, _soap_input(id=item_id, alert_max_latency=750, alert_is_active=False))
        service.handle()

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_max_latency'] == 750
        assert opaque['alert_is_active'] is False

    def test_the_settings_ride_in_the_config_message(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, alert_max_latency=2500)

        service = _new_service(Edit, session_factory, _base_input(id=item_id))
        service.handle()

        message = service.config_dispatcher.publish.call_args[0][0]
        assert message['alert_max_latency'] == 2500

    def test_a_get_then_edit_round_trip_keeps_the_settings(self, session_factory:'any_') -> 'None':
        slots = dumps([{'time_from': '22:00', 'time_to': '06:00', 'is_on': False, 'silence_seconds': 3600}])
        item_id = _create(session_factory, alert_max_latency=2500, alert_silence_slots=slots, alert_llm_connection='ops.llm')

        # What the listing's inline edit does - read the object, change one field, save it whole
        item_dict = _get(session_factory, item_id)
        item_dict['id'] = item_id
        item_dict['cluster_id'] = _cluster_id
        item_dict['service'] = item_dict['service_name']
        item_dict['is_active'] = False
        item_dict['security_groups'] = None

        service = _new_service(Edit, session_factory, item_dict)
        service.handle()

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_max_latency'] == 2500
        assert opaque['alert_silence_slots'] == slots
        assert opaque['alert_llm_connection'] == 'ops.llm'

# ################################################################################################################################
# ################################################################################################################################

class TestGetList:

    def test_a_rest_channel_lists_every_setting_with_the_defaults_filled_in(self, session_factory:'any_') -> 'None':
        _ = _create(session_factory, alert_max_latency=2500)

        # A channel stored before a setting existed has nothing under that name
        session = session_factory()
        item = session.query(HTTPSOAP).filter(HTTPSOAP.name==_channel_name).one()
        opaque = parse_instance_opaque_attr(item)
        del opaque['alert_client_errors']
        item.opaque1 = dumps(opaque)
        session.commit()
        session.close()

        rows = _get_list(session_factory, CONNECTION.CHANNEL, URL_TYPE.PLAIN_HTTP)
        row = rows[0]

        defaults = get_defaults(alert_type_channels)

        for name in _storage_names:
            assert name in row

        assert row['alert_max_latency'] == 2500
        assert row['alert_client_errors'] == defaults['client_errors']

    def test_a_soap_channel_lists_every_setting_with_the_defaults_filled_in(self, session_factory:'any_') -> 'None':
        _ = _create(session_factory, **_soap_input(alert_auth_failures=3))

        # A channel stored before a setting existed has nothing under that name
        session = session_factory()
        item = session.query(HTTPSOAP).filter(HTTPSOAP.name==_channel_name).one()
        opaque = parse_instance_opaque_attr(item)
        del opaque['alert_client_errors']
        item.opaque1 = dumps(opaque)
        session.commit()
        session.close()

        rows = _get_list(session_factory, CONNECTION.CHANNEL, URL_TYPE.SOAP)
        row = rows[0]

        defaults = get_defaults(alert_type_channels)

        for name in _storage_names:
            assert name in row

        assert row['alert_auth_failures'] == 3
        assert row['alert_client_errors'] == defaults['client_errors']

    def test_a_soap_outgoing_connection_lists_settings(self, session_factory:'any_') -> 'None':
        _ = _create(session_factory, **_soap_outgoing_input())

        rows = _get_list(session_factory, CONNECTION.OUTGOING, URL_TYPE.SOAP)
        row = rows[0]
        defaults = get_defaults(alert_type_rest)

        # Every rest setting reads at its default, the channel-only ones are absent
        for name in _rest_storage_names:
            assert name in row, name

        assert row['alert_status_codes'] == defaults['status_codes']
        assert row['alert_connection_failures'] == defaults['connection_failures']

        for name in _storage_names:
            if name not in _rest_storage_names:
                assert name not in row, name

# ################################################################################################################################
# ################################################################################################################################
