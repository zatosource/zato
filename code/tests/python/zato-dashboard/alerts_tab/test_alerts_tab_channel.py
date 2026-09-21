# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The HTTP/SOAP screen's channel and outgoing connection forms and the message built from what they post - every
# storage name of the type in seconds, the prefixed fields of an edit, the REST and SOAP settings of an outgoing
# connection and none of the channel-only ones, and a listed channel's windows read back as a count and a unit.

# pytest
import pytest

# Zato
from zato.common.ext.bunch import Bunch

# Zato - Dashboard
from zato.admin.web import alerts_tab
from zato.admin.web.forms.http_soap import EditForm as ChannelEditForm
from zato.admin.web.views import http_soap_message
from zato.common.alerting.object_config import alert_type_channels, alert_type_rest, alert_type_soap, Unit_Field_Suffix
from zato.common.api import EMAIL, GENERIC, ZATO_NONE

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist
    any_ = any_
    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

_smtp_names = ['ops.smtp', 'billing.smtp']
_m365_name = 'ops.m365'
_generic_imap_name = 'archive.imap'
_llm_names = ['ops.llm', 'ops.llm.backup']

# ################################################################################################################################
# ################################################################################################################################

class _FakeClient:
    """ Answers the two email listings, the LLM connection listing and the service listing.
    """
    def __init__(self) -> 'None':
        self.calls:'anylist' = []

    def invoke(self, service:'str', request:'anydict') -> 'any_':
        self.calls.append((service, request))

        if service == 'zato.email.smtp.get-list':
            out = []
            for name in _smtp_names:
                out.append(Bunch(name=name))

        elif service == 'zato.email.imap.get-list':
            out = [
                Bunch(name=_m365_name, server_type=EMAIL.IMAP.ServerType.Microsoft365),
                Bunch(name=_generic_imap_name, server_type=EMAIL.IMAP.ServerType.Generic),
            ]

        elif service == 'zato.generic.connection.get-list':
            assert request['type_'] == GENERIC.CONNECTION.TYPE.OUTCONN_LLM
            out = []
            for name in _llm_names:
                out.append(Bunch(name=name))

        elif service == 'zato.service.get-list':
            out = Bunch(data=[Bunch(name='demo.ping', id=1)])

        else:
            raise Exception(f'Unexpected service `{service}`')

        return out

# ################################################################################################################################

@pytest.fixture
def req() -> 'any_':
    out = Bunch()
    out.zato = Bunch()
    out.zato.client = _FakeClient()
    out.zato.cluster_id = 1
    return out

# ################################################################################################################################
# ################################################################################################################################

def _channel_params(connection:'str', transport:'str', prefix:'str'='') -> 'anydict':
    """ What the browser posts from a channel or connection form of the HTTP/SOAP screen, with every field
    the message builder reads and the Alerts tab's own fields filled in the way the tab posts them.
    """
    out = {
        'connection': connection,
        'transport': transport,
        'cluster_id': '1',
        prefix + 'name': 'orders.api',
        prefix + 'is_active': 'on',
        prefix + 'security': ZATO_NONE,
        prefix + 'url_path': '/orders',
        prefix + 'service': 'orders.get',
        prefix + 'alert_is_active': 'on',
        prefix + 'alert_consecutive_failures': '4',
        prefix + 'alert_error_rate': '15',
        prefix + 'alert_window': '10',
        prefix + 'alert_window_unit': 'minute',
        prefix + 'alert_server_errors': '5',
        prefix + 'alert_server_errors_window': '1',
        prefix + 'alert_server_errors_window_unit': 'hour',
        prefix + 'alert_max_latency': '2500',
        prefix + 'alert_latency_window': '5',
        prefix + 'alert_latency_window_unit': 'minute',
        prefix + 'alert_auth_failures': '20',
        prefix + 'alert_auth_failures_window': '1',
        prefix + 'alert_auth_failures_window_unit': 'hour',
        prefix + 'alert_client_errors': '50',
        prefix + 'alert_client_errors_window': '5',
        prefix + 'alert_client_errors_window_unit': 'minute',
        prefix + 'alert_traffic_expected': 'on',
        prefix + 'alert_silence_window': '2',
        prefix + 'alert_silence_window_unit': 'hour',
        prefix + 'alert_silence_slots': _slots_text,
        prefix + 'alert_use_llm': 'on',
        prefix + 'alert_email_connection': 'smtp:ops.smtp',
        prefix + 'alert_llm_connection': 'ops.llm',
    }
    return out

# ################################################################################################################################

