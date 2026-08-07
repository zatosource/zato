# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from contextlib import contextmanager

# Zato
from common import audit_log_env, delete_all_events
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.audit_log.reports import Range_Day
from zato.common.audit_log.usage import get_object_options, get_usage, normalize_sources, usage_csv, Usage_Sources
from zato.common.hl7.audit import audit_ack_sent
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import anylist

    envgen = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-usage-server'

# One object of each covered kind
_rest_channel  = 'usage.test.rest-channel'
_soap_channel  = 'usage.test.soap-channel'
_rest_outgoing = 'usage.test.rest-outgoing'
_mllp_channel  = 'usage.test.mllp-channel'
_mllp_outgoing = 'usage.test.mllp-outgoing'
_fhir_outgoing = 'usage.test.fhir-outgoing'

# The security definition the REST channel's caller authenticated with
_rest_caller = 'usage.test.caller'

# The sending facility of the MLLP channel's messages - MLLP's caller identity
_mllp_facility = 'CLINIC_A'

# What a caller with no identity at all is reported as
_caller_anonymous = 'Anonymous'

# Hostile object values that must be treated as plain names - no error, no match
_hostile_names = [
    "'; DROP TABLE event; --",
    'a"b\'c',
    'name&with=query#chars',
]

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def _usage_env(tmp_path:'os.PathLike') -> 'envgen':
    """ A per-test SQLite audit database with the usage events seeded.
    """
    db_path = os.path.join(str(tmp_path), 'audit.db')

    details = {
        'type': AuditLogCtx.Type_SQLite,
        'name': db_path,
    }

    with audit_log_env(details):
        delete_all_events()
        _seed_events()
        yield

# ################################################################################################################################

def _seed_events() -> 'None':
    """ One completed exchange per covered source, plus decoys that must never count -
    request-sent rows of the same sources and events of sources the page does not cover.
    """
    audit_log = AuditLog(_server_name)

    # The REST channel's caller authenticated, twice, so its pair counts two calls
    audit_log.insert(AuditSource.REST_Channel, AuditEvent.Response_Sent, _rest_channel,
        cid='cid-rest-1', ext_client_id=_rest_caller, outcome=AuditOutcome.OK)
    audit_log.insert(AuditSource.REST_Channel, AuditEvent.Response_Sent, _rest_channel,
        cid='cid-rest-2', ext_client_id=_rest_caller, outcome=AuditOutcome.OK)

    # One completing event for each of the other covered sources - the MLLP channel's
    # acknowledgment goes through the real writer, which records the sending facility
    # as the caller identity
    audit_log.insert(AuditSource.SOAP_Channel, AuditEvent.Response_Sent, _soap_channel,
        cid='cid-soap-1', outcome=AuditOutcome.OK)
    audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Response_Received, _rest_outgoing,
        cid='cid-out-1', outcome=AuditOutcome.OK)
    _ = audit_ack_sent(audit_log, _mllp_channel, 'AA', 'MSA|AA|MSG00001',
        cid='cid-mllp-1', msg_id='MSG00001', facility=_mllp_facility)
    audit_log.insert(AuditSource.MLLP_Outgoing, AuditEvent.Ack_Received, _mllp_outgoing,
        cid='cid-mllp-out-1', outcome=AuditOutcome.OK)
    audit_log.insert(AuditSource.FHIR, AuditEvent.Response_Received, _fhir_outgoing,
        cid='cid-fhir-1', outcome=AuditOutcome.OK)

    # Decoys - a request-sent row of a covered outgoing source, the extra row
    # a destination delivery writes, must not double the count ..
    audit_log.insert(AuditSource.MLLP_Outgoing, AuditEvent.Request_Sent, _mllp_outgoing,
        cid='cid-mllp-out-1', outcome=AuditOutcome.OK)
    audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _rest_outgoing,
        cid='cid-out-1', outcome=AuditOutcome.OK)

    # .. and events of sources the page does not cover at all.
    audit_log.insert(AuditSource.Email_IMAP, AuditEvent.Message_Received, 'usage.test.imap',
        cid='cid-imap-1', outcome=AuditOutcome.OK)

# ################################################################################################################################

def _rows_for(rows:'anylist', name:'str') -> 'anylist':
    out = [item for item in rows if item.channel == name]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestGetUsage:

    def test_only_the_completing_event_of_each_source_counts(self, tmp_path:'os.PathLike') -> 'None':

        with _usage_env(tmp_path):
            now = utcnow()
            rows = get_usage(now, Range_Day, [], [])

            # One row per object and caller - the six seeded objects, nothing else,
            # so no request-sent decoy and no IMAP event made it in
            names = sorted(row.channel for row in rows)
            expected = sorted([
                _rest_channel, _soap_channel, _rest_outgoing,
                _mllp_channel, _mllp_outgoing, _fhir_outgoing,
            ])
            assert names == expected

            # The outgoing rows count their one completing event, not the extra request-sent
            outgoing_row = _rows_for(rows, _mllp_outgoing)[0]
            assert outgoing_row.calls == 1

            rest_outgoing_row = _rows_for(rows, _rest_outgoing)[0]
            assert rest_outgoing_row.calls == 1

