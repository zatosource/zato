# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase
from unittest.mock import MagicMock

# Zato
from zato.common.api import CONNECTION, URL_TYPE
from zato.common.destination.constants import Channel_Fan_Out_Fields, Default_Delivery_Mode, Respond_From_Service
from zato.common.ext.bunch import Bunch
from zato.server.connection.http_soap.url_data import URLData
from zato.server.destination.channel import new_channel_item
from zato.server.destination.hook import get_config
from zato.server.service.internal.http_soap.destination_settings import prepare_destination_settings

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_channel_id = 4101
_channel_name = 'hl7.rest.adt-feed'
_url_path = '/api/hl7/v2'
_match_target = ':::(GET):::ZATO_ANY_INTERNAL:::/api/hl7/v2'

# One REST destination, in the JSON text the Dashboard writes
_destinations = '[{"name":"to-lab","type":"rest","connection":"lab-system","is_active":true}]'

# ################################################################################################################################
# ################################################################################################################################

def _make_url_data() -> 'URLData':
    out = object.__new__(URLData)
    out.config_manager = MagicMock()

    return out

# ################################################################################################################################

def _make_msg(**kwargs:'any_') -> 'Bunch':
    """ A channel create or edit message of a REST channel.
    """
    out = Bunch()
    out.id = _channel_id
    out.name = _channel_name
    out.url_path = _url_path
    out.service_name = 'hl7.adt.handle'
    out.transport = URL_TYPE.PLAIN_HTTP
    out.match_slash = False

    for key, value in kwargs.items():
        out[key] = value

    return out

# ################################################################################################################################

def _make_mllp_config(**kwargs:'any_') -> 'Bunch':
    """ The configuration the MLLP channel's wrapper builds its own channel item from.
    """
    out = Bunch()
    out.id = 77
    out.name = 'adt-feed'
    out.is_internal = False
    out.data_format = 'hl7-v2'
    out.destinations = _destinations
    out.respond_from = Respond_From_Service
    out.delivery_mode = Default_Delivery_Mode
    out.is_audit_export_payload_active = False

    for key, value in kwargs.items():
        out[key] = value

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestARestChannelItemHasTheFanOutItWasGiven(TestCase):
    """ A REST channel given a fan-out at create or edit time has it on the item the pipeline reads,
    in the same shape the MLLP channel's own item has, so that a message received over REST goes
    to the same places as one received over MLLP.
    """

    def test_a_rest_channel_with_destinations_fans_out_as_the_mllp_channel_does(self) -> 'None':

        url_data = _make_url_data()
        mllp_config = _make_mllp_config()

        msg = _make_msg()
        for name in Channel_Fan_Out_Fields:
            msg[name] = mllp_config[name]

        rest_item = url_data._channel_item_from_msg(msg, _match_target, {})
        mllp_item = new_channel_item(mllp_config)

        for name in Channel_Fan_Out_Fields:
            self.assertEqual(rest_item[name], mllp_item[name])

        rest_config = get_config(rest_item)
        mllp_config_parsed = get_config(mllp_item)

        self.assertIsNotNone(rest_config)
        self.assertIsNotNone(mllp_config_parsed)

        rest_names = sorted(entry.name for entry in rest_config.entries) # type: ignore[union-attr]
        mllp_names = sorted(entry.name for entry in mllp_config_parsed.entries) # type: ignore[union-attr]

        self.assertEqual(rest_names, mllp_names)

# ################################################################################################################################

    def test_a_rest_channel_without_a_fan_out_has_no_destinations_and_delivers_nowhere(self) -> 'None':

        url_data = _make_url_data()
        msg = _make_msg()

        rest_item = url_data._channel_item_from_msg(msg, _match_target, {})

        for name in Channel_Fan_Out_Fields:
            self.assertNotIn(name, rest_item)

        self.assertIsNone(get_config(rest_item))

# ################################################################################################################################
# ################################################################################################################################

class TestAChannelEditedWithoutAFanOutKeepsTheOneItHas(TestCase):
    """ The REST channel's own edit page sends no fan-out, so an edit from that page keeps the fan-out the
    MLLP channel gave the REST channel, whereas an edit that does send one replaces it.
    """

    def test_an_edit_that_sends_nothing_keeps_the_stored_fan_out(self) -> 'None':

        input = Bunch()
        input.connection = CONNECTION.CHANNEL
        input.transport = URL_TYPE.PLAIN_HTTP

        stored = {
            'destinations': _destinations,
            'respond_from': 'to-lab',
            'delivery_mode': Default_Delivery_Mode,
        }

        skip_opaque:'list[str]' = []
        prepare_destination_settings(input, skip_opaque, stored)

        for name in Channel_Fan_Out_Fields:
            self.assertEqual(input[name], stored[name])

        self.assertEqual(skip_opaque, [])

# ################################################################################################################################

    def test_an_edit_that_sends_a_fan_out_replaces_the_stored_one(self) -> 'None':

        input = Bunch()
        input.connection = CONNECTION.CHANNEL
        input.transport = URL_TYPE.PLAIN_HTTP
        input.destinations = '[]'
        input.respond_from = Respond_From_Service

        stored = {
            'destinations': _destinations,
            'respond_from': 'to-lab',
        }

        skip_opaque:'list[str]' = []
        prepare_destination_settings(input, skip_opaque, stored)

        self.assertEqual(input.destinations, '[]')
        self.assertEqual(input.respond_from, Respond_From_Service)

# ################################################################################################################################

    def test_a_new_channel_without_a_fan_out_is_stored_without_one(self) -> 'None':

        input = Bunch()
        input.connection = CONNECTION.CHANNEL
        input.transport = URL_TYPE.PLAIN_HTTP

        skip_opaque:'list[str]' = []
        prepare_destination_settings(input, skip_opaque, {})

        for name in Channel_Fan_Out_Fields:
            self.assertNotIn(name, input)

# ################################################################################################################################

    def test_an_outgoing_connection_has_no_fan_out_to_store(self) -> 'None':

        input = Bunch()
        input.connection = CONNECTION.OUTGOING
        input.transport = URL_TYPE.PLAIN_HTTP
        input.destinations = _destinations

        skip_opaque:'list[str]' = []
        prepare_destination_settings(input, skip_opaque, {})

        for name in Channel_Fan_Out_Fields:
            self.assertIn(name, skip_opaque)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
