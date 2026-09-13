# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Alerts tab of an outgoing REST, SOAP or FHIR connection - its sections in order with the health check above the failures and
# the traffic, the status codes line carrying its text field and summarising the codes, the connection failures line, every
# storage field of the type on both pages' forms, and the storage names the config hands the tab's JavaScript. The SOAP
# tab has a SOAP faults line of its own right after the status codes, and the alert rules page a SOAP outgoing row with
# the fault codes cell.

# pytest
import pytest

# Zato
from zato.common.ext.bunch import Bunch

# Zato - Dashboard
from zato.admin.web import alerts_tab
from zato.admin.web.alerts_tab_lines import Fault_Codes_Default, Fault_Codes_Field, Faults_Window_Unit_Field, \
    Health_Check_Run_Every_Field, Health_Check_Run_Unit_Field, Health_Check_Summary_Empty, Line_Kind_Popover, \
    Outcome_Codes_Default, Outcome_Codes_Field, Outcomes_Window_Unit_Field, Section_Core, Section_Failures, Section_Health, \
    Section_Traffic, Status_Codes_Field, Status_Codes_Default, Status_Codes_Window_Unit_Field, Unit_Field_Suffix
from zato.admin.web.forms.http_soap import CreateForm as ChannelCreateForm, EditForm as ChannelEditForm
from zato.admin.web.forms.outgoing.hl7.fhir import CreateForm as FHIRCreateForm, EditForm as FHIREditForm
from zato.admin.web.forms.outgoing.soap import CreateForm as SOAPCreateForm, EditForm as SOAPEditForm
from zato.admin.web.views.alerting import _build_config_cell, _type_cells, _type_titles
from zato.common.alerting.object_config import alert_type_fhir, alert_type_rest, alert_type_soap, get_defaults, \
    get_field_names, storage_name

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

# The create and edit forms of each page the tab is on - the outgoing REST page shares the channels' forms,
# the outgoing SOAP page has forms of its own
_page_forms = [
    pytest.param((ChannelCreateForm, ChannelEditForm), id='rest'),
    pytest.param((SOAPCreateForm, SOAPEditForm), id='soap'),
]

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

    @pytest.mark.parametrize('page_forms', _page_forms)
    def test_the_sections_run_core_health_check_failures_traffic(self, req:'any_', page_forms:'any_') -> 'None':

        create_form_class, _ = page_forms
        form = create_form_class(req=req, alert_type=alert_type_rest)
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
        assert line['rows'] == [[Status_Codes_Field], ['status_code_threshold', 'status_codes_window']]
        assert line['unit_field'] == Status_Codes_Window_Unit_Field

        # The codes are typed as text with the placeholder showing the shape ..
        assert line['text_fields'] == {Status_Codes_Field: Status_Codes_Default}
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

    @pytest.mark.parametrize('page_forms', _page_forms)
    def test_the_form_carries_every_field_of_the_type_with_the_defaults(self, req:'any_', page_forms:'any_') -> 'None':

        create_form_class, _ = page_forms
        form = create_form_class(req=req, alert_type=alert_type_rest)
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

    @pytest.mark.parametrize('page_forms', _page_forms)
    def test_the_edit_form_fields_are_prefixed(self, req:'any_', page_forms:'any_') -> 'None':

        _, edit_form_class = page_forms
        form = edit_form_class(prefix='edit', req=req, alert_type=alert_type_rest)
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

class TestOutgoingSoapTab:

    def test_the_soap_lines_carry_the_faults_right_after_the_status_codes(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_soap)

        line_names:'strlist' = []

        for line in config['lines']:
            line_names.append(line['name'])

        assert line_names == ['active', 'use_llm', 'llm', 'email', 'health_check', 'failures_in_a_row', 'error_rate',
            'status_codes', 'soap_faults', 'connection_failures', 'slow_responses']

        # The REST tab has no such line
        rest_config = alerts_tab.get_alerts_tab_config(alert_type_rest)
        assert 'soap_faults' not in _lines_by_name(rest_config)

# ################################################################################################################################

    def test_the_soap_faults_line_carries_its_codes_and_summarises_them(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_soap)
        line = _lines_by_name(config)['soap_faults']

        assert line['kind'] == Line_Kind_Popover
        assert line['label'] == 'SOAP faults'
        assert line['fields'] == [Fault_Codes_Field, 'fault_threshold', 'faults_window']
        assert line['rows'] == [[Fault_Codes_Field], ['fault_threshold', 'faults_window']]
        assert line['unit_field'] == Faults_Window_Unit_Field

        # The codes are typed as text with the default showing the shape ..
        assert line['text_fields'] == {Fault_Codes_Field: Fault_Codes_Default}
        assert Fault_Codes_Default == 'Receiver, Server, Sender, Client'
        assert config['field_kinds'][Fault_Codes_Field] == 'text'

        # .. and the summary names the count, the codes text and the window with its unit.
        assert '{fault_threshold|fault|faults}' in line['summary']
        assert f'{{{Fault_Codes_Field}}}' in line['summary']
        assert f'{{{Faults_Window_Unit_Field}@faults_window}}' in line['summary']

        assert config['field_labels']['faults_window'] == 'In the last'

# ################################################################################################################################

    def test_the_soap_forms_carry_the_fault_fields_and_the_rest_forms_do_not(self, req:'any_') -> 'None':

        soap_form = SOAPCreateForm(req=req, alert_type=alert_type_soap)
        defaults = get_defaults(alert_type_soap)

        for name in get_field_names(alert_type_soap):
            assert storage_name(name) in soap_form.fields, name

        assert soap_form.fields[storage_name(Fault_Codes_Field)].initial == defaults['fault_codes']
        assert soap_form.fields[storage_name('fault_threshold')].initial == defaults['fault_threshold']

        rest_form = ChannelCreateForm(req=req, alert_type=alert_type_rest)

        for name in ('fault_codes', 'fault_threshold', 'faults_window'):
            assert storage_name(name) not in rest_form.fields, name

