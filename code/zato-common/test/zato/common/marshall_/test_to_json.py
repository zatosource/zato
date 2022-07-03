# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads
from unittest import main

# BSON (MongoDB)
from bson import ObjectId

# Zato
from zato.common.ext.dataclasses import dataclass
from zato.common.marshal_.api import Model
from zato.common.test import BaseSIOTestCase

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False, repr=False)
class User(Model):
    user_name: str

# ################################################################################################################################
# ################################################################################################################################

class ToJSONTestCase(BaseSIOTestCase):

    def test_serialize_string(self):

        # Test data
        user_name = 'abc'

        user = User()
        user.user_name = user_name

        serialized = user.to_json()
        deserialized = loads(serialized)

        self.assertDictEqual(deserialized, {'user_name': user_name})

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
