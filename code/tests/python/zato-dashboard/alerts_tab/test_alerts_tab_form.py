# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Bunch
from zato.common.ext.bunch import Bunch

# Zato
from zato.admin.web import alerts_tab
from zato.admin.web.alerts_tab_lines import Arrival_Overdue_Unit_Default, Line_Kind_Pick, Section_Callers, Section_Core, \
    Section_Failures, Section_Traffic, Silence_Window_Unit_Field
from zato.admin.web.alerts_tab_picks import get_live_items, Live_Type_Email_Connection, Live_Type_LLM_Connection, \
    Pick_Select_Class
from zato.admin.web.forms import INITIAL_CHOICES
from zato.admin.web.forms.http_soap import CreateForm as ChannelCreateForm, EditForm as ChannelEditForm
from zato.admin.web.forms.outgoing.ftp import CreateForm as FTPCreateForm
from zato.admin.web.forms.outgoing.sftp import CreateForm as SFTPCreateForm, EditForm as SFTPEditForm
from zato.admin.web.forms.outgoing.smb import CreateForm as SMBCreateForm
from zato.admin.web.views import http_soap as http_soap_views
from zato.admin.web.views.live_form_updates import OBJECT_TYPE_CONFIG
from zato.admin.web.views.outgoing import ftp, sftp, smb
from zato.common.alerting.object_config import alert_type_channels, alert_type_file_transfer, encode_email_connection, \
    Email_Conn_Type_IMAP, Email_Conn_Type_SMTP, get_defaults as get_storage_defaults, Unit_Field_Suffix
from zato.common.api import EMAIL, GENERIC, ZATO_NONE

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strlist
    any_ = any_
    anydict = anydict
    anylist = anylist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

_alert_type = alert_type_file_transfer

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

def _option_values(form:'any_', field_name:'str') -> 'anylist':
    """ Every option value of a select but the first.
    """
    out:'anylist' = []

    for value, _ in form.fields[field_name].choices[1:]:
        out.append(value)

    return out

# ################################################################################################################################

def _option_labels(form:'any_', field_name:'str') -> 'anylist':
    """ Every option label of a select but the first.
    """
    out:'anylist' = []

    for _, label in form.fields[field_name].choices[1:]:
        out.append(label)

    return out

# ################################################################################################################################

def _pick_rows(context:'anydict') -> 'anydict':
    """ The pick lines of a rendered tab context, by name.
    """
    out:'anydict' = {}

    for section in context['sections']:
        for line in section['lines']:
            if line['kind'] == Line_Kind_Pick:
                out[line['name']] = line

    return out

# ################################################################################################################################

def _lines_by_name(config:'anydict') -> 'anydict':
    """ The lines of a tab config, by name.
    """
    out:'anydict' = {}

    for line in config['lines']:
        out[line['name']] = line

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestAlertsTabForm:

    def test_create_form_has_every_tab_field_with_seeded_defaults(self, req:'any_') -> 'None':

        form = SFTPCreateForm(req=req)
        defaults = alerts_tab.get_defaults(_alert_type)

        for storage_field_name in alerts_tab.get_storage_field_names(_alert_type):
            assert storage_field_name in form.fields, storage_field_name

        assert form.fields['alert_is_active'].initial is True
        assert form.fields['alert_consecutive_failures'].initial == defaults['consecutive_failures']
        assert form.fields['alert_warning_failures'].initial == 10
        assert form.fields['alert_error_failures'].initial == 20
        assert form.fields['alert_test_transfers'].initial is False
        assert form.fields['alert_use_llm'].initial is True

        assert form.fields['alert_window'].initial == 1
        assert form.fields['alert_window_unit'].initial == 'day'

        assert form.fields['alert_arrival_overdue_unit'].initial == Arrival_Overdue_Unit_Default

