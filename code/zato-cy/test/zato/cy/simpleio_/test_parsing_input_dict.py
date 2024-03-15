# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from decimal import Decimal as decimal_Decimal
from uuid import UUID as uuid_UUID, uuid4

# dateutil
from dateutil.parser import parse as dt_parse

# Zato
from zato.common.api import DATA_FORMAT
from zato.common.test import BaseSIOTestCase
from zato.server.service import Service

# Zato - Cython
from zato.bunch import Bunch
from zato.simpleio import backward_compat_default_value, AsIs, Bool, CSV, CySimpleIO, Date, DateTime, Decimal, \
     Dict, DictList, Float, Int, List, NotGiven, Opaque, Text, UUID

# ################################################################################################################################
# ################################################################################################################################

class JSONInputParsing(BaseSIOTestCase):

# ################################################################################################################################

    def test_parse_basic_request(self):

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', Int('bbb'), Opaque('ccc'), '-ddd', '-eee'

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        aaa = 'aaa-111'
        bbb = '222'
        ccc = object()
        eee = 'eee-111'

        # Note that 'ddd' is optional and we are free to skip it
        data = {
            'aaa': aaa,
            'bbb': bbb,
            'ccc': ccc,
            'eee': eee,
        }

        input = MyService._sio.parse_input(data, DATA_FORMAT.DICT)

        self.assertIsInstance(input, Bunch)

        self.assertEqual(input.aaa, aaa)
        self.assertEqual(input.bbb, int(bbb))
        self.assertIs(input.ccc, ccc)
        self.assertEqual(input.ddd, backward_compat_default_value)
        self.assertEqual(input.eee, eee)

# ################################################################################################################################

    def test_parse_all_elem_types_non_list(self):

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', AsIs('bbb'), Bool('ccc'), CSV('ddd'), Date('eee'), DateTime('fff'), Decimal('ggg'), \
                    Dict('hhh', 'a', 'b', 'c'), DictList('iii', 'd', 'e', 'f'), Float('jjj'), Int('mmm'), List('nnn'), \
                    Opaque('ooo'), Text('ppp'), UUID('qqq')

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        aaa = 'aaa-111'
        bbb = object()
        ccc = True
        ddd = '1,2,3,4'
        eee = '1999-12-31'
        fff = '1988-01-29T11:22:33.0000Z'
        ggg = '123.456'
        hhh = {'a':1, 'b':2, 'c':3}
        iii = [{'d':4, 'e':5, 'f':6}, {'d':44, 'e':55, 'f':66}]
        jjj = '111.222'
        mmm = '9090'
        nnn = [1, 2, 3, 4]
        ooo = object()
        ppp = 'mytext'
        qqq = 'd011d054-db4b-4320-9e24-7f4c217af673'

        # Note that 'ddd' is optional and we are free to skip it
        data = {
            'aaa': aaa,
            'bbb': bbb,
            'ccc': ccc,
            'ddd': ddd,
            'eee': eee,
            'fff': fff,
            'ggg': ggg,
            'hhh': hhh,
            'iii': iii,
            'jjj': jjj,
            'mmm': mmm,
            'nnn': nnn,
            'ooo': ooo,
            'ppp': ppp,
            'qqq': qqq,
        }

        input = MyService._sio.parse_input(data, DATA_FORMAT.DICT)
        self.assertIsInstance(input, Bunch)

        self.assertEqual(input.aaa, aaa)
        self.assertIs(input.bbb, bbb)
        self.assertTrue(input.ccc)
        self.assertListEqual(input.ddd, ['1', '2', '3', '4'])

        self.assertIsInstance(input.eee, datetime)
        self.assertEqual(input.eee.year, 1999)
        self.assertEqual(input.eee.month, 12)
        self.assertEqual(input.eee.day, 31)

        self.assertIsInstance(input.fff, datetime)
        self.assertEqual(input.fff.year, 1988)
        self.assertEqual(input.fff.month, 1)
        self.assertEqual(input.fff.day, 29)

