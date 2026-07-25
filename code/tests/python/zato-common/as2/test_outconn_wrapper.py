# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.typing_ import cast_
from zato.server.generic.api.outconn_as2 import OutconnAS2Wrapper

# Zato
from .outconn_helpers import connection_config, Connection_Name, FakeServer, make_facade, new_mock_client, Payload

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

class TestWrapper:

    def test_send_goes_through_a_pooled_connection(self, parties:'TestParties') -> 'None':

        server = FakeServer()
        config = connection_config(parties)

        wrapper = OutconnAS2Wrapper(config, server)
        wrapper.add_client()

        # The pooled connection talks to the mock wire.
        requests = []
        results = []

        client = cast_('any_', wrapper.client)
        connection = client.queue.queue[0]
        connection.http_client = new_mock_client(parties, requests, results)

        result = wrapper.send('cid-1', Payload)

        assert result.is_ok
        assert len(requests) == 1

        first_result = results[0]
        assert not first_result.is_error

        # The connection went back to the pool after the send.
        assert wrapper.client.queue.qsize() == 1

# ################################################################################################################################

    def test_add_client_without_a_signing_key_adds_nothing(self, parties:'TestParties') -> 'None':

        server = FakeServer()
        config = connection_config(parties, as2_signing_key='')

        wrapper = OutconnAS2Wrapper(config, server)
        wrapper.add_client()

        assert wrapper.client.queue.qsize() == 0

# ################################################################################################################################
# ################################################################################################################################

class TestFacade:

    def test_send_carries_the_cid_for_the_user(self, parties:'any_') -> 'None':

        requests = []
        results = []

        facade = make_facade(parties, requests, results)

        # The one-liner a service runs - no cid anywhere in user code.
        connection = facade[Connection_Name]
        result = connection.send(Payload)

        assert result.is_ok
        assert len(requests) == 1

        first_result = results[0]
        assert not first_result.is_error

        first_payload = first_result.payloads[0]
        assert first_payload.data == Payload

# ################################################################################################################################

    def test_an_unknown_name_raises_a_key_error(self, parties:'any_') -> 'None':

        facade = make_facade(parties, [], [])

        with pytest.raises(KeyError):
            _ = facade['No Such Partner']

# ################################################################################################################################
# ################################################################################################################################