# The silence slots the channel form tests post, the way the tab's JS serializes them
_slots_text = '[{"time_from": "22:00", "time_to": "06:00", "is_on": false, "silence_seconds": 3600}]'

# The settings the channel form tests expect in the message, each duration already in seconds
_expected_channel_settings = {
    'alert_is_active': True,
    'alert_consecutive_failures': 4,
    'alert_error_rate': 15,
    'alert_window': 600,
    'alert_server_errors': 5,
    'alert_server_errors_window': 3600,
    'alert_max_latency': 2500,
    'alert_latency_window': 300,
    'alert_auth_failures': 20,
    'alert_auth_failures_window': 3600,
    'alert_client_errors': 50,
    'alert_client_errors_window': 300,
    'alert_traffic_expected': True,
    'alert_silence_window': 7200,
    'alert_silence_slots': _slots_text,
    'alert_use_llm': True,
    'alert_email_connection': 'smtp:ops.smtp',
    'alert_llm_connection': 'ops.llm',
}

# ################################################################################################################################

def _outgoing_rest_params(prefix:'str'='') -> 'anydict':
    """ The Alerts tab's own fields of an outgoing REST connection's form, the way the tab posts them -
    the status codes with the whitespace a person may leave around them.
    """
    out = {
        prefix + 'alert_status_codes': ' 401, 403, 4xx, 5xx ',
        prefix + 'alert_status_code_threshold': '6',
        prefix + 'alert_status_codes_window': '15',
        prefix + 'alert_status_codes_window_unit': 'minute',
        prefix + 'alert_connection_failures': '2',
        prefix + 'alert_connection_failures_window': '1',
        prefix + 'alert_connection_failures_window_unit': 'hour',
        prefix + 'alert_dlq_messages': '3',
        prefix + 'alert_queue_depth': '250',
    }
    return out

def _outgoing_soap_params(prefix:'str'='') -> 'anydict':
    """ The Alerts tab's own fields of an outgoing SOAP connection's form - the REST ones and the faults on top,
    the fault codes with the whitespace a person may leave around them.
    """
    out = _outgoing_rest_params(prefix)
    out.update({
        prefix + 'alert_fault_codes': ' Receiver, x:Timeout ',
        prefix + 'alert_fault_threshold': '2',
        prefix + 'alert_faults_window': '30',
        prefix + 'alert_faults_window_unit': 'minute',
    })
    return out

# The settings the outgoing REST form tests expect in the message, each duration already in seconds
_expected_outgoing_rest_settings = {
    'alert_is_active': True,
    'alert_consecutive_failures': 4,
    'alert_error_rate': 15,
    'alert_window': 600,
    'alert_status_codes': '401, 403, 4xx, 5xx',
    'alert_status_code_threshold': 6,
    'alert_status_codes_window': 900,
    'alert_connection_failures': 2,
    'alert_connection_failures_window': 3600,
    'alert_max_latency': 2500,
    'alert_latency_window': 300,
    'alert_dlq_messages': 3,
    'alert_queue_depth': 250,
    'alert_use_llm': True,
    'alert_email_connection': 'smtp:ops.smtp',
    'alert_llm_connection': 'ops.llm',
}

# ################################################################################################################################
# ################################################################################################################################

class TestChannelForm:

    def test_edit_form_fields_are_prefixed(self, req:'any_') -> 'None':

        form = ChannelEditForm(prefix='edit', req=req, alert_type=alert_type_channels)

        for field_name in ('alert_window', 'alert_silence_window', 'alert_silence_slots', 'alert_traffic_expected'):
            rendered = str(form[field_name])
            assert f'name="edit-{field_name}"' in rendered, field_name
            assert f'id="id_edit-{field_name}"' in rendered, field_name

# ################################################################################################################################

    def test_a_rest_channel_message_carries_every_storage_name_in_seconds(self) -> 'None':

        params = _channel_params('channel', 'plain_http')
        message = http_soap_message.get_edit_create_message(params)

        for name in alerts_tab.get_storage_field_names(alert_type_channels):
            if name.endswith(Unit_Field_Suffix):
                assert name not in message, name
            else:
                assert name in message, name

        for name, value in _expected_channel_settings.items():
            assert message[name] == value, name

        assert message['name'] == 'orders.api'
        assert message['url_path'] == '/orders'

# ################################################################################################################################

    def test_an_edit_message_reads_the_prefixed_fields(self) -> 'None':

        params = _channel_params('channel', 'plain_http', prefix='edit-')
        params['id'] = '17'

        message = http_soap_message.get_edit_create_message(params, prefix='edit-')

        assert message['id'] == '17'
        for name, value in _expected_channel_settings.items():
            assert message[name] == value, name

