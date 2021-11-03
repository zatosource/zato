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

# ################################################################################################################################
# ################################################################################################################################

class JSONToDataclass(TestCase):
    def test_unmarshall(self):

        @dataclass(init=False)
        class User(Model):
            user_name: str

        @dataclass(init=False)
        class MyRequest(Model):
            user_id: int
            user: User

        data = {
            'user_id': 123,
            'user': {
                'user_name': 'zzz'
            }
        }

        api = MarshalAPI()
        result = api.from_dict(data, MyRequest)

        print('QQQ-1', result)

        # result = from_dict(MyRequest, data) # type: MyRequest
        # print(111, result.user.user_name)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