# ################################################################################################################################

    def test_parse_all_elem_types_list(self):

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', AsIs('bbb'), Bool('ccc'), CSV('ddd'), Date('eee'), DateTime('fff'), Decimal('ggg'), \
                    Dict('hhh', 'a', 'b', 'c'), DictList('iii', 'd', 'e', 'f'), Float('jjj'), Int('mmm'), List('nnn'), \
                    Opaque('ooo'), Text('ppp'), UUID('qqq')

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        aaa = 'aaa-111'
        bbb = object()
        ccc = True
        ddd = '1,2,3,4'
        eee = '1999-12-31'
        fff = '1988-01-29T11:22:33.0000Z'
        ggg = '123.456'
        hhh = {'a':1, 'b':2, 'c':3}
        iii = [{'d':4, 'e':5, 'f':6}, {'d':44, 'e':55, 'f':66}]
        jjj = '111.222'
        mmm = '9090'
        nnn = [1, 2, 3, 4]
        ooo = object()
        ppp = 'mytext'
        qqq = 'd011d054-db4b-4320-9e24-7f4c217af673'

        aaa2 = 'aaa-222'
        bbb2 = object()
        ccc2 = False
        ddd2 = '5,6,7,8'
        eee2 = '1999-12-25'
        fff2 = '1977-01-29T11:22:33.0000Z'
        ggg2 = '999.777'
        hhh2 = {'a':12, 'b':22, 'c':32}
        iii2 = [{'d':42, 'e':52, 'f':62}, {'d':442, 'e':552, 'f':662}]
        jjj2 = '333.444'
        mmm2 = '7171'
        nnn2 = [5, 6, 7, 8]
        ooo2 = object()
        ppp2 = 'mytext2'
        qqq2 = 'd011d054-db4b-4320-9e24-7f4c217af672'

        # Note that 'ddd' is optional and we are free to skip it
        data = [{
            'aaa': aaa,
            'bbb': bbb,
            'ccc': ccc,
            'ddd': ddd,
            'eee': eee,
            'fff': fff,
            'ggg': ggg,
            'hhh': hhh,
            'iii': iii,
            'jjj': jjj,
            'mmm': mmm,
            'nnn': nnn,
            'ooo': ooo,
            'ppp': ppp,
            'qqq': qqq,
        },
        {
            'aaa': aaa2,
            'bbb': bbb2,
            'ccc': ccc2,
            'ddd': ddd2,
            'eee': eee2,
            'fff': fff2,
            'ggg': ggg2,
            'hhh': hhh2,
            'iii': iii2,
            'jjj': jjj2,
            'mmm': mmm2,
            'nnn': nnn2,
            'ooo': ooo2,
            'ppp': ppp2,
            'qqq': qqq2,
        }]

        input = MyService._sio.parse_input(data, DATA_FORMAT.DICT)

        self.assertIsInstance(input, list)
        self.assertEqual(len(input), 2)

        input1 = input[0]
        input2 = input[1]

        self.assertEqual(input1.aaa, aaa)
        self.assertIs(input1.bbb, bbb)
        self.assertTrue(input1.ccc)
        self.assertListEqual(input1.ddd, ['1', '2', '3', '4'])

        self.assertIsInstance(input1.eee, datetime)
        self.assertEqual(input1.eee.year, 1999)
        self.assertEqual(input1.eee.month, 12)
        self.assertEqual(input1.eee.day, 31)

        self.assertIsInstance(input1.fff, datetime)
        self.assertEqual(input1.fff.year, 1988)
        self.assertEqual(input1.fff.month, 1)
        self.assertEqual(input1.fff.day, 29)
        self.assertEqual(input1.fff.hour, 11)
        self.assertEqual(input1.fff.minute, 22)
        self.assertEqual(input1.fff.second, 33)

        self.assertEqual(input2.aaa, aaa2)
        self.assertIs(input2.bbb, bbb2)
        self.assertFalse(input2.ccc)
        self.assertListEqual(input2.ddd, ['5', '6', '7', '8'])

        self.assertIsInstance(input2.eee, datetime)
        self.assertEqual(input2.eee.year, 1999)
        self.assertEqual(input2.eee.month, 12)
        self.assertEqual(input2.eee.day, 25)

        self.assertIsInstance(input2.fff, datetime)
        self.assertEqual(input2.fff.year, 1977)
        self.assertEqual(input2.fff.month, 1)
        self.assertEqual(input2.fff.day, 29)
        self.assertEqual(input2.fff.hour, 11)
        self.assertEqual(input2.fff.minute, 22)
        self.assertEqual(input2.fff.second, 33)

