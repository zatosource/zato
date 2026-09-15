# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Alerts tab of an outgoing LLM connection - the core four, six failure lines with the truncated completions and the
# refusals among them, two traffic lines with the token budget, the status codes line summarising the LLM's own codes with
# 429 first, the two latencies in seconds that take fractions, the budget with its unit select of thousands, millions and
# billions splitting and joining on the way through the forms, and the alert rules page an LLM row with the new cells.

# pytest
import pytest

# Zato
from zato.common.alerting import config_map
from zato.common.ext.bunch import Bunch

# Zato - Dashboard
from zato.admin.web import alerts_tab
from zato.admin.web.alerts_tab_lines import Latency_Window_Unit_Field, Line_Kind_Popover, Refusals_Window_Unit_Field, \
    Section_Core, Section_Failures, Section_Traffic, Status_Codes_Default, Status_Codes_Field, Token_Budget_Unit_Field, \
    Token_Budget_Window_Unit_Field, Truncations_Window_Unit_Field, Unit_Field_Suffix
from zato.admin.web.alerts_tab_lines_llm import LLM_Status_Codes_Default
from zato.admin.web.forms.outgoing.llm import CreateForm as LLMCreateForm, EditForm as LLMEditForm
from zato.admin.web.views.alerting_config_cells import _type_cells, _type_titles
from zato.common.alerting.object_config import alert_type_llm, alert_type_rest, get_defaults, get_field_names, storage_name

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

class TestLLMTab:

    def test_the_lines_run_core_failures_traffic_with_the_llms_own_among_them(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_llm)

        line_names:'strlist' = []

        for line in config['lines']:
            line_names.append(line['name'])

        assert line_names == ['active', 'use_llm', 'llm', 'email', 'failures_in_a_row', 'error_rate', 'status_codes',
            'connection_failures', 'truncated_completions', 'refusals', 'slow_completions', 'token_budget']

        lines = _lines_by_name(config)

        assert lines['email']['section'] == Section_Core
        assert lines['status_codes']['section'] == Section_Failures
        assert lines['truncated_completions']['section'] == Section_Failures
        assert lines['refusals']['section'] == Section_Failures
        assert lines['slow_completions']['section'] == Section_Traffic
        assert lines['token_budget']['section'] == Section_Traffic

        # An outgoing connection has no traffic it expects and the LLM has no health check - and the REST latency
        # gives way to the two-step one
        for name in ('silence', 'health_check', 'slow_responses', 'soap_faults', 'operation_outcomes', 'auth_failures'):
            assert name not in lines, name

# ################################################################################################################################

    def test_the_status_codes_line_summarises_the_llms_own_codes_with_429_first(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_llm)
        line = _lines_by_name(config)['status_codes']

        assert line['kind'] == Line_Kind_Popover
        assert line['text_fields'] == {Status_Codes_Field: LLM_Status_Codes_Default}
        assert LLM_Status_Codes_Default == '429, 401, 403, 5xx'
        assert config['field_kinds'][Status_Codes_Field] == config_map.Kind_Text

        # The HTTP types keep the REST default, without the 429
        rest_line = _lines_by_name(alerts_tab.get_alerts_tab_config(alert_type_rest))['status_codes']
        assert rest_line['text_fields'] == {Status_Codes_Field: Status_Codes_Default}
        assert Status_Codes_Default == '401, 403, 5xx'

# ################################################################################################################################

    def test_the_truncated_completions_and_the_refusals_lines_count_completions_that_came_back_with_a_200(self) -> 'None':

        lines = _lines_by_name(alerts_tab.get_alerts_tab_config(alert_type_llm))

        truncated = lines['truncated_completions']
        assert truncated['label'] == 'Truncated completions'
        assert truncated['fields'] == ['truncations', 'truncations_window']
        assert truncated['unit_field'] == Truncations_Window_Unit_Field
        assert '{truncations|completion|completions} cut short by the token limit' in truncated['summary']
        assert 'max tokens was reached' in truncated['how_it_works']
        assert 'with a 200' in truncated['how_it_works']

        refusals = lines['refusals']
        assert refusals['label'] == 'Refusals'
        assert refusals['fields'] == ['refusals', 'refusals_window']
        assert refusals['unit_field'] == Refusals_Window_Unit_Field
        assert '{refusals|refusal|refusals}' in refusals['summary']
        assert 'content filter' in refusals['how_it_works']
        assert 'with a 200' in refusals['how_it_works']

# ################################################################################################################################

    def test_the_slow_completions_line_speaks_seconds_on_one_row_and_takes_fractions(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_llm)
        line = _lines_by_name(config)['slow_completions']

        assert line['label'] == 'Slow completions'
        assert line['fields'] == ['warning_latency', 'error_latency', 'latency_window']
        assert line['rows'] == [['warning_latency', 'error_latency'], ['latency_window']]
        assert line['unit_field'] == Latency_Window_Unit_Field
        assert '{warning_latency|second|seconds}' in line['summary']
        assert '{error_latency|second|seconds}' in line['summary']

        assert config['field_kinds']['warning_latency'] == config_map.Kind_Seconds
        assert config['field_kinds']['error_latency'] == config_map.Kind_Seconds

        # The seconds are typed as fractions and stored as such, whole ones reading as integers
        assert alerts_tab.pre_process_alert_item(alert_type_llm, 'alert_warning_latency', '7.5') == 7.5
        assert alerts_tab.pre_process_alert_item(alert_type_llm, 'alert_error_latency', '15') == 15
        assert isinstance(alerts_tab.pre_process_alert_item(alert_type_llm, 'alert_error_latency', '15.0'), int)

