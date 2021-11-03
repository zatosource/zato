# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.ext.dataclasses import dataclass, field
from zato.common.marshal_.api import MarshalAPI, Model
from zato.common.test import rand_int, rand_string

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

class JSONToDataclass(TestCase):

# ################################################################################################################################

    def xtest_unmarshall(self):

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
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