# ################################################################################################################################

    def test_parse_default_with_default_input_value(self):

        _default_bbb = 112233
        _default_fff = object()
        _default_input_value = object()

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', Int('-bbb', default=_default_bbb), Opaque('ccc'), '-ddd', Text('-eee'), \
                    Text('-fff', default=_default_fff)
                default_input_value = _default_input_value

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        aaa = 'aaa-111'
        ccc = object()
        eee = 'eee-111'

        # Note that 'ddd' is optional and we are free to skip it
        data = {
            'aaa': aaa,
            'ccc': ccc,
            'eee': eee,
        }

        input = MyService._sio.parse_input(data, DATA_FORMAT.DICT)
        self.assertIsInstance(input, Bunch)

        self.assertEqual(input.aaa, aaa)
        self.assertEqual(input.bbb, _default_bbb)
        self.assertIs(input.ccc, ccc)
        self.assertEqual(input.ddd, _default_input_value)
        self.assertEqual(input.eee, eee)
        self.assertEqual(input.fff, _default_fff)

# ################################################################################################################################

    def test_parse_default_no_default_input_value(self):

        _default_bbb = 112233
        _default_fff = object()

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', Int('-bbb', default=_default_bbb), Opaque('ccc'), '-ddd', Text('-eee'), \
                    Text('-fff', default=_default_fff)

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        aaa = 'aaa-111'
        ccc = object()
        eee = 'eee-111'

        # Note that 'ddd' is optional and we are free to skip it
        data = {
            'aaa': aaa,
            'ccc': ccc,
            'eee': eee,
        }

        input = MyService._sio.parse_input(data, DATA_FORMAT.DICT)
        self.assertIsInstance(input, Bunch)

        self.assertEqual(input.aaa, aaa)
        self.assertEqual(input.bbb, _default_bbb)
        self.assertIs(input.ccc, ccc)
        self.assertEqual(input.ddd, backward_compat_default_value)
        self.assertEqual(input.eee, eee)
        self.assertEqual(input.fff, _default_fff)

# ################################################################################################################################

    def test_parse_default_backward_compat_default_input_value(self):

        _default_bbb = 112233
        _default_fff = object()
        _default_input_value = object()

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', Int('-bbb', default=_default_bbb), Opaque('ccc'), '-ddd', Text('-eee'), \
                    Text('-fff', default=_default_fff)
                default_value = _default_input_value

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        aaa = 'aaa-111'
        ccc = object()
        eee = 'eee-111'

        # Note that 'ddd' is optional and we are free to skip it
        data = {
            'aaa': aaa,
            'ccc': ccc,
            'eee': eee,
        }

        input = MyService._sio.parse_input(data, DATA_FORMAT.DICT)
        self.assertIsInstance(input, Bunch)

        self.assertEqual(input.aaa, aaa)
        self.assertEqual(input.bbb, _default_bbb)
        self.assertIs(input.ccc, ccc)
        self.assertEqual(input.ddd, _default_input_value)
        self.assertEqual(input.eee, eee)
        self.assertEqual(input.fff, _default_fff)

# ################################################################################################################################

    def test_parse_default_all_elem_types(self):

        bbb = object()
        ccc = False
        ddd = [1, 2, 3, 4]
        eee = datetime(year=1990, month=1, day=29)
        fff = datetime(year=1990, month=1, day=29, hour=1, minute=2, second=3)
        ggg = decimal_Decimal('12.34')
        hhh = {'a':1, 'b':2, 'c':3}
        iii = [{'a':1, 'b':2, 'c':3}, {'a':11, 'b':22, 'c':33}]
        jjj = 99.77
        mmm = 123
        nnn = ['a', 'b', 'c']
        ooo = object()
        ppp = 'mytext'
        qqq = uuid4().hex

        class MyService(Service):
            class SimpleIO:
                input = '-aaa', AsIs('-bbb', default=bbb), Bool('-ccc', default=ccc), CSV('-ddd', default=ddd), \
                    Date('-eee', default=eee), DateTime('-fff', default=fff), Decimal('-ggg', default=ggg), \
                    Dict('-hhh', 'a', 'b', 'c', default=hhh), DictList('-iii', 'd', 'e', 'f', default=iii), \
                    Float('-jjj', default=jjj), Int('-mmm', default=mmm), List('-nnn', default=nnn), \
                    Opaque('-ooo', default=ooo), Text('-ppp', default=ppp), UUID('-qqq', default=qqq)

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        # Note that the input document is empty
        input = MyService._sio.parse_input({}, DATA_FORMAT.DICT)
        self.assertIsInstance(input, Bunch)

        self.assertEqual(input.aaa, backward_compat_default_value)
        self.assertEqual(input.bbb, bbb)
        self.assertEqual(input.ccc, ccc)
        self.assertEqual(input.ddd, ddd)
        self.assertEqual(input.eee, eee)
        self.assertEqual(input.fff, fff)
        self.assertEqual(input.ggg, ggg)
        self.assertEqual(input.hhh, hhh)
        self.assertEqual(input.iii, iii)
        self.assertEqual(input.jjj, jjj)
        self.assertEqual(input.mmm, mmm)
        self.assertEqual(input.nnn, nnn)
        self.assertEqual(input.ooo, ooo)
        self.assertEqual(input.ppp, ppp)
        self.assertEqual(input.qqq, qqq)

