# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import contextmanager
from datetime import datetime

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Zato
from zato.common.alerting.collectors.common import Measure_Auth_Failures, Measure_Error_Rate, Measure_File_Runs, \
    Measure_Latency
from zato.common.alerting.object_config import alert_type_channels, alert_type_file_transfer, encode_email_connection, \
    Email_Conn_Type_IMAP, get_defaults, to_storage
from zato.common.alerting.object_settings import build_rule_values, build_window_seconds_by_object, get_email_connection, \
    get_llm_connection, get_muted_rule_names, get_names_with_toggle, get_silence_expected_names, is_object_active, \
    load_object_settings
from zato.common.api import CONNECTION, FileTransfer, GENERIC, URL_TYPE
from zato.common.audit_log.api import AuditSource
from zato.common.json_internal import dumps
from zato.common.odb.model import Base, Cluster, GenericConn, HTTPSOAP
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, stranydict
    any_ = any_
    sessiongen = Iterator[SASession]
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The moment the slot tests resolve against - ten in the morning UTC
_now = datetime(2026, 9, 12, 10, 0, 0)

# ################################################################################################################################
# ################################################################################################################################

# The cluster the test connections belong to, and one they do not
_cluster_id = 1
_other_cluster_id = 2

# The connections the tests store
_sftp_name = 'sftp.settings'
_ftp_name = 'ftp.settings'
_other_cluster_name = 'sftp.elsewhere'
_as2_name = 'as2.no-alerts'

# The schedules the SFTP connection carries
_schedule_name = 'Daily results'
_other_schedule_name = 'Weekly summary'

# The email connection the SFTP connection's alerts leave through
_imap_name = 'Ops mailbox'

# The channels the tests store - a REST channel with settings, one without, a SOAP channel with settings
# and an outgoing connection of each transport
_rest_channel_name = 'orders.api'
_plain_rest_channel_name = 'orders.status'
_soap_channel_name = 'orders.soap'
_rest_outgoing_name = 'crm.api'
_soap_outgoing_name = 'crm.soap'

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def _session() -> 'sessiongen':
    """ An in-memory SQLite database with the cluster and generic connection tables and two clusters.
    """
    engine = create_engine('sqlite://')

    tables = [
        Cluster.__table__,
        GenericConn.__table__,
        HTTPSOAP.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)

    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    session.add(Cluster(_cluster_id, 'test-cluster', '', 'sqlite'))
    session.add(Cluster(_other_cluster_id, 'other-cluster', '', 'sqlite'))
    session.commit()

    yield session

    session.close()
    engine.dispose()

# ################################################################################################################################

def _add_connection(session:'SASession', name:'str', conn_type:'str', cluster_id:'int', opaque:'stranydict') -> 'None':
    """ Stores one generic connection with the given opaque attributes.
    """
    item = cast_('any_', GenericConn())
    item.name = name
    item.type_ = conn_type
    item.is_active = True
    item.is_internal = False
    item.is_channel = False
    item.is_outconn = True
    item.cluster_id = cluster_id
    item.opaque1 = dumps(opaque)

    session.add(item)
    session.commit()

# ################################################################################################################################

def _add_http_soap(
    session:'SASession',
    name:'str',
    connection:'str',
    transport:'str',
    cluster_id:'int',
    opaque:'stranydict',
    ) -> 'None':
    """ Stores one HTTPSOAP row with the given opaque attributes.
    """
    item = cast_('any_', HTTPSOAP())
    item.name = name
    item.is_active = True
    item.is_internal = False
    item.connection = connection
    item.transport = transport
    item.url_path = '/' + name
    item.soap_action = ''
    item.cluster = session.query(Cluster).filter(Cluster.id==cluster_id).one()
    item.opaque1 = dumps(opaque)

    session.add(item)
    session.commit()

# ################################################################################################################################

def _new_schedule(name:'str') -> 'stranydict':
    """ The fields a stored schedule always carries.
    """
    out = {
        'id': name,
        'name': name,
        'directory': '/incoming',
        'expected_by': '09:00',
    }
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestLoadObjectSettings:

    def test_every_alert_type_is_present_even_with_no_connections(self) -> 'None':
        with _session() as session:
            settings = load_object_settings(session, _cluster_id)

        assert settings == {alert_type_file_transfer: {}, alert_type_channels: {}}

# ################################################################################################################################

    def test_a_connection_without_stored_settings_reads_at_the_defaults(self) -> 'None':
        with _session() as session:
            _add_connection(session, _sftp_name, GENERIC.CONNECTION.TYPE.OUTCONN_SFTP, _cluster_id, {})
            settings = load_object_settings(session, _cluster_id)

        by_object = settings[alert_type_file_transfer]

        assert list(by_object) == [_sftp_name]
        assert by_object[_sftp_name] == get_defaults(alert_type_file_transfer)