# ################################################################################################################################

    def test_rest_channel_form_carries_the_channel_tab(self, req:'any_') -> 'None':

        form = ChannelCreateForm(req=req, alert_type=alert_type_channels)
        defaults = alerts_tab.get_defaults(alert_type_channels)

        for storage_field_name in alerts_tab.get_storage_field_names(alert_type_channels):
            assert storage_field_name in form.fields, storage_field_name

        assert form.fields['alert_is_active'].initial is True
        assert form.fields['alert_consecutive_failures'].initial == defaults['consecutive_failures']
        assert form.fields['alert_error_rate'].initial == 10
        assert form.fields['alert_server_errors'].initial == 5
        assert form.fields['alert_max_latency'].initial == 5000
        assert form.fields['alert_auth_failures'].initial == 10
        assert form.fields['alert_client_errors'].initial == 50
        assert form.fields['alert_use_llm'].initial is True
        assert form.fields['alert_traffic_expected'].initial is False

        assert form.fields['alert_window'].initial == 5
        assert form.fields['alert_window_unit'].initial == 'minute'
        assert form.fields['alert_silence_window'].initial == 1
        assert form.fields['alert_silence_window_unit'].initial == 'hour'

        for name in ('server_errors', 'latency', 'auth_failures', 'client_errors'):
            assert form.fields[f'alert_{name}_window'].initial == 5, name
            assert form.fields[f'alert_{name}_window_unit'].initial == 'minute', name

        assert form.fields['alert_silence_slots'].initial == '[]'
        assert 'type="hidden"' in str(form['alert_silence_slots'])

        plain_form = ChannelCreateForm(req=req)
        assert 'alert_is_active' not in plain_form.fields

# ################################################################################################################################

    def test_rest_channel_tab_context_and_config(self, req:'any_') -> 'None':

        form = ChannelCreateForm(req=req, alert_type=alert_type_channels)
        context = alerts_tab.get_alerts_tab_context(form, alert_type_channels)
        config = alerts_tab.get_alerts_tab_config(alert_type_channels)

        section_labels:'strlist' = []

        for section in context['sections']:
            section_labels.append(section['label'])

        assert section_labels == [Section_Core, Section_Failures, Section_Callers, Section_Traffic]

        line_names:'strlist' = []

        for line in config['lines']:
            line_names.append(line['name'])

        assert line_names == ['active', 'use_llm', 'llm', 'email', 'failures_in_a_row', 'error_rate', 'server_errors',
            'rejected_callers', 'bad_requests', 'slow_responses', 'silence']

        silence_line = config['lines'][-1]

        assert silence_line['label'] == 'No requests received'
        assert silence_line['fields'] == ['traffic_expected', 'silence_window', 'silence_slots']
        assert silence_line['off_field'] == 'traffic_expected'
        assert silence_line['summary_off'] == 'Alerts off'
        assert silence_line['unit_field'] == Silence_Window_Unit_Field
        assert silence_line['slots_field'] == 'silence_slots'
        assert '{silence_slots#' in silence_line['summary']

        lines_by_name = _lines_by_name(config)

        windows = {
            'error_rate': ('error_rate', 'window'),
            'server_errors': ('server_errors', 'server_errors_window'),
            'rejected_callers': ('auth_failures', 'auth_failures_window'),
            'bad_requests': ('client_errors', 'client_errors_window'),
            'slow_responses': ('max_latency', 'latency_window'),
        }

        for line_name, (number, window) in windows.items():
            line = lines_by_name[line_name]
            assert line['rows'] == [[number], [window]], line_name
            assert line['unit_field'] == window + '_unit', line_name
            assert f'{{{window}_unit@{window}}}' in line['summary'], line_name
            assert config['field_labels'][window] == 'In the last', line_name

        for line in _pick_rows(context).values():
            rendered = str(line['field'])
            assert f'class="{Pick_Select_Class}"' in rendered
            assert f'<option value="{INITIAL_CHOICES[0]}" selected>{INITIAL_CHOICES[1]}</option>' in rendered
            assert line['has_options'] is True

        assert 'alert_silence_window_unit' in config['storage_field_names']
        assert 'alert_window_unit' in config['storage_field_names']
        assert 'alert_latency_window_unit' in config['storage_field_names']
        assert 'alert_silence_slots' in config['storage_field_names']

        assert config['duration_units'] == [
            {'name': 'minute', 'seconds': 60},
            {'name': 'hour', 'seconds': 3600},
            {'name': 'day', 'seconds': 86400},
        ]
        assert config['slots_kind'] == 'time_slots'
        assert config['duration_kind'] == 'duration'

# ################################################################################################################################

    def test_ftp_and_smb_forms_carry_the_tab_too(self, req:'any_') -> 'None':

        for form_class in (FTPCreateForm, SMBCreateForm):
            form = form_class(req=req)
            for storage_field_name in alerts_tab.get_storage_field_names(_alert_type):
                assert storage_field_name in form.fields, (form_class, storage_field_name)

