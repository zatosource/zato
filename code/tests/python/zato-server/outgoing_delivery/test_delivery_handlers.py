# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from contextlib import contextmanager
from json import dumps
from unittest.mock import MagicMock

# Zato
from zato.common.ext.bunch import Bunch
from zato.common.pubsub.outgoing import deliver_envelope
from zato.server.config import ConfigDict
from zato.server.connection.outgoing_delivery import OutgoingType, register_delivery_handlers

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import any_, anylist, stranydict

    anygen = Iterator[any_]

# ################################################################################################################################
# ################################################################################################################################

# The connection every test here delivers to - the id it keeps for as long as it exists,
# the name it starts out with and the name a rename gives it.
_conn_id = 17
_conn_name = 'Order Intake'
_conn_name_renamed = 'Order Intake EU'

# The document a FHIR connection is published to with.
_fhir_resource_type = 'Patient'
_fhir_document = {'resourceType': _fhir_resource_type, 'name': [{'family': 'Kowalska'}]}

# ################################################################################################################################
# ################################################################################################################################

class _RESTResponse:
    """ What an outgoing REST connection answers an invocation with.
    """

    def __init__(self, is_accepted:'bool') -> 'None':
        self.is_accepted = is_accepted

    def raise_for_status(self) -> 'None':
        if not self.is_accepted:
            raise Exception('The connection did not accept the message')

# ################################################################################################################################
# ################################################################################################################################

class _RESTWrapper:
    """ Stands in for an outgoing REST connection's wrapper, recording what was sent through it.
    """

    def __init__(self) -> 'None':
        self.invocations:'anylist' = []
        self.is_accepted = True

    def rest_invoke(self, cid:'str', data:'str') -> '_RESTResponse':
        self.invocations.append((cid, data))
        out = _RESTResponse(self.is_accepted)
        return out

# ################################################################################################################################
# ################################################################################################################################

class _FHIRClient:
    """ Stands in for the client an outgoing FHIR connection hands out of its pool.
    """

    def __init__(self) -> 'None':
        self.requests:'anylist' = []

    def _do_request(self, method:'str', path:'str', data:'stranydict') -> 'None':
        self.requests.append((method, path, data))

# ################################################################################################################################
# ################################################################################################################################

class _FHIRWrapper:
    """ Stands in for an outgoing FHIR connection's wrapper and the pool behind it.
    """

    def __init__(self) -> 'None':
        self.fhir_client = _FHIRClient()
        self.client_options:'anylist' = []

    @contextmanager
    def client(self, should_block:'bool'=False, block_timeout:'int'=0) -> 'anygen':
        self.client_options.append((should_block, block_timeout))
        yield self.fhir_client

# ################################################################################################################################
# ################################################################################################################################

