# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How the Alerts tab's fields travel between a form and storage - a posted value typed the way the backend keeps it,
# a duration's count and unit joined into seconds on the way in and split back on the way out, and the tab's
# defaults agreeing with the shared ones.

# Zato
from zato.common.ext.bunch import Bunch

# Zato - Dashboard
from zato.admin.web import alerts_tab
from zato.admin.web.alerts_tab_lines import Arrival_Overdue_Unit_Default
from zato.common.alerting.object_config import alert_type_channels, alert_type_file_transfer, \
    get_defaults as get_storage_defaults

# ################################################################################################################################
# ################################################################################################################################

_alert_type = alert_type_file_transfer

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

    def test_join_unit_fields_stores_seconds_and_drops_the_unit(self) -> 'None':

        input_dict = {'name': 'abc', 'alert_window': 3, 'alert_window_unit': 'hour', 'alert_arrival_overdue_unit': 'day'}
        alerts_tab.join_unit_fields(_alert_type, input_dict)

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
        alerts_tab.join_unit_fields(alert_type_channels, input_dict)

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

    def test_split_unit_fields_reads_seconds_back_as_count_and_unit(self) -> 'None':

        item = Bunch(name='abc', alert_window=2 * 86400)
        alerts_tab.split_unit_fields(_alert_type, item)

        assert item.alert_window == 2
        assert item.alert_window_unit == 'day'
        assert item.alert_arrival_overdue_unit == Arrival_Overdue_Unit_Default

# ################################################################################################################################

    def test_round_trip_through_storage(self) -> 'None':

        input_dict = {}

        for name, value in (('alert_window', '90'), ('alert_window_unit', 'minute'), ('alert_is_active', 'on')):
            input_dict[name] = alerts_tab.pre_process_alert_item(_alert_type, name, value)

        alerts_tab.join_unit_fields(_alert_type, input_dict)
        assert input_dict['alert_window'] == 5400

        item = Bunch(input_dict)
        alerts_tab.split_unit_fields(_alert_type, item)

        assert item.alert_window == 90
        assert item.alert_window_unit == 'minute'
        assert item.alert_is_active is True

# ################################################################################################################################

    def test_tab_defaults_agree_with_the_shared_ones(self) -> 'None':

        tab_defaults = alerts_tab.get_form_defaults(_alert_type)
        shared_defaults = get_storage_defaults(_alert_type)

        for name, value in shared_defaults.items():
            if name == 'window':
                assert tab_defaults['window'] * 86400 == value
                continue
            assert tab_defaults[name] == value, name

# ################################################################################################################################
# ################################################################################################################################
