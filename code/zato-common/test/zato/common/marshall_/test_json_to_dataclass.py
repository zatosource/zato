# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.ext.dataclasses import dataclass, field
from zato.common.marshal_.api import MarshalAPI, Model
from zato.common.test import rand_int, rand_string
from zato.common.test.marshall_ import CreateUserRequest, Role, TestService, User
from zato.common.typing_ import cast_, list_field, dictlist, strlistnone

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.marshal_.api import ModelCtx
    from zato.server.service import Service
    ModelCtx = ModelCtx
    Service = Service

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

        service = cast_('Service', None)
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

    def test_unmarshall_optional_list_of_strings_given_on_input(self):

        elem1 = rand_string()
        elem2 = rand_string()
        elem3 = rand_string()

        my_list = [elem1, elem2, elem3]

        @dataclass
        class MyRequest(Model):
            my_list: strlistnone = list_field()

        request1 = {
            'my_list': my_list
        }

        service = None
        api = MarshalAPI()

        result = api.from_dict(cast_('Service', service), request1, MyRequest) # type: MyRequest
        self.assertListEqual(my_list, cast_('list', result.my_list))

# ################################################################################################################################

    def test_unmarshall_optional_list_of_strings_not_given_on_input(self):

        @dataclass
        class MyRequest(Model):
            my_list: strlistnone = list_field()

        request1 = {}

        service = None
        api = MarshalAPI()

        result = api.from_dict(cast_('Service', service), request1, MyRequest) # type: MyRequest
        self.assertListEqual([], cast_('list', result.my_list))

# ################################################################################################################################

    def test_unmarshall_default(self):

        request_id = rand_int()
        user_name  = rand_string()
        locality   = rand_string()

        @dataclass
        class CreateAdminRequest(CreateUserRequest):
            admin_type: str = field(default='MyDefaultValue') # type: ignore

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

        service = cast_('Service', None)
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
            def after_created(self, ctx:'ModelCtx') -> 'None':

                if not isinstance(ctx.service, TestService):
                    raise ValueError('Expected for service class to be {} instead of {}'.format(
                        TestService, type(ctx.service)))

                if not isinstance(ctx.data, dict): # type: ignore
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

        service = cast_('Service', TestService())
        api = MarshalAPI()
        api.from_dict(service, data, MyRequestWithAfterCreated)

# ################################################################################################################################

    def test_unmarshall_input_is_a_dataclass(self):

        @dataclass(init=False)
        class MyModel(Model):
            my_field: str

        expected_value = 'abc'

        data = {'my_field': expected_value}
        service = cast_('Service', None)
        api = MarshalAPI()

        result = api.from_dict(service, data, MyModel) # type: MyModel
        self.assertEqual(result.my_field, expected_value)

# ################################################################################################################################

    def test_unmarshall_input_is_a_dictlist(self):

        @dataclass(init=False)
        class MyModel(Model):
            my_field: dictlist

        expected_value = [{
            'abc':111,
            'zxc':222
        }]

        data = {'my_field': expected_value}
        service = cast_('Service', None)
        api = MarshalAPI()

        result = api.from_dict(service, data, MyModel) # type: MyModel
        self.assertEqual(result.my_field, expected_value)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
