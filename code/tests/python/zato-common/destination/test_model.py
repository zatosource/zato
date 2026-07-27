# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps, loads

# pytest
import pytest

# Zato
from zato.common.destination.constants import DeliveryMode, DestinationType, Respond_From_Service
from zato.common.destination.model import count_entries, describe_entries, dump_entries, get_entry, get_option, \
    has_active_entries, parse_config, parse_entries, select_entries, DestinationException

# ################################################################################################################################
# ################################################################################################################################

# The channel the tests configure destinations for
_channel_name = 'hl7.test.channel'

# The connections the destinations point at
_mllp_connection = 'hl7.forward.ehr'
_rest_connection = 'rest.billing'
_fhir_connection = 'fhir.ehr'

# ################################################################################################################################
# ################################################################################################################################

def _get_stored_list() -> 'str':
    """ Returns a destination list in the form a channel stores it - two destinations,
    each with the keys the Dashboard writes.
    """
    entries = [
        {
            'name': _mllp_connection,
            'type': DestinationType.MLLP,
            'connection': _mllp_connection,
            'is_active': True,
            'options': {},
        },
        {
            'name': _rest_connection,
            'type': DestinationType.REST,
            'connection': _rest_connection,
            'is_active': True,
            'options': {'method': 'PUT'},
        },
    ]

    out = dumps(entries)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestParsing:

    def test_a_stored_list_is_parsed_in_the_order_it_was_declared_in(self) -> 'None':
        entries = parse_entries(_get_stored_list())

        assert len(entries) == 2

        first = entries[0]
        second = entries[1]

        assert first.name == _mllp_connection
        assert first.type == DestinationType.MLLP
        assert first.connection == _mllp_connection
        assert first.is_active is True
        assert first.options == {}

        assert second.name == _rest_connection
        assert second.type == DestinationType.REST
        assert second.options == {'method': 'PUT'}

# ################################################################################################################################

    def test_a_channel_with_no_destinations_parses_to_an_empty_list(self) -> 'None':
        assert parse_entries('') == []

# ################################################################################################################################

    def test_a_list_that_was_already_parsed_is_accepted_as_it_is(self) -> 'None':
        entries = parse_entries([
            {'name': _fhir_connection, 'type': DestinationType.FHIR, 'connection': _fhir_connection},
        ])

        assert len(entries) == 1
        assert entries[0].connection == _fhir_connection

# ################################################################################################################################

    def test_a_destination_without_a_name_is_addressed_by_its_connection(self) -> 'None':
        entries = parse_entries([{'type': DestinationType.REST, 'connection': _rest_connection}])

        assert entries[0].name == _rest_connection

# ################################################################################################################################

    def test_a_destination_of_an_unknown_type_is_refused(self) -> 'None':
        with pytest.raises(DestinationException) as raised:
            _ = parse_entries([{'type': 'carrier-pigeon', 'connection': _rest_connection}])

        assert 'unknown type `carrier-pigeon`' in str(raised.value)

# ################################################################################################################################

    def test_a_destination_with_no_connection_is_refused(self) -> 'None':
        with pytest.raises(DestinationException):
            _ = parse_entries([{'type': DestinationType.REST}])

# ################################################################################################################################

    def test_a_destination_with_no_type_is_refused(self) -> 'None':
        with pytest.raises(DestinationException):
            _ = parse_entries([{'connection': _rest_connection}])

# ################################################################################################################################

    def test_a_list_that_is_not_json_is_refused(self) -> 'None':
        with pytest.raises(DestinationException) as raised:
            _ = parse_entries('this is not a destination list')

        assert 'not valid JSON' in str(raised.value)

# ################################################################################################################################

    def test_a_json_document_that_is_not_a_list_is_refused(self) -> 'None':
        with pytest.raises(DestinationException) as raised:
            _ = parse_entries(dumps({'connection': _rest_connection}))

        assert 'not a list' in str(raised.value)

# ################################################################################################################################
# ################################################################################################################################

class TestConfiguration:

    def test_a_channel_answers_from_its_service_by_default(self) -> 'None':
        config = parse_config(_channel_name, _get_stored_list())

        assert config.channel_name == _channel_name
        assert config.respond_from == Respond_From_Service
        assert config.delivery_mode == DeliveryMode.Same_Time

# ################################################################################################################################

    def test_a_channel_may_answer_from_one_of_its_destinations(self) -> 'None':
        config = parse_config(_channel_name, _get_stored_list(), _rest_connection, DeliveryMode.In_Order)

        assert config.respond_from == _rest_connection
        assert config.delivery_mode == DeliveryMode.In_Order

# ################################################################################################################################

    def test_a_channel_cannot_answer_from_a_destination_it_does_not_have(self) -> 'None':
        with pytest.raises(DestinationException) as raised:
            _ = parse_config(_channel_name, _get_stored_list(), 'rest.nowhere')

        assert 'replies from `rest.nowhere`' in str(raised.value)

# ################################################################################################################################

    def test_a_channel_cannot_deliver_in_a_mode_that_does_not_exist(self) -> 'None':
        with pytest.raises(DestinationException) as raised:
            _ = parse_config(_channel_name, _get_stored_list(), Respond_From_Service, 'whenever-it-suits')

        assert 'mode `whenever-it-suits`' in str(raised.value)

