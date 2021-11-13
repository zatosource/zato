# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from unittest import main

# Bunch
from bunch import bunchify

# PyYAML
from yaml import FullLoader, load as yaml_load

# Zato
from ..common import DataclassMyService, service_name, sio_config
from zato.common.api import APISPEC, URL_TYPE
from zato.common.marshal_.simpleio import DataClassSimpleIO
from zato.common.test import BaseSIOTestCase
from zato.common.util.file_system import fs_safe_name
from zato.server.apispec import Generator
from zato.server.apispec.openapi import OpenAPIGenerator

# ################################################################################################################################

if 0:
    from bunch import Bunch

    Bunch = Bunch

# ################################################################################################################################

class _MatchTestCompiled:
    group_names = ['phone_number']

# ################################################################################################################################
# ################################################################################################################################

class DataClassOpenAPITestCase(BaseSIOTestCase):

    def test_dc_generate_open_api(self):

        MyClass = deepcopy(DataclassMyService)
        DataClassSimpleIO.attach_sio(None, self.get_server_config(), MyClass)

        service_store_services = {
            'my.impl.name': {
                'name': service_name,
                'service_class': MyClass,
            }
        }
        include = ['*']
        exclude = []
        query   = ''
        tags    = 'public'

        generator = Generator(service_store_services, sio_config, include, exclude, query, tags, needs_sio_desc=False)

        info = generator.get_info()
        info = bunchify(info)

        channel_data = [{
            'service_name': service_name,
            'transport':    URL_TYPE.PLAIN_HTTP,
            'url_path':     '/test/{phone_number}',
            'match_target_compiled': _MatchTestCompiled()
        }]
        needs_api_invoke = True
        needs_rest_channels = True
        api_invoke_path = APISPEC.GENERIC_INVOKE_PATH

        open_api_generator = OpenAPIGenerator(info, channel_data, needs_api_invoke, needs_rest_channels, api_invoke_path)

        result = open_api_generator.generate()
        result = yaml_load(result, FullLoader)
        result = bunchify(result)

        #from json import dumps
        #result = dumps(result)

        #print(result)

        components = result.components # type: Bunch
        info       = result.info       # type: Bunch
        openapi    = result.openapi    # type: Bunch
        paths      = result.paths      # type: Bunch
        servers    = result.servers    # type: Bunch

        #
        # Servers
        #
        localhost = servers[0]
        self.assertEqual(localhost.url, 'http://127.0.0.1:17010')

        #
        # Info
        #
        self.assertEqual(info.title, 'API spec')
        self.assertEqual(info.version, '1.0')
        self.assertEqual(openapi, '3.0.2')

        #
        # Schemas
        #
        schemas = components.schemas

        self.assertListEqual(sorted(schemas), [
            'request_my_service',
            'response_my_service',
            'test.zato.common.Account',
            'test.zato.common.AccountList',
            'test.zato.common.User',
        ])

        user         = schemas['test.zato.common.User']        # type: Bunch
        account      = schemas['test.zato.common.Account']     # type: Bunch
        account_list = schemas['test.zato.common.AccountList'] # type: Bunch

        request_my_service  = schemas['request_my_service']  # type: Bunch
        response_my_service = schemas['response_my_service'] # type: Bunch

        #
        # Request my.service
        #
        self.assertEqual(request_my_service.title, 'Request object for my.service')
        self.assertEqual(request_my_service.type,  'object')

        self.assertListEqual(request_my_service.required, ['request_id', 'user'])
        self.assertDictEqual(request_my_service.properties, {
            'request_id': {
                'description': '',
                'subtype':     'int32',
                'type':        'integer',
            },
            'user': {
                '$ref':        '#/components/schemas/test.zato.common.User',
                'description': '',
            },
        })

        #
        # Response my.service
        #
        self.assertEqual(response_my_service.title, 'Response object for my.service')
        self.assertEqual(response_my_service.type,  'object')

        self.assertListEqual(response_my_service.required, ['account_list', 'current_balance', 'pref_account'])
        self.assertDictEqual(response_my_service.properties, {
            'account_list': {
                '$ref':        '#/components/schemas/test.zato.common.AccountList',
                'description': '',
            },
            'current_balance': {
                'description': '',
                'subtype':     'int32',
                'type':        'integer',
            },
            'last_account_no': {
                'description': '',
                'subtype':     'int32',
                'type':        'integer',
            },
            'pref_account': {
                '$ref':        '#/components/schemas/test.zato.common.Account',
                'description': '',
            },
        })

        #
        # Account schema
        #
        self.assertListEqual(account.required, ['account_no', 'account_segment', 'account_type'])
        self.assertDictEqual(account.properties, {
            'account_no': {
                'description': '',
                'subtype':     'int32',
                'type':        'integer',
            },
            'account_segment': {
                'description': '',
                'subtype':     'string',
                'type':        'string',
            },
            'account_type': {
                'description': '',
                'subtype':     'string',
                'type':        'string',
            },
        })

        #
        # AccountList schema
        #
        self.assertListEqual(account_list.required, ['account_list'])
        self.assertDictEqual(account_list.properties, {
            'account_list': {
                'description': '',
                'type':        'array',
                'items': {
                    '$ref': '#/components/schemas/test.zato.common.Account',
                }
            }
        })

        #
        # User schema
        #
        self.assertListEqual(user.required, ['user_name'])
        self.assertDictEqual(user.properties, {
            'user_name': {
                'description': '',
                'subtype':     'string',
                'type':        'string',
            }
        })

        return

        '''
        result_components = result.components # type: Bunch
        result_info       = result.info       # type: Bunch
        result_openapi    = result.openapi    # type: Bunch
        result_paths      = result.paths      # type: Bunch
        result_servers    = result.servers    # type: Bunch

        localhost = result_servers[0]
        self.assertEqual(localhost.url, 'http://127.0.0.1:17010')

        self.assertEqual(result_info.title, 'API spec')
        self.assertEqual(result_info.version, '1.0')
        self.assertEqual(result_openapi, '3.0.2')

        self.assertEqual(len(result_components.schemas), 5)

        request_my_service_properties = result_components.schemas.request_my_service.properties
        request_my_service_required   = result_components.schemas.request_my_service.required
        request_my_service_title      = result_components.schemas.request_my_service.title
        request_my_service_type       = result_components.schemas.request_my_service.type

        response_my_service_required   = result_components.schemas.response_my_service.required
        response_my_service_title      = result_components.schemas.response_my_service.title
        response_my_service_type       = result_components.schemas.response_my_service.type

        self.assertEqual(request_my_service_title, 'Request object for my.service')
        self.assertEqual(response_my_service_title, 'Response object for my.service')

        self.assertEqual(request_my_service_type, 'object')
        self.assertEqual(response_my_service_type, 'object')

        self.assertListEqual(sorted(request_my_service_required), ['customer_id', 'user_id'])
        self.assertListEqual(sorted(response_my_service_required), ['address_id', 'address_name'])

        self.assertEqual(request_my_service_properties.input_req_user_id.type, 'integer')
        self.assertEqual(request_my_service_properties.input_req_user_id.format, 'int32')
        self.assertEqual(request_my_service_properties.input_req_user_id.description,
            'This is the first line.\nHere is another.\nAnd here are some more lines.')

        self.assertEqual(request_my_service_properties.input_req_customer_id.type, 'integer')
        self.assertEqual(request_my_service_properties.input_req_customer_id.format, 'int32')
        self.assertEqual(request_my_service_properties.input_req_customer_id.description, '')

        self.assertEqual(request_my_service_properties.input_opt_user_name.type, 'string')
        self.assertEqual(request_my_service_properties.input_opt_user_name.format, 'string')
        self.assertEqual(request_my_service_properties.input_opt_user_name.description, 'b111')

        self.assertEqual(request_my_service_properties.input_opt_customer_name.type, 'string')
        self.assertEqual(request_my_service_properties.input_opt_customer_name.format, 'string')
        self.assertEqual(request_my_service_properties.input_opt_customer_name.description, '')

        self.assertEqual(len(result_paths), 2)

        for url_path in ['/test/{phone_number}', '/zato/api/invoke/my.service']:

            my_service_path = result_paths[url_path] # type: Bunch
            post = my_service_path.post

            self.assertListEqual(post.consumes, ['application/json'])
            self.assertEqual(post.operationId, 'post_{}'.format(fs_safe_name(url_path)))
            self.assertTrue(post.requestBody.required)
            self.assertEqual(
                post.requestBody.content['application/json'].schema['$ref'], '#/components/schemas/request_my_service')
            self.assertEqual(
                post.responses['200'].content['application/json'].schema['$ref'], '#/components/schemas/response_my_service')
        '''

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
