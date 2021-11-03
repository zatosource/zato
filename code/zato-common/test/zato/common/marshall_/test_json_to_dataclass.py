# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.ext.dataclasses import dataclass, field
from zato.common.marshal_.api import MarshalAPI, Model, ModelCtx
from zato.common.marshal_.simpleio import DataClassSimpleIO
from zato.common.test import BaseSIOTestCase, rand_int, rand_string

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False, repr=False)
class User(Model):
    user_name: str

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=True, repr=False)
class MyRequest(Model):
    request_id: int
    user: User

# ################################################################################################################################
# ################################################################################################################################

class TestService:
    pass

# ################################################################################################################################
# ################################################################################################################################

class JSONToDataclassTestCase(TestCase):

    def test_unmarshall(self):

        request_id   = rand_int()
        user_name = rand_string()

        data = {
            'request_id': request_id,
            'user': {
                'user_name': user_name
            }
        }

        service = None
        api = MarshalAPI()

        result = api.from_dict(service, data, MyRequest) # type: MyRequest

        self.assertIs(type(result), MyRequest)
        self.assertIsInstance(result.user, User)

        self.assertEqual(result.request_id, request_id)
        self.assertEqual(result.user.user_name, user_name)

# ################################################################################################################################

    def test_unmarshall_default(self):

        request_id = rand_int()
        user_name  = rand_string()

        @dataclass
        class MyRequestWithDefault(MyRequest):
            request_group: str = field(default='MyRequestGroup')

        data = {
            'request_id': request_id,
            'user': {
                'user_name': user_name
            }
        }

        service = None
        api = MarshalAPI()

        result = api.from_dict(service, data, MyRequestWithDefault) # type: MyRequestWithDefault

        self.assertIs(type(result), MyRequestWithDefault)
        self.assertIsInstance(result.user, User)

        self.assertEqual(result.request_id, request_id)
        self.assertEqual(result.request_group, 'MyRequestGroup')
        self.assertEqual(result.user.user_name, user_name)

# ################################################################################################################################

    def test_unmarshall_after_created(self):

        request_id = 123456789
        user_name  = 'my.user.name'

        @dataclass
        class MyRequestWithAfterCreated(MyRequest):
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

        data = {
            'request_id': request_id,
            'user': {
                'user_name': user_name
            }
        }

        service = TestService()
        api = MarshalAPI()
        api.from_dict(service, data, MyRequestWithAfterCreated)

# ################################################################################################################################
# ################################################################################################################################

class SIOAttachTestCase(TestCase):

    def test_attach_sio(self):

        class MyService(Service):
            class SimpleIO:
                input = MyRequest

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        self.assertEquals(MyService._sio.definition._input_required.get_elem_names(), ['aaa', 'bbb', 'ccc'])
        self.assertEquals(MyService._sio.definition._input_optional.get_elem_names(), ['ddd', 'eee'])

        self.assertEquals(MyService._sio.definition._output_required.get_elem_names(), ['qqq', 'www'])
        self.assertEquals(MyService._sio.definition._output_optional.get_elem_names(), ['eee', 'fff'])

        self.assertTrue(MyService._sio.definition.has_input_required)
        self.assertTrue(MyService._sio.definition.has_input_optional)

        self.assertTrue(MyService._sio.definition.has_output_required)
        self.assertTrue(MyService._sio.definition.has_output_optional)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
