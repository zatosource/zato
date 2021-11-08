# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from .base import CreatePhoneListRequest, CreateUserRequest
from zato.common.marshal_.api import ElementMissing, MarshalAPI
from zato.common.test import rand_int, rand_string

# ################################################################################################################################
# ################################################################################################################################

class ValidationTestCase(TestCase):

# ################################################################################################################################

    def xtest_validate_top_simple_elem_missing(self):

        # Input is entirely missing here
        data = {}

        service = None
        api = MarshalAPI()

        with self.assertRaises(ElementMissing) as cm:
            api.from_dict(service, data, CreateUserRequest)

        e = cm.exception # type: ElementMissing
        self.assertEquals(e.reason, 'Element missing: /request_id')

# ################################################################################################################################

    def xtest_validate_top_level_dict_missing(self):

        request_id = rand_int()

        # The user element is entirely missing here
        data = {
            'request_id': request_id,
            'role_list': [],
        }

        service = None
        api = MarshalAPI()

        with self.assertRaises(ElementMissing) as cm:
            api.from_dict(service, data, CreateUserRequest)

        e = cm.exception # type: ElementMissing
        self.assertEquals(e.reason, 'Element missing: /user')

# ################################################################################################################################

    def xtest_validate_nested_dict_missing(self):

        request_id = rand_int()
        user_name  = rand_string()

        # The address element is entirely missing here
        data = {
            'request_id': request_id,
            'user': {
                'user_name': user_name,
            },
            'role_list': [],
        }

        service = None
        api = MarshalAPI()

        with self.assertRaises(ElementMissing) as cm:
            api.from_dict(service, data, CreateUserRequest)

        e = cm.exception # type: ElementMissing
        self.assertEquals(e.reason, 'Element missing: /user/address')


# ################################################################################################################################

    def xtest_unmarshall_top_level_list_elem_missing(self):

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

                # Element name is missing here
                {'type': role_type1},

                {'type': role_type2, 'name': role_name2},
            ]
        }

        service = None
        api = MarshalAPI()

        with self.assertRaises(ElementMissing) as cm:
            api.from_dict(service, data, CreateUserRequest)

        e = cm.exception # type: ElementMissing
        self.assertEquals(e.reason, 'Element missing: /role_list[0]/name')

# ################################################################################################################################

    def test_unmarshall_nested_list_elem_missing_0_0(self):

        data = {
            'phone_list': [
                {'attr_list': [{'type':'name_0_0'}]},
            ]
        }

        service = None
        api = MarshalAPI()

        with self.assertRaises(ElementMissing) as cm:
            api.from_dict(service, data, CreatePhoneListRequest)

        e = cm.exception # type: ElementMissing
        self.assertEquals(e.reason, 'Element missing: /phone_list[0]/attr_list[0]/name')

# ################################################################################################################################

    def xtest_unmarshall_nested_list_elem_missing_0_1(self):

        data = {
            'phone_list': [
                {'attr_list': [{'type':'type_0_0', 'name':'name_0_0'}, {'type':'type_0_1'}]},
                # {'attr_list': [{'type':'type_1_0', 'name':'name_2_0'}, {'type':'type_2_1', 'name':'name_2_1'}, {'type':'type_2_2', 'name':'name_2_2'}]},
                # {'attr_list': [{'type':'type_2_0', 'name':'name_2_0'}, {'type':'type_2_1', 'name':'name_2_1'}, {'type':'type_2_2', 'name':'name_2_2'}]},
                # {'attr_list': [{'type':'type_2_0', 'name':'name_2_0'}, {'type':'type_2_1', 'name':'name_2_1'}, {'type':'type_2_2', 'name':'name_2_2'}]},
                # {'attr_list': [{'type':'type_2_0', 'name':'name_2_0'}, {'type':'type_2_1', 'name':'name_2_1'}, {'type':'type_2_2', 'name':'name_2_2'}]},
                # {'attr_list': [{'type':'type_2_0', 'name':'name_2_0'}, {'type':'type_2_1', 'name':'name_2_1'}, {'type':'type_2_2'}]},
            ]
        }

        service = None
        api = MarshalAPI()

        with self.assertRaises(ElementMissing) as cm:
            api.from_dict(service, data, CreatePhoneListRequest)

        e = cm.exception # type: ElementMissing
        self.assertEquals(e.reason, 'Element missing: /phone_list[0]/attr_list[1]/name')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
