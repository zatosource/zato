# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class MarshalAPI:

    def from_dict(self, data, DataClass):
        pass

    def to_dict(self):
        pass

# ################################################################################################################################
# ################################################################################################################################

'''
# Zato
from zato.common.marshal_.api import MarshalAPI
from zato.common.ext.dataclasses import dataclass

@dataclass(init=False)
class User:
    user_name: str

@dataclass(init=False)
class MyRequest:
    user_id: int
    user: User

data = {
    'user_id': 123,
    'user': 'zzz'
}

api = MarshalAPI()
result = api.from_dict(data, MyRequest)

# result = from_dict(MyRequest, data) # type: MyRequest
# print(111, result.user.user_name)
'''
