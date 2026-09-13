# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Alerts tab of an outgoing REST connection - its sections in order with the health check above the failures and the traffic,
# the status codes line carrying its text field and summarising the codes, the connection failures line, every
# storage field of the type on the form, and the storage names the config hands the tab's JavaScript.

# pytest
import pytest

# Zato
from zato.common.ext.bunch import Bunch

# Zato - Dashboard
from zato.admin.web import alerts_tab
from zato.admin.web.alerts_tab_lines import Health_Check_Run_Every_Field, Health_Check_Run_Unit_Field, \
    Health_Check_Summary_Empty, Line_Kind_Popover, Section_Core, Section_Failures, Section_Health, Section_Traffic, \
    Status_Codes_Field, Status_Codes_Placeholder, Status_Codes_Window_Unit_Field, Unit_Field_Suffix
from zato.admin.web.forms.http_soap import CreateForm as ChannelCreateForm, EditForm as ChannelEditForm
from zato.common.alerting.object_config import alert_type_rest, get_defaults, get_field_names, storage_name

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

class _FakeClient:
    """ Answers the listings the tab's picks ask for with nothing, so the tab renders its create sentences.
    """
    def invoke(self, service:'str', request:'anydict') -> 'any_':

        if service == 'zato.service.get-list':
            out = Bunch(data=[])
        else:
            out = []

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

def _lines_by_name(config:'anydict') -> 'anydict':
    """ The lines of a tab config, by name.
    """
    out:'anydict' = {}

    for line in config['lines']:
        out[line['name']] = line

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingRestTab:

    def test_the_sections_run_core_health_check_failures_traffic(self, req:'any_') -> 'None':

        form = ChannelCreateForm(req=req, alert_type=alert_type_rest)
        context = alerts_tab.get_alerts_tab_context(form, alert_type_rest)

        section_labels:'strlist' = []

        for section in context['sections']:
            section_labels.append(section['label'])

        assert section_labels == [Section_Core, Section_Health, Section_Failures, Section_Traffic]

# ################################################################################################################################

    def test_the_lines_run_in_the_order_of_the_tab(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_rest)

        line_names:'strlist' = []

        for line in config['lines']:
            line_names.append(line['name'])

        assert line_names == ['active', 'use_llm', 'llm', 'email', 'health_check', 'failures_in_a_row', 'error_rate',
            'status_codes', 'connection_failures', 'slow_responses']

# ################################################################################################################################

    def test_the_status_codes_line_carries_its_text_and_summarises_the_codes(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_rest)
        line = _lines_by_name(config)['status_codes']

        assert line['kind'] == Line_Kind_Popover
        assert line['label'] == 'Status codes'
        assert line['fields'] == [Status_Codes_Field, 'status_code_threshold', 'status_codes_window']
        assert line['rows'] == [[Status_Codes_Field], ['status_code_threshold'], ['status_codes_window']]
        assert line['unit_field'] == Status_Codes_Window_Unit_Field

        # The codes are typed as text with the placeholder showing the shape ..
        assert line['text_fields'] == {Status_Codes_Field: Status_Codes_Placeholder}
        assert config['field_kinds'][Status_Codes_Field] == 'text'

        # .. and the summary names the count, the codes text and the window with its unit.
        assert '{status_code_threshold|response|responses}' in line['summary']
        assert f'{{{Status_Codes_Field}}}' in line['summary']
        assert f'{{{Status_Codes_Window_Unit_Field}@status_codes_window}}' in line['summary']

        assert config['field_labels']['status_codes_window'] == 'In the last'

# ################################################################################################################################

    def test_the_connection_failures_line_counts_timeouts_and_failures(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_rest)
        line = _lines_by_name(config)['connection_failures']

        assert line['kind'] == Line_Kind_Popover
        assert line['fields'] == ['connection_failures', 'connection_failures_window']
        assert line['rows'] == [['connection_failures'], ['connection_failures_window']]
        assert '{connection_failures|timeout or connection failure|timeouts or connection failures}' in line['summary']

# ################################################################################################################################

    def test_the_health_check_line_edits_the_pages_own_run_every(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_rest)
        line = _lines_by_name(config)['health_check']

        assert line['fields'] == [Health_Check_Run_Every_Field]
        assert line['unit_field'] == Health_Check_Run_Unit_Field
        assert line['summary_empty'] == Health_Check_Summary_Empty
        assert f'{{{Health_Check_Run_Unit_Field}@{Health_Check_Run_Every_Field}}}' in line['summary']

        # A page field is the form's own, so it is a count on the tab and never among the storage names
        assert Health_Check_Run_Every_Field in config['page_fields']
        assert config['field_kinds'][Health_Check_Run_Every_Field] == 'number'
        assert config['field_labels'][Health_Check_Run_Every_Field] == 'Ping every'
        assert storage_name(Health_Check_Run_Every_Field) not in config['storage_field_names']

# ################################################################################################################################

    def test_the_form_carries_every_field_of_the_type_with_the_defaults(self, req:'any_') -> 'None':

        form = ChannelCreateForm(req=req, alert_type=alert_type_rest)
        defaults = get_defaults(alert_type_rest)

        for name in get_field_names(alert_type_rest):
            field_name = storage_name(name)
            assert field_name in form.fields, field_name

        assert form.fields[storage_name(Status_Codes_Field)].initial == defaults['status_codes']
        assert form.fields[storage_name('status_code_threshold')].initial == defaults['status_code_threshold']
        assert form.fields[storage_name('connection_failures')].initial == defaults['connection_failures']

        # The channel-only fields are not on an outgoing connection's form
        for name in ('auth_failures', 'server_errors', 'traffic_expected', 'silence_slots'):
            assert storage_name(name) not in form.fields, name

# ################################################################################################################################

    def test_the_edit_form_fields_are_prefixed(self, req:'any_') -> 'None':

        form = ChannelEditForm(prefix='edit', req=req, alert_type=alert_type_rest)
        rendered = str(form[storage_name(Status_Codes_Field)])

        assert 'name="edit-alert_status_codes"' in rendered
        assert 'id="id_edit-alert_status_codes"' in rendered

# ################################################################################################################################

    def test_the_storage_names_carry_each_window_with_its_unit(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_rest)
        storage_names = config['storage_field_names']

        for window in ('window', 'status_codes_window', 'connection_failures_window', 'latency_window'):
            assert storage_name(window) in storage_names, window
            assert storage_name(window + Unit_Field_Suffix) in storage_names, window

        assert storage_name(Status_Codes_Field) in storage_names

# ################################################################################################################################
# ################################################################################################################################
