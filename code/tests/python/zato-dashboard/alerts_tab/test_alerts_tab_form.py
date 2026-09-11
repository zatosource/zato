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
from zato.admin.web.forms.outgoing.ftp import CreateForm as FTPCreateForm
from zato.admin.web.forms.outgoing.sftp import CreateForm as SFTPCreateForm, EditForm as SFTPEditForm
from zato.admin.web.forms.outgoing.smb import CreateForm as SMBCreateForm
from zato.common.alerting.object_config import encode_email_connection, Email_Conn_Type_IMAP, Email_Conn_Type_SMTP, \
    get_defaults as get_storage_defaults
from zato.common.api import EMAIL

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

# ################################################################################################################################
# ################################################################################################################################

class _FakeClient:
    """ Stands in for the Dashboard's client to the server - answers the two email listings and nothing else.
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
    """ Every option value of a grouped select, groups flattened.
    """
    out:'anylist' = []

    for _ignored_group_label, options in form.fields[field_name].choices[1:]:
        for value, _ignored_label in options:
            out.append(value)

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

        # Both groups end with the entry opening the create page and neither says it is empty
        for kind in (Email_Conn_Type_SMTP, Email_Conn_Type_IMAP):
            assert encode_email_connection(kind, alerts_tab.Email_Create_New_Value) in values
            assert encode_email_connection(kind, alerts_tab.Email_None_Value) not in values

        # The listings were asked for once each, with the cluster
        services = []
        for service, request in req.zato.client.calls:
            services.append(service)
            assert request == {'cluster_id': 1}

        assert sorted(services) == ['zato.email.imap.get-list', 'zato.email.smtp.get-list']

# ################################################################################################################################

    def test_empty_group_says_so_with_a_disabled_entry(self, req:'any_') -> 'None':

        # No SMTP connections at all this time
        def invoke(service:'str', request:'anydict') -> 'anylist':
            if service == 'zato.email.smtp.get-list':
                return []
            return _FakeClient().invoke(service, request)

        req.zato.client.invoke = invoke

        form = SFTPCreateForm(req=req)
        values = _option_values(form, 'alert_email_connection')
        rendered = str(form['alert_email_connection'])

        none_value = encode_email_connection(Email_Conn_Type_SMTP, alerts_tab.Email_None_Value)
        assert none_value in values
        assert f'value="{none_value}" disabled' in rendered

# ################################################################################################################################

    def test_config_json_carries_storage_and_checkbox_names(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(_alert_type)

        assert config['storage_field_names'] == [
            'alert_is_active', 'alert_consecutive_failures', 'alert_warning_failures', 'alert_error_failures',
            'alert_window', 'alert_arrival_overdue', 'alert_test_transfers', 'alert_use_llm', 'alert_email_connection',
            'alert_window_unit', 'alert_arrival_overdue_unit',
        ]
        assert config['checkbox_field_names'] == ['alert_is_active', 'alert_test_transfers', 'alert_use_llm']

        # Every line names fields the config knows the kind or the role of
        for line in config['lines']:
            for field_name in line['fields']:
                is_known = field_name in config['field_kinds'] or field_name in (config['is_active_field'], config['email_field'])
                assert is_known, field_name

        # The create entries lead to the email pages with their create form open
        for group in config['email_groups']:
            assert group['create_url'].endswith('?cluster=1&create=1')

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

# ################################################################################################################################

    def test_join_durations_stores_seconds_and_drops_the_unit(self) -> 'None':

        input_dict = {'name': 'abc', 'alert_window': 3, 'alert_window_unit': 'hour', 'alert_arrival_overdue_unit': 'day'}
        alerts_tab.join_durations(_alert_type, input_dict)

        assert input_dict == {'name': 'abc', 'alert_window': 3 * 3600, 'alert_arrival_overdue_unit': 'day'}

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