# ################################################################################################################################

    def test_the_mode_the_service_decides_in_is_not_available_yet(self) -> 'None':
        with pytest.raises(DestinationException):
            _ = parse_config(_channel_name, _get_stored_list(), Respond_From_Service, DeliveryMode.Service_Decides)

# ################################################################################################################################

    def test_unset_answers_mean_the_defaults_are_in_force(self) -> 'None':
        config = parse_config(_channel_name, _get_stored_list(), '', '')

        assert config.respond_from == Respond_From_Service
        assert config.delivery_mode == DeliveryMode.Same_Time

# ################################################################################################################################
# ################################################################################################################################

class TestLookups:

    def test_a_destination_is_found_by_the_name_it_is_addressed_by(self) -> 'None':
        config = parse_config(_channel_name, _get_stored_list())

        found = get_entry(config, _rest_connection)

        assert found
        assert found.connection == _rest_connection
        assert get_entry(config, 'rest.nowhere') is None

# ################################################################################################################################

    def test_an_option_a_destination_does_not_carry_comes_from_its_default(self) -> 'None':
        config = parse_config(_channel_name, _get_stored_list())

        with_method = get_entry(config, _rest_connection)
        without_method = get_entry(config, _mllp_connection)

        assert with_method
        assert without_method

        assert get_option(with_method, 'method', 'POST') == 'PUT'
        assert get_option(without_method, 'method', 'POST') == 'POST'

# ################################################################################################################################

    def test_a_channel_whose_every_destination_is_paused_reaches_none_of_them(self) -> 'None':
        active = parse_config(_channel_name, _get_stored_list())

        paused = parse_config(_channel_name, [
            {'name': _rest_connection, 'type': DestinationType.REST, 'connection': _rest_connection,
                'is_active': False},
        ])

        assert has_active_entries(active) is True
        assert has_active_entries(paused) is False

# ################################################################################################################################

    def test_a_channel_counts_the_destinations_it_declares(self) -> 'None':
        assert count_entries(_get_stored_list()) == 2
        assert count_entries('') == 0

# ################################################################################################################################

    def test_a_list_that_cannot_be_read_counts_as_no_destinations(self) -> 'None':
        assert count_entries('this is not a destination list') == 0

# ################################################################################################################################
# ################################################################################################################################

class TestStoredAndDescribedForms:

    def test_a_parsed_list_is_written_back_in_the_form_it_is_stored_in(self) -> 'None':
        entries = parse_entries(_get_stored_list())

        stored = dump_entries(entries)

        # What comes back out is what went in, which is what makes an import of an export work
        assert parse_entries(stored) == entries

# ################################################################################################################################

    def test_the_stored_form_carries_every_key_the_dashboard_reads(self) -> 'None':
        entries = parse_entries([{'type': DestinationType.MLLP, 'connection': _mllp_connection}])

        stored = loads(dump_entries(entries))

        assert stored == [{
            'name': _mllp_connection,
            'type': DestinationType.MLLP,
            'connection': _mllp_connection,
            'is_active': True,
            'options': {},
        }]

# ################################################################################################################################

    def test_a_channel_with_no_destinations_is_written_as_an_empty_list(self) -> 'None':
        assert loads(dump_entries([])) == []

# ################################################################################################################################

    def test_the_described_form_leaves_out_the_options_a_destination_does_not_have(self) -> 'None':
        entries = parse_entries(_get_stored_list())

        described = describe_entries(entries)

        # The first destination is of a type that takes no options at all ..
        assert 'options' not in described[0]
        assert described[0]['connection'] == _mllp_connection

        # .. while the second carries the one it was given.
        assert described[1]['options'] == {'method': 'PUT'}

# ################################################################################################################################

    def test_a_described_list_is_read_back_as_the_one_it_came_from(self) -> 'None':
        entries = parse_entries(_get_stored_list())

        assert parse_entries(describe_entries(entries)) == entries

# ################################################################################################################################
# ################################################################################################################################

class TestNarrowing:

    def test_one_message_may_go_to_some_of_the_destinations_only(self) -> 'None':
        config = parse_config(_channel_name, _get_stored_list())

        narrowed = select_entries(config, [_rest_connection])

        assert len(narrowed.entries) == 1
        assert narrowed.entries[0].connection == _rest_connection
        assert narrowed.channel_name == _channel_name
        assert narrowed.delivery_mode == config.delivery_mode

# ################################################################################################################################

    def test_naming_no_destination_narrows_to_none_of_them(self) -> 'None':
        config = parse_config(_channel_name, _get_stored_list())

        narrowed = select_entries(config, [])

        assert narrowed.entries == []

# ################################################################################################################################

    def test_a_reply_from_a_destination_left_out_comes_from_the_service(self) -> 'None':
        config = parse_config(_channel_name, _get_stored_list(), _rest_connection)

        # The destination that was to reply is not among the ones this message goes to ..
        narrowed = select_entries(config, [_mllp_connection])
        assert narrowed.respond_from == Respond_From_Service

        # .. while one that is keeps replying.
        kept = select_entries(config, [_rest_connection])
        assert kept.respond_from == _rest_connection

# ################################################################################################################################
# ################################################################################################################################
