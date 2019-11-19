# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.server.service import AsIs, Boolean, Bool, CSV, Dict, Float, Int, Integer, List, ListOfDicts, Nested, Opaque, Service, \
     Unicode, UTC

# Test support services below

# ################################################################################################################################

class String(Service):
    name = '_test.string'

    class SimpleIO:
        input_required = ('a', 'b', 'c')
        output_required = ('aa', 'bb', 'cc')

# ################################################################################################################################

class String2(Service):
    name = '_test.string2'

    class SimpleIO:
        input_required = ('a2', 'b2', 'c2')
        input_optional = ('a2a', 'b2b', 'c2c')
        output_optional = ('aa', 'bb', 'cc')

# ################################################################################################################################

class String3(Service):
    name = '_test.string3'

    class SimpleIO:
        input_optional = ('a2a', 'b2b', 'c2c')
        output_required = ('aa', 'bb', 'cc')
        output_optional = ('aaa', 'bbb', 'ccc')

# ################################################################################################################################

class BoolInt(Service):
    name = '_test.bool-int'

    class SimpleIO:
        input_required = ('id', 'a_id', 'a_count', 'a_size', 'a_timeout', 'is_a', 'needs_a', 'should_a')
        input_optional = ('id', 'b_id', 'b_count', 'b_size', 'b_timeout', 'is_b', 'needs_b', 'should_b')
        output_required = ('id', 'c_id', 'c_count', 'c_size', 'c_timeout', 'is_c', 'needs_c', 'should_c')
        output_optional = ('id', 'd_id', 'd_count', 'd_size', 'd_timeout', 'is_d', 'needs_d', 'should_d')

# ################################################################################################################################

class ForceTypeService(Service):
    name = '_test.force-type'

    class SimpleIO:
        input_required = (AsIs('is_a'), Boolean('b'), Bool('c'), CSV('d'), Dict('e'), Float('f'), Int('g'), Integer('h'),
            List('i'), ListOfDicts('j'), Nested('k'), Opaque('l'), Unicode('m'), UTC('n'))

        input_optional = (AsIs('is_aa'), Boolean('bb'), Bool('cc'), CSV('dd'), Dict('ee'), Float('ff'), Int('gg'), Integer('hh'),
            List('ii'), ListOfDicts('jj'), Nested('kk'), Opaque('ll'), Unicode('mm'), UTC('nn'))

        output_required = (AsIs('is_aaa'), Boolean('bbb'), Bool('ccc'), CSV('ddd'), Dict('eee'), Float('fff'), Int('ggg'),
            Integer('hhh'), List('iii'), ListOfDicts('jjj'), Nested('kkk'), Opaque('lll'), Unicode('mmm'), UTC('nnn'))

        output_optional = (AsIs('is_aaaa'), Boolean('bbbb'), Bool('cccc'), CSV('dddd'), Dict('eeee'), Float('ffff'), Int('gggg'),
            Integer('hhhh'), List('iiii'), ListOfDicts('jjjj'), Nested('kkkk'), Opaque('llll'), Unicode('mmmm'), UTC('nnnn'))

# ################################################################################################################################

class RequestResponse(Service):
    name = '_test.request-response'

    class SimpleIO:
        request_elem = 'my_request_elem'
        response_elem = 'my_response_elem'

# ################################################################################################################################
