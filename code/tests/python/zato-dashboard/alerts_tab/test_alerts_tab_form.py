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
from zato.admin.web.alerts_tab_picks import get_live_items
from zato.admin.web.forms import INITIAL_CHOICES
from zato.admin.web.forms.http_soap import CreateForm as ChannelCreateForm
from zato.admin.web.forms.outgoing.ftp import CreateForm as FTPCreateForm
from zato.admin.web.forms.outgoing.sftp import CreateForm as SFTPCreateForm, EditForm as SFTPEditForm
from zato.admin.web.forms.outgoing.smb import CreateForm as SMBCreateForm
from zato.common.alerting.object_config import alert_type_channels, encode_email_connection, Email_Conn_Type_IMAP, \
    Email_Conn_Type_SMTP, get_defaults as get_storage_defaults
from zato.common.api import EMAIL, GENERIC

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist
    any_ = any_
    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

_alert_type = alerts_tab.alert_type_file_transfer

# What the backend services list - two SMTP connections, one Microsoft 365 IMAP one and one generic IMAP one
_smtp_names = ['ops.smtp', 'billing.smtp']
_m365_name = 'ops.m365'
_generic_imap_name = 'legacy.imap'
_llm_names = ['ops.llm', 'ops.llm.backup']

# ################################################################################################################################
# ################################################################################################################################

class _FakeClient:
    """ Stands in for the Dashboard's client to the server - answers the two email listings
    and the LLM connection listing and nothing else.
    """
    def __init__(self) -> 'None':
        self.calls:'anylist' = []

    def invoke(self, service:'str', request:'anydict') -> 'anylist':
        self.calls.append((service, request))

        if service == 'zato.email.smtp.get-list':
            out = []
            for name in _smtp_names:
                out.append(Bunch(name=name))
            return out

        if service == 'zato.email.imap.get-list':
            out = [
                Bunch(name=_m365_name, server_type=EMAIL.IMAP.ServerType.Microsoft365),
                Bunch(name=_generic_imap_name, server_type=EMAIL.IMAP.ServerType.Generic),
            ]
            return out

        if service == 'zato.generic.connection.get-list':
            assert request['type_'] == GENERIC.CONNECTION.TYPE.OUTCONN_LLM
            out = []
            for name in _llm_names:
                out.append(Bunch(name=name))
            return out

        # The REST channel form lists the services a channel may invoke, off a response object
        if service == 'zato.service.get-list':
            out = Bunch(data=[Bunch(name='demo.ping', id=1)])
            return out

        raise Exception(f'Unexpected service `{service}`')

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
    """ Every option value of a select but the first, the one meaning no connection.
    """
    out:'anylist' = []

    for value, _ignored_label in form.fields[field_name].choices[1:]:
        out.append(value)

    return out

# ################################################################################################################################

def _option_labels(form:'any_', field_name:'str') -> 'anylist':
    """ Every option label of a select but the first.
    """
    out:'anylist' = []

    for _ignored_value, label in form.fields[field_name].choices[1:]:
        out.append(label)

    return out

# ################################################################################################################################

def _pick_rows(context:'anydict') -> 'anydict':
    """ The pick lines of a rendered tab context, by name.
    """
    out:'anydict' = {}

    for section in context['sections']:
        for line in section['lines']:
            if line['kind'] == alerts_tab.Line_Kind_Pick:
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

        # The seeded window of a day reads as 1 day, not 86400 seconds
        assert form.fields['alert_window'].initial == 1
        assert form.fields['alert_window_unit'].initial == 'day'

        # The arrival unit is the tab's own and starts at an hour
        assert form.fields['alert_arrival_overdue_unit'].initial == alerts_tab.Arrival_Overdue_Unit_Default

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

        # A channel does not expect traffic until it says so - the silence rule ships inactive
        assert form.fields['alert_traffic_expected'].initial is False

        # The seeded window of five minutes and silence of an hour read as counts with a unit
        assert form.fields['alert_window'].initial == 5
        assert form.fields['alert_window_unit'].initial == 'minute'
        assert form.fields['alert_silence_window'].initial == 1
        assert form.fields['alert_silence_window_unit'].initial == 'hour'

        # Each measure has a window of its own, each seeded at five minutes
        for name in ('server_errors', 'latency', 'auth_failures', 'client_errors'):
            assert form.fields[f'alert_{name}_window'].initial == 5, name
            assert form.fields[f'alert_{name}_window_unit'].initial == 'minute', name

        # The time slots start empty, as a JSON list in a hidden field
        assert form.fields['alert_silence_slots'].initial == '[]'
        assert 'type="hidden"' in str(form['alert_silence_slots'])

        # A form without an alert type has no tab
        plain_form = ChannelCreateForm(req=req)
        assert 'alert_is_active' not in plain_form.fields

