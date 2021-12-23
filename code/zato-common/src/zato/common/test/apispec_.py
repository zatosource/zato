# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import List as list_

# Bunch
from bunch import Bunch

# PyYAML
from yaml import FullLoader, load as yaml_load

# Zato
from zato.common.ext.dataclasses import dataclass
from zato.common.typing_ import optional
from zato.common.util.file_system import fs_safe_name
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test import BaseSIOTestCase

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

service_name = 'my.service'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class User(Model):

    user_name:    str # This is a string

    address_data: dict            # This is a dict
    prefs_dict:   optional[dict]  # This is an optional dict

    phone_list:   list            # This is a list
    email_list:   optional[list]  # This is an optional list

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class Account(Model):

    # This description is above the field
    account_no:      int

    account_type:    str # This is an inline description

    account_segment: str
    """ This is a multiline description,
    it has two lines.
    """

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class AccountList(Model):
    account_list: list_[Account]

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class MyRequest(Model):
    request_id: int
    user: User

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class MyResponse(Model):
    current_balance: int
    last_account_no: int = 567
    pref_account: Account
    account_list: AccountList

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

class DataclassMyService(Service):
    """ This is my service.

    It has a docstring.
    """
    class SimpleIO:
        input  = MyRequest
        output = MyResponse

# ################################################################################################################################
# ################################################################################################################################

def run_common_apispec_assertions(self:'BaseSIOTestCase', data:'str') -> 'None':

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
