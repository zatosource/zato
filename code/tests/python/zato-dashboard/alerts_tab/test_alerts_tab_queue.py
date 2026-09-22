# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Queue section of the Alerts tab - the two queue delivery lines every outgoing connection that can use a queue
# carries, REST, SOAP, FHIR and MLLP outgoing alike, each a popover over one number with no window, at the seeded
# defaults, in a section of their own at the end of the tab, and on no other type's tab. The cells of the alert
# rules screen carry the two fields for the same four types.

# Zato
from zato.admin.web import alerts_tab
from zato.admin.web.alerts_tab_lines import Line_Kind_Popover
from zato.admin.web.alerts_tab_lines_queue import queue_alert_types, Section_Queue
from zato.admin.web.views.alerting_config_cells import _build_config_cell, _type_cells
from zato.common.alerting.object_config import alert_type_channels, alert_type_fhir, alert_type_file_transfer, alert_type_llm, \
    alert_type_mcp, alert_type_mllp_channel, alert_type_mllp_outgoing, alert_type_rest, alert_type_soap, get_defaults
from zato.common.alerting.seed.rules_queue import DLQ_Threshold_Value, Queue_Depth_Threshold_Value

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strlist
    anydict = anydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The types whose connections have no queue
_other_types = (alert_type_channels, alert_type_file_transfer, alert_type_llm, alert_type_mcp, alert_type_mllp_channel)

# ################################################################################################################################
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

class TestQueueSection:

    def test_the_four_types_are_the_ones_that_can_use_a_queue(self) -> 'None':
        assert sorted(queue_alert_types) == sorted([alert_type_rest, alert_type_soap, alert_type_fhir, alert_type_mllp_outgoing])

# ################################################################################################################################

    def test_the_two_lines_close_the_tab_in_a_section_of_their_own(self) -> 'None':

        for alert_type in queue_alert_types:
            config = alerts_tab.get_alerts_tab_config(alert_type)

            line_names:'strlist' = []
            for line in config['lines']:
                line_names.append(line['name'])

            assert line_names[-2:] == ['dlq_messages', 'queue_backlog'], alert_type

            lines = _lines_by_name(config)
            assert lines['dlq_messages']['section'] == Section_Queue, alert_type
            assert lines['queue_backlog']['section'] == Section_Queue, alert_type

            # No line of any other section comes after them
            for line in config['lines'][:-2]:
                assert line['section'] != Section_Queue, (alert_type, line['name'])

# ################################################################################################################################

    def test_the_dlq_line_is_a_popover_over_one_number_with_no_window(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_rest)
        line = _lines_by_name(config)['dlq_messages']

        assert line['kind'] == Line_Kind_Popover
        assert line['label'] == 'Messages in the DLQ'
        assert line['fields'] == ['dlq_messages']
        assert line['rows'] == [['dlq_messages']]
        assert 'unit_field' not in line

        assert line['summary'] == 'Alert at {dlq_messages|message|messages} in the DLQ'
        assert 'DLQ' in line['how_it_works']

        assert config['field_labels']['dlq_messages'] == 'Alert at'
        assert config['field_kinds']['dlq_messages'] == 'number'

# ################################################################################################################################

    def test_the_backlog_line_is_a_popover_over_one_number_with_no_window(self) -> 'None':

        config = alerts_tab.get_alerts_tab_config(alert_type_mllp_outgoing)
        line = _lines_by_name(config)['queue_backlog']

        assert line['kind'] == Line_Kind_Popover
        assert line['label'] == 'Queue backlog'
        assert line['fields'] == ['queue_depth']
        assert line['rows'] == [['queue_depth']]
        assert 'unit_field' not in line

        assert line['summary'] == 'Alert at {queue_depth|message|messages} waiting in the queue'

        assert config['field_labels']['queue_depth'] == 'Alert at'
        assert config['field_kinds']['queue_depth'] == 'number'

# ################################################################################################################################

    def test_the_defaults_are_the_seeded_ones(self) -> 'None':

        for alert_type in queue_alert_types:
            defaults = get_defaults(alert_type)

            assert defaults['dlq_messages'] == DLQ_Threshold_Value, alert_type
            assert defaults['queue_depth'] == Queue_Depth_Threshold_Value, alert_type

# ################################################################################################################################

    def test_no_other_type_carries_the_section(self) -> 'None':

        for alert_type in _other_types:
            config = alerts_tab.get_alerts_tab_config(alert_type)
            lines = _lines_by_name(config)

            assert 'dlq_messages' not in lines, alert_type
            assert 'queue_backlog' not in lines, alert_type

            for line in config['lines']:
                assert line['section'] != Section_Queue, (alert_type, line['name'])

# ################################################################################################################################
# ################################################################################################################################

class TestQueueCells:

    def test_the_four_types_carry_the_two_cells_before_the_llm_one(self) -> 'None':

        for alert_type in queue_alert_types:
            cells = _type_cells[alert_type]
            assert cells[-3:] == ['dlq_messages', 'queue_depth', 'use_llm'], alert_type

        for alert_type in _other_types:
            assert 'dlq_messages' not in _type_cells[alert_type], alert_type
            assert 'queue_depth' not in _type_cells[alert_type], alert_type

# ################################################################################################################################

    def test_the_cells_read_as_plain_numbers(self) -> 'None':

        values = {'dlq_messages': 1, 'queue_depth': 1000}

        cell = _build_config_cell('dlq_messages', 'number', values)
        assert cell == {
            'name': 'dlq_messages',
            'label': 'DLQ messages',
            'suffix': '',
            'kind': 'number',
            'value': 1,
            'display': '1',
        }

        cell = _build_config_cell('queue_depth', 'number', values)
        assert cell is not None
        assert cell['label'] == 'Queue depth'
        assert cell['display'] == '1000'

# ################################################################################################################################
# ################################################################################################################################
