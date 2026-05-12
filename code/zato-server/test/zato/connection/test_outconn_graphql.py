# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sys
from unittest import TestCase, main
from unittest.mock import MagicMock, patch

# Set up gql mocks before any imports that reference them
_mock_gql_module = MagicMock()
_mock_gql_transport = MagicMock()
_mock_gql_transport_requests = MagicMock()

sys.modules.setdefault('gql', _mock_gql_module)
sys.modules.setdefault('gql.transport', _mock_gql_transport)
sys.modules.setdefault('gql.transport.requests', _mock_gql_transport_requests)

# Zato
from zato.server.connection.facade import GraphQLFacade, GraphQLInvoker # noqa: E402

# ################################################################################################################################
# ################################################################################################################################

class TestGraphQLInvokerExecute(TestCase):
    """ Tests for GraphQLInvoker.execute method.
    """

    def _get_invoker(self) -> 'GraphQLInvoker':
        outconn_graphql = {
            'my-graphql': MagicMock(config={
                'address': 'https://graphql.example.com/api',
                'default_query_timeout': 30,
            })
        }
        invoker = GraphQLInvoker('my-graphql', outconn_graphql)
        return invoker

# ################################################################################################################################

    @patch('gql.Client')
    @patch('gql.transport.requests.RequestsHTTPTransport')
    @patch('gql.gql')
    def test_query_success(self, mock_gql_parse, mock_transport_class, mock_client_class):
        invoker = self._get_invoker()

        mock_session = MagicMock()
        mock_session.execute.return_value = {'data': {'users': [{'id': '1', 'name': 'Alice'}]}}
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_session)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        mock_parsed_query = MagicMock()
        mock_gql_parse.return_value = mock_parsed_query

        result = invoker.execute('{ users { id name } }')

        mock_gql_parse.assert_called_once_with('{ users { id name } }')
        mock_session.execute.assert_called_once_with(mock_parsed_query)
        self.assertEqual(result, {'data': {'users': [{'id': '1', 'name': 'Alice'}]}})

# ################################################################################################################################

    @patch('gql.Client')
    @patch('gql.transport.requests.RequestsHTTPTransport')
    @patch('gql.gql')
    def test_query_with_params(self, mock_gql_parse, mock_transport_class, mock_client_class):
        invoker = self._get_invoker()

        mock_session = MagicMock()
        mock_session.execute.return_value = {'data': {'user': {'id': '1', 'name': 'Alice'}}}
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_session)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        mock_parsed_query = MagicMock()
        mock_gql_parse.return_value = mock_parsed_query

        params = {'user_id': '1'}
        result = invoker.execute('query GetUser($user_id: ID!) { user(id: $user_id) { id name } }', params=params)

        mock_session.execute.assert_called_once_with(mock_parsed_query, variable_values=params)
        self.assertEqual(result, {'data': {'user': {'id': '1', 'name': 'Alice'}}})

# ################################################################################################################################

    @patch('gql.Client')
    @patch('gql.transport.requests.RequestsHTTPTransport')
    @patch('gql.gql')
    def test_query_without_params(self, mock_gql_parse, mock_transport_class, mock_client_class):
        invoker = self._get_invoker()

        mock_session = MagicMock()
        mock_session.execute.return_value = {'data': {'schema': {'queryType': {'name': 'Query'}}}}
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_session)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        mock_parsed_query = MagicMock()
        mock_gql_parse.return_value = mock_parsed_query

        result = invoker.execute('{ __schema { queryType { name } } }')

        mock_session.execute.assert_called_once_with(mock_parsed_query)
        self.assertEqual(result, {'data': {'schema': {'queryType': {'name': 'Query'}}}})

# ################################################################################################################################

    @patch('gql.Client')
    @patch('gql.transport.requests.RequestsHTTPTransport')
    @patch('gql.gql')
    def test_query_timeout(self, mock_gql_parse, mock_transport_class, mock_client_class):
        outconn_graphql = {
            'my-graphql': MagicMock(config={
                'address': 'https://graphql.example.com/api',
                'default_query_timeout': 5,
            })
        }
        invoker = GraphQLInvoker('my-graphql', outconn_graphql)

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=MagicMock())
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client
        mock_gql_parse.return_value = MagicMock()

        invoker.execute('{ users { id } }')

        mock_transport_class.assert_called_once_with(
            url='https://graphql.example.com/api',
            timeout=5,
        )

# ################################################################################################################################

    @patch('gql.Client')
    @patch('gql.transport.requests.RequestsHTTPTransport')
    @patch('gql.gql')
    def test_query_network_error(self, mock_gql_parse, mock_transport_class, mock_client_class):
        invoker = self._get_invoker()

        mock_session = MagicMock()
        mock_session.execute.side_effect = Exception('Connection refused')
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_session)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        mock_gql_parse.return_value = MagicMock()

        with self.assertRaises(Exception) as exception_context:
            invoker.execute('{ users { id } }')

        self.assertIn('Connection refused', str(exception_context.exception))