# ################################################################################################################################

    def test_parse_nested_dict_only_default_sio_level(self):

        _default_input_value = 'default-input-value'

        aaa = 'aaa'
        bbb = 'bbb'
        ccc = Dict('ccc', 'ddd', 'eee', '-fff')
        sss = Dict('sss', '-qqq')
        ggg = Dict('ggg', '-hhh', '-jjj', sss)

        class MyService(Service):
            class SimpleIO:
                input = Dict(aaa, bbb, ccc, ggg, '-ppp')
                default_input_value = _default_input_value

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        data = {
            'aaa': {
                'bbb': 'bbb-111',
                'ccc': {
                    'ddd': 'ddd-111',
                    'eee': 'eee-111',
                },
                'ggg': {
                    'sss': {}
                }
            }
        }

        input = MyService._sio.parse_input(data, DATA_FORMAT.DICT)
        self.assertIsInstance(input, Bunch)

        self.assertEqual(input.aaa.bbb, 'bbb-111')
        self.assertEqual(input.aaa.ccc.ddd, 'ddd-111')
        self.assertEqual(input.aaa.ccc.eee, 'eee-111')
        self.assertEqual(input.aaa.ccc.fff, _default_input_value)
        self.assertEqual(input.aaa.ccc.eee, 'eee-111')
        self.assertEqual(input.aaa.ggg.hhh, _default_input_value)
        self.assertEqual(input.aaa.ggg.sss.qqq, _default_input_value)

# ################################################################################################################################

    def test_parse_nested_dict_customer_no_defaults(self):

        locality = Dict('locality', 'type', 'name')
        address = Dict('address', locality, 'street')
        email = Dict('email', 'personal', 'business')
        customer = Dict('customer', 'name', email, address)

        class MyService(Service):
            class SimpleIO:
                input = customer

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        data = Bunch()
        data.customer = Bunch()
        data.customer.name = 'my-name'
        data.customer.email = Bunch()
        data.customer.email.personal = 'my-personal-email'
        data.customer.email.business = 'my-business-email'
        data.customer.address = Bunch()
        data.customer.address.street = 'my-street'
        data.customer.address.locality = Bunch()
        data.customer.address.locality.type = 'my-type'
        data.customer.address.locality.name = 'my-name'

        input = MyService._sio.parse_input(data, DATA_FORMAT.DICT)
        self.assertIsInstance(input, Bunch)

        self.assertEqual(input.customer.name, data.customer.name)
        self.assertEqual(input.customer.email.personal, data.customer.email.personal)
        self.assertEqual(input.customer.email.business, data.customer.email.business)
        self.assertEqual(input.customer.address.street, data.customer.address.street)
        self.assertEqual(input.customer.address.locality.type, data.customer.address.locality.type)
        self.assertEqual(input.customer.address.locality.name, data.customer.address.locality.name)