def _new_envelope(conn_type:'str', data:'str') -> 'stranydict':
    """ The envelope a publication to one connection turns into - the id is what it is delivered by
    and the name is the one it went by when it was published, which a rename may have changed since.
    """
    out = {
        'conn_type': conn_type,
        'conn_id': _conn_id,
        'conn_name': _conn_name,
        'data': data,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class RESTDeliveryTestCase(unittest.TestCase):
    """ How a message published to an outgoing REST connection reaches it.
    """

    def setUp(self) -> 'None':

        register_delivery_handlers()

        self.wrapper = _RESTWrapper()

        self.config_dict = ConfigDict('out_plain_http', Bunch())
        self._store_under(_conn_name)

        self.server = MagicMock()
        self.server.config_manager.config_store.out_plain_http = self.config_dict

# ################################################################################################################################

    def _store_under(self, conn_name:'str') -> 'None':
        """ Puts the connection in the configuration under one name, which is what an edit does.
        """
        item = Bunch()
        item.config = {'id': _conn_id, 'name': conn_name}
        item.conn = self.wrapper

        self.config_dict[conn_name] = item
        self.config_dict.set_key_id_data(item.config)

# ################################################################################################################################

    def test_message_reaches_the_connection(self) -> 'None':

        envelope = _new_envelope(OutgoingType.REST, 'Order 1234')
        deliver_envelope(self.server, 'test-cid', envelope)

        self.assertEqual(self.wrapper.invocations, [('test-cid', 'Order 1234')])

# ################################################################################################################################

    def test_a_renamed_connection_still_receives_the_message(self) -> 'None':
        """ The envelope carries the name from before the rename, and it is the id that finds the connection.
        """
        del self.config_dict[_conn_name]
        self._store_under(_conn_name_renamed)

        envelope = _new_envelope(OutgoingType.REST, 'Order 1234')
        deliver_envelope(self.server, 'test-cid', envelope)

        self.assertEqual(self.wrapper.invocations, [('test-cid', 'Order 1234')])

# ################################################################################################################################

    def test_a_connection_that_is_gone_raises(self) -> 'None':

        del self.config_dict[_conn_name]

        envelope = _new_envelope(OutgoingType.REST, 'Order 1234')

        with self.assertRaises(Exception) as context:
            deliver_envelope(self.server, 'test-cid', envelope)

        self.assertIn(str(_conn_id), str(context.exception))

# ################################################################################################################################

    def test_a_response_that_was_not_accepted_raises(self) -> 'None':
        """ What the handler raises is what makes the message stay in the queue for another attempt.
        """
        self.wrapper.is_accepted = False

        envelope = _new_envelope(OutgoingType.REST, 'Order 1234')

        with self.assertRaises(Exception) as context:
            deliver_envelope(self.server, 'test-cid', envelope)

        self.assertIn('did not accept the message', str(context.exception))

# ################################################################################################################################
# ################################################################################################################################

class FHIRDeliveryTestCase(unittest.TestCase):
    """ How a document published to an outgoing FHIR connection reaches it.
    """

    def setUp(self) -> 'None':

        register_delivery_handlers()

        self.wrapper = _FHIRWrapper()

        self.connections:'stranydict' = {}
        self._store_under(_conn_name)

        self.server = MagicMock()
        self.server.config_manager.outconn_hl7_fhir = self.connections

# ################################################################################################################################

    def _store_under(self, conn_name:'str') -> 'None':
        """ Puts the connection in the configuration under one name, which is what an edit does.
        """
        item = Bunch()
        item.id = _conn_id
        item.name = conn_name
        item.conn = self.wrapper

        self.connections[conn_name] = item

# ################################################################################################################################

    def test_document_reaches_the_connection(self) -> 'None':

        envelope = _new_envelope(OutgoingType.FHIR, dumps(_fhir_document))
        deliver_envelope(self.server, 'test-cid', envelope)

        requests = self.wrapper.fhir_client.requests
        self.assertEqual(len(requests), 1)

        method, path, data = requests[0]

        # A resource is created by posting it to the path its own type names
        self.assertEqual(method, 'POST')
        self.assertEqual(path, _fhir_resource_type)
        self.assertEqual(data, _fhir_document)

# ################################################################################################################################

    def test_the_client_is_waited_for(self) -> 'None':
        """ A connection whose pool is still being built is waited for rather than given up on.
        """
        envelope = _new_envelope(OutgoingType.FHIR, dumps(_fhir_document))
        deliver_envelope(self.server, 'test-cid', envelope)

        should_block, block_timeout = self.wrapper.client_options[0]

        self.assertTrue(should_block)
        self.assertTrue(block_timeout > 0)

# ################################################################################################################################

    def test_a_renamed_connection_still_receives_the_document(self) -> 'None':
        """ These connections live in a dict keyed by name, so what finds this one is its id.
        """
        del self.connections[_conn_name]
        self._store_under(_conn_name_renamed)

        envelope = _new_envelope(OutgoingType.FHIR, dumps(_fhir_document))
        deliver_envelope(self.server, 'test-cid', envelope)

        self.assertEqual(len(self.wrapper.fhir_client.requests), 1)

# ################################################################################################################################

    def test_a_connection_that_is_gone_raises(self) -> 'None':

        del self.connections[_conn_name]

        envelope = _new_envelope(OutgoingType.FHIR, dumps(_fhir_document))

        with self.assertRaises(Exception) as context:
            deliver_envelope(self.server, 'test-cid', envelope)

        self.assertIn(str(_conn_id), str(context.exception))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
