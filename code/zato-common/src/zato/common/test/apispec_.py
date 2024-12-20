# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Bunch
from bunch import Bunch

# PyYAML
from yaml import FullLoader, load as yaml_load

# Zato
from zato.common.util.file_system import fs_safe_name
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from unittest import TestCase
    from zato.common.typing_ import anydict
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

sio_config = Bunch()

sio_config.int = Bunch()
sio_config.bool = Bunch()
sio_config.secret = Bunch()
sio_config.bytes_to_str = Bunch()

sio_config.int.prefix = set()
sio_config.int.exact = set()
sio_config.int.suffix = {'_id'}

sio_config.bool.prefix = set()
sio_config.bool.exact = set()
sio_config.bool.suffix = set()

service_name = 'helpers.dataclass-service'

# ################################################################################################################################
# ################################################################################################################################

class CyMyService(Service):
    """ This is my service.

    It has a docstring.
    """
    class SimpleIO:
        """
        * input_req_user_id - This is the first line.

        Here is another.

        And here
        are some
        more lines.

        * input_opt_user_name - b111

        * output_req_address_id - c111 c222 c333 c444

        * output_opt_address_name - d111

          d222
        """
        input_required = 'input_req_user_id', 'input_req_customer_id'
        input_optional = 'input_opt_user_name', 'input_opt_customer_name'
        output_required = 'output_req_address_id', 'output_req_address_name'
        output_optional = 'output_opt_address_type', 'output_opt_address_subtype'

# ################################################################################################################################
# ################################################################################################################################

def run_common_apispec_assertions(self:'TestCase', data:'str', with_all_paths:'bool'=True) -> 'None':

    result = yaml_load(data, FullLoader)

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
    self.assertEqual(openapi, '3.0.3')

    #
    # Schemas
    #
    schemas = components['schemas']

    user_class         = 'zato.server.service.internal.helpers.MyUser'
    account_class      = 'zato.server.service.internal.helpers.MyAccount'
    account_list_class = 'zato.server.service.internal.helpers.MyAccountList'

    self.assertListEqual(sorted(schemas), [
        'request_helpers_dataclass_service',
        'response_helpers_dataclass_service',
        f'{account_class}',
        f'{account_list_class}',
        f'{user_class}',
    ])

    user         = schemas[f'{user_class}']        # type: anydict
    account      = schemas[f'{account_class}']     # type: anydict
    account_list = schemas[f'{account_list_class}'] # type: anydict

    request  = schemas['request_helpers_dataclass_service']  # type: anydict
    response = schemas['response_helpers_dataclass_service'] # type: anydict

    #
    # Request my.service
    #
    self.assertEqual(request['title'], 'Request object for helpers.dataclass-service')
    self.assertEqual(request['type'],  'object')

    self.assertListEqual(request['required'], ['request_id', 'user'])
    self.assertDictEqual(request['properties'], {
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
    self.assertEqual(response['title'], 'Response object for helpers.dataclass-service')
    self.assertEqual(response['type'],  'object')

    self.assertListEqual(response['required'], ['account_list', 'current_balance', 'pref_account'])
    self.assertDictEqual(response['properties'], {
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

    if with_all_paths:

        # Both /test/{phone_number} and /zato/api/invoke/helpers.dataclass-service
        expected_len_paths = 2
        url_paths = ['/test/{phone_number}', '/zato/api/invoke/helpers.dataclass-service']
    else:

        # Only /zato/api/invoke/helpers.dataclass-service
        expected_len_paths = 1
        url_paths = ['/zato/api/invoke/helpers.dataclass-service']

    self.assertEqual(len(paths), expected_len_paths)

    #
    # Information generic to all channels
    #
    for url_path in url_paths:

        service_path = paths[url_path] # type: anydict
        post = service_path['post']    # type: anydict

        self.assertEqual(post['operationId'], 'post_{}'.format(fs_safe_name(url_path)))
        self.assertTrue(post['requestBody']['required'])
        self.assertEqual(
            post['requestBody']['content']['application/json']['schema']['$ref'],
            '#/components/schemas/request_helpers_dataclass_service')
        self.assertEqual(
            post['responses']['200']['content']['application/json']['schema']['$ref'],
            '#/components/schemas/response_helpers_dataclass_service')

    #
    # Only the dedicated channel gets path parameters ..
    #
    if with_all_paths:
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
    path   = paths['/zato/api/invoke/helpers.dataclass-service']
    self.assertNotIn('parameters', path['post'])

# ################################################################################################################################
# ################################################################################################################################
