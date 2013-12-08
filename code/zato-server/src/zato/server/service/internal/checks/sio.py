# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Nose
from nose.tools import eq_

# Zato
from zato.server.service import AsIs, CSV, Boolean, Dict, Integer, List, Service, Unicode, UTC
from zato.server.service.internal.checks import CheckService

# ################################################################################################################################

class AsIsService(Service):
    class SimpleIO:
        input_required = (AsIs('id'), AsIs('a_id'), AsIs('b_count'), AsIs('c_size'), AsIs('d_timeout'),
                          AsIs('is_e'), AsIs('needs_f'), AsIs('should_g'))
        output_required = (AsIs('id'), AsIs('a_id'), AsIs('b_count'), AsIs('c_size'), AsIs('d_timeout'),
                          AsIs('is_e'), AsIs('needs_f'), AsIs('should_g'))

    def handle(self):
        eq_(self.request.input.id, 'id')
        eq_(self.request.input.a_id, 'a')
        eq_(self.request.input.b_count, 'b')
        eq_(self.request.input.c_size, 'c')
        eq_(self.request.input.d_timeout, 'd')
        eq_(self.request.input.is_e, 'e')
        eq_(self.request.input.needs_f, 'f')
        eq_(self.request.input.should_g, 'g')

        self.response.payload.id = 'id'
        self.response.payload.a_id = 'a'
        self.response.payload.b_count = 'b'
        self.response.payload.c_size = 'c'
        self.response.payload.d_timeout = 'd'
        self.response.payload.is_e = 'e'
        self.response.payload.needs_f = 'f'
        self.response.payload.should_g = 'g'

# ################################################################################################################################

class BooleanService(Service):
    class SimpleIO:
        input_required = (Boolean('bool1'), Boolean('bool2'))
        output_required = (Boolean('bool1'), Boolean('bool2'))

    def handle(self):
        eq_(self.request.input.bool1, True)
        eq_(self.request.input.bool2, False)

        self.response.payload.bool1 = False
        self.response.payload.bool2 = True

# ################################################################################################################################

class DictService(Service):
    class SimpleIO:
        input_required = (Dict('dict1'), Dict('dict2'))
        #output_required = (Dict('dict3'), Dict('dict4'))

    def handle(self):
        eq_(sorted(self.request.input.dict1.items()) [1])
        #eq_(self.request.input.bool2, False)

        #self.response.payload.bool1 = False
        #self.response.payload.bool2 = True

# ################################################################################################################################

class IntegerService(Service):
    class SimpleIO:
        input_required = (Integer('int1'), Integer('int2'))
        output_required = (Integer('int3'), Integer('int4'))

    def handle(self):
        eq_(self.request.input.int1, 1)
        eq_(self.request.input.int2, 2)

        self.response.payload.int3 = 3
        self.response.payload.int4 = 4

# ################################################################################################################################

class UnicodeService(Service):
    class SimpleIO:
        input_required = (Unicode('uni_a'), Unicode('uni_b'))
        output_required = (Unicode('uni_c'), Unicode('uni_d'))

    def handle(self):
        eq_(self.request.input.uni_a, 'a')
        eq_(self.request.input.uni_b, 'b')

        self.response.payload.uni_c = 'c'
        self.response.payload.uni_d = 'd'

# ################################################################################################################################

class UTCService(Service):
    class SimpleIO:
        input_required = (UTC('utc1'), UTC('utc2'))
        output_required = (UTC('utc1'), UTC('utc2'))

    def handle(self):
        eq_(self.request.input.utc1, '2019-01-26T22:33:44')
        eq_(self.request.input.utc2, '2023-12-19T21:31:41')

        self.response.payload.utc1 = '1234-11-22T01:02:03+00:00'
        self.response.payload.utc2 = '2918-03-19T21:22:23+00:00'

# ################################################################################################################################

class CheckSIO(CheckService):

    def check_list(self):
        response = self.invoke_check('zato.checks.sio.list-service', {
            'non_list_item1': '1',
            'non_list_item2': '2',
            'list_item1': ['1', '2', '3'],
            'list_item2': ['4', '5', '6'],
        })

        eq_(response.non_list_item1, '1')
        eq_(response.non_list_item2, '2')
        eq_(response.list_item1, ['1', '2', '3'])
        eq_(response.list_item2, ['4', '5', '6'])

    def check_as_is(self):
        response = self.invoke_check('zato.checks.sio.as-is-service', {
            'id': 'id',
            'a_id': 'a',
            'b_count': 'b',
            'c_size': 'c',
            'd_timeout': 'd',
            'is_e': 'e',
            'needs_f': 'f',
            'should_g': 'g',
        })

        eq_(response.id, 'id')
        eq_(response.a_id, 'a')
        eq_(response.b_count, 'b')
        eq_(response.c_size, 'c')
        eq_(response.d_timeout, 'd')
        eq_(response.is_e, 'e')
        eq_(response.needs_f, 'f')
        eq_(response.should_g, 'g')

    def check_boolean(self):
        response = self.invoke_check('zato.checks.sio.boolean-service', {
            'bool1': True,
            'bool2': False,
        })

        eq_(response.bool1, False)
        eq_(response.bool2, True)

    def check_dict(self):
        response = self.invoke_check('zato.checks.sio.dict-service', {
            'dict1': {'key1_1': 'value1_1', 'key1_2':'value1_2'},
            'dict2': {'key2_1': 'value2_1', 'key2_2':'value2_2'},
        })

        #eq_(response.bool1, False)
        #eq_(response.bool2, True)

    def check_integer(self):
        response = self.invoke_check('zato.checks.sio.integer-service', {
            'int1': 1,
            'int2': 2,
        })

        eq_(response.int3, 3)
        eq_(response.int4, 4)

    def check_unicode(self):
        response = self.invoke_check('zato.checks.sio.unicode-service', {
            'uni_a': 'a',
            'uni_b': 'b',
        })

        eq_(response.uni_c, 'c')
        eq_(response.uni_d, 'd')

    def check_utc(self):
        response = self.invoke_check('zato.checks.sio.utc-service', {
            'utc1': '2019-01-26T22:33:44+00:00',
            'utc2': '2023-12-19T21:31:41+00:00',
        })

        eq_(response.utc1, '1234-11-22T01:02:03')
        eq_(response.utc2, '2918-03-19T21:22:23')

    def handle(self):
        # TODO: Add XML checks everywhere

        self.check_list() # TODO
        self.check_as_is()
        self.check_boolean()
        #self.check_csv() TODO: CSV is not implemened yet
        #self.check_dict() TODO: Dict is not implemened yet
        self.check_integer()
        self.check_unicode()
        self.check_utc()

# ################################################################################################################################
