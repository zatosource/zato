# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Alerts popup of an MCP gateway - the sixteen lines in five sections, Core, Failures, Callers, Traffic and
# Configuration, the two latencies in seconds, the volume line carrying a size unit select of its own and summarising
# as megabytes, the one line with no window, every storage field of the type on the wizard's forms, the storage names
# the config hands the popup's JavaScript, and the alert rules page an MCP row with its size cell.

# pytest
import pytest

# Zato
from zato.common.alerting import config_map
from zato.common.ext.bunch import Bunch

# Zato - Dashboard
from zato.admin.web import alerts_tab
from zato.admin.web.alerts_tab_lines import Invalid_Calls_Window_Unit_Field, Latency_Window_Unit_Field, Line_Kind_Popover, \
    Repeat_Calls_Window_Unit_Field, Section_Callers, Section_Configuration, Section_Core, Section_Failures, Section_Traffic, \
    Unit_Field_Suffix, Volume_Budget_Unit_Field, Volume_Budget_Window_Unit_Field
from zato.admin.web.forms.gateway.mcp import CreateForm as MCPCreateForm, EditForm as MCPEditForm
from zato.admin.web.views.alerting_config_cells import _build_config_cell, _type_cells, _type_titles
from zato.common.alerting.object_config import alert_type_llm, alert_type_mcp, get_defaults, get_field_names, storage_name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strlist
    any_ = any_
    anydict = anydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

