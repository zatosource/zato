# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from unittest import main, TestCase
from unittest.mock import MagicMock

# Bunch
from zato.common.ext.bunch import bunchify

# Zato
from zato.common.odata.client import ODataClient
from zato.server.connection.facade import ODataConnection, ODataFacade

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Env_Key_Should_Test = 'Zato_Test_OData'
    Env_Key_Address = 'Zato_Test_OData_Address'
    Env_Key_Username = 'Zato_Test_OData_Username'
    Env_Key_Secret = 'Zato_Test_OData_Secret'
    Env_Key_Entity_Set = 'Zato_Test_OData_Entity_Set'

# ################################################################################################################################
# ################################################################################################################################

class OutconnODataLiveTestCase(TestCase):
    """ Live tests against a real OData service, gated by the Zato_Test_OData env key.
    """

    def get_config(self, conn_name:'str') -> 'Bunch':

        config = bunchify({
            'name': conn_name,
            'is_active': True,
            'address': os.environ[ModuleCtx.Env_Key_Address],
            'odata_version': '4.0',
            'auth_type': 'basic',
            'username': os.environ[ModuleCtx.Env_Key_Username],
            'secret': os.environ[ModuleCtx.Env_Key_Secret],
            'timeout': 20,
            'page_size': 0,
            'needs_csrf_token': False,
        })

        return config

# ################################################################################################################################

    def test_ping(self):
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn_name = 'OutconnODataLiveTestCase.test_ping'
        config = self.get_config(conn_name)

        client = ODataClient(config)
        status_code = client.ping()
        self.assertLess(status_code, 400)

# ################################################################################################################################

    def test_read(self):
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn_name = 'OutconnODataLiveTestCase.test_read'
        config = self.get_config(conn_name)

        entity_set = os.environ[ModuleCtx.Env_Key_Entity_Set]

        client = ODataClient(config)
        items = client.read(entity_set, top=1)
        self.assertIsInstance(items, list)

# ################################################################################################################################
# ################################################################################################################################

class ODataConnectionTestCase(TestCase):
    """ Tests for the pooled ODataConnection proxy used by the self.odata facade.
    """

    def _get_connection(self) -> 'tuple':

        # The pooled client that the wrapper's queue hands out
        client = MagicMock()

        # The context manager returned by wrapper.client(...)
        borrowed = MagicMock()
        borrowed.__enter__ = MagicMock(return_value=client)
        borrowed.__exit__ = MagicMock(return_value=False)

        wrapper = MagicMock()
        wrapper.client.return_value = borrowed

        item = MagicMock()
        item.conn = wrapper

        outconn_odata = {'my-odata': item}
        connection = ODataConnection('my-odata', outconn_odata)

        return connection, client, wrapper

# ################################################################################################################################

    def test_read_borrows_and_returns_client(self):
        connection, client, wrapper = self._get_connection()
        client.read.return_value = [{'ID': 1}]

        result = connection.read('Customers', filter="Name eq 'Alice'")

        client.read.assert_called_once_with('Customers', filter="Name eq 'Alice'")
        self.assertEqual(result, [{'ID': 1}])

        # The client must have been borrowed with blocking enabled
        wrapper.client.assert_called_once_with(should_block=True, block_timeout=30)

# ################################################################################################################################

    def test_get(self):
        connection, client, _ = self._get_connection()
        client.get.return_value = {'ID': 1, 'Name': 'Alice'}

        result = connection.get('Customers', 1)

        client.get.assert_called_once_with('Customers', 1)
        self.assertEqual(result['Name'], 'Alice')

# ################################################################################################################################

    def test_create(self):
        connection, client, _ = self._get_connection()
        client.create.return_value = {'ID': 2}

        result = connection.create('Customers', {'Name': 'Bob'})

        client.create.assert_called_once_with('Customers', {'Name': 'Bob'})
        self.assertEqual(result['ID'], 2)

# ################################################################################################################################

    def test_update(self):
        connection, client, _ = self._get_connection()

        _ = connection.update('Customers', 2, {'Name': 'Bob Updated'})

        client.update.assert_called_once_with('Customers', 2, {'Name': 'Bob Updated'})

# ################################################################################################################################

    def test_delete(self):
        connection, client, _ = self._get_connection()

        _ = connection.delete('Customers', 2)

        client.delete.assert_called_once_with('Customers', 2)

# ################################################################################################################################

    def test_count(self):
        connection, client, _ = self._get_connection()
        client.count.return_value = 42

        result = connection.count('Customers')

        client.count.assert_called_once_with('Customers')
        self.assertEqual(result, 42)

# ################################################################################################################################

    def test_ping(self):
        connection, client, _ = self._get_connection()
        client.ping.return_value = 200

        result = connection.ping()

        client.ping.assert_called_once_with()
        self.assertEqual(result, 200)

# ################################################################################################################################

    def test_iter_keeps_client_borrowed(self):
        connection, client, _ = self._get_connection()
        client.iter.return_value = iter([{'ID': 1}, {'ID': 2}])

        items = list(connection.iter('Customers'))

        client.iter.assert_called_once_with('Customers')
        self.assertEqual(len(items), 2)

# ################################################################################################################################

    def test_repr(self):
        connection, _, _ = self._get_connection()

        repr_string = repr(connection)

        self.assertIn('ODataConnection', repr_string)
        self.assertIn('my-odata', repr_string)

# ################################################################################################################################
# ################################################################################################################################

class ODataFacadeTestCase(TestCase):
    """ Tests for ODataFacade dict-like access - the same facade class serves every subtype
    of the OData implementation, e.g. self.odata and self.sap.
    """

    def test_getitem_returns_connection(self):
        outconn_odata = {'test-conn': MagicMock()}

        facade = ODataFacade()
        facade.init(outconn_odata)

        connection = facade['test-conn']

        self.assertIsInstance(connection, ODataConnection)

# ################################################################################################################################

    def test_getitem_raises_on_missing(self):
        facade = ODataFacade()
        facade.init({})

        with self.assertRaises(KeyError):
            _ = facade['nonexistent']

# ################################################################################################################################

    def test_getitem_returns_connection_for_sap(self):

        # The SAP facade is the same class initialized from the SAP connection config dict
        outconn_sap = {'test-sap-conn': MagicMock()}

        facade = ODataFacade()
        facade.init(outconn_sap)

        connection = facade['test-sap-conn']

        self.assertIsInstance(connection, ODataConnection)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