# ################################################################################################################################

    def test_stored_settings_win_over_the_defaults(self) -> 'None':
        stored = to_storage(alert_type_file_transfer, {'warning_failures': 2, 'is_active': False, 'llm_connection': 'ops.llm'})

        with _session() as session:
            _add_connection(session, _ftp_name, GENERIC.CONNECTION.TYPE.OUTCONN_FTP, _cluster_id, stored)
            settings = load_object_settings(session, _cluster_id)

        values = settings[alert_type_file_transfer][_ftp_name]

        assert values['warning_failures'] == 2
        assert values['is_active'] is False
        assert values['llm_connection'] == 'ops.llm'

        # What was not stored is still at its default
        assert values['error_failures'] == 20
        assert values['use_llm'] is True

# ################################################################################################################################

    def test_a_schedule_reads_its_connections_settings(self) -> 'None':
        stored = to_storage(alert_type_file_transfer, {'arrival_overdue': 3})
        stored[FileTransfer.Scheduler.Schedules_Field] = [_new_schedule(_schedule_name), _new_schedule(_other_schedule_name)]

        with _session() as session:
            _add_connection(session, _sftp_name, GENERIC.CONNECTION.TYPE.OUTCONN_SFTP, _cluster_id, stored)
            settings = load_object_settings(session, _cluster_id)

        by_object = settings[alert_type_file_transfer]

        assert sorted(by_object) == sorted([_sftp_name, _schedule_name, _other_schedule_name])
        assert by_object[_schedule_name]['arrival_overdue'] == 3
        assert by_object[_other_schedule_name] == by_object[_sftp_name]

# ################################################################################################################################

    def test_other_clusters_and_other_types_are_left_out(self) -> 'None':
        with _session() as session:
            _add_connection(session, _sftp_name, GENERIC.CONNECTION.TYPE.OUTCONN_SFTP, _cluster_id, {})
            _add_connection(session, _other_cluster_name, GENERIC.CONNECTION.TYPE.OUTCONN_SFTP, _other_cluster_id, {})
            _add_connection(session, _as2_name, GENERIC.CONNECTION.TYPE.OUTCONN_AS2, _cluster_id, {})
            settings = load_object_settings(session, _cluster_id)

        assert list(settings[alert_type_file_transfer]) == [_sftp_name]

# ################################################################################################################################

    def test_rest_and_soap_channels_load_under_channels(self) -> 'None':
        stored = to_storage(alert_type_channels, {'consecutive_failures': 5, 'traffic_expected': True})
        soap_stored = to_storage(alert_type_channels, {'auth_failures': 3})

        with _session() as session:
            _add_http_soap(session, _rest_channel_name, CONNECTION.CHANNEL, URL_TYPE.PLAIN_HTTP, _cluster_id, stored)
            _add_http_soap(session, _plain_rest_channel_name, CONNECTION.CHANNEL, URL_TYPE.PLAIN_HTTP, _cluster_id, {})
            _add_http_soap(session, _soap_channel_name, CONNECTION.CHANNEL, URL_TYPE.SOAP, _cluster_id, soap_stored)
            _add_http_soap(session, _rest_outgoing_name, CONNECTION.OUTGOING, URL_TYPE.PLAIN_HTTP, _cluster_id, {})
            _add_http_soap(session, _soap_outgoing_name, CONNECTION.OUTGOING, URL_TYPE.SOAP, _cluster_id, {})
            _add_http_soap(session, 'elsewhere.api', CONNECTION.CHANNEL, URL_TYPE.PLAIN_HTTP, _other_cluster_id, {})
            settings = load_object_settings(session, _cluster_id)

        by_channel = settings[alert_type_channels]

        assert sorted(by_channel) == sorted([_rest_channel_name, _plain_rest_channel_name, _soap_channel_name])

        assert by_channel[_rest_channel_name]['consecutive_failures'] == 5
        assert by_channel[_rest_channel_name]['traffic_expected'] is True
        assert by_channel[_rest_channel_name]['auth_failures'] == 10

        assert by_channel[_plain_rest_channel_name] == get_defaults(alert_type_channels)

        assert by_channel[_soap_channel_name]['auth_failures'] == 3
        assert by_channel[_soap_channel_name]['consecutive_failures'] == 3

# ################################################################################################################################
# ################################################################################################################################

class TestChannelSettings:

    def test_a_channel_with_alerts_off_is_not_active(self) -> 'None':
        values = get_defaults(alert_type_channels)
        values['is_active'] = False

        assert is_object_active(values) is False

