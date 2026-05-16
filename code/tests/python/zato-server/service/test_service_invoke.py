# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

# Zato
from zato.common.api import CHANNEL, DATA_FORMAT
from zato.common.exception import Inactive, ZatoException
from zato.common.marshal_.api import Model
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class TestServiceInvoke(unittest.TestCase):

    def _make_service(self) -> 'tuple':
        """ Builds a minimally-wired Service instance with mocked
        server, service store, and update_handle.
        """

        # Build the service under test ..
        service = Service.__new__(Service)
        service.name = 'caller.service'
        service.impl_name = 'my.module.CallerService'
        service.cid = 'test-cid-123'
        service.logger = MagicMock()
        service.config_dispatcher = MagicMock()
        service._config_manager = MagicMock()

        # .. set up the mock server and service store ..
        service.server = MagicMock()
        service.server.service_store.name_to_impl_name = {
            'target.service': 'my.module.TargetService',
        }

        # .. create the target service instance that new_instance returns ..
        target_instance = MagicMock()
        target_instance.set_response_data = MagicMock()
        target_instance.get_name.return_value = 'target.service'

        new_instance_result = (target_instance, True)
        service.server.service_store.new_instance.return_value = new_instance_result

        # .. and mock update_handle to return a canned response.
        expected_response = {'result': 'ok'}
        service.update_handle = MagicMock(return_value=expected_response)

        return service, target_instance

# ################################################################################################################################

    def test_invoke_by_name_with_dict(self) -> 'None':
        """ Invoke by service name string with a dict payload.
        """
        service, target = self._make_service()
        payload = {'key': 'val'}

        result = service.invoke('target.service', payload)

        self.assertEqual(result, {'result': 'ok'})

        service.update_handle.assert_called_once()

        call_args = service.update_handle.call_args[0]
        passed_target = call_args[1]
        passed_payload = call_args[2]

        self.assertIs(passed_target, target)
        self.assertEqual(passed_payload, payload)

# ################################################################################################################################

    def test_invoke_by_class(self) -> 'None':
        """ Invoke by passing a Service subclass instead of a name string.
        """
        service, _ = self._make_service()
        payload = {'key': 'val'}

        class TargetService(Service):
            name = 'target.service'

        result = service.invoke(TargetService, payload)

        self.assertEqual(result, {'result': 'ok'})

# ################################################################################################################################

    def test_invoke_with_inline_kwargs(self) -> 'None':
        """ When no explicit payload is given, extra kwargs become the payload dict.
        """
        service, _ = self._make_service()

        _ = service.invoke('target.service', order_id=456, status='pending')

        call_args = service.update_handle.call_args[0]
        passed_payload = call_args[2]

        expected_payload = {'order_id': 456, 'status': 'pending'}
        self.assertEqual(passed_payload, expected_payload)

# ################################################################################################################################

    def test_invoke_with_string_payload(self) -> 'None':
        """ A plain string can be passed as the payload.
        """
        service, _ = self._make_service()

        _ = service.invoke('target.service', 'hello')

        call_args = service.update_handle.call_args[0]
        passed_payload = call_args[2]

        self.assertEqual(passed_payload, 'hello')

# ################################################################################################################################

    def test_invoke_with_int_payload(self) -> 'None':
        """ A plain integer can be passed as the payload.
        """
        service, _ = self._make_service()

        _ = service.invoke('target.service', 42)

        call_args = service.update_handle.call_args[0]
        passed_payload = call_args[2]

        self.assertEqual(passed_payload, 42)

# ################################################################################################################################

    def test_invoke_with_dataclass_payload(self) -> 'None':
        """ A dataclass instance can be passed as the payload.
        """

        @dataclass(init=False)
        class CustomerRequest(Model):
            customer_id: str = ''
            name: str = ''

        service, _ = self._make_service()

        request = CustomerRequest()
        request.customer_id = 'CUST-001'
        request.name = 'Test Customer'

        _ = service.invoke('target.service', request)

        call_args = service.update_handle.call_args[0]
        passed_payload = call_args[2]

        self.assertIs(passed_payload, request)
        self.assertEqual(passed_payload.customer_id, 'CUST-001')
        self.assertEqual(passed_payload.name, 'Test Customer')

# ################################################################################################################################

    def test_invoke_self_raises(self) -> 'None':
        """ A service cannot invoke itself - ZatoException is raised.
        """
        service, _ = self._make_service()

        # Map the caller's own name so it resolves to the same impl_name
        service.server.service_store.name_to_impl_name['caller.service'] = 'my.module.CallerService'

        with self.assertRaises(ZatoException):
            service.invoke('caller.service')

# ################################################################################################################################

    def test_invoke_inactive_service_raises(self) -> 'None':
        """ Invoking an inactive service raises Inactive.
        """
        service, target = self._make_service()

        inactive_result = (target, False)
        service.server.service_store.new_instance.return_value = inactive_result

        with self.assertRaises(Inactive):
            service.invoke('target.service', 'payload')

# ################################################################################################################################

    def test_invoke_by_id(self) -> 'None':
        """ invoke_by_id resolves the impl_name from the integer ID.
        """
        service, _ = self._make_service()
        service.server.service_store.id_to_impl_name = {
            123: 'my.module.TargetService',
        }

        payload = {'key': 'val'}
        result = service.invoke_by_id(123, payload)

        self.assertEqual(result, {'result': 'ok'})

# ################################################################################################################################

    def test_invoke_with_data_format(self) -> 'None':
        """ The data_format parameter is forwarded to update_handle.
        """
        service, _ = self._make_service()
        payload = {'key': 'val'}

        _ = service.invoke('target.service', payload, data_format=DATA_FORMAT.JSON)

        call_args = service.update_handle.call_args[0]
        passed_data_format = call_args[4]

        self.assertEqual(passed_data_format, DATA_FORMAT.JSON)

# ################################################################################################################################

    def test_invoke_default_channel_is_invoke(self) -> 'None':
        """ The default channel passed to update_handle is CHANNEL.INVOKE.
        """
        service, _ = self._make_service()
        payload = {'key': 'val'}

        _ = service.invoke('target.service', payload)

        call_args = service.update_handle.call_args[0]
        passed_channel = call_args[3]

        self.assertEqual(passed_channel, CHANNEL.INVOKE)

# ################################################################################################################################

    def test_invoke_default_cid_is_callers(self) -> 'None':
        """ When no cid kwarg is given, the caller's own cid is forwarded.
        """
        service, _ = self._make_service()
        payload = {'key': 'val'}

        _ = service.invoke('target.service', payload)

        call_args = service.update_handle.call_args[0]
        passed_cid = call_args[9]

        self.assertEqual(passed_cid, 'test-cid-123')

# ################################################################################################################################

    @patch('zato.server.service.spawn_greenlet')
    def test_invoke_async_returns_cid(self, mock_spawn:'any_') -> 'None':
        """ invoke_async returns a correlation ID string and spawns a greenlet.
        """
        service, _ = self._make_service()

        cid = service.invoke_async('target.service', 'some-payload')

        self.assertIsInstance(cid, str)

        cid_length = len(cid)
        self.assertGreater(cid_length, 0)

        mock_spawn.assert_called_once()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
