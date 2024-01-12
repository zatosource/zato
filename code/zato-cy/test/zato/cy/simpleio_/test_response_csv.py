# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# dateparser
from dateparser import parse as dt_parse

# Zato
from zato.common.api import DATA_FORMAT
from zato.common.test import BaseSIOTestCase
from zato.server.service import Service

# Zato - Cython
from zato.simpleio import AsIs, Bool, CySimpleIO, Date, DateTime, Decimal, \
     Float, Int, Opaque, SerialisationError, Text, UUID

# ################################################################################################################################
# ################################################################################################################################

class CSVResponse(BaseSIOTestCase):

# ################################################################################################################################

    def test_response_basic(self):

        class MyService(Service):
            class SimpleIO:
                output = 'aaa', Int('bbb'), Opaque('ccc'), '-ddd', '-eee'
                csv_delimiter = ';'

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        aaa = 'aaa-111'
        bbb = '222'
        ccc = 'ccc-ccc-ccc'
        eee = 'eee-444'

        # Note that 'ddd' is optional and we are free to skip it
        data = {
            'aaa': aaa,
            'bbb': bbb,
            'ccc': ccc,
            'eee': eee,
        }

        result = MyService._sio.get_output(data, DATA_FORMAT.CSV)
        lines = result.splitlines()

        self.assertEqual(lines[0], 'aaa;bbb;ccc;ddd;eee')
        self.assertEqual(lines[1], 'aaa-111;222;ccc-ccc-ccc;;eee-444')

# ################################################################################################################################

    def test_response_multiline(self):

        class MyService(Service):
            class SimpleIO:
                output = 'aaa', Int('bbb'), Opaque('ccc'), '-ddd', '-eee'
                csv_delimiter = ':'

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        aaa1 = 'aaa-111-1'
        bbb1 = '2221'
        ccc1 = 'ccc-ccc-ccc-1'
        eee1 = 'eee-444-1'

        aaa2 = 'aaa-111-2'
        bbb2 = '2222'
        ccc2 = 'ccc-ccc-ccc-2'
        eee2 = 'eee-444-2'

        # Note that 'ddd' is optional and we are free to skip it
        data1 = {'aaa': aaa1, 'bbb': bbb1, 'ccc': ccc1, 'eee': eee1}
        data2 = {'aaa': aaa2, 'bbb': bbb2, 'ccc': ccc2, 'eee': eee2}

        data = [data1, data2]

        result = MyService._sio.get_output(data, DATA_FORMAT.CSV)
        lines = result.splitlines()

        self.assertEqual(lines[0], 'aaa:bbb:ccc:ddd:eee')
        self.assertEqual(lines[1], 'aaa-111-1:2221:ccc-ccc-ccc-1::eee-444-1')
        self.assertEqual(lines[2], 'aaa-111-2:2222:ccc-ccc-ccc-2::eee-444-2')

# ################################################################################################################################

    def test_response_all_elem_types(self):

        class MyService(Service):
            class SimpleIO:
                output = 'aaa', AsIs('bbb'), Bool('ccc'), 'ddd', Date('eee'), DateTime('fff'), Decimal('ggg'), \
                    Float('jjj'), Int('mmm'), Opaque('ooo'), Text('ppp'), UUID('qqq')

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        aaa = 'aaa-111'
        bbb = 'bbb-222-bbb'
        ccc = 'True'
        ddd = ''
        eee = dt_parse('1999-12-31')
        fff = '1988-01-29T11:22:33.0000Z'
        ggg = '123.456'

        jjj = '111.222'
        mmm = '9090'

        ooo = 'ZZZ-ZZZ-ZZZ'
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
            'jjj': jjj,
            'mmm': mmm,
            'ooo': ooo,
            'ppp': ppp,
            'qqq': qqq
        }

        result = MyService._sio.get_output(data, DATA_FORMAT.CSV)
        lines = result.splitlines()

        self.assertEqual(lines[0], 'aaa,bbb,ccc,ddd,eee,fff,ggg,jjj,mmm,ooo,ppp,qqq')
        self.assertEqual(lines[1], 'aaa-111,bbb-222-bbb,True,,1999-12-31,1988-01-29T11:22:33+00:00,123.456,111.222,9090,' \
            'ZZZ-ZZZ-ZZZ,mytext,d011d054-db4b-4320-9e24-7f4c217af673')

# ################################################################################################################################

    def test_response_invalid_input(self):

        class MyService(Service):
            class SimpleIO:
                output = Int('aaa'), 'bbb'

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        aaa = 'aaa'
        bbb = '222'

        # Note that the value of 'aaa' is not an integer
        data = {
            'aaa': aaa,
            'bbb': bbb
        }

        with self.assertRaises(SerialisationError):
            MyService._sio.get_output(data, DATA_FORMAT.CSV)

# ################################################################################################################################
# ################################################################################################################################