# ################################################################################################################################

    def test_a_channels_numbers_stand_in_for_the_rule_defaults(self) -> 'None':
        values = get_defaults(alert_type_channels)
        values['consecutive_failures'] = 5
        values['server_errors'] = 20
        values['auth_failures_window'] = 3600

        rule_values = build_rule_values(alert_type_channels, values, _now)

        assert rule_values['max_consecutive_failures'] == 5
        assert rule_values['server_error_rate_threshold'] == 0.2
        assert rule_values['silence_seconds'] == 3600
        assert 'traffic_expected' not in rule_values
        assert 'silence_slots' not in rule_values

        # Every window of a channel is a window_seconds - the error rate's speaks when no rule is named,
        # the one of the rule being matched otherwise
        assert rule_values['window_seconds'] == 300
        assert build_rule_values(alert_type_channels, values, _now, 'Auth_Failures')['window_seconds'] == 3600
        assert build_rule_values(alert_type_channels, values, _now, 'Server_Errors')['window_seconds'] == 300

# ################################################################################################################################

    def test_traffic_expected_off_mutes_channel_silent(self) -> 'None':
        values = get_defaults(alert_type_channels)

        assert values['traffic_expected'] is False
        assert get_muted_rule_names(alert_type_channels, values, _now) == ['Channel_Silent']

        values['traffic_expected'] = True
        assert get_muted_rule_names(alert_type_channels, values, _now) == []

# ################################################################################################################################

    def test_the_slot_of_the_moment_decides_the_silence(self) -> 'None':
        values = get_defaults(alert_type_channels)
        values['traffic_expected'] = False
        values['silence_window'] = 3600

        # Business hours expect a request every fifteen minutes, the all-day slot expects nothing
        values['silence_slots'] = dumps([
            {'time_from': '09:00', 'time_to': '17:00', 'is_on': True, 'silence_seconds': 900},
        ])

        assert get_muted_rule_names(alert_type_channels, values, _now) == []
        assert build_rule_values(alert_type_channels, values, _now)['silence_seconds'] == 900

        night = datetime(2026, 9, 12, 23, 0, 0)

        assert get_muted_rule_names(alert_type_channels, values, night) == ['Channel_Silent']
        assert build_rule_values(alert_type_channels, values, night)['silence_seconds'] == 3600

# ################################################################################################################################

    def test_a_slot_switched_off_mutes_the_all_day_switch(self) -> 'None':
        values = get_defaults(alert_type_channels)
        values['traffic_expected'] = True
        values['silence_slots'] = dumps([
            {'time_from': '09:00', 'time_to': '17:00', 'is_on': False, 'silence_seconds': 900},
        ])

        assert get_muted_rule_names(alert_type_channels, values, _now) == ['Channel_Silent']

# ################################################################################################################################

    def test_the_channels_expecting_traffic(self) -> 'None':
        expecting = get_defaults(alert_type_channels)
        expecting['traffic_expected'] = True

        quiet = get_defaults(alert_type_channels)

        off = get_defaults(alert_type_channels)
        off['traffic_expected'] = True
        off['is_active'] = False

        by_object = {_rest_channel_name: expecting, _plain_rest_channel_name: quiet, _soap_channel_name: off}
        object_settings = {alert_type_channels: by_object}

        assert get_names_with_toggle(by_object, 'traffic_expected') == {_rest_channel_name, _soap_channel_name}
        assert get_silence_expected_names(object_settings, _now) == {_rest_channel_name}
        assert get_silence_expected_names({alert_type_file_transfer: {}}, _now) == set()

# ################################################################################################################################

    def test_a_channels_own_windows_apply_to_rest_and_soap_channels(self) -> 'None':
        values = get_defaults(alert_type_channels)
        values['auth_failures_window'] = 3600

        object_settings = {alert_type_channels: {_rest_channel_name: values}}

        source_windows = {
            Measure_Error_Rate: 300,
            Measure_Auth_Failures: 300,
            Measure_Latency: 300,
        }
        window_seconds_by_source = {
            AuditSource.REST_Channel: source_windows,
            AuditSource.SOAP_Channel: source_windows,
            AuditSource.MLLP_Channel: source_windows,
        }

        out = build_window_seconds_by_object(object_settings, window_seconds_by_source)

        for source in (AuditSource.REST_Channel, AuditSource.SOAP_Channel):
            assert out[source][_rest_channel_name][Measure_Auth_Failures] == 3600
            assert Measure_Error_Rate not in out[source][_rest_channel_name]
            assert Measure_Latency not in out[source][_rest_channel_name]

        # An MLLP channel has no settings of its own, so no window of its own either
        assert AuditSource.MLLP_Channel not in out