# ################################################################################################################################

    def test_a_soap_channel_message_carries_the_alert_settings(self) -> 'None':
        params = _channel_params('channel', 'soap')
        message = http_soap_message.get_edit_create_message(params)

        for name in alerts_tab.get_storage_field_names(alert_type_channels):
            if name.endswith(Unit_Field_Suffix):
                assert name not in message, name
            else:
                assert name in message, name

        for name, value in _expected_channel_settings.items():
            assert message[name] == value, name

# ################################################################################################################################

    def test_a_soap_channel_edit_message_reads_the_prefixed_fields(self) -> 'None':

        params = _channel_params('channel', 'soap', prefix='edit-')
        params['id'] = '18'

        message = http_soap_message.get_edit_create_message(params, prefix='edit-')

        assert message['id'] == '18'
        for name, value in _expected_channel_settings.items():
            assert message[name] == value, name

# ################################################################################################################################

    def test_an_outgoing_rest_message_carries_the_rest_settings(self) -> 'None':

        params = _channel_params('outgoing', 'plain_http')
        params.update(_outgoing_rest_params())

        message = http_soap_message.get_edit_create_message(params)

        for name in alerts_tab.get_storage_field_names(alert_type_rest):
            if name.endswith(Unit_Field_Suffix):
                assert name not in message, name
            else:
                assert name in message, name

        for name, value in _expected_outgoing_rest_settings.items():
            assert message[name] == value, name

        # The channel-only settings are not read off an outgoing connection's form
        for name in ('alert_server_errors', 'alert_auth_failures', 'alert_traffic_expected', 'alert_silence_slots'):
            assert name not in message, name

# ################################################################################################################################

    def test_an_outgoing_soap_message_carries_the_soap_settings(self) -> 'None':

        params = _channel_params('outgoing', 'soap')
        params.update(_outgoing_soap_params())

        message = http_soap_message.get_edit_create_message(params)

        # Every setting of the soap type - the rest settings and the faults on top ..
        for name in alerts_tab.get_storage_field_names(alert_type_soap):
            if name.endswith(Unit_Field_Suffix):
                assert name not in message, name
            else:
                assert name in message, name

        for name, value in _expected_outgoing_rest_settings.items():
            assert message[name] == value, name

        assert message['alert_fault_codes'] == 'Receiver, x:Timeout'
        assert message['alert_fault_threshold'] == 2
        assert message['alert_faults_window'] == 1800

        # .. and none of the channel-only ones
        soap_names = alerts_tab.get_storage_field_names(alert_type_soap)
        for name in alerts_tab.get_storage_field_names(alert_type_channels):
            if name not in soap_names:
                assert name not in message, name

# ################################################################################################################################

    def test_a_listed_channel_shows_each_window_as_a_count_and_a_unit(self) -> 'None':

        item = Bunch(name='orders.api', alert_silence_window=7200, alert_window=600, alert_auth_failures_window=86400)
        alerts_tab.split_unit_fields(alert_type_channels, item)

        assert item.alert_silence_window == 2
        assert item.alert_silence_window_unit == 'hour'
        assert item.alert_window == 10
        assert item.alert_window_unit == 'minute'
        assert item.alert_auth_failures_window == 1
        assert item.alert_auth_failures_window_unit == 'day'

        # A window that was not stored still gets the unit its select starts on
        assert item.alert_latency_window_unit == 'minute'

# ################################################################################################################################

    def test_the_silence_window_round_trips_through_storage(self) -> 'None':

        input_dict = {}

        for name, value in (('alert_silence_window', '90'), ('alert_silence_window_unit', 'minute'),
            ('alert_traffic_expected', 'on'), ('alert_silence_slots', _slots_text)):
            input_dict[name] = alerts_tab.pre_process_alert_item(alert_type_channels, name, value)

        alerts_tab.join_unit_fields(alert_type_channels, input_dict)
        assert input_dict['alert_silence_window'] == 5400
        assert 'alert_silence_window_unit' not in input_dict

        item = Bunch(input_dict)
        alerts_tab.split_unit_fields(alert_type_channels, item)

        assert item.alert_silence_window == 90
        assert item.alert_silence_window_unit == 'minute'
        assert item.alert_traffic_expected is True
        assert item.alert_silence_slots == _slots_text

# ################################################################################################################################
# ################################################################################################################################
