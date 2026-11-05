# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase
from unittest.mock import MagicMock, patch

# Zato
from zato.common.api import URL_TYPE
from zato.server.api_portal.cache import SpecCache
from zato.server.api_portal.spec import _service_entries, get_spec_inputs

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

_orders_service = 'api.orders.get'
_customers_service = 'api.customers.get'

# ################################################################################################################################
# ################################################################################################################################

class _OrdersService:
    http_method_handlers = {}

class _OrdersServiceRedeployed:
    http_method_handlers = {}

class _CustomersService:
    http_method_handlers = {}

# ################################################################################################################################
# ################################################################################################################################

def _make_channel_item(channel_id:'int', service_name:'str', http_accept:'str'='') -> 'anydict':
    """ A REST channel that OpenAPI documents describe.
    """
    out = {
        'id': channel_id,
        'name': service_name,
        'connection': 'channel',
        'transport': URL_TYPE.PLAIN_HTTP,
        'is_active': True,
        'is_internal': False,
        'service_name': service_name,
        'url_path': '/' + service_name.replace('.', '/'),
        'method': 'GET',
        'http_accept': http_accept,
    }

    return out

# ################################################################################################################################

def _make_server() -> 'any_':
    """ A server with two documented channels, each with its service deployed.
    """
    out = MagicMock()
    out.url_data.channel_data = [
        _make_channel_item(1, _orders_service),
        _make_channel_item(2, _customers_service),
    ]

    out.service_store.name_to_impl_name = {}
    out.service_store.services = {}

    _deploy(out, _orders_service, _OrdersService)
    _deploy(out, _customers_service, _CustomersService)

    return out

# ################################################################################################################################

def _deploy(server:'any_', service_name:'str', service_class:'any_') -> 'None':
    impl_name = service_name + '.impl'

    server.service_store.name_to_impl_name[service_name] = impl_name
    server.service_store.services[impl_name] = {'service_class': service_class}

# ################################################################################################################################

def _undeploy(server:'any_', service_name:'str') -> 'None':
    impl_name = server.service_store.name_to_impl_name.pop(service_name)
    del server.service_store.services[impl_name]

# ################################################################################################################################
# ################################################################################################################################

class SpecInputsTestCase(TestCase):
    """ The inputs of a document are its channels, each with the class of its service.
    """

# ################################################################################################################################

    def test_documented_channels_and_their_services(self) -> 'None':
        server = _make_server()
        self.assertEqual(get_spec_inputs(server), [(1, _OrdersService), (2, _CustomersService)])

# ################################################################################################################################

    def test_a_channel_whose_service_is_not_deployed(self) -> 'None':
        server = _make_server()
        _undeploy(server, _customers_service)

        self.assertEqual(get_spec_inputs(server), [(1, _OrdersService), (2, None)])

# ################################################################################################################################

    def test_a_channel_excluded_from_documents(self) -> 'None':
        server = _make_server()
        server.url_data.channel_data[1]['should_include_in_openapi'] = False

        self.assertEqual(get_spec_inputs(server), [(1, _OrdersService)])

# ################################################################################################################################
# ################################################################################################################################

class SpecCacheFreshnessTestCase(TestCase):
    """ Each read of the cached document rebuilds it if its channels or services have changed since it was built.
    """

# ################################################################################################################################

    def setUp(self) -> 'None':
        self.server = _make_server()
        self.cache = SpecCache()

        build_patcher = patch('zato.server.api_portal.cache.build_full_spec', return_value=({'paths': {}}, {}))
        report_patcher = patch('zato.server.api_portal.cache.report_breaking_changes')

        self.build_full_spec = build_patcher.start()
        _ = report_patcher.start()

        self.addCleanup(build_patcher.stop)
        self.addCleanup(report_patcher.stop)

# ################################################################################################################################

    def _get_build_count(self) -> 'int':
        out = self.build_full_spec.call_count
        return out

# ################################################################################################################################

    def test_the_first_read_builds_the_document(self) -> 'None':
        _ = self.cache.get(self.server)
        self.assertEqual(self._get_build_count(), 1)

# ################################################################################################################################

    def test_an_unchanged_document_is_not_rebuilt(self) -> 'None':
        _ = self.cache.get(self.server)
        _ = self.cache.get(self.server)

        self.assertEqual(self._get_build_count(), 1)

# ################################################################################################################################

    def test_a_deleted_service(self) -> 'None':
        _ = self.cache.get(self.server)
        _undeploy(self.server, _customers_service)
        _ = self.cache.get(self.server)

        self.assertEqual(self._get_build_count(), 2)

# ################################################################################################################################

    def test_a_deleted_security_definition_with_channels(self) -> 'None':
        """ Deleting a security definition removes its channels from the server's channel data.
        """
        _ = self.cache.get(self.server)
        _ = self.server.url_data.channel_data.pop()
        _ = self.cache.get(self.server)

        self.assertEqual(self._get_build_count(), 2)

# ################################################################################################################################

    def test_a_redeployed_service(self) -> 'None':
        _ = self.cache.get(self.server)
        _deploy(self.server, _orders_service, _OrdersServiceRedeployed)
        _ = self.cache.get(self.server)

        self.assertEqual(self._get_build_count(), 2)

# ################################################################################################################################

    def test_a_change_to_an_undocumented_channel(self) -> 'None':
        _ = self.cache.get(self.server)

        excluded = _make_channel_item(3, _orders_service)
        excluded['should_include_in_openapi'] = False
        self.server.url_data.channel_data.append(excluded)

        _ = self.cache.get(self.server)

        self.assertEqual(self._get_build_count(), 1)

# ################################################################################################################################
# ################################################################################################################################

class ResponseMediaTypeEntryTestCase(TestCase):
    """ A channel that names an Accept value of its own documents it as the media type of its responses.
    """

# ################################################################################################################################

    def _get_media_type(self, http_accept:'str') -> 'str':
        server = _make_server()
        channel_item = _make_channel_item(1, _orders_service, http_accept)

        entries = _service_entries(server, channel_item, {})

        out = entries[0]['response_media_type']
        return out

# ################################################################################################################################

    def test_a_channel_with_an_accept_value_of_its_own(self) -> 'None':
        self.assertEqual(self._get_media_type('application/xml'), 'application/xml')

# ################################################################################################################################

    def test_a_channel_that_accepts_anything(self) -> 'None':
        self.assertEqual(self._get_media_type('*/*'), '')

# ################################################################################################################################

    def test_a_channel_without_an_accept_value(self) -> 'None':
        self.assertEqual(self._get_media_type(''), '')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