# ################################################################################################################################
# ################################################################################################################################

class TestRuleValues:

    def test_numbers_travel_under_the_names_the_rules_read(self) -> 'None':
        values = get_defaults(alert_type_file_transfer)
        values['consecutive_failures'] = 5
        values['window'] = 3600

        rule_values = build_rule_values(alert_type_file_transfer, values)

        assert rule_values == {
            'max_consecutive_failures': 5,
            'warning_failure_count': 10,
            'error_failure_count': 20,
            'window_seconds': 3600,
            'arrival_overdue_multiplier': 1,
        }

# ################################################################################################################################

    def test_toggles_carry_no_rule_value(self) -> 'None':
        values = get_defaults(alert_type_file_transfer)
        rule_values = build_rule_values(alert_type_file_transfer, values)

        assert 'test_transfers' not in rule_values
        assert 'use_llm' not in rule_values
        assert 'is_active' not in rule_values

# ################################################################################################################################
# ################################################################################################################################

class TestMutedRules:

    def test_a_toggle_that_is_off_mutes_its_rules(self) -> 'None':
        values = get_defaults(alert_type_file_transfer)
        values['test_transfers'] = False

        assert get_muted_rule_names(alert_type_file_transfer, values) == ['Test_Transfer_Failing']

# ################################################################################################################################

    def test_a_toggle_that_is_on_mutes_nothing(self) -> 'None':
        values = get_defaults(alert_type_file_transfer)
        values['test_transfers'] = True

        assert get_muted_rule_names(alert_type_file_transfer, values) == []

# ################################################################################################################################

    def test_the_llm_toggle_mutes_nothing_either_way(self) -> 'None':
        values = get_defaults(alert_type_file_transfer)
        values['test_transfers'] = True
        values['use_llm'] = False

        assert get_muted_rule_names(alert_type_file_transfer, values) == []

# ################################################################################################################################
# ################################################################################################################################

class TestActiveAndEmail:

    def test_is_active(self) -> 'None':
        values = get_defaults(alert_type_file_transfer)
        assert is_object_active(values) is True

        values['is_active'] = False
        assert is_object_active(values) is False

# ################################################################################################################################

    def test_email_connection(self) -> 'None':
        values = get_defaults(alert_type_file_transfer)
        assert get_email_connection(values) == ''

        values['email_connection'] = encode_email_connection(Email_Conn_Type_IMAP, _imap_name)
        assert get_email_connection(values) == encode_email_connection(Email_Conn_Type_IMAP, _imap_name)

# ################################################################################################################################

    def test_llm_connection(self) -> 'None':
        values = get_defaults(alert_type_file_transfer)
        assert get_llm_connection(values) == ''

        values['llm_connection'] = 'ops.llm'
        assert get_llm_connection(values) == 'ops.llm'

# ################################################################################################################################
# ################################################################################################################################

class TestWindowByObject:

    def test_only_objects_with_a_window_of_their_own_are_listed(self) -> 'None':
        same = get_defaults(alert_type_file_transfer)
        own = get_defaults(alert_type_file_transfer)
        own['window'] = 600

        object_settings = {alert_type_file_transfer: {_sftp_name: same, _ftp_name: own}}
        source_windows = {Measure_Error_Rate: 86400, Measure_Latency: 86400, Measure_File_Runs: 86400}
        window_seconds_by_source = {AuditSource.File_Outgoing: source_windows}

        out = build_window_seconds_by_object(object_settings, window_seconds_by_source)

        own_windows = {Measure_Error_Rate: 600, Measure_Latency: 600, Measure_File_Runs: 600}
        assert out == {AuditSource.File_Outgoing: {_ftp_name: own_windows}}

# ################################################################################################################################

    def test_without_a_source_window_every_object_is_measured_on_its_own(self) -> 'None':
        values = get_defaults(alert_type_file_transfer)
        object_settings = {alert_type_file_transfer: {_sftp_name: values}}

        out = build_window_seconds_by_object(object_settings, {})

        own_windows = {Measure_Error_Rate: 86400, Measure_Latency: 86400, Measure_File_Runs: 86400}
        assert out == {AuditSource.File_Outgoing: {_sftp_name: own_windows}}

# ################################################################################################################################

    def test_no_settings_no_windows(self) -> 'None':
        source_windows = {Measure_Error_Rate: 86400, Measure_Latency: 86400, Measure_File_Runs: 86400}
        out = build_window_seconds_by_object({alert_type_file_transfer: {}}, {AuditSource.File_Outgoing: source_windows})
        assert out == {}

# ################################################################################################################################
# ################################################################################################################################