# ################################################################################################################################

    @patch('gql.Client')
    @patch('gql.transport.requests.RequestsHTTPTransport')
    @patch('gql.gql')
    def test_ping_success(self, mock_gql_parse, mock_transport_class, mock_client_class):
        invoker = self._get_invoker()

        mock_session = MagicMock()
        mock_session.execute.return_value = {'data': {'__schema': {'queryType': {'name': 'Query'}}}}
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_session)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        mock_gql_parse.return_value = MagicMock()

        result = invoker.ping()

        self.assertTrue(result)

# ################################################################################################################################

    @patch('gql.Client')
    @patch('gql.transport.requests.RequestsHTTPTransport')
    @patch('gql.gql')
    def test_ping_failure(self, mock_gql_parse, mock_transport_class, mock_client_class):
        invoker = self._get_invoker()

        mock_session = MagicMock()
        mock_session.execute.side_effect = Exception('Server unavailable')
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_session)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        mock_gql_parse.return_value = MagicMock()

        with self.assertRaises(Exception) as exception_context:
            invoker.ping()

        self.assertIn('Server unavailable', str(exception_context.exception))

# ################################################################################################################################

    @patch('gql.Client')
    @patch('gql.transport.requests.RequestsHTTPTransport')
    @patch('gql.gql')
    def test_transport_uses_correct_address(self, mock_gql_parse, mock_transport_class, mock_client_class):
        outconn_graphql = {
            'custom-conn': MagicMock(config={
                'address': 'https://custom.graphql.io/v1/graphql',
                'default_query_timeout': 60,
            })
        }
        invoker = GraphQLInvoker('custom-conn', outconn_graphql)

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=MagicMock())
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client
        mock_gql_parse.return_value = MagicMock()

        invoker.execute('{ health }')

        mock_transport_class.assert_called_once_with(
            url='https://custom.graphql.io/v1/graphql',
            timeout=60,
        )

# ################################################################################################################################

    @patch('gql.Client')
    @patch('gql.transport.requests.RequestsHTTPTransport')
    @patch('gql.gql')
    def test_execute_with_pre_parsed_query(self, mock_gql_parse, mock_transport_class, mock_client_class):
        invoker = self._get_invoker()

        mock_session = MagicMock()
        mock_session.execute.return_value = {'data': {'result': True}}
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_session)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        pre_parsed = MagicMock()
        pre_parsed.__class__ = type('DocumentNode', (), {})

        result = invoker.execute(pre_parsed)

        mock_gql_parse.assert_not_called()
        mock_session.execute.assert_called_once_with(pre_parsed)
        self.assertEqual(result, {'data': {'result': True}})

# ################################################################################################################################

    @patch('gql.Client')
    @patch('gql.transport.requests.RequestsHTTPTransport')
    @patch('gql.gql')
    def test_execute_mutation(self, mock_gql_parse, mock_transport_class, mock_client_class):
        invoker = self._get_invoker()

        mock_session = MagicMock()
        mock_session.execute.return_value = {'data': {'createUser': {'id': '99', 'name': 'Bob'}}}
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_session)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        mock_parsed = MagicMock()
        mock_gql_parse.return_value = mock_parsed

        mutation = 'mutation CreateUser($name: String!) { createUser(name: $name) { id name } }'
        params = {'name': 'Bob'}
        result = invoker.execute(mutation, params=params)

        mock_gql_parse.assert_called_once_with(mutation)
        mock_session.execute.assert_called_once_with(mock_parsed, variable_values=params)
        self.assertEqual(result['data']['createUser']['name'], 'Bob')

# ################################################################################################################################

    def test_repr(self):
        outconn_graphql = {
            'my-conn': MagicMock()
        }
        invoker = GraphQLInvoker('my-conn', outconn_graphql)

        repr_string = repr(invoker)

        self.assertIn('GraphQLInvoker', repr_string)
        self.assertIn('my-conn', repr_string)

# ################################################################################################################################
# ################################################################################################################################

class TestGraphQLFacade(TestCase):
    """ Tests for GraphQLFacade dict-like access.
    """

    def test_getitem_returns_invoker(self):
        config_manager = MagicMock()
        config_manager.outconn_graphql = {
            'test-conn': MagicMock(config={
                'address': 'https://example.com/graphql',
                'default_query_timeout': 30,
            })
        }

        facade = GraphQLFacade()
        facade.init(config_manager)

        invoker = facade['test-conn']

        self.assertIsInstance(invoker, GraphQLInvoker)

# ################################################################################################################################

    def test_getitem_raises_on_missing(self):
        config_manager = MagicMock()
        config_manager.outconn_graphql = {}

        facade = GraphQLFacade()
        facade.init(config_manager)

        with self.assertRaises(KeyError):
            _ = facade['nonexistent']

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
