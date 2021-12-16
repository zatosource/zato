# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from .base import CreateUserRequest, Role, TestService, User
from zato.common.ext.dataclasses import dataclass, field
from zato.common.marshal_.api import MarshalAPI, ModelCtx
from zato.common.marshal_.simpleio import DataClassSimpleIO
from zato.common.test import BaseSIOTestCase, rand_int, rand_string

# ################################################################################################################################
# ################################################################################################################################

class JSONToDataclassTestCase(TestCase):

    def test_unmarshall(self):

        request_id = rand_int()
        user_name  = rand_string()
        locality   = rand_string()

        role_type1 = 111
        role_type2 = 222

        role_name1 = 'role.name.111'
        role_name2 = 'role.name.222'

        data = {
            'request_id': request_id,
            'user': {
                'user_name': user_name,
                'address': {
                    'locality': locality,
                }
            },
            'role_list': [
                {'type': role_type1, 'name': role_name1},
                {'type': role_type2, 'name': role_name2},
            ]
        }

        service = None
        api = MarshalAPI()

        result = api.from_dict(service, data, CreateUserRequest) # type: CreateUserRequest

        self.assertIs(type(result), CreateUserRequest)
        self.assertIsInstance(result.user, User)

        self.assertEqual(result.request_id, request_id)
        self.assertEqual(result.user.user_name, user_name)

        self.assertIsInstance(result.role_list, list)
        self.assertEqual(len(result.role_list), 2)

        role1 = result.role_list[0] # type: Role
        role2 = result.role_list[1] # type: Role

        self.assertIsInstance(role1, Role)
        self.assertIsInstance(role2, Role)

        self.assertEqual(role1.type, role_type1)
        self.assertEqual(role1.name, role_name1)

        self.assertEqual(role2.type, role_type2)
        self.assertEqual(role2.name, role_name2)

# ################################################################################################################################

    def test_unmarshall_default(self):

        request_id = rand_int()
        user_name  = rand_string()
        locality   = rand_string()

        @dataclass
        class CreateAdminRequest(CreateUserRequest):
            admin_type: str = field(default='MyDefaultValue')

        data = {
            'request_id': request_id,
            'user': {
                'user_name': user_name,
                'address': {
                    'locality': locality,
                }
            },
            'role_list': [],
        }

        service = None
        api = MarshalAPI()

        result = api.from_dict(service, data, CreateAdminRequest) # type: CreateAdminRequest

        self.assertIs(type(result), CreateAdminRequest)
        self.assertIsInstance(result.user, User)

        self.assertEqual(result.request_id, request_id)
        self.assertEqual(result.admin_type, CreateAdminRequest.admin_type)
        self.assertEqual(result.user.user_name, user_name)

# ################################################################################################################################

    def test_unmarshall_and_run_after_created(self):

        request_id = 123456789
        user_name  = 'my.user.name'
        locality   = 'my.locality'

        @dataclass
        class MyRequestWithAfterCreated(CreateUserRequest):
            def after_created(self, ctx):
                # type: (ModelCtx)

                if not isinstance(ctx.service, TestService):
                    raise ValueError('Expected for service class to be {} instead of {}'.format(
                        TestService, type(ctx.service)))

                if not isinstance(ctx.data, dict):
                    raise ValueError('Expected for service class to be a dict instead of {}'.format(type(ctx.data)))

                request_id = ctx.data['request_id']
                user_name  = ctx.data['user']['user_name']

                if request_id != 123456789:
                    raise ValueError('Value of request_id should be 123456789 instead of `{}`'.format(request_id))

                if user_name != 'my.user.name':
                    raise ValueError('Value of request_id should be "my.user.name"instead of `{}`'.format(user_name))

                if locality != 'my.locality':
                    raise ValueError('Value of locality should be "my.locality"instead of `{}`'.format(locality))

        data = {
            'request_id': request_id,
            'user': {
                'user_name': user_name,
                'address': {
                    'locality': locality,
                }
            },
            'role_list': [],
        }

        service = TestService()
        api = MarshalAPI()
        api.from_dict(service, data, MyRequestWithAfterCreated)

# ################################################################################################################################
# ################################################################################################################################

class SIOAttachTestCase(BaseSIOTestCase):

    def test_attach_sio(self):

        from zato.server.service import Service

        class MyService(Service):
            class SimpleIO:
                input = CreateUserRequest

        DataClassSimpleIO.attach_sio(None, self.get_server_config(), MyService)
        self.assertIsInstance(MyService._sio, DataClassSimpleIO)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