# ################################################################################################################################

    def test_parse_nested_dict_customer_deep_defaults_sio_level(self):

        locality = Dict('locality', '-type', '-name')
        address = Dict('address', locality, 'street')
        email = Dict('email', 'personal', 'business')
        customer = Dict('customer', 'name', email, address)

        _default_input_value = 'default-input-value'

        class MyService(Service):
            class SimpleIO:
                input = customer
                default_input_value = 'default-input-value'

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        # Note that locality has no type nor name and we expect for the SimpleIO-level default value to be used
        data = Bunch()
        data.customer = Bunch()
        data.customer.name = 'my-name'
        data.customer.email = Bunch()
        data.customer.email.personal = 'my-personal-email'
        data.customer.email.business = 'my-business-email'
        data.customer.address = Bunch()
        data.customer.address.street = 'my-street'
        data.customer.address.locality = Bunch()

        input = MyService._sio.parse_input(data, DATA_FORMAT.DICT)
        self.assertIsInstance(input, Bunch)

        self.assertEqual(input.customer.name, data.customer.name)
        self.assertEqual(input.customer.email.personal, data.customer.email.personal)
        self.assertEqual(input.customer.email.business, data.customer.email.business)
        self.assertEqual(input.customer.address.street, data.customer.address.street)
        self.assertEqual(input.customer.address.locality.type, _default_input_value)
        self.assertEqual(input.customer.address.locality.name, _default_input_value)

# ################################################################################################################################

    def test_parse_nested_dict_customer_deep_defaults_elem_level(self):

        locality_default = object()

        locality = Dict('locality', '-type', '-name', default=locality_default)
        address = Dict('address', locality, '-street')
        email = Dict('email', 'personal', 'business')
        customer = Dict('customer', 'name', email, address)

        _default_input_value = 'default-input-value'

        class MyService(Service):
            class SimpleIO:
                input = customer
                default_input_value = 'default-input-value'

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        # Note that this locality has no type nor name but we expect for that Dict's default value to be used,
        # also, address has no street but since this Dict has no default value, again, SimpleIO one will be used.
        data = Bunch()
        data.customer = Bunch()
        data.customer.name = 'my-name'
        data.customer.email = Bunch()
        data.customer.email.personal = 'my-personal-email'
        data.customer.email.business = 'my-business-email'
        data.customer.address = Bunch()
        data.customer.address.locality = Bunch()

        input = MyService._sio.parse_input(data, DATA_FORMAT.DICT)
        self.assertIsInstance(input, Bunch)

        self.assertEqual(input.customer.name, data.customer.name)
        self.assertEqual(input.customer.email.personal, data.customer.email.personal)
        self.assertEqual(input.customer.email.business, data.customer.email.business)
        self.assertEqual(input.customer.address.street, _default_input_value)
        self.assertEqual(input.customer.address.locality.type, locality_default)
        self.assertEqual(input.customer.address.locality.name, locality_default)

# ################################################################################################################################

    def test_parse_nested_dict_all_sio_elems(self):

        locality = Dict('locality', Int('type'), Text('name'), AsIs('coords'), Decimal('geo_skip'), Float('geo_diff'))
        address = Dict('address', locality, UUID('street_id'), CSV('prefs'), DateTime('since'), List('types'), Opaque('opaque1'))
        email = Dict('email', Text('value'), Bool('is_business'), Date('join_date'), DictList('preferred_order', 'name', 'pos'))
        customer = Dict('customer', 'name', email, address)

        class MyService(Service):
            class SimpleIO:
                input = customer

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        data = Bunch()
        data.customer = Bunch()
        data.customer.name = 'my-name'
        data.customer.email = Bunch()
        data.customer.email.value = 'my-email'
        data.customer.email.is_business = True
        data.customer.email.join_date = '1999-12-31'
        data.customer.email.preferred_order = [{'name':'address2', 'pos':'2'}, {'name':'address1', 'pos':'1'}]
        data.customer.address = Bunch()
        data.customer.address.locality = Bunch()
        data.customer.address.locality.type = '111'
        data.customer.address.locality.name = 'my-locality'
        data.customer.address.locality.coords = object()
        data.customer.address.locality.geo_skip = '123.456'
        data.customer.address.locality.geo_diff = '999.777'
        data.customer.address.street_id = uuid4().hex
        data.customer.address.prefs = '1,2,3,4'
        data.customer.address.since = '27-11-1988T11:22:33'
        data.customer.address.types = ['a', 'b', 'c', 'd']
        data.customer.address.opaque1 = object()

        input = MyService._sio.parse_input(data, DATA_FORMAT.DICT)
        self.assertIsInstance(input, Bunch)

        self.assertEqual(input.customer.name, data.customer.name)
        self.assertEqual(input.customer.email.value, data.customer.email.value)
        self.assertEqual(input.customer.email.is_business, data.customer.email.is_business)
        self.assertEqual(input.customer.email.join_date, dt_parse(data.customer.email.join_date))
        self.assertListEqual(input.customer.email.preferred_order, data.customer.email.preferred_order)
        self.assertEqual(input.customer.address.locality.type, int(data.customer.address.locality.type))
        self.assertEqual(input.customer.address.locality.name, data.customer.address.locality.name)
        self.assertIs(input.customer.address.locality.coords, data.customer.address.locality.coords)
        self.assertEqual(input.customer.address.locality.geo_skip, decimal_Decimal(data.customer.address.locality.geo_skip))
        self.assertEqual(input.customer.address.locality.geo_diff, float(data.customer.address.locality.geo_diff))
        self.assertEqual(input.customer.address.street_id, uuid_UUID(data.customer.address.street_id))
        self.assertEqual(input.customer.address.prefs, data.customer.address.prefs.split(','))
        self.assertEqual(input.customer.address.since, dt_parse(data.customer.address.since))
        self.assertEqual(input.customer.address.types, data.customer.address.types)
        self.assertIs(input.customer.address.opaque1, data.customer.address.opaque1)