# ################################################################################################################################

    def test_the_token_budget_line_carries_a_unit_select_of_its_own_next_to_the_windows(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_llm)
        line = _lines_by_name(config)['token_budget']

        assert line['label'] == 'Token budget'
        assert line['fields'] == ['token_budget', 'token_budget_window']
        assert line['unit_field'] == Token_Budget_Window_Unit_Field
        assert line['field_units'] == {'token_budget': Token_Budget_Unit_Field}
        assert f'{{{Token_Budget_Unit_Field}@token_budget}} tokens' in line['summary']
        assert f'{{{Token_Budget_Window_Unit_Field}@token_budget_window}}' in line['summary']
        assert 'Input and output tokens are added up' in line['how_it_works']

        assert config['field_kinds']['token_budget'] == config_map.Kind_Amount

        # Both unit selects reach the JavaScript through the storage names
        storage_names = config['storage_field_names']
        assert storage_name(Token_Budget_Unit_Field) in storage_names
        assert storage_name(Token_Budget_Window_Unit_Field) in storage_names
        assert storage_name('truncations_window' + Unit_Field_Suffix) in storage_names
        assert storage_name('refusals_window' + Unit_Field_Suffix) in storage_names

# ################################################################################################################################

    def test_the_budget_splits_for_the_form_and_joins_back_for_storage(self) -> 'None':

        # What the backend lists - the stored ones ..
        item = {'alert_token_budget': 10000000, 'alert_token_budget_window': 86400, 'alert_truncations_window': 300}
        alerts_tab.split_unit_fields(alert_type_llm, item)

        # .. read as ten millions over one day on the edit form ..
        assert item['alert_token_budget'] == 10
        assert item['alert_token_budget_unit'] == 'million'
        assert item['alert_token_budget_window'] == 1
        assert item['alert_token_budget_window_unit'] == 'day'
        assert item['alert_truncations_window'] == 5
        assert item['alert_truncations_window_unit'] == 'minute'

        # .. and what the form sends - two and a half millions over an hour - joins back into ones and seconds
        input_dict = {
            'alert_token_budget': 2.5, 'alert_token_budget_unit': 'million',
            'alert_token_budget_window': 1, 'alert_token_budget_window_unit': 'hour',
        }
        alerts_tab.join_unit_fields(alert_type_llm, input_dict)

        assert input_dict == {'alert_token_budget': 2500000, 'alert_token_budget_window': 3600}

        # A fraction of a thousand is a fraction on the way in and ones on the way out
        assert alerts_tab.pre_process_alert_item(alert_type_llm, 'alert_token_budget', '0.5') == 0.5
        assert config_map.join_amount(0.5, 'thousand') == 500

# ################################################################################################################################

    def test_the_forms_carry_every_field_of_the_type_and_nothing_else(self, req:'any_') -> 'None':

        defaults = get_defaults(alert_type_llm)

        for form_class in (LLMCreateForm, LLMEditForm):
            form = form_class(req=req)

            for name in get_field_names(alert_type_llm):
                assert storage_name(name) in form.fields, name

            assert form.fields[storage_name(Status_Codes_Field)].initial == defaults['status_codes']
            assert form.fields[storage_name('truncations')].initial == defaults['truncations']
            assert form.fields[storage_name('refusals')].initial == defaults['refusals']
            assert form.fields[storage_name('warning_latency')].initial == defaults['warning_latency']
            assert form.fields[storage_name('error_latency')].initial == defaults['error_latency']

            # The budget's initial is its split - ten millions over a day
            assert form.fields[storage_name('token_budget')].initial == 10
            assert form.fields[storage_name(Token_Budget_Unit_Field)].initial == 'million'
            assert form.fields[storage_name('token_budget_window')].initial == 1
            assert form.fields[storage_name(Token_Budget_Window_Unit_Field)].initial == 'day'

            # The two latencies and the budget take fractions
            for name in ('warning_latency', 'error_latency', 'token_budget'):
                assert form.fields[storage_name(name)].widget.attrs['step'] == alerts_tab.Fractional_Step, name

            for name in ('max_latency', 'traffic_expected', 'silence_window', 'auth_failures', 'fault_codes', 'outcome_codes',
                'health_check_run_every'):
                assert storage_name(name) not in form.fields, name

# ################################################################################################################################

    def test_the_edit_form_fields_are_prefixed(self, req:'any_') -> 'None':

        form = LLMEditForm(req=req, prefix='edit')

        assert form['alert_status_codes'].html_name == 'edit-alert_status_codes'
        assert form['alert_token_budget'].html_name == 'edit-alert_token_budget'
        assert form['alert_token_budget_unit'].html_name == 'edit-alert_token_budget_unit'

# ################################################################################################################################

    def test_the_type_page_renders_the_llm_row_with_its_cells(self) -> 'None':

        assert _type_titles['llm'] == 'LLM'

        assert _type_cells['llm'] == ['consecutive_failures', 'error_rate', 'window', 'status_codes', 'truncations', 'refusals',
            'token_budget', 'warning_latency', 'error_latency', 'use_llm']

        for name in ('max_latency', 'fault_codes', 'outcome_codes', 'auth_failures', 'traffic_expected', 'connection_failures'):
            assert name not in _type_cells['llm'], name

# ################################################################################################################################
# ################################################################################################################################
