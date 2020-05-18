# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from unittest import main, TestCase

# Bunch
from bunch import bunchify

# PyYAML
from yaml import load as yaml_load

# Zato
from common import MyService, service_name, sio_config
from zato.common import APISPEC
from zato.server.apispec import Generator, ServiceInfo
from zato.server.apispec.openapi import OpenAPIGenerator

# ################################################################################################################################

if 0:
    from bunch import Bunch

    Bunch = Bunch

# ################################################################################################################################
# ################################################################################################################################

class OpenAPITestCase(TestCase):

    def test_generate_open_api(self):

        service_store_services = {
            'my.impl.name': {
                'name': 'my.name',
                'service_class': MyService,
            }
        }
        include = ['*']
        exclude = []
        query   = ''
        tags    = 'public'

        generator = Generator(service_store_services, sio_config, include, exclude, query, tags, needs_sio_desc=False)

        info = generator.get_info()
        info = bunchify(info)

        channel_data = []
        needs_api_invoke = True
        needs_rest_channels = True
        api_invoke_path = APISPEC.GENERIC_INVOKE_PATH

        open_api_generator = OpenAPIGenerator(info, channel_data, needs_api_invoke, needs_rest_channels, api_invoke_path)

        result = open_api_generator.generate()
        result = yaml_load(result)
        result = bunchify(result)

        result_components = result.components # type: Bunch
        result_info       = result.info       # type: Bunch
        result_openapi    = result.openapi    # type: Bunch
        result_paths      = result.paths      # type: Bunch
        result_servers    = result.servers    # type: Bunch

        self.assertEqual(len(result_components.schemas), 1)

        response_my_name_properties = result_components.schemas.response_my_name.properties
        response_my_name_required   = result_components.schemas.response_my_name.required
        response_my_name_title      = result_components.schemas.response_my_name.title
        response_my_name_type       = result_components.schemas.response_my_name.type

        self.assertEqual(response_my_name_properties.address_id.type, 'integer')
        self.assertEqual(response_my_name_properties.address_id.format, 'int32')

        self.assertEqual(response_my_name_properties.address_name.type, 'string')
        self.assertEqual(response_my_name_properties.address_name.format, 'string')

        self.assertEqual(response_my_name_properties.address_subtype.type, 'string')
        self.assertEqual(response_my_name_properties.address_subtype.format, 'string')

        self.assertEqual(response_my_name_properties.address_type.type, 'string')
        self.assertEqual(response_my_name_properties.address_type.format, 'string')

        self.assertListEqual(response_my_name_required, ['address_id', 'address_name'])
        self.assertEqual(response_my_name_title, 'Response object for my.name')
        self.assertEqual(response_my_name_type, 'object')

        print(111, repr(response_my_name_type))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
