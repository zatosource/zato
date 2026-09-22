# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Alerts popup of an outgoing MLLP connection - the nine lines of the channel's popup with the connection failures
# in place of the silence, the negative acks line speaking of what the remote system answered, the connection failures
# line of unacknowledged messages, every storage field of the type on the wizard's forms, the storage names the config
# hands the popup's JavaScript, and the alert rules page an MLLP outgoing row with the codes and the failures cells.

# pytest
import pytest

# Zato
from zato.common.ext.bunch import Bunch

# Zato - Dashboard
from zato.admin.web import alerts_tab
from zato.admin.web.alerts_tab_lines import Ack_Codes_Default, Ack_Codes_Field, Acks_Window_Unit_Field, \
    Connection_Failures_Window_Unit_Field, Line_Kind_Popover, Section_Core, Section_Failures, Section_Traffic, Unit_Field_Suffix
from zato.admin.web.forms.outgoing.hl7.mllp import CreateForm as MLLPCreateForm, EditForm as MLLPEditForm
from zato.admin.web.views.alerting_config_cells import _type_cells, _type_titles
from zato.common.alerting.object_config import alert_type_fhir, alert_type_mllp_channel, alert_type_mllp_outgoing, get_defaults, \
    get_field_names, storage_name

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

class TestMllpOutgoingPopup:

    def test_the_lines_run_core_failures_traffic_without_silence_or_anything_http(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_mllp_outgoing)

        line_names:'strlist' = []

        for line in config['lines']:
            line_names.append(line['name'])

        assert line_names == ['active', 'use_llm', 'llm', 'email', 'failures_in_a_row', 'error_rate', 'negative_acks',
            'connection_failures', 'slow_responses', 'dlq_messages', 'queue_backlog']

        lines = _lines_by_name(config)

        assert lines['email']['section'] == Section_Core
        assert lines['negative_acks']['section'] == Section_Failures
        assert lines['connection_failures']['section'] == Section_Failures
        assert lines['slow_responses']['section'] == Section_Traffic

        # An outgoing connection has no traffic it expects, and nothing HTTP is measured about it
        for name in ('silence', 'health_check', 'status_codes', 'soap_faults', 'operation_outcomes', 'auth_failures'):
            assert name not in lines, name

# ################################################################################################################################

    def test_the_negative_acks_line_speaks_of_what_the_remote_system_answered(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_mllp_outgoing)
        line = _lines_by_name(config)['negative_acks']

        assert line['kind'] == Line_Kind_Popover
        assert line['label'] == 'Negative acks'
        assert line['fields'] == [Ack_Codes_Field, 'ack_threshold', 'acks_window']
        assert line['rows'] == [[Ack_Codes_Field], ['ack_threshold', 'acks_window']]
        assert line['unit_field'] == Acks_Window_Unit_Field
        assert line['text_fields'] == {Ack_Codes_Field: Ack_Codes_Default}
        assert config['field_kinds'][Ack_Codes_Field] == 'text'

        # The codes are what the remote system answered, the channel's what it sent back
        assert 'the remote system answered' in line['how_it_works']
        assert "connection's audit log" in line['how_it_works']

        channel_line = _lines_by_name(alerts_tab.get_alerts_tab_config(alert_type_mllp_channel))['negative_acks']
        assert 'the channel sent back' in channel_line['how_it_works']

        assert '{ack_threshold|ack|acks}' in line['summary']
        assert f'{{{Ack_Codes_Field}}}' in line['summary']

# ################################################################################################################################

    def test_the_connection_failures_line_counts_unacknowledged_messages(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_mllp_outgoing)
        line = _lines_by_name(config)['connection_failures']

        assert line['label'] == 'Connection failures'
        assert line['fields'] == ['connection_failures', 'connection_failures_window']
        assert line['unit_field'] == Connection_Failures_Window_Unit_Field
        assert 'unacknowledged message' in line['summary']
        assert 'no acknowledgment at all' in line['how_it_works']

        # A FHIR connection's line speaks of calls that got no response
        fhir_line = _lines_by_name(alerts_tab.get_alerts_tab_config(alert_type_fhir))['connection_failures']
        assert 'unacknowledged' not in fhir_line['summary']

# ################################################################################################################################

    def test_the_wizard_forms_carry_every_field_of_the_type_and_nothing_else(self, req:'any_') -> 'None':

        defaults = get_defaults(alert_type_mllp_outgoing)

        for form_class in (MLLPCreateForm, MLLPEditForm):
            form = form_class(req=req)

            for name in get_field_names(alert_type_mllp_outgoing):
                assert storage_name(name) in form.fields, name

            assert form.fields[storage_name(Ack_Codes_Field)].initial == defaults['ack_codes']
            assert form.fields[storage_name('ack_threshold')].initial == defaults['ack_threshold']
            assert form.fields[storage_name('connection_failures')].initial == defaults['connection_failures']

            for name in ('traffic_expected', 'silence_window', 'auth_failures', 'client_errors', 'server_error_rate',
                'status_codes', 'fault_codes', 'outcome_codes'):
                assert storage_name(name) not in form.fields, name

# ################################################################################################################################

    def test_the_edit_form_fields_are_prefixed(self, req:'any_') -> 'None':

        form = MLLPEditForm(req=req, prefix='edit')

        assert form['alert_ack_codes'].html_name == 'edit-alert_ack_codes'
        assert form['alert_connection_failures'].html_name == 'edit-alert_connection_failures'

# ################################################################################################################################

    def test_the_storage_names_carry_the_windows_with_their_units(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_mllp_outgoing)
        storage_names = config['storage_field_names']

        assert storage_name(Ack_Codes_Field) in storage_names
        assert storage_name('acks_window') in storage_names
        assert storage_name('acks_window' + Unit_Field_Suffix) in storage_names
        assert storage_name('connection_failures_window') in storage_names
        assert storage_name('connection_failures_window' + Unit_Field_Suffix) in storage_names

        for name in ('traffic_expected', 'silence_window', 'auth_failures', 'status_codes'):
            assert storage_name(name) not in storage_names, name

# ################################################################################################################################

    def test_the_type_page_renders_the_mllp_outgoing_row_with_its_cells(self) -> 'None':

        assert _type_titles['mllp_outgoing'] == 'MLLP outgoing'

        assert _type_cells['mllp_outgoing'] == ['consecutive_failures', 'error_rate', 'window', 'ack_codes',
            'connection_failures', 'max_latency', 'dlq_messages', 'queue_depth', 'use_llm']

        assert 'connection_failures' not in _type_cells['mllp_channel']

        for name in ('status_codes', 'fault_codes', 'outcome_codes', 'auth_failures', 'traffic_expected'):
            assert name not in _type_cells['mllp_outgoing'], name

# ################################################################################################################################
# ################################################################################################################################