# ################################################################################################################################

    def test_edit_form_fields_are_prefixed(self, req:'any_') -> 'None':

        form = SFTPEditForm(prefix='edit', req=req)
        rendered = str(form['alert_window'])

        assert 'name="edit-alert_window"' in rendered
        assert 'id="id_edit-alert_window"' in rendered

# ################################################################################################################################

    def test_email_select_lists_real_connections(self, req:'any_') -> 'None':

        form = SFTPCreateForm(req=req)
        values = _option_values(form, 'alert_email_connection')

        for name in _smtp_names:
            assert encode_email_connection(Email_Conn_Type_SMTP, name) in values

        assert encode_email_connection(Email_Conn_Type_IMAP, _m365_name) in values
        assert encode_email_connection(Email_Conn_Type_IMAP, _generic_imap_name) not in values

        labels = _option_labels(form, 'alert_email_connection')
        assert labels == ['SMTP/ops.smtp', 'SMTP/billing.smtp', 'Microsoft 365/ops.m365']
        assert len(values) == 3

        services:'strlist' = []

        for service, request in req.zato.client.calls:
            services.append(service)
            if service != 'zato.generic.connection.get-list':
                assert request == {'cluster_id': 1}

        assert sorted(services) == ['zato.email.imap.get-list', 'zato.email.smtp.get-list', 'zato.generic.connection.get-list']

# ################################################################################################################################

    def test_llm_select_lists_the_llm_connections_by_plain_name(self, req:'any_') -> 'None':

        form = SFTPCreateForm(req=req)
        values = _option_values(form, 'alert_llm_connection')

        assert values == _llm_names
        assert _option_labels(form, 'alert_llm_connection') == _llm_names

        for service, request in req.zato.client.calls:
            if service == 'zato.generic.connection.get-list':
                assert request == {'cluster_id': 1, 'type_': GENERIC.CONNECTION.TYPE.OUTCONN_LLM, 'paginate': False}

# ################################################################################################################################

    def test_no_llm_connections_swaps_the_select_for_the_create_sentence(self, req:'any_') -> 'None':

        def invoke(service:'str', request:'anydict') -> 'any_':
            if service == 'zato.generic.connection.get-list':
                out = []
            else:
                out = _FakeClient().invoke(service, request)
            return out

        req.zato.client.invoke = invoke

        form = SFTPCreateForm(req=req)
        context = alerts_tab.get_alerts_tab_context(form, _alert_type)
        picks = _pick_rows(context)

        assert _option_values(form, 'alert_llm_connection') == []
        assert picks['llm']['has_options'] is False
        assert picks['llm']['empty_html'] == \
            'No LLM connections found. Click to <a href="/zato/outgoing/llm/?cluster=1&amp;create=1" target="_blank">create one</a>.'

        assert picks['email']['has_options'] is True

# ################################################################################################################################

    def test_no_email_connections_swaps_the_select_for_the_two_create_links(self, req:'any_') -> 'None':

        def invoke(service:'str', request:'anydict') -> 'any_':
            if service in ('zato.email.smtp.get-list', 'zato.email.imap.get-list'):
                out = []
            else:
                out = _FakeClient().invoke(service, request)
            return out

        req.zato.client.invoke = invoke

        form = SFTPCreateForm(req=req)
        context = alerts_tab.get_alerts_tab_context(form, _alert_type)
        picks = _pick_rows(context)

        assert _option_values(form, 'alert_email_connection') == []
        assert picks['email']['has_options'] is False
        assert picks['email']['empty_html'] == 'No email connections found. Click to create an ' + \
            '<a href="/zato/email/smtp/?cluster=1&amp;create=1" target="_blank">SMTP</a> or a ' + \
            '<a href="/zato/email/imap/?cluster=1&amp;create=1" target="_blank">Microsoft 365</a> one.'

# ################################################################################################################################

    def test_one_empty_kind_still_lists_the_other(self, req:'any_') -> 'None':

        def invoke(service:'str', request:'anydict') -> 'any_':
            if service == 'zato.email.smtp.get-list':
                out = []
            else:
                out = _FakeClient().invoke(service, request)
            return out

        req.zato.client.invoke = invoke

        form = SFTPCreateForm(req=req)
        m365_value = encode_email_connection(Email_Conn_Type_IMAP, _m365_name)

        assert _option_values(form, 'alert_email_connection') == [m365_value]
        assert _option_labels(form, 'alert_email_connection') == ['Microsoft 365/ops.m365']

