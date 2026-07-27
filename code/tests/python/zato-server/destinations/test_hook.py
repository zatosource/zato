# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditOutcome
from zato.common.destination.constants import DeliveryMode, DestinationType, Respond_From_Service
from zato.common.destination.coordinator import new_transports
from zato.common.typing_ import cast_
from zato.server.destination.hook import get_config, run_destinations, run_for_service, ServiceDispatcher

from fake_service import FakeService, MLLP_Response

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.destination.coordinator import DeliveryTransports
    from zato.common.destination.model import ChannelDestinationConfig
    from zato.common.typing_ import any_, anylist, stranydict
    from zato.server.service import Service

    anylist = anylist
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The channel whose destinations the tests deliver to
_channel_name = 'hl7.test.channel'

# The connections the destinations point at
_mllp_connection = 'hl7.forward.ehr'
_rest_connection = 'rest.billing'

# What arrived on the channel
_request_payload = 'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FACILITY|20260101120000||ADT^A01|MSG00001|P|2.5'

# ################################################################################################################################
# ################################################################################################################################

def _new_channel_item(
    destinations:'anylist | str',
    respond_from:'str' = Respond_From_Service,
    delivery_mode:'str' = DeliveryMode.In_Order,
    ) -> 'stranydict':
    """ Returns a channel item the way a channel wrapper hands one over.
    """
    if destinations:
        if not isinstance(destinations, str):
            destinations = dumps(destinations)

    out = {
        'id': 1,
        'name': _channel_name,
        'is_internal': False,
        'data_format': 'hl7-v2',
        'destinations': destinations,
        'respond_from': respond_from,
        'delivery_mode': delivery_mode,
    }

    return out

# ################################################################################################################################

def _get_stored_list() -> 'anylist':
    out = [
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
            'options': {'method': 'POST'},
        },
    ]

    return out

# ################################################################################################################################

def _new_service() -> 'FakeService':
    out = FakeService(_request_payload)
    return out

# ################################################################################################################################

def _as_service(fake:'FakeService') -> 'Service':
    out = cast_('Service', fake)
    return out

# ################################################################################################################################

class _SynchronousTransports:
    """ The transports the pipeline builds, except that what would go out in a greenlet goes out
    here and now, so a test sees the whole fan-out rather than only the part the caller waits for.
    """
    def __init__(self, service:'Service') -> 'None':
        self.dispatcher = ServiceDispatcher(service)
        self.sleeps:'anylist' = []

# ################################################################################################################################

    def make(self) -> 'DeliveryTransports':
        out = new_transports(self.dispatcher.send, self.sleep, self.spawn)
        return out

# ################################################################################################################################

    def sleep(self, seconds:'float') -> 'None':
        self.sleeps.append(seconds)

# ################################################################################################################################

    def spawn(self, function:'any_', *args:'any_') -> 'None':
        function(*args)

# ################################################################################################################################

def _new_config() -> 'ChannelDestinationConfig':
    """ Returns the configuration the pipeline reads off a channel item.
    """
    channel_item = _new_channel_item(_get_stored_list())

    out = get_config(channel_item)
    assert out

    return out

# ################################################################################################################################

def _count_hop_rows() -> 'int':
    engine = get_audit_engine()

    query = select(event_table)
    query = query.where(event_table.c.event_type == AuditEvent.Request_Sent)

    with engine.connect() as connection:
        out = len(connection.execute(query).fetchall())

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestReadingTheChannelConfiguration:

    def test_a_channel_that_declares_destinations_is_configured_from_what_it_stores(self) -> 'None':
        channel_item = _new_channel_item(_get_stored_list(), _mllp_connection)

        config = get_config(channel_item)

        assert config
        assert config.channel_name == _channel_name
        assert config.respond_from == _mllp_connection
        assert config.delivery_mode == DeliveryMode.In_Order
        assert len(config.entries) == 2

# ################################################################################################################################

    def test_a_channel_that_declares_none_has_no_configuration_at_all(self) -> 'None':
        channel_item = _new_channel_item('')

        assert get_config(channel_item) is None

# ################################################################################################################################

    def test_a_channel_that_has_never_had_one_has_no_configuration_at_all(self) -> 'None':
        # Every channel that does not use the feature looks like this
        assert get_config({'name': _channel_name}) is None

# ################################################################################################################################

    def test_a_channel_whose_every_destination_is_paused_has_nothing_to_deliver_to(self) -> 'None':
        stored = _get_stored_list()

        for entry in stored:
            entry['is_active'] = False

        channel_item = _new_channel_item(stored)

        assert get_config(channel_item) is None

# ################################################################################################################################
# ################################################################################################################################

class TestDeliveringWhatAServiceHandled:

    def test_every_destination_receives_the_message_the_service_was_given(self) -> 'None':
        fake = _new_service()
        service = _as_service(fake)

        config = _new_config()
        overrides = fake.destination.get_overrides()
        transports = _SynchronousTransports(service)

        result = run_destinations(service, config, overrides, fake.request.raw, transports.make())

        assert result.has_response is False

        assert fake.mllp.calls[0][1] == _request_payload
        assert fake.rest.calls[0][2] == (_request_payload,)

# ################################################################################################################################

    def test_what_the_service_said_through_its_facade_is_what_goes_out(self) -> 'None':
        fake = _new_service()
        service = _as_service(fake)

        fake.destination.payload = 'What the service made of it'
        fake.destination[_rest_connection] = None

        config = _new_config()
        overrides = fake.destination.get_overrides()
        transports = _SynchronousTransports(service)

        _ = run_destinations(service, config, overrides, fake.request.raw, transports.make())

        assert fake.mllp.calls[0][1] == 'What the service made of it'
        assert fake.rest.calls == []

# ################################################################################################################################

    def test_every_delivery_is_recorded_under_the_server_it_ran_on(self) -> 'None':
        fake = _new_service()
        service = _as_service(fake)

        config = _new_config()
        overrides = fake.destination.get_overrides()
        transports = _SynchronousTransports(service)

        _ = run_destinations(service, config, overrides, fake.request.raw, transports.make())

        engine = get_audit_engine()

        query = select(event_table)
        query = query.where(event_table.c.event_type == AuditEvent.Request_Sent)
        query = query.order_by(event_table.c.id)

        with engine.connect() as connection:
            rows = connection.execute(query).fetchall()

        assert len(rows) == 2

        for row in rows:
            assert row.server_name == fake.server.name
            assert row.cid == fake.cid
            assert row.outcome == AuditOutcome.OK

# ################################################################################################################################
# ################################################################################################################################

class TestTheServicePipeline:

    def test_a_channel_with_no_destinations_delivers_nothing(self) -> 'None':
        fake = _new_service()
        service = _as_service(fake)

        channel_item = _new_channel_item('')

        assert run_for_service(service, channel_item) is None

        assert fake.mllp.calls == []
        assert fake.rest.calls == []
        assert _count_hop_rows() == 0

# ################################################################################################################################

    def test_the_destination_a_channel_replies_from_produces_the_reply(self) -> 'None':
        fake = _new_service()
        service = _as_service(fake)

        # The one destination the channel has is the one it replies from, so the whole delivery
        # is the one the caller waits for and nothing is left running afterwards.
        stored = _get_stored_list()[:1]
        channel_item = _new_channel_item(stored, _mllp_connection)

        result = run_for_service(service, channel_item)

        assert result
        assert result.has_response is True
        assert result.response == MLLP_Response

        assert fake.mllp.calls[0][1] == _request_payload
        assert _count_hop_rows() == 1

# ################################################################################################################################
# ################################################################################################################################
