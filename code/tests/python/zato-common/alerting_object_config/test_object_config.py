# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.alerting import config_map
from zato.common.alerting.object_config import alert_type_file_transfer, apply_defaults, conn_type_to_alert_type, \
    decode_email_connection, Email_Conn_Type_IMAP, Email_Conn_Type_SMTP, Email_Connection_Default, Email_Connection_Field, \
    encode_email_connection, field_display, field_help, Field_Prefix, from_storage, get_defaults, get_field_kinds, \
    get_field_names, Is_Active_Field, Kind_Active, Kind_Email, storage_name, to_storage
from zato.common.api import GENERIC

# ################################################################################################################################
# ################################################################################################################################

_alert_type = alert_type_file_transfer

# ################################################################################################################################
# ################################################################################################################################

class TestFieldNames:

    def test_field_names_follow_config_map_between_active_and_email(self) -> 'None':

        names = get_field_names(_alert_type)

        assert names[0] == Is_Active_Field
        assert names[-1] == Email_Connection_Field

        own_names = []
        for field in config_map.type_fields[_alert_type]:
            own_names.append(field['name'])

        assert names[1:-1] == own_names
        assert names == [
            'is_active', 'consecutive_failures', 'warning_failures', 'error_failures', 'window',
            'arrival_overdue', 'test_transfers', 'use_llm', 'email_connection',
        ]

# ################################################################################################################################

    def test_field_kinds(self) -> 'None':

        kinds = get_field_kinds(_alert_type)

        assert kinds[Is_Active_Field] == Kind_Active
        assert kinds[Email_Connection_Field] == Kind_Email
        assert kinds['consecutive_failures'] == config_map.Kind_Number
        assert kinds['window'] == config_map.Kind_Duration
        assert kinds['test_transfers'] == config_map.Kind_Toggle
        assert kinds['use_llm'] == config_map.Kind_Ruleset_Toggle

# ################################################################################################################################

    def test_storage_name(self) -> 'None':
        assert Field_Prefix == 'alert_'
        assert storage_name('window') == 'alert_window'

# ################################################################################################################################

    def test_connection_types_map_to_the_file_transfer_type(self) -> 'None':

        for conn_type in (GENERIC.CONNECTION.TYPE.OUTCONN_SFTP, GENERIC.CONNECTION.TYPE.OUTCONN_FTP,
            GENERIC.CONNECTION.TYPE.OUTCONN_SMB):
            assert conn_type_to_alert_type[conn_type] == _alert_type

        assert GENERIC.CONNECTION.TYPE.OUTCONN_AS2 not in conn_type_to_alert_type

# ################################################################################################################################

    def test_every_field_has_display_and_help(self) -> 'None':

        for name in get_field_names(_alert_type):

            assert name in field_help, name

            # The Active switch and the email connection are not values with a label and a unit
            if name in (Is_Active_Field, Email_Connection_Field):
                continue

            label, unit = field_display[name]
            assert label
            assert isinstance(unit, str)

# ################################################################################################################################
# ################################################################################################################################

class TestDefaults:

    def test_defaults_come_from_the_seeded_rules(self) -> 'None':

        defaults = get_defaults(_alert_type)

        assert defaults == {
            'is_active': True,
            'consecutive_failures': 3,
            'warning_failures': 10,
            'error_failures': 20,
            'window': 86400,
            'arrival_overdue': 1,
            'test_transfers': False,
            'use_llm': True,
            'email_connection': Email_Connection_Default,
        }

# ################################################################################################################################

    def test_defaults_are_a_fresh_copy_each_time(self) -> 'None':

        first = get_defaults(_alert_type)
        first['window'] = 1

        second = get_defaults(_alert_type)
        assert second['window'] == 86400

# ################################################################################################################################

    def test_apply_defaults_fills_only_what_is_missing(self) -> 'None':

        item = {'name': 'abc', 'alert_window': 3600, 'alert_is_active': False}
        apply_defaults(_alert_type, item)

        assert item['name'] == 'abc'
        assert item['alert_window'] == 3600
        assert item['alert_is_active'] is False
        assert item['alert_consecutive_failures'] == 3
        assert item['alert_email_connection'] == Email_Connection_Default

        for name in get_field_names(_alert_type):
            assert storage_name(name) in item

# ################################################################################################################################
# ################################################################################################################################

class TestStorage:

    def test_to_storage_prefixes_only_known_fields(self) -> 'None':

        values = {'window': 60, 'is_active': True, 'unknown': 1}
        assert to_storage(_alert_type, values) == {'alert_window': 60, 'alert_is_active': True}

# ################################################################################################################################

    def test_from_storage_reads_only_what_the_object_carries(self) -> 'None':

        item = {'name': 'abc', 'alert_window': 60, 'alert_use_llm': False, 'other_field': 'x'}
        assert from_storage(_alert_type, item) == {'window': 60, 'use_llm': False}

# ################################################################################################################################

    def test_round_trip(self) -> 'None':

        values = get_defaults(_alert_type)
        values['error_failures'] = 7

        stored = to_storage(_alert_type, values)
        assert from_storage(_alert_type, stored) == values

# ################################################################################################################################
# ################################################################################################################################

class TestEmailConnection:

    def test_encode_decode(self) -> 'None':

        value = encode_email_connection(Email_Conn_Type_SMTP, 'ops.smtp')
        assert value == 'smtp:ops.smtp'
        assert decode_email_connection(value) == (Email_Conn_Type_SMTP, 'ops.smtp')

        # A name with the separator in it keeps it whole
        value = encode_email_connection(Email_Conn_Type_IMAP, 'a:b')
        assert decode_email_connection(value) == (Email_Conn_Type_IMAP, 'a:b')

# ################################################################################################################################

    def test_decode_without_a_kind(self) -> 'None':
        assert decode_email_connection('ops.smtp') == ('', 'ops.smtp')
        assert decode_email_connection('') == ('', '')

# ################################################################################################################################
# ################################################################################################################################