class _FakeClient:
    """ Answers the listings the popup's picks ask for with nothing, so the popup renders its create sentences.
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

class TestMCPGatewayPopup:

    def test_the_lines_run_core_failures_callers_traffic_configuration(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_mcp)

        line_names:'strlist' = []
        sections:'strlist' = []

        for line in config['lines']:
            line_names.append(line['name'])

            if line['section'] not in sections:
                sections.append(line['section'])

        assert line_names == ['active', 'use_llm', 'llm', 'email', 'failures_in_a_row', 'error_rate', 'invalid_tool_calls',
            'rejected_responses', 'rejected_callers', 'throttled_callers', 'repeated_calls', 'slow_tool_calls',
            'truncated_responses', 'response_volume', 'silence', 'too_many_tools']

        assert sections == [Section_Core, Section_Failures, Section_Callers, Section_Traffic, Section_Configuration]

        lines = _lines_by_name(config)

        assert lines['invalid_tool_calls']['section'] == Section_Failures
        assert lines['rejected_responses']['section'] == Section_Failures
        assert lines['rejected_callers']['section'] == Section_Callers
        assert lines['throttled_callers']['section'] == Section_Callers
        assert lines['repeated_calls']['section'] == Section_Callers
        assert lines['slow_tool_calls']['section'] == Section_Traffic
        assert lines['truncated_responses']['section'] == Section_Traffic
        assert lines['response_volume']['section'] == Section_Traffic
        assert lines['silence']['section'] == Section_Traffic
        assert lines['too_many_tools']['section'] == Section_Configuration

        # Nothing of an outgoing connection's is on a gateway, and nothing of the gateway's is on an LLM connection
        for name in ('status_codes', 'connection_failures', 'token_budget', 'refusals', 'health_check', 'negative_acks'):
            assert name not in lines, name

        llm_lines = _lines_by_name(alerts_tab.get_alerts_tab_config(alert_type_llm))
        for name in ('invalid_tool_calls', 'repeated_calls', 'response_volume', 'too_many_tools'):
            assert name not in llm_lines, name

# ################################################################################################################################

    def test_the_agent_lines_carry_a_count_and_a_window_each(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_mcp)
        lines = _lines_by_name(config)

        invalid = lines['invalid_tool_calls']

        assert invalid['kind'] == Line_Kind_Popover
        assert invalid['label'] == 'Invalid tool calls'
        assert invalid['fields'] == ['invalid_calls', 'invalid_calls_window']
        assert invalid['rows'] == [['invalid_calls'], ['invalid_calls_window']]
        assert invalid['unit_field'] == Invalid_Calls_Window_Unit_Field
        assert '{invalid_calls|invalid tool call|invalid tool calls}' in invalid['summary']
        assert f'{{{Invalid_Calls_Window_Unit_Field}@invalid_calls_window}}' in invalid['summary']

        repeated = lines['repeated_calls']

        assert repeated['label'] == 'Repeated calls'
        assert repeated['fields'] == ['repeat_calls', 'repeat_calls_window']
        assert repeated['unit_field'] == Repeat_Calls_Window_Unit_Field
        assert 'one session calls one tool {repeat_calls|time|times}' in repeated['summary']

        assert lines['rejected_callers']['fields'] == ['auth_failures', 'auth_failures_window']
        assert lines['throttled_callers']['fields'] == ['throttled_calls', 'throttled_calls_window']
        assert lines['rejected_responses']['fields'] == ['rejections', 'rejections_window']
        assert lines['truncated_responses']['fields'] == ['truncations', 'truncations_window']

# ################################################################################################################################

    def test_the_slow_line_carries_the_two_latencies_in_seconds(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_mcp)
        line = _lines_by_name(config)['slow_tool_calls']

        assert line['label'] == 'Slow tool calls'
        assert line['fields'] == ['warning_latency', 'error_latency', 'latency_window']
        assert line['rows'] == [['warning_latency', 'error_latency'], ['latency_window']]
        assert line['unit_field'] == Latency_Window_Unit_Field
        assert '{warning_latency|second|seconds}' in line['summary']
        assert '{error_latency|second|seconds}' in line['summary']

        assert config['field_kinds']['warning_latency'] == config_map.Kind_Seconds
        assert config['field_kinds']['error_latency'] == config_map.Kind_Seconds

        # The seconds are typed as fractions and stored as such, whole ones reading as integers
        assert alerts_tab.pre_process_alert_item(alert_type_mcp, 'alert_warning_latency', '7.5') == 7.5
        assert alerts_tab.pre_process_alert_item(alert_type_mcp, 'alert_error_latency', '15') == 15

# ################################################################################################################################

    def test_the_volume_line_carries_a_size_unit_select_and_summarises_as_megabytes(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_mcp)
        line = _lines_by_name(config)['response_volume']

        assert line['label'] == 'Response volume'
        assert line['fields'] == ['volume_budget', 'volume_budget_window']
        assert line['unit_field'] == Volume_Budget_Window_Unit_Field
        assert line['field_units'] == {'volume_budget': Volume_Budget_Unit_Field}
        assert f'{{{Volume_Budget_Unit_Field}@volume_budget}} of responses' in line['summary']
        assert f'{{{Volume_Budget_Window_Unit_Field}@volume_budget_window}}' in line['summary']

        assert config['field_kinds']['volume_budget'] == config_map.Kind_Size

        # The default of a hundred million bytes reads as a hundred megabytes over a day on the form ..
        item = {'alert_volume_budget': 100000000, 'alert_volume_budget_window': 86400, 'alert_repeat_calls_window': 300}
        alerts_tab.split_unit_fields(alert_type_mcp, item)

        assert item['alert_volume_budget'] == 100
        assert item['alert_volume_budget_unit'] == 'megabyte'
        assert item['alert_volume_budget_window'] == 1
        assert item['alert_volume_budget_window_unit'] == 'day'
        assert item['alert_repeat_calls_window'] == 5
        assert item['alert_repeat_calls_window_unit'] == 'minute'

        # .. and what the form sends - two gigabytes over an hour - joins back into bytes and seconds.
        input_dict = {
            'alert_volume_budget': 2, 'alert_volume_budget_unit': 'gigabyte',
            'alert_volume_budget_window': 1, 'alert_volume_budget_window_unit': 'hour',
        }
        alerts_tab.join_unit_fields(alert_type_mcp, input_dict)

        assert input_dict == {'alert_volume_budget': 2000000000, 'alert_volume_budget_window': 3600}

        # The size cell of the rules page reads the same way
        cell = _build_config_cell('volume_budget', config_map.Kind_Size, {'volume_budget': 100000000})
        assert cell is not None

        assert cell['kind'] == 'size'
        assert cell['display'] == '100 megabytes'

# ################################################################################################################################

    def test_the_tools_line_has_no_window_and_the_silence_line_speaks_of_tool_calls(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_mcp)
        lines = _lines_by_name(config)

        tools = lines['too_many_tools']

        assert tools['label'] == 'Too many tools'
        assert tools['fields'] == ['max_tools']
        assert tools['rows'] == [['max_tools']]
        assert 'unit_field' not in tools
        assert '{max_tools|tool|tools}' in tools['summary']
        assert 'audit log off' in tools['how_it_works']

        silence = lines['silence']

        assert silence['label'] == 'On no tool calls'
        assert silence['off_field'] == 'traffic_expected'
        assert silence['summary_off'] == 'Alerts off'
        assert 'gateway' in silence['how_it_works']

# ################################################################################################################################

    def test_the_wizard_forms_carry_every_field_of_the_type_and_nothing_else(self, req:'any_') -> 'None':

        defaults = get_defaults(alert_type_mcp)

        for form_class in (MCPCreateForm, MCPEditForm):
            form = form_class(req=req)

            for name in get_field_names(alert_type_mcp):
                assert storage_name(name) in form.fields, name

            assert form.fields[storage_name('invalid_calls')].initial == defaults['invalid_calls']
            assert form.fields[storage_name('repeat_calls')].initial == defaults['repeat_calls']
            assert form.fields[storage_name('max_tools')].initial == defaults['max_tools']
            assert form.fields[storage_name('warning_latency')].initial == defaults['warning_latency']
            assert form.fields[storage_name('error_latency')].initial == defaults['error_latency']

            # The budget's initial is its split - a hundred megabytes over a day
            assert form.fields[storage_name('volume_budget')].initial == 100
            assert form.fields[storage_name(Volume_Budget_Unit_Field)].initial == 'megabyte'
            assert form.fields[storage_name('volume_budget_window')].initial == 1
            assert form.fields[storage_name(Volume_Budget_Window_Unit_Field)].initial == 'day'

            # The two latencies and the budget take fractions
            for name in ('warning_latency', 'error_latency', 'volume_budget'):
                assert form.fields[storage_name(name)].widget.attrs['step'] == alerts_tab.Fractional_Step, name

            for name in ('max_latency', 'status_codes', 'connection_failures', 'token_budget', 'refusals', 'ack_codes',
                'health_check_run_every'):
                assert storage_name(name) not in form.fields, name

# ################################################################################################################################

    def test_the_edit_form_fields_are_prefixed(self, req:'any_') -> 'None':

        form = MCPEditForm(req=req, prefix='edit')

        assert form['alert_invalid_calls'].html_name == 'edit-alert_invalid_calls'
        assert form['alert_volume_budget'].html_name == 'edit-alert_volume_budget'
        assert form['alert_volume_budget_unit'].html_name == 'edit-alert_volume_budget_unit'
        assert form['alert_max_tools'].html_name == 'edit-alert_max_tools'

# ################################################################################################################################

    def test_the_storage_names_carry_every_window_with_its_unit(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_mcp)
        storage_names = config['storage_field_names']

        for name in ('invalid_calls_window', 'rejections_window', 'auth_failures_window', 'throttled_calls_window',
            'repeat_calls_window', 'latency_window', 'truncations_window', 'volume_budget_window', 'silence_window'):
            assert storage_name(name) in storage_names, name
            assert storage_name(name + Unit_Field_Suffix) in storage_names, name

        assert storage_name(Volume_Budget_Unit_Field) in storage_names
        assert storage_name('max_tools') in storage_names

        for name in ('status_codes', 'token_budget', 'connection_failures'):
            assert storage_name(name) not in storage_names, name

# ################################################################################################################################

    def test_the_type_page_renders_the_mcp_row_with_its_cells(self) -> 'None':

        assert _type_titles['mcp'] == 'MCP'

        assert _type_cells['mcp'] == ['consecutive_failures', 'error_rate', 'window', 'invalid_calls', 'rejections',
            'auth_failures', 'throttled_calls', 'repeat_calls', 'warning_latency', 'error_latency', 'truncations',
            'volume_budget', 'max_tools', 'use_llm']

        for name in ('max_latency', 'max_tool_call_time', 'status_codes', 'token_budget', 'traffic_expected'):
            assert name not in _type_cells['mcp'], name

# ################################################################################################################################
# ################################################################################################################################
