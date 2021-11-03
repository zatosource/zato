# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.ext.dataclasses import dataclass
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

        self.assertIsInstance(result, MyRequest)
        self.assertIsInstance(result.user, User)

        self.assertEqual(result.request_id, request_id)
        self.assertEqual(result.user.user_name, user_name)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