# ################################################################################################################################

    def test_parse_nested_dict_all_sio_elems_some_missing(self):

        _default_input_value = 'default-input-value'
        default_locality = 'default-locality'
        default_address = 'default-address'

        locality = Dict('locality',
            Int('type'), Text('name'), AsIs('-coords'), Decimal('geo_skip'), Float('geo_diff'),
            default=default_locality)

        address = Dict('address',
            locality, UUID('-street_id'), CSV('prefs'), DateTime('since'), List('types'), Opaque('opaque1'),
            default=default_address)

        email = Dict('email', Text('value'), Bool('is_business'), Date('-join_date'), DictList('preferred_order', 'name', '-pos'))
        customer = Dict('customer', 'name', email, address)

        class MyService(Service):
            class SimpleIO:
                input = customer
                default_input_value = 'default-input-value'

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        # Note that 'join_date', 'street_id', 'coords' and one of 'pos' keys are missing in input below,
        # the test ensures that default values are used in their place.

        data = Bunch()
        data.customer = Bunch()
        data.customer.name = 'my-name'
        data.customer.email = Bunch()
        data.customer.email.value = 'my-email'
        data.customer.email.is_business = True
        data.customer.email.preferred_order = [{'name':'address2', 'pos':'2'}, {'name':'address1'}]
        data.customer.address = Bunch()
        data.customer.address.locality = Bunch()
        data.customer.address.locality.type = '111'
        data.customer.address.locality.name = 'my-locality'
        data.customer.address.locality.geo_skip = '123.456'
        data.customer.address.locality.geo_diff = '999.777'
        data.customer.address.prefs = '1,2,3,4'
        data.customer.address.since = '27-11-1988T11:22:33'
        data.customer.address.types = ['a', 'b', 'c', 'd']
        data.customer.address.opaque1 = object()

        input = MyService._sio.parse_input(data, DATA_FORMAT.DICT)
        self.assertIsInstance(input, Bunch)

        self.assertEqual(input.customer.name, data.customer.name)
        self.assertEqual(input.customer.email.value, data.customer.email.value)
        self.assertEqual(input.customer.email.is_business, data.customer.email.is_business)
        self.assertEqual(input.customer.email.join_date, _default_input_value)

        self.assertDictEqual(input.customer.email.preferred_order[0], data.customer.email.preferred_order[0])
        self.assertEqual(input.customer.email.preferred_order[1].name, data.customer.email.preferred_order[1]['name'])
        self.assertEqual(input.customer.email.preferred_order[1].pos, _default_input_value)

        self.assertEqual(input.customer.address.locality.type, int(data.customer.address.locality.type))
        self.assertEqual(input.customer.address.locality.name, data.customer.address.locality.name)
        self.assertEqual(input.customer.address.locality.coords, default_locality)
        self.assertEqual(input.customer.address.locality.geo_skip, decimal_Decimal(data.customer.address.locality.geo_skip))
        self.assertEqual(input.customer.address.locality.geo_diff, float(data.customer.address.locality.geo_diff))
        self.assertEqual(input.customer.address.street_id, default_address)
        self.assertEqual(input.customer.address.prefs, data.customer.address.prefs.split(','))
        self.assertEqual(input.customer.address.since, dt_parse(data.customer.address.since))
        self.assertEqual(input.customer.address.types, data.customer.address.types)
        self.assertIs(input.customer.address.opaque1, data.customer.address.opaque1)