# ################################################################################################################################

    def test_live_items_read_the_way_the_selects_do(self, req:'any_') -> 'None':

        form = SFTPCreateForm(req=req)

        for live_type, field_name in (
            (Live_Type_Email_Connection, 'alert_email_connection'),
            (Live_Type_LLM_Connection, 'alert_llm_connection'),
        ):
            expected:'anylist' = []

            for value, label in form.fields[field_name].choices[1:]:
                expected.append({'id': value, 'name': label})

            assert get_live_items(req, live_type) == expected, live_type

        for live_type in (Live_Type_Email_Connection, Live_Type_LLM_Connection):
            config = OBJECT_TYPE_CONFIG[live_type]
            expected = get_live_items(req, live_type)

            assert config['id_field'] == 'id'
            assert config['label_format'] == '{name}'
            assert config['fetch_func'](req) == expected

# ################################################################################################################################

    def test_config_json_carries_storage_and_checkbox_names(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(_alert_type)

        assert config['storage_field_names'] == [
            'alert_is_active', 'alert_consecutive_failures', 'alert_warning_failures', 'alert_error_failures',
            'alert_window', 'alert_arrival_overdue', 'alert_test_transfers', 'alert_use_llm', 'alert_email_connection',
            'alert_llm_connection', 'alert_window_unit', 'alert_arrival_overdue_unit',
        ]
        assert config['checkbox_field_names'] == ['alert_is_active', 'alert_test_transfers', 'alert_use_llm']
        assert config['pick_fields'] == ['llm_connection', 'email_connection']

        known_names = list(config['field_kinds'])
        known_names.append(config['is_active_field'])
        known_names.extend(config['pick_fields'])

        for line in config['lines']:
            for field_name in line['fields']:
                assert field_name in known_names, field_name

        lines_by_name = _lines_by_name(config)

        email_line = lines_by_name['email']
        llm_line = lines_by_name['llm']

        assert email_line['kind'] == Line_Kind_Pick
        assert email_line['field'] == 'email_connection'
        assert email_line['live_type'] == Live_Type_Email_Connection
        assert 'depends_on' not in email_line

        assert llm_line['kind'] == Line_Kind_Pick
        assert llm_line['field'] == 'llm_connection'
        assert llm_line['live_type'] == Live_Type_LLM_Connection
        assert llm_line['depends_on'] == 'use_llm'

        line_names = list(lines_by_name)
        assert line_names.index('llm') == line_names.index('use_llm') + 1

# ################################################################################################################################

    def test_storage_names_match_the_views(self) -> 'None':

        storage_names = alerts_tab.get_storage_field_names(_alert_type)
        checkbox_names = alerts_tab.get_checkbox_field_names(_alert_type)

        for module in (sftp, ftp, smb):
            for name in storage_names:
                assert name in module._fields_optional, (module.__name__, name)

        for module in (sftp, ftp):
            for name in checkbox_names:
                assert name in module._fields_checkbox, (module.__name__, name)

# ################################################################################################################################
# ################################################################################################################################

class TestAlertsTabStorage:

    def test_pre_process_alert_item_types_the_values(self) -> 'None':

        assert alerts_tab.pre_process_alert_item(_alert_type, 'alert_is_active', 'on') is True
        assert alerts_tab.pre_process_alert_item(_alert_type, 'alert_is_active', None) is False
        assert alerts_tab.pre_process_alert_item(_alert_type, 'alert_test_transfers', '') is False
        assert alerts_tab.pre_process_alert_item(_alert_type, 'alert_use_llm', 'on') is True

        assert alerts_tab.pre_process_alert_item(_alert_type, 'alert_consecutive_failures', '5') == 5
        assert alerts_tab.pre_process_alert_item(_alert_type, 'alert_window', '3') == 3

        assert alerts_tab.pre_process_alert_item(_alert_type, 'alert_window_unit', 'hour') == 'hour'
        assert alerts_tab.pre_process_alert_item(_alert_type, 'alert_email_connection', 'smtp:ops') == 'smtp:ops'

        slots_text = '[{"time_from": "22:00", "time_to": "06:00", "is_on": false, "silence_seconds": 3600}]'
        assert alerts_tab.pre_process_alert_item(alert_type_channels, 'alert_silence_slots', slots_text) == slots_text
        assert alerts_tab.pre_process_alert_item(alert_type_channels, 'alert_silence_window', '30') == 30
        assert alerts_tab.pre_process_alert_item(alert_type_channels, 'alert_latency_window', '2') == 2

# ################################################################################################################################

    def test_join_durations_stores_seconds_and_drops_the_unit(self) -> 'None':

        input_dict = {'name': 'abc', 'alert_window': 3, 'alert_window_unit': 'hour', 'alert_arrival_overdue_unit': 'day'}
        alerts_tab.join_durations(_alert_type, input_dict)

        assert input_dict == {'name': 'abc', 'alert_window': 3 * 3600, 'alert_arrival_overdue_unit': 'day'}

        input_dict = {
            'alert_window': 5, 'alert_window_unit': 'minute',
            'alert_server_errors_window': 1, 'alert_server_errors_window_unit': 'hour',
            'alert_latency_window': 2, 'alert_latency_window_unit': 'day',
            'alert_auth_failures_window': 15, 'alert_auth_failures_window_unit': 'minute',
            'alert_client_errors_window': 3, 'alert_client_errors_window_unit': 'hour',
            'alert_silence_window': 1, 'alert_silence_window_unit': 'hour',
            'alert_silence_slots': '[]',
        }
        alerts_tab.join_durations(alert_type_channels, input_dict)

        assert input_dict == {
            'alert_window': 300,
            'alert_server_errors_window': 3600,
            'alert_latency_window': 2 * 86400,
            'alert_auth_failures_window': 900,
            'alert_client_errors_window': 3 * 3600,
            'alert_silence_window': 3600,
            'alert_silence_slots': '[]',
        }

# ################################################################################################################################

    def test_split_durations_reads_seconds_back_as_count_and_unit(self) -> 'None':

        item = Bunch(name='abc', alert_window=2 * 86400)
        alerts_tab.split_durations(_alert_type, item)

        assert item.alert_window == 2
        assert item.alert_window_unit == 'day'
        assert item.alert_arrival_overdue_unit == Arrival_Overdue_Unit_Default

# ################################################################################################################################

    def test_round_trip_through_storage(self) -> 'None':

        input_dict = {}

        for name, value in (('alert_window', '90'), ('alert_window_unit', 'minute'), ('alert_is_active', 'on')):
            input_dict[name] = alerts_tab.pre_process_alert_item(_alert_type, name, value)

        alerts_tab.join_durations(_alert_type, input_dict)
        assert input_dict['alert_window'] == 5400

        item = Bunch(input_dict)
        alerts_tab.split_durations(_alert_type, item)

        assert item.alert_window == 90
        assert item.alert_window_unit == 'minute'
        assert item.alert_is_active is True

# ################################################################################################################################

    def test_tab_defaults_agree_with_the_shared_ones(self) -> 'None':

        tab_defaults = alerts_tab.get_defaults(_alert_type)
        shared_defaults = get_storage_defaults(_alert_type)

        for name, value in shared_defaults.items():
            if name == 'window':
                assert tab_defaults['window'] * 86400 == value
                continue
            assert tab_defaults[name] == value, name

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
        message = http_soap_views._get_edit_create_message(params)

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

        message = http_soap_views._get_edit_create_message(params, prefix='edit-')

        assert message['id'] == '17'
        for name, value in _expected_channel_settings.items():
            assert message[name] == value, name

# ################################################################################################################################

    def test_a_soap_channel_and_the_outgoing_connections_carry_no_alert_settings(self) -> 'None':

        for connection, transport in (('channel', 'soap'), ('outgoing', 'plain_http'), ('outgoing', 'soap')):
            params = _channel_params(connection, transport)
            message = http_soap_views._get_edit_create_message(params)

            for name in alerts_tab.get_storage_field_names(alert_type_channels):
                assert name not in message, (connection, transport, name)

# ################################################################################################################################

    def test_a_listed_channel_shows_each_window_as_a_count_and_a_unit(self) -> 'None':

        item = Bunch(name='orders.api', alert_silence_window=7200, alert_window=600, alert_auth_failures_window=86400)
        alerts_tab.split_durations(alert_type_channels, item)

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

        alerts_tab.join_durations(alert_type_channels, input_dict)
        assert input_dict['alert_silence_window'] == 5400
        assert 'alert_silence_window_unit' not in input_dict

        item = Bunch(input_dict)
        alerts_tab.split_durations(alert_type_channels, item)

        assert item.alert_silence_window == 90
        assert item.alert_silence_window_unit == 'minute'
        assert item.alert_traffic_expected is True
        assert item.alert_silence_slots == _slots_text

# ################################################################################################################################
# ################################################################################################################################
