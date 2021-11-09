# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from .base import CreateAttrListRequest, CreatePhoneListRequest, CreateUserRequest
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
        self.assertEquals(e.reason, 'Element missing: /request_id')

# ################################################################################################################################

    def test_validate_top_level_dict_missing(self):

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

    def test_validate_nested_dict_missing(self):

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

    def test_unmarshall_top_level_list_elem_missing(self):

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
                {'type': role_type1, 'ZZZ': role_name1},
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

    def test_unmarshall_top_level_list_is_missing(self):

        # There is no input (and attr_list is a list that is missing)
        data = {}

        service = None
        api = MarshalAPI()

        with self.assertRaises(ElementMissing) as cm:
            api.from_dict(service, data, CreateAttrListRequest)

        e = cm.exception # type: ElementMissing
        self.assertEquals(e.reason, 'Element missing: /attr_list')

# ################################################################################################################################

    def test_unmarshall_top_level_list_dict_empty(self):

        data = {
            'attr_list': [{}],
        }

        service = None
        api = MarshalAPI()

        with self.assertRaises(ElementMissing) as cm:
            api.from_dict(service, data, CreateAttrListRequest)

        e = cm.exception # type: ElementMissing
        self.assertEquals(e.reason, 'Element missing: /attr_list[0]/name')

# ################################################################################################################################

    def test_unmarshall_top_level_list_dict_missing(self):

        data = {
            'attr_list': [],
        }

        service = None
        api = MarshalAPI()

        result = api.from_dict(service, data, CreateAttrListRequest) # type: CreateAttrListRequest

        # It is not an error to send a list that is empty,
        # which is unlike not sending the list at all (as checked in other tests).
        self.assertListEqual(result.attr_list, [])

# ################################################################################################################################

    def test_unmarshall_top_level_list_0(self):

        data = {
            'attr_list': [
                {'type':'type_0'},
            ],
        }

        service = None
        api = MarshalAPI()

        with self.assertRaises(ElementMissing) as cm:
            api.from_dict(service, data, CreateAttrListRequest)

        e = cm.exception # type: ElementMissing
        self.assertEquals(e.reason, 'Element missing: /attr_list[0]/name')

# ################################################################################################################################

    def test_unmarshall_top_level_list_1(self):

        data = {
            'attr_list': [
                {'type':'type_0', 'name':'name_0'},
                {'type':'type_1'},
            ],
        }

        service = None
        api = MarshalAPI()

        with self.assertRaises(ElementMissing) as cm:
            api.from_dict(service, data, CreateAttrListRequest)

        e = cm.exception # type: ElementMissing
        self.assertEquals(e.reason, 'Element missing: /attr_list[1]/name')

# ################################################################################################################################

    def test_unmarshall_top_level_list_5(self):

        data = {
            'attr_list': [
                {'type':'type_0', 'name':'name_0'},
                {'type':'type_1', 'name':'name_1'},
                {'type':'type_2', 'name':'name_2'},
                {'type':'type_3', 'name':'name_3'},
                {'type':'type_4', 'name':'name_4'},
                {'type':'type_5'},
            ],
        }

        service = None
        api = MarshalAPI()

        with self.assertRaises(ElementMissing) as cm:
            api.from_dict(service, data, CreateAttrListRequest)

        e = cm.exception # type: ElementMissing
        self.assertEquals(e.reason, 'Element missing: /attr_list[5]/name')

# ################################################################################################################################

    def test_unmarshall_nested_list_elem_missing_0(self):

        data = {
            'phone_list': [
                {'attr_list': [         # noqa: JS101
                    {'type':'type_0'},
                ]},                     # noqa: JS102
            ]
        }

        service = None
        api = MarshalAPI()

        with self.assertRaises(ElementMissing) as cm:
            api.from_dict(service, data, CreatePhoneListRequest)

        e = cm.exception # type: ElementMissing
        self.assertEquals(e.reason, 'Element missing: /phone_list[0]/attr_list[0]/name')

# ################################################################################################################################

    def test_unmarshall_nested_list_elem_missing_1(self):

        data = {
            'phone_list': [
                {'attr_list': [                           # noqa: JS101
                    {'type':'type_0', 'name':'name_0'},
                    {'type':'type_1', 'ZZZZ':'name_1'},
                ]},                                       # noqa: JS102
            ]
        }

        service = None
        api = MarshalAPI()

        with self.assertRaises(ElementMissing) as cm:
            api.from_dict(service, data, CreatePhoneListRequest)

        e = cm.exception # type: ElementMissing
        self.assertEquals(e.reason, 'Element missing: /phone_list[0]/attr_list[1]/name')

# ################################################################################################################################

    def test_unmarshall_nested_list_elem_missing_1_1(self):

        data = {
            'phone_list': [
                {'attr_list': [{'type':'type_0_0', 'name':'name_0_0'}, {'type':'type_0_1', 'name':'name_0_1'},]},
                {'attr_list': [{'type':'type_1_0', 'name':'name_1_0'}, {'type':'type_1_1', 'name':'name_1_1'}]},
                {'attr_list': [{'type':'type_2_0', 'name':'name_2_0'}, {'type':'type_2_1', 'ZZZZ':'name_2_1'}]},
            ]
        }

        service = None
        api = MarshalAPI()

        with self.assertRaises(ElementMissing) as cm:
            api.from_dict(service, data, CreatePhoneListRequest)

        e = cm.exception # type: ElementMissing
        self.assertEquals(e.reason, 'Element missing: /phone_list[2]/attr_list[1]/name')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