# ################################################################################################################################

    def test_top_level_skip_empty_input_true_no_force_empty_with_class(self):

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', 'bbb', '-ccc', '-ddd'

                class SkipEmpty:
                    input = True

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        data = Bunch()
        data.aaa = 'aaa'
        data.bbb = 'bbb'

        input = MyService._sio.parse_input(data, DATA_FORMAT.DICT)
        self.assertIsInstance(input, Bunch)
        self.assertDictEqual(input, {
            'aaa': 'aaa',
            'bbb': 'bbb',
        })

# ################################################################################################################################

    def test_top_level_skip_empty_input_true_no_force_empty_with_attribute(self):

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', 'bbb', '-ccc', '-ddd'
                skip_empty_keys = True

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        data = Bunch()
        data.aaa = 'aaa'
        data.bbb = 'bbb'

        input = MyService._sio.parse_input(data, DATA_FORMAT.DICT)
        self.assertIsInstance(input, Bunch)
        self.assertDictEqual(input, {
            'aaa': 'aaa',
            'bbb': 'bbb',
            'ccc': '', # This should be empty by default because they are input data
            'ddd': '', # (Ditto)
        })

# ################################################################################################################################

    def test_top_level_skip_empty_input_true_with_force_empty_single(self):

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', 'bbb', '-ccc', '-ddd', '-eee', '-fff'

                class SkipEmpty:
                    input = True
                    force_empty_input = 'eee'

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        data = Bunch()
        data.aaa = 'aaa'
        data.bbb = 'bbb'

        input = MyService._sio.parse_input(data, DATA_FORMAT.DICT)
        self.assertIsInstance(input, Bunch)
        self.assertDictEqual(input, {
            'aaa': 'aaa',
            'bbb': 'bbb',
            'eee': backward_compat_default_value,
        })

# ################################################################################################################################

    def test_top_level_skip_empty_input_true_with_force_empty_multiple(self):

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', 'bbb', '-ccc', '-ddd', '-eee', '-fff'

                class SkipEmpty:
                    input = True
                    force_empty_input = 'eee', 'fff'

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        data = Bunch()
        data.aaa = 'aaa'
        data.bbb = 'bbb'

        input = MyService._sio.parse_input(data, DATA_FORMAT.DICT)
        self.assertIsInstance(input, Bunch)
        self.assertDictEqual(input, {
            'aaa': 'aaa',
            'bbb': 'bbb',
            'eee': backward_compat_default_value,
            'fff': backward_compat_default_value,
        })

# ################################################################################################################################

    def test_top_level_skip_empty_input_single(self):

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', 'bbb', '-ccc', '-ddd', '-eee', '-fff'
                default_value = NotGiven

                class SkipEmpty:
                    input = 'ccc'

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        data = Bunch()
        data.aaa = 'aaa'
        data.bbb = 'bbb'

        input = MyService._sio.parse_input(data, DATA_FORMAT.DICT)

        self.assertIsInstance(input, Bunch)
        self.assertDictEqual(input, {
            'aaa': 'aaa',
            'bbb': 'bbb',
            'ddd': NotGiven,
            'eee': NotGiven,
            'fff': NotGiven,
        })

# ################################################################################################################################

    def test_top_level_skip_empty_input_multiple(self):

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', 'bbb', '-ccc', '-ddd', '-eee', '-fff'
                default_value = NotGiven

                class SkipEmpty:
                    input = 'ccc', 'ddd'

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        data = Bunch()
        data.aaa = 'aaa'
        data.bbb = 'bbb'

        input = MyService._sio.parse_input(data, DATA_FORMAT.DICT)

        self.assertIsInstance(input, Bunch)
        self.assertDictEqual(input, {
            'aaa': 'aaa',
            'bbb': 'bbb',
            'eee': NotGiven,
            'fff': NotGiven,
        })

# ################################################################################################################################
# ################################################################################################################################
