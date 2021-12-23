# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from unittest import main


# PyYAML
from yaml import FullLoader, load as yaml_load

# Zato
from zato.common.test.apispec_ import DataclassMyService, service_name, sio_config
from zato.common.api import APISPEC, URL_TYPE
from zato.common.marshal_.simpleio import DataClassSimpleIO
from zato.common.test import BaseSIOTestCase
from zato.common.util.file_system import fs_safe_name
from zato.server.apispec.spec.core import Generator
from zato.server.apispec.spec.openapi import OpenAPIGenerator

# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################

class _MatchTestCompiled:
    group_names = ['phone_number']

# ################################################################################################################################
# ################################################################################################################################

class DataClassOpenAPITestCase(BaseSIOTestCase):

    def test_dataclass_generate_open_api(self):

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
        tags    = ['public']

        generator = Generator(service_store_services, sio_config, include, exclude, query, tags, needs_sio_desc=False)

        initial_info = generator.get_info() # type: any_

        channel_data = [{
            'service_name': service_name,
            'transport':    URL_TYPE.PLAIN_HTTP,
            'url_path':     '/test/{phone_number}',
            'match_target_compiled': _MatchTestCompiled()
        }]

        needs_api_invoke = True
        needs_rest_channels = True
        api_invoke_path = APISPEC.GENERIC_INVOKE_PATH

        open_api_generator = OpenAPIGenerator(initial_info, channel_data, needs_api_invoke, needs_rest_channels, api_invoke_path)

        result = open_api_generator.generate()

        f = open('/home/dsuch/tmp/zzz.yaml', 'w')
        f.write(result)
        f.close()

        result = yaml_load(result, FullLoader)

        components = result['components'] # type: anydict
        info       = result['info']       # type: anydict
        openapi    = result['openapi']    # type: anydict
        paths      = result['paths']      # type: anydict
        servers    = result['servers']    # type: anydict

        #
        # Servers
        #
        localhost = servers[0] # type: anydict
        self.assertEqual(localhost['url'], 'http://127.0.0.1:17010')

        #
        # Info
        #
        self.assertEqual(info['title'], 'API spec')
        self.assertEqual(info['version'], '1.0')
        self.assertEqual(openapi, '3.0.2')

        #
        # Schemas
        #
        schemas = components['schemas']

        user_class         = 'zato.common.test.apispec_.User'
        account_class      = 'zato.common.test.apispec_.Account'
        account_list_class = 'zato.common.test.apispec_.AccountList'

        self.assertListEqual(sorted(schemas), [
            'request_my_service',
            'response_my_service',
            f'{account_class}',
            f'{account_list_class}',
            f'{user_class}',
        ])

        user         = schemas[f'{user_class}']        # type: anydict
        account      = schemas[f'{account_class}']     # type: anydict
        account_list = schemas[f'{account_list_class}'] # type: anydict

        request_my_service  = schemas['request_my_service']  # type: anydict
        response_my_service = schemas['response_my_service'] # type: anydict

        #
        # Request my.service
        #
        self.assertEqual(request_my_service['title'], 'Request object for my.service')
        self.assertEqual(request_my_service['type'],  'object')

        self.assertListEqual(request_my_service['required'], ['request_id', 'user'])
        self.assertDictEqual(request_my_service['properties'], {
            'request_id': {
                'description': '',
                'type':        'integer',
            },
            'user': {
                '$ref':        f'#/components/schemas/{user_class}',
                'description': '',
            },
        })

        #
        # Response my.service
        #
        self.assertEqual(response_my_service['title'], 'Response object for my.service')
        self.assertEqual(response_my_service['type'],  'object')

        self.assertListEqual(response_my_service['required'], ['account_list', 'current_balance', 'pref_account'])
        self.assertDictEqual(response_my_service['properties'], {
            'account_list': {
                '$ref':        f'#/components/schemas/{account_list_class}',
                'description': '',
            },
            'current_balance': {
                'description': '',
                'type':        'integer',
            },
            'last_account_no': {
                'description': '',
                'type':        'integer',
            },
            'pref_account': {
                '$ref':        f'#/components/schemas/{account_class}',
                'description': '',
            },
        })

        #
        # Account schema
        #
        self.assertListEqual(account['required'], ['account_no', 'account_segment', 'account_type'])
        self.assertDictEqual(account['properties'], {
            'account_no': {
                'description': 'This description is above the field',
                'type':        'integer',
            },
            'account_segment': {
                'description': """This is a multiline description,
it has two lines.""",
                'type':        'string',
            },
            'account_type': {
                'description': 'This is an inline description',
                'type':        'string',
            },
        })

        #
        # AccountList schema
        #
        self.assertListEqual(account_list['required'], ['account_list'])
        self.assertDictEqual(account_list['properties'], {
            'account_list': {
                'description': '',
                'type':        'array',
                'items': {
                    '$ref': f'#/components/schemas/{account_class}',
                }
            }
        })

        #
        # User schema
        #
        self.assertListEqual(user['required'], ['address_data', 'phone_list', 'user_name'])
        self.assertDictEqual(user['properties'], {
            'address_data': {
                'description': 'This is a dict',
                'type': 'object',
                'additionalProperties': {},
            },
            'email_list': {
                'description': 'This is an optional list',
                'type': 'array',
                'items': {}
            },
            'prefs_dict': {
                'description': 'This is an optional dict',
                'type': 'object',
                'additionalProperties': {},
            },
            'phone_list': {
                'description': 'This is a list',
                'type': 'array',
                'items': {}
            },
            'user_name': {
                'description': 'This is a string',
                'type': 'string',
            },
        })

        localhost = servers[0]
        self.assertEqual(localhost['url'], 'http://127.0.0.1:17010')

        self.assertEqual(len(paths), 2)

        #
        # Information generic to all channels
        #
        for url_path in ['/test/{phone_number}', '/zato/api/invoke/my.service']:

            my_service_path = paths[url_path] # type: anydict
            post = my_service_path['post']    # type: anydict

            self.assertEqual(post['operationId'], 'post_{}'.format(fs_safe_name(url_path)))
            self.assertTrue(post['requestBody']['required'])
            self.assertEqual(
                post['requestBody']['content']['application/json']['schema']['$ref'],
                '#/components/schemas/request_my_service')
            self.assertEqual(
                post['responses']['200']['content']['application/json']['schema']['$ref'],
                '#/components/schemas/response_my_service')

        #
        # Only the dedicated channel gets path parameters ..
        #
        path   = paths['/test/{phone_number}']
        params = path['post']['parameters']

        self.assertListEqual(params, [{
            'description': '',
            'in': 'path',
            'name': 'phone_number',
            'required': True,
            'schema': {
                'format': 'string',
                'type': 'string'
            }
        }])

        # .. whereas the generic API invoker has no path parameters.
        path   = paths['/zato/api/invoke/my.service']
        self.assertNotIn('parameters', path['post'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
