# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Alerts popup of an MLLP channel - the nine lines of a REST channel's tab minus everything HTTP, with the negative
# acks line under Failures carrying the codes text and summarising them, the silence line speaking of messages, every
# storage field of the type on the wizard's forms, the storage names the config hands the popup's JavaScript, and the
# alert rules page an MLLP channels row with the codes cell.

# pytest
import pytest

# Zato
from zato.common.ext.bunch import Bunch

# Zato - Dashboard
from zato.admin.web import alerts_tab
from zato.admin.web.alerts_tab_lines import Ack_Codes_Default, Ack_Codes_Field, Acks_Window_Unit_Field, Line_Kind_Popover, \
    Section_Core, Section_Failures, Section_Traffic, Unit_Field_Suffix
from zato.admin.web.forms.channel.hl7.mllp import CreateForm as MLLPCreateForm, EditForm as MLLPEditForm
from zato.admin.web.views.alerting_config_cells import _build_config_cell, _type_cells, _type_titles
from zato.common.alerting.object_config import alert_type_channels, alert_type_mllp_channel, get_defaults, get_field_names, \
    storage_name

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

class TestMllpChannelPopup:

    def test_the_lines_run_core_failures_traffic_without_anything_http(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_mllp_channel)

        line_names:'strlist' = []

        for line in config['lines']:
            line_names.append(line['name'])

        assert line_names == ['active', 'use_llm', 'llm', 'email', 'failures_in_a_row', 'error_rate', 'negative_acks',
            'slow_responses', 'silence']

        lines = _lines_by_name(config)

        assert lines['email']['section'] == Section_Core
        assert lines['negative_acks']['section'] == Section_Failures
        assert lines['silence']['section'] == Section_Traffic

        # A REST channel's HTTP lines are nowhere on an MLLP channel, and its acks are nowhere on a REST one
        for name in ('server_errors', 'auth_failures', 'client_errors', 'health_check', 'status_codes'):
            assert name not in lines, name

        assert 'negative_acks' not in _lines_by_name(alerts_tab.get_alerts_tab_config(alert_type_channels))

# ################################################################################################################################

    def test_the_negative_acks_line_carries_its_codes_and_summarises_them(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_mllp_channel)
        line = _lines_by_name(config)['negative_acks']

        assert line['kind'] == Line_Kind_Popover
        assert line['label'] == 'Negative acks'
        assert line['fields'] == [Ack_Codes_Field, 'ack_threshold', 'acks_window']
        assert line['rows'] == [[Ack_Codes_Field], ['ack_threshold', 'acks_window']]
        assert line['unit_field'] == Acks_Window_Unit_Field

        # The codes are typed as text with the default showing the shape ..
        assert line['text_fields'] == {Ack_Codes_Field: Ack_Codes_Default}
        assert Ack_Codes_Default == 'AE, AR, CE, CR'
        assert config['field_kinds'][Ack_Codes_Field] == 'text'

        # .. and the summary names the count, the codes text and the window with its unit.
        assert '{ack_threshold|ack|acks}' in line['summary']
        assert f'{{{Ack_Codes_Field}}}' in line['summary']
        assert f'{{{Acks_Window_Unit_Field}@acks_window}}' in line['summary']

        assert config['field_labels']['acks_window'] == 'In the last'
        assert config['field_labels']['ack_threshold'] == 'Alert after'

# ################################################################################################################################

    def test_the_silence_line_speaks_of_messages_and_says_only_whether_it_is_on(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_mllp_channel)
        line = _lines_by_name(config)['silence']

        assert line['label'] == 'On no messages'
        assert line['off_field'] == 'traffic_expected'
        assert line['summary_off'] == 'Alerts off'
        assert 'rule' in line['summary']
        assert 'message' in line['how_it_works']

        # A REST channel's line speaks of requests
        rest_line = _lines_by_name(alerts_tab.get_alerts_tab_config(alert_type_channels))['silence']
        assert rest_line['label'] == 'On no requests'
        assert rest_line['summary_off'] == 'Alerts off'

# ################################################################################################################################

    def test_the_wizard_forms_carry_every_field_of_the_type_and_nothing_http(self, req:'any_') -> 'None':

        defaults = get_defaults(alert_type_mllp_channel)

        for form_class in (MLLPCreateForm, MLLPEditForm):
            form = form_class(req=req)

            for name in get_field_names(alert_type_mllp_channel):
                assert storage_name(name) in form.fields, name

            assert form.fields[storage_name(Ack_Codes_Field)].initial == defaults['ack_codes']
            assert form.fields[storage_name('ack_threshold')].initial == defaults['ack_threshold']

            for name in ('auth_failures', 'client_errors', 'server_error_rate', 'status_codes', 'fault_codes', 'outcome_codes'):
                assert storage_name(name) not in form.fields, name

# ################################################################################################################################

    def test_the_edit_form_fields_are_prefixed(self, req:'any_') -> 'None':

        form = MLLPEditForm(req=req, prefix='edit')

        assert form['alert_ack_codes'].html_name == 'edit-alert_ack_codes'
        assert form['alert_ack_threshold'].html_name == 'edit-alert_ack_threshold'

# ################################################################################################################################

    def test_the_storage_names_carry_the_acks_window_with_its_unit(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_mllp_channel)
        storage_names = config['storage_field_names']

        assert storage_name('acks_window') in storage_names
        assert storage_name('acks_window' + Unit_Field_Suffix) in storage_names
        assert storage_name(Ack_Codes_Field) in storage_names

        for name in ('auth_failures', 'client_errors', 'server_error_rate'):
            assert storage_name(name) not in storage_names, name

# ################################################################################################################################

    def test_the_type_page_renders_the_mllp_row_with_its_text_cell(self) -> 'None':

        assert _type_titles['mllp_channel'] == 'MLLP channels'

        assert 'ack_codes' in _type_cells['mllp_channel']
        assert 'ack_codes' not in _type_cells['channels']
        assert 'ack_codes' not in _type_cells['fhir']

        for name in ('status_codes', 'fault_codes', 'outcome_codes', 'auth_failures'):
            assert name not in _type_cells['mllp_channel'], name

        values = {'ack_codes': 'AR, CR'}
        cell = _build_config_cell('ack_codes', 'text', values)

        assert cell == {
            'name': 'ack_codes',
            'label': 'Ack codes',
            'suffix': '',
            'kind': 'text',
            'value': 'AR, CR',
            'display': 'AR, CR',
        }

# ################################################################################################################################
# ################################################################################################################################
