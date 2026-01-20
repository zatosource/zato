# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import tempfile
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.channel_rest import ChannelImporter
from zato.common.test.enmasse_._template_rest_gateway import template_rest_gateway
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_ = any_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseChannelRESTGatewayImporter(TestCase):
    """ Tests importing REST channels with gateway_service_list.
    """

    def setUp(self) -> 'None':
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_rest_gateway.encode('utf-8'))
        self.temp_file.close()

        self.importer = EnmasseYAMLImporter()
        self.channel_importer = ChannelImporter(self.importer)

        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse()

# ################################################################################################################################

    def _setup_test_environment(self) -> 'None':
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

# ################################################################################################################################

    def test_channel_rest_gateway_service_list(self) -> 'None':
        """ Test that gateway_service_list is correctly imported as opaque data.
        """
        self._setup_test_environment()

        channel_defs = self.yaml_config['channel_rest']
        self.assertEqual(len(channel_defs), 2, 'Expected 2 REST channel definitions')

        channels_created, _ = self.channel_importer.sync_channel_rest(channel_defs, self.session)

        self.assertEqual(len(channels_created), 2, 'Expected 2 channels created')

        channel_with_gateway:'any_' = None
        channel_without_gateway:'any_' = None

        for channel in channels_created:
            if channel.name == 'enmasse.channel.rest.gateway.1':
                channel_with_gateway = channel
            elif channel.name == 'enmasse.channel.rest.gateway.2':
                channel_without_gateway = channel

        self.assertIsNotNone(channel_with_gateway, 'Channel with gateway_service_list not found')
        self.assertIsNotNone(channel_without_gateway, 'Channel without gateway_service_list not found')

        self.assertIsNotNone(channel_with_gateway.opaque1, 'Channel should have opaque1 attribute')
        opaque_attrs = json.loads(channel_with_gateway.opaque1)
        self.assertIn('gateway_service_list', opaque_attrs, 'gateway_service_list not found in opaque1')

        expected_value = 'demo.ping\napi.my-service'
        self.assertEqual(opaque_attrs['gateway_service_list'], expected_value,
            'gateway_service_list value mismatch')

        if channel_without_gateway.opaque1:
            opaque_attrs_2 = json.loads(channel_without_gateway.opaque1)
            self.assertNotIn('gateway_service_list', opaque_attrs_2,
                'gateway_service_list should not be present')

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