# ################################################################################################################################

    def test_the_soap_storage_names_carry_the_faults_window_with_its_unit(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_soap)
        storage_names = config['storage_field_names']

        assert storage_name('faults_window') in storage_names
        assert storage_name('faults_window' + Unit_Field_Suffix) in storage_names
        assert storage_name(Fault_Codes_Field) in storage_names

# ################################################################################################################################

    def test_the_type_page_renders_the_soap_row_with_its_text_cells(self) -> 'None':

        assert _type_titles['rest'] == 'REST outgoing'
        assert _type_titles['soap'] == 'SOAP outgoing'

        assert 'fault_codes' in _type_cells['soap']
        assert 'fault_codes' not in _type_cells['rest']

        values = {'fault_codes': 'Receiver, Server'}
        cell = _build_config_cell('fault_codes', 'text', values)

        assert cell == {
            'name': 'fault_codes',
            'label': 'Fault codes',
            'suffix': '',
            'kind': 'text',
            'value': 'Receiver, Server',
            'display': 'Receiver, Server',
        }

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingFhirTab:

    def test_the_fhir_lines_carry_the_outcomes_right_after_the_status_codes(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_fhir)

        line_names:'strlist' = []

        for line in config['lines']:
            line_names.append(line['name'])

        assert line_names == ['active', 'use_llm', 'llm', 'email', 'health_check', 'failures_in_a_row', 'error_rate',
            'status_codes', 'operation_outcomes', 'connection_failures', 'slow_responses']

        # Neither the REST tab nor the SOAP one has such a line, and the FHIR one has no faults
        assert 'operation_outcomes' not in _lines_by_name(alerts_tab.get_alerts_tab_config(alert_type_rest))
        assert 'operation_outcomes' not in _lines_by_name(alerts_tab.get_alerts_tab_config(alert_type_soap))
        assert 'soap_faults' not in _lines_by_name(config)

# ################################################################################################################################

    def test_the_operation_outcomes_line_carries_its_codes_and_summarises_them(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_fhir)
        line = _lines_by_name(config)['operation_outcomes']

        assert line['kind'] == Line_Kind_Popover
        assert line['label'] == 'Operation outcomes'
        assert line['fields'] == [Outcome_Codes_Field, 'outcome_threshold', 'outcomes_window']
        assert line['rows'] == [[Outcome_Codes_Field], ['outcome_threshold', 'outcomes_window']]
        assert line['unit_field'] == Outcomes_Window_Unit_Field

        # The codes are typed as text with the default showing the shape ..
        assert line['text_fields'] == {Outcome_Codes_Field: Outcome_Codes_Default}
        assert Outcome_Codes_Default == 'exception, transient, timeout, throttled, lock-error, no-store, too-costly'
        assert config['field_kinds'][Outcome_Codes_Field] == 'text'

        # .. and the summary names the count, the codes text and the window with its unit.
        assert '{outcome_threshold|outcome|outcomes}' in line['summary']
        assert f'{{{Outcome_Codes_Field}}}' in line['summary']
        assert f'{{{Outcomes_Window_Unit_Field}@outcomes_window}}' in line['summary']

        assert config['field_labels']['outcomes_window'] == 'In the last'
        assert config['field_labels']['outcome_threshold'] == 'Alert after'

# ################################################################################################################################

    def test_the_fhir_forms_carry_the_outcome_and_health_check_fields(self, req:'any_') -> 'None':

        defaults = get_defaults(alert_type_fhir)

        for form_class in (FHIRCreateForm, FHIREditForm):
            form = form_class(req=req, security_list=[])

            for name in get_field_names(alert_type_fhir):
                assert storage_name(name) in form.fields, name

            assert form.fields[storage_name(Outcome_Codes_Field)].initial == defaults['outcome_codes']
            assert form.fields[storage_name('outcome_threshold')].initial == defaults['outcome_threshold']

            # The health check schedule is edited on the tab as fields of the page's own form
            assert Health_Check_Run_Every_Field in form.fields
            assert Health_Check_Run_Unit_Field in form.fields

            for name in ('fault_codes', 'fault_threshold', 'faults_window'):
                assert storage_name(name) not in form.fields, name

# ################################################################################################################################

    def test_the_fhir_storage_names_carry_the_outcomes_window_with_its_unit(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_fhir)
        storage_names = config['storage_field_names']

        assert storage_name('outcomes_window') in storage_names
        assert storage_name('outcomes_window' + Unit_Field_Suffix) in storage_names
        assert storage_name(Outcome_Codes_Field) in storage_names

# ################################################################################################################################

    def test_the_type_page_renders_the_fhir_row_with_its_text_cell(self) -> 'None':

        assert _type_titles['fhir'] == 'FHIR outgoing'

        assert 'outcome_codes' in _type_cells['fhir']
        assert 'outcome_codes' not in _type_cells['rest']
        assert 'outcome_codes' not in _type_cells['soap']
        assert 'fault_codes' not in _type_cells['fhir']

        values = {'outcome_codes': 'exception, not-found'}
        cell = _build_config_cell('outcome_codes', 'text', values)

        assert cell == {
            'name': 'outcome_codes',
            'label': 'Outcome codes',
            'suffix': '',
            'kind': 'text',
            'value': 'exception, not-found',
            'display': 'exception, not-found',
        }

# ################################################################################################################################
# ################################################################################################################################
