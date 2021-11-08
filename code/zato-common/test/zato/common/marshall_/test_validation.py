# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from .base import CreateUserRequest
from zato.common.marshal_.api import ElementMissing, MarshalAPI
from zato.common.test import rand_int, rand_string

# ################################################################################################################################
# ################################################################################################################################

class ValidationTestCase(TestCase):

# ################################################################################################################################

    def test_validate_top_simple_elem_missing(self):

        # Input is entirely missing here
        data = {}

        service = None
        api = MarshalAPI()

        with self.assertRaises(ElementMissing) as cm:
            api.from_dict(service, data, CreateUserRequest)

        e = cm.exception # type: ElementMissing
        self.assertEquals(e.reason, 'Element missing: /user')

# ################################################################################################################################

    def test_validate_top_level_dict_missing(self):

        request_id = rand_int()

        # The user element is entirely missing here
        data = {
            'request_id': request_id,
        }

        service = None
        api = MarshalAPI()

        with self.assertRaises(ElementMissing) as cm:
            api.from_dict(service, data, CreateUserRequest)

        e = cm.exception # type: ElementMissing
        self.assertEquals(e.reason, 'Element missing: /user')

# ################################################################################################################################

    def test_validate_nested_dict_missing(self):

        request_id = rand_int()
        user_name  = rand_string()

        # The address element is entirely missing here
        data = {
            'request_id': request_id,
            'user': {
                'user_name': user_name,
            }
        }

        service = None
        api = MarshalAPI()

        with self.assertRaises(ElementMissing) as cm:
            api.from_dict(service, data, CreateUserRequest)

        e = cm.exception # type: ElementMissing
        self.assertEquals(e.reason, 'Element missing: /user/address')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
