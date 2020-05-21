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
                'name': service_name,
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

        print(result)

        return

        result = yaml_load(result)
        result = bunchify(result)

        result_components = result.components # type: Bunch
        result_info       = result.info       # type: Bunch
        result_openapi    = result.openapi    # type: Bunch
        result_paths      = result.paths      # type: Bunch
        result_servers    = result.servers    # type: Bunch

        self.assertEqual(len(result_components.schemas), 1)

        response_my_service_properties = result_components.schemas.response_my_service.properties
        response_my_service_required   = result_components.schemas.response_my_service.required
        response_my_service_title      = result_components.schemas.response_my_service.title
        response_my_service_type       = result_components.schemas.response_my_service.type

        self.assertEqual(response_my_service_properties.address_id.type, 'integer')
        self.assertEqual(response_my_service_properties.address_id.format, 'int32')

        self.assertEqual(response_my_service_properties.address_name.type, 'string')
        self.assertEqual(response_my_service_properties.address_name.format, 'string')

        self.assertEqual(response_my_service_properties.address_subtype.type, 'string')
        self.assertEqual(response_my_service_properties.address_subtype.format, 'string')

        self.assertEqual(response_my_service_properties.address_type.type, 'string')
        self.assertEqual(response_my_service_properties.address_type.format, 'string')

        self.assertListEqual(response_my_service_required, ['address_id', 'address_name'])
        self.assertEqual(response_my_service_title, 'Response object for my.service')
        self.assertEqual(response_my_service_type, 'object')

        self.assertEqual(result_info.title, 'API spec')
        self.assertEqual(result_info.version, '1.0')
        self.assertEqual(result_openapi, '3.0.0')

        self.assertEqual(len(result_paths), 1)

        path_my_name = result_paths[APISPEC.GENERIC_INVOKE_PATH.format(service_name=service_name)]

        post            = path_my_name.post
        post_parameters = post.parameters
        post_responses  = post.responses

        user_id       = post_parameters[0] # type: Bunch
        customer_id   = post_parameters[1] # type: Bunch
        user_name     = post_parameters[2] # type: Bunch
        customer_name = post_parameters[3] # type: Bunch

        self.assertEqual(user_id.description, 'This is the first line.\nHere is another.\nAnd here are some more lines.')
        self.assertEqual(user_id['in'], 'query')
        self.assertEqual(user_id.name, 'user_id')
        self.assertTrue(user_id.required)
        self.assertEqual(user_id.schema.type, 'integer')
        self.assertEqual(user_id.schema.format, 'int32')

        self.assertIsNone(customer_id.description)
        self.assertEqual(customer_id['in'], 'query')
        self.assertEqual(customer_id.name, 'customer_id')
        self.assertTrue(customer_id.required)
        self.assertEqual(customer_id.schema.type, 'integer')
        self.assertEqual(customer_id.schema.format, 'int32')

        self.assertEqual(user_name.description, 'b111')
        self.assertEqual(user_name['in'], 'query')
        self.assertEqual(user_name.name, 'user_name')
        self.assertFalse(user_name.required)
        self.assertEqual(user_name.schema.type, 'string')
        self.assertEqual(user_name.schema.format, 'string')

        self.assertIsNone(customer_name.description, 'b111')
        self.assertEqual(customer_name['in'], 'query')
        self.assertEqual(customer_name.name, 'customer_name')
        self.assertFalse(customer_name.required)
        self.assertEqual(customer_name.schema.type, 'string')
        self.assertEqual(customer_name.schema.format, 'string')

        self.assertEqual(len(post_responses), 1)
        response_200 = post_responses['200']

        self.assertEqual(response_200.description, '')
        self.assertEqual(response_200.content['application/json'].schema['$ref'], '#/components/schemas/response_my_service')

        self.assertEqual(len(result_servers), 1)

        localhost = result_servers[0]
        self.assertEqual(localhost.url, 'http://localhost:11223')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