# ################################################################################################################################

    def test_each_row_carries_its_source_and_caller(self, tmp_path:'os.PathLike') -> 'None':

        with _usage_env(tmp_path):
            now = utcnow()
            rows = get_usage(now, Range_Day, [], [])

            rest_row = _rows_for(rows, _rest_channel)[0]
            assert rest_row.source == AuditSource.REST_Channel
            assert rest_row.caller == _rest_caller
            assert rest_row.calls == 2

            # An MLLP channel's caller is the sending facility of its messages
            mllp_row = _rows_for(rows, _mllp_channel)[0]
            assert mllp_row.source == AuditSource.MLLP_Channel
            assert mllp_row.caller == _mllp_facility

            # An exchange recorded with no identity at all came from an anonymous caller
            fhir_row = _rows_for(rows, _fhir_outgoing)[0]
            assert fhir_row.source == AuditSource.FHIR
            assert fhir_row.caller == _caller_anonymous

# ################################################################################################################################

    def test_the_sources_filter_narrows_the_rows(self, tmp_path:'os.PathLike') -> 'None':

        with _usage_env(tmp_path):
            now = utcnow()
            rows = get_usage(now, Range_Day, [AuditSource.MLLP_Channel, AuditSource.MLLP_Outgoing], [])

            names = sorted(row.channel for row in rows)
            assert names == sorted([_mllp_channel, _mllp_outgoing])

# ################################################################################################################################

    def test_the_objects_filter_narrows_the_rows(self, tmp_path:'os.PathLike') -> 'None':

        with _usage_env(tmp_path):
            now = utcnow()
            rows = get_usage(now, Range_Day, [], [_rest_channel, _fhir_outgoing])

            names = sorted(row.channel for row in rows)
            assert names == sorted([_rest_channel, _fhir_outgoing])

# ################################################################################################################################

    def test_unknown_sources_are_dropped(self, tmp_path:'os.PathLike') -> 'None':

        with _usage_env(tmp_path):
            now = utcnow()

            # Nothing the map does not know ever reaches a query - dropping every pick
            # means no source filter at all, so all the covered rows come back
            rows = get_usage(now, Range_Day, ['no-such-source', "'; DROP TABLE event; --"], [])
            assert len(rows) == 6

            # A hostile pick next to a real one leaves the real one alone
            rows = get_usage(now, Range_Day, ['no-such-source', AuditSource.FHIR], [])
            assert len(rows) == 1
            assert rows[0].channel == _fhir_outgoing

# ################################################################################################################################

    def test_hostile_object_values_are_plain_values(self, tmp_path:'os.PathLike') -> 'None':

        with _usage_env(tmp_path):
            now = utcnow()

            # No error and no match - the values bind as query parameters
            rows = get_usage(now, Range_Day, [], _hostile_names)
            assert rows == []

# ################################################################################################################################

    def test_the_link_carries_the_name_url_quoted(self, tmp_path:'os.PathLike') -> 'None':

        audit_log_details = {
            'type': AuditLogCtx.Type_SQLite,
            'name': os.path.join(str(tmp_path), 'audit.db'),
        }

        hostile_name = 'name&with=query#chars'

        with audit_log_env(audit_log_details):
            delete_all_events()

            audit_log = AuditLog(_server_name)
            audit_log.insert(AuditSource.REST_Channel, AuditEvent.Response_Sent, hostile_name,
                cid='cid-hostile-1', outcome=AuditOutcome.OK)

            now = utcnow()
            rows = get_usage(now, Range_Day, [], [])

            assert len(rows) == 1

            # The raw name never appears in the link - its unsafe characters are quoted
            link = rows[0].link
            assert f'object_name={hostile_name}' not in link
            assert 'object_name=name%26with%3Dquery%23chars' in link

# ################################################################################################################################
# ################################################################################################################################

class TestNormalizeSources:

    def test_only_covered_sources_survive(self) -> 'None':

        picked = [AuditSource.REST_Channel, 'no-such-source', AuditSource.FHIR]
        assert normalize_sources(picked) == [AuditSource.REST_Channel, AuditSource.FHIR]

        assert normalize_sources([]) == []

# ################################################################################################################################

    def test_the_covered_sources_are_the_six_expected_ones(self) -> 'None':

        expected = (
            AuditSource.REST_Channel,
            AuditSource.REST_Outgoing,
            AuditSource.SOAP_Channel,
            AuditSource.MLLP_Channel,
            AuditSource.MLLP_Outgoing,
            AuditSource.FHIR,
        )
        assert Usage_Sources == expected

# ################################################################################################################################
# ################################################################################################################################

class TestGetObjectOptions:

    def test_names_are_grouped_under_their_sources(self, tmp_path:'os.PathLike') -> 'None':

        with _usage_env(tmp_path):
            options = get_object_options()

            assert options[AuditSource.REST_Channel] == [_rest_channel]
            assert options[AuditSource.SOAP_Channel] == [_soap_channel]
            assert options[AuditSource.REST_Outgoing] == [_rest_outgoing]
            assert options[AuditSource.MLLP_Channel] == [_mllp_channel]
            assert options[AuditSource.MLLP_Outgoing] == [_mllp_outgoing]
            assert options[AuditSource.FHIR] == [_fhir_outgoing]

            # Only the covered sources are offered - the IMAP decoy has no entry
            assert AuditSource.Email_IMAP not in options

# ################################################################################################################################
# ################################################################################################################################

class TestUsageCSV:

    def test_the_table_renders_with_the_type_column(self, tmp_path:'os.PathLike') -> 'None':

        with _usage_env(tmp_path):
            now = utcnow()
            rows = get_usage(now, Range_Day, [AuditSource.REST_Channel], [])

            content = usage_csv(rows)
            lines = content.strip().splitlines()

            assert lines[0] == 'channel,type,caller,calls,first_call,last_call'

            # The one REST channel row carries its source as the type and its call count
            assert lines[1].startswith(f'{_rest_channel},{AuditSource.REST_Channel},{_rest_caller},2,')

# ################################################################################################################################
# ################################################################################################################################
