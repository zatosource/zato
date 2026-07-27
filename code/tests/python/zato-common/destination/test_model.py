# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps

# pytest
import pytest

# Zato
from zato.common.destination.constants import DeliveryMode, DestinationType, Respond_From_Service
from zato.common.destination.model import get_entry, get_option, has_active_entries, parse_config, parse_entries, \
    DestinationException

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
# ################################################################################################################################