# ################################################################################################################################

    def test_rest_channel_tab_context_and_config(self, req:'any_') -> 'None':

        form = ChannelCreateForm(req=req, alert_type=alert_type_channels)
        context = alerts_tab.get_alerts_tab_context(form, alert_type_channels)
        config = alerts_tab.get_alerts_tab_config(alert_type_channels)

        section_labels = []
        for section in context['sections']:
            section_labels.append(section['label'])
        assert section_labels == [alerts_tab.Section_Core, alerts_tab.Section_Failures, alerts_tab.Section_Callers,
            alerts_tab.Section_Traffic]

        line_names = []
        for line in config['lines']:
            line_names.append(line['name'])
        assert line_names == ['active', 'use_llm', 'llm', 'email', 'failures_in_a_row', 'error_rate', 'server_errors',
            'rejected_callers', 'bad_requests', 'slow_responses', 'silence']

        # The silence line carries its own switch, reads as Alerts off while it is off, has a unit of its
        # own and the time slots its popover edits, and its summary says how many slots there are
        silence_line = config['lines'][-1]
        assert silence_line['label'] == 'No requests received'
        assert silence_line['fields'] == ['traffic_expected', 'silence_window', 'silence_slots']
        assert silence_line['off_field'] == 'traffic_expected'
        assert silence_line['summary_off'] == 'Alerts off'
        assert silence_line['unit_field'] == alerts_tab.Silence_Window_Unit_Field
        assert silence_line['slots_field'] == 'silence_slots'
        assert '{silence_slots#' in silence_line['summary']

        # Every threshold line has its number on one row and its window on the next, with a unit of its own
        lines_by_name = {}
        for line in config['lines']:
            lines_by_name[line['name']] = line

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

        # The connection selects are the lines' own answers, starting with the dashboard's own first option
        for line in _pick_rows(context).values():
            rendered = str(line['field'])
            assert f'class="{alerts_tab.Pick_Select_Class}"' in rendered
            assert f'<option value="{INITIAL_CHOICES[0]}" selected>{INITIAL_CHOICES[1]}</option>' in rendered
            assert line['has_options'] is True

        # Every unit select the lines name is on the form
        assert 'alert_silence_window_unit' in config['storage_field_names']
        assert 'alert_window_unit' in config['storage_field_names']
        assert 'alert_latency_window_unit' in config['storage_field_names']
        assert 'alert_silence_slots' in config['storage_field_names']

        # What the popovers need to turn seconds into a count and a unit
        assert config['duration_units'] == [('minute', 60), ('hour', 3600), ('day', 86400)]
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

        # Only the Microsoft 365 IMAP connections can send, the generic one is not offered
        assert encode_email_connection(Email_Conn_Type_IMAP, _m365_name) in values
        assert encode_email_connection(Email_Conn_Type_IMAP, _generic_imap_name) not in values

        # The options are flat, each labelled with its kind before its name, and nothing but connections is listed
        labels = _option_labels(form, 'alert_email_connection')
        assert labels == ['SMTP/ops.smtp', 'SMTP/billing.smtp', 'Microsoft 365/ops.m365']
        assert len(values) == 3

        # The email listings were asked for once each, with the cluster
        services = []
        for service, request in req.zato.client.calls:
            services.append(service)
            if service != 'zato.generic.connection.get-list':
                assert request == {'cluster_id': 1}

        assert sorted(services) == ['zato.email.imap.get-list', 'zato.email.smtp.get-list', 'zato.generic.connection.get-list']

# ################################################################################################################################

    def test_llm_select_lists_the_llm_connections_by_plain_name(self, req:'any_') -> 'None':

        form = SFTPCreateForm(req=req)
        values = _option_values(form, 'alert_llm_connection')

        # An LLM value is the connection's name alone, there is no kind in front of it, and the label is the same
        assert values == _llm_names
        assert _option_labels(form, 'alert_llm_connection') == _llm_names

        # The listing was asked for the LLM connections only
        for service, request in req.zato.client.calls:
            if service == 'zato.generic.connection.get-list':
                assert request == {'cluster_id': 1, 'type_': GENERIC.CONNECTION.TYPE.OUTCONN_LLM, 'paginate': False}

# ################################################################################################################################

    def test_no_llm_connections_swaps_the_select_for_the_create_sentence(self, req:'any_') -> 'None':

        def invoke(service:'str', request:'anydict') -> 'anylist':
            if service == 'zato.generic.connection.get-list':
                return []
            return _FakeClient().invoke(service, request)

        req.zato.client.invoke = invoke

        form = SFTPCreateForm(req=req)
        context = alerts_tab.get_alerts_tab_context(form, _alert_type)
        picks = _pick_rows(context)

        # The select holds the first option alone, so the line shows the sentence with the one create link instead
        assert _option_values(form, 'alert_llm_connection') == []
        assert picks['llm']['has_options'] is False
        assert picks['llm']['empty_html'] == \
            'No LLM connections found. Click to <a href="/zato/outgoing/llm/?cluster=1&amp;create=1" target="_blank">create one</a>.'

        # The email line still has its connections
        assert picks['email']['has_options'] is True

# ################################################################################################################################

    def test_no_email_connections_swaps_the_select_for_the_two_create_links(self, req:'any_') -> 'None':

        def invoke(service:'str', request:'anydict') -> 'anylist':
            if service in ('zato.email.smtp.get-list', 'zato.email.imap.get-list'):
                return []
            return _FakeClient().invoke(service, request)

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

        # No SMTP connections at all this time
        def invoke(service:'str', request:'anydict') -> 'anylist':
            if service == 'zato.email.smtp.get-list':
                return []
            return _FakeClient().invoke(service, request)

        req.zato.client.invoke = invoke

        form = SFTPCreateForm(req=req)
        assert _option_values(form, 'alert_email_connection') == [encode_email_connection(Email_Conn_Type_IMAP, _m365_name)]
        assert _option_labels(form, 'alert_email_connection') == ['Microsoft 365/ops.m365']

# ################################################################################################################################

    def test_live_items_read_the_way_the_selects_do(self, req:'any_') -> 'None':

        # The poll lists the very options the form builds - the id being the value and the name the label
        form = SFTPCreateForm(req=req)

        for live_type, field_name in (
            (alerts_tab.Live_Type_Email_Connection, 'alert_email_connection'),
            (alerts_tab.Live_Type_LLM_Connection, 'alert_llm_connection'),
        ):
            expected = []
            for value, label in form.fields[field_name].choices[1:]:
                expected.append({'id': value, 'name': label})

            assert get_live_items(req, live_type) == expected, live_type

        # The dispatch table of the live form updates view knows both types
        from zato.admin.web.views.live_form_updates import OBJECT_TYPE_CONFIG

        for live_type in (alerts_tab.Live_Type_Email_Connection, alerts_tab.Live_Type_LLM_Connection):
            config = OBJECT_TYPE_CONFIG[live_type]
            assert config['id_field'] == 'id'
            assert config['label_format'] == '{name}'
            assert config['fetch_func'](req) == get_live_items(req, live_type)

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
        assert 'pick_kind_separator' not in config
        assert 'pick_create_new_value' not in config

        # Every line names fields the config knows the kind or the role of
        for line in config['lines']:
            for field_name in line['fields']:
                is_known = field_name in config['field_kinds'] or field_name == config['is_active_field'] or field_name in config['pick_fields']
                assert is_known, field_name

        # The pick lines name their field and the type the live form updates poll knows their connections as
        lines_by_name = {}
        for line in config['lines']:
            lines_by_name[line['name']] = line

        email_line = lines_by_name['email']
        llm_line = lines_by_name['llm']

        assert email_line['kind'] == alerts_tab.Line_Kind_Pick
        assert email_line['field'] == 'email_connection'
        assert email_line['live_type'] == alerts_tab.Live_Type_Email_Connection
        assert 'depends_on' not in email_line
        assert 'groups' not in email_line

        assert llm_line['kind'] == alerts_tab.Line_Kind_Pick
        assert llm_line['field'] == 'llm_connection'
        assert llm_line['live_type'] == alerts_tab.Live_Type_LLM_Connection
        assert llm_line['depends_on'] == 'use_llm'

        # The LLM line comes right after the Use LLM switch it depends on
        line_names = list(lines_by_name)
        assert line_names.index('llm') == line_names.index('use_llm') + 1

# ################################################################################################################################

    def test_storage_names_match_the_views(self) -> 'None':

        from zato.admin.web.views.outgoing import ftp, sftp, smb

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

        # The time slots of a channel travel as the JSON text they are
        slots_text = '[{"time_from": "22:00", "time_to": "06:00", "is_on": false, "silence_seconds": 3600}]'
        assert alerts_tab.pre_process_alert_item(alert_type_channels, 'alert_silence_slots', slots_text) == slots_text
        assert alerts_tab.pre_process_alert_item(alert_type_channels, 'alert_silence_window', '30') == 30
        assert alerts_tab.pre_process_alert_item(alert_type_channels, 'alert_latency_window', '2') == 2

# ################################################################################################################################

    def test_join_durations_stores_seconds_and_drops_the_unit(self) -> 'None':

        input_dict = {'name': 'abc', 'alert_window': 3, 'alert_window_unit': 'hour', 'alert_arrival_overdue_unit': 'day'}
        alerts_tab.join_durations(_alert_type, input_dict)

        assert input_dict == {'name': 'abc', 'alert_window': 3 * 3600, 'alert_arrival_overdue_unit': 'day'}

        # Every window of a channel is joined on its own
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

        # A unit the object does not carry starts at its default
        assert item.alert_arrival_overdue_unit == alerts_tab.Arrival_Overdue_Unit_Default

# ################################################################################################################################

    def test_round_trip_through_storage(self) -> 'None':

        # What the form sends, as the view receives it, ..
        input_dict = {}
        for name, value in (('alert_window', '90'), ('alert_window_unit', 'minute'), ('alert_is_active', 'on')):
            input_dict[name] = alerts_tab.pre_process_alert_item(_alert_type, name, value)

        alerts_tab.join_durations(_alert_type, input_dict)
        assert input_dict['alert_window'] == 5400

        # .. is what the listing turns back into what the edit form shows.
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
