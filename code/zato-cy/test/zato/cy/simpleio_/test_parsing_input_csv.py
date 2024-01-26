# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from decimal import Decimal as decimal_Decimal
from uuid import UUID as uuid_UUID

# Zato
from zato.common.api import DATA_FORMAT
from zato.common.test import BaseSIOTestCase
from zato.server.service import Service

# Zato - Cython
from zato.simpleio import backward_compat_default_value, AsIs, Bool, CySimpleIO, Date, DateTime, Decimal, \
     Float, Int, Opaque, Text, UUID

# ################################################################################################################################
# ################################################################################################################################

class CSVInputParsing(BaseSIOTestCase):

# ################################################################################################################################

    def test_parse_basic_request(self):

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', Int('bbb'), Opaque('ccc'), '-ddd', '-eee'

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        aaa = 'aaa-111'
        bbb = '222'
        ccc = 'ccc-ccc-ccc'
        eee = 'eee-444'

        # Note that 'ddd' is optional and we are free to skip it
        data = '{},{},{},,{}'.format(aaa, bbb, ccc, eee)

        input = MyService._sio.parse_input(data, DATA_FORMAT.CSV)
        self.assertIsInstance(input, list)

        input = input[0]
        self.assertEqual(input.aaa, aaa)
        self.assertEqual(input.bbb, int(bbb))
        self.assertEqual(input.ccc, ccc)
        self.assertEqual(input.ddd, backward_compat_default_value)
        self.assertEqual(input.eee, eee)

# ################################################################################################################################

    def test_csv_config(self):

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', Int('bbb'), Opaque('ccc'), '-ddd', '-eee'
                csv_delimiter = '|'

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        aaa = 'aaa-111'
        bbb = '222'
        ccc = 'ccc-ccc-ccc'
        eee = 'eee-444'

        # Note that 'ddd' is optional and we are free to skip it
        data = '{}|{}|{}||{}'.format(aaa, bbb, ccc, eee)

        input = MyService._sio.parse_input(data, DATA_FORMAT.CSV)
        self.assertIsInstance(input, list)

        input = input[0]
        self.assertEqual(input.aaa, aaa)
        self.assertEqual(input.bbb, int(bbb))
        self.assertEqual(input.ccc, ccc)
        self.assertEqual(input.ddd, backward_compat_default_value)
        self.assertEqual(input.eee, eee)

# ################################################################################################################################

    def test_parse_multiline(self):

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', Int('bbb'), Opaque('ccc'), '-ddd', '-eee'

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
        data  = '{},{},{},,{}'.format(aaa1, bbb1, ccc1, eee1)
        data += '\n'
        data += '{},{},{},,{}'.format(aaa2, bbb2, ccc2, eee2)

        input = MyService._sio.parse_input(data, DATA_FORMAT.CSV)
        self.assertIsInstance(input, list)

        input1 = input[0]
        input2 = input[1]

        self.assertEqual(input1.aaa, aaa1)
        self.assertEqual(input1.bbb, int(bbb1))
        self.assertEqual(input1.ccc, ccc1)
        self.assertEqual(input1.ddd, backward_compat_default_value)
        self.assertEqual(input1.eee, eee1)

        self.assertEqual(input2.aaa, aaa2)
        self.assertEqual(input2.bbb, int(bbb2))
        self.assertEqual(input2.ccc, ccc2)
        self.assertEqual(input2.ddd, backward_compat_default_value)
        self.assertEqual(input2.eee, eee2)

# ################################################################################################################################

    def test_parse_all_elem_types(self):

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', AsIs('bbb'), Bool('ccc'), 'ddd', Date('eee'), DateTime('fff'), Decimal('ggg'), \
                    Float('jjj'), Int('mmm'), Opaque('ooo'), Text('ppp'), UUID('qqq')

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        aaa = 'aaa-111'
        bbb = 'bbb-222-bbb'
        ccc = 'True'
        ddd = ''
        eee = '1999-12-31'
        fff = '1988-01-29T11:22:33.0000Z'
        ggg = '123.456'

        jjj = '111.222'
        mmm = '9090'

        ooo = 'ZZZ-ZZZ-ZZZ'
        ppp = 'mytext'
        qqq = 'd011d054-db4b-4320-9e24-7f4c217af673'

        # Note that 'ddd' is optional and we are free to skip it
        data = ','.join([
            aaa, bbb, ccc, ddd, eee, fff, ggg, jjj, mmm, ooo, ppp, qqq
        ])

        input = MyService._sio.parse_input(data, DATA_FORMAT.CSV)
        self.assertIsInstance(input, list)
        input = input[0]

        self.assertEqual(input.aaa, aaa)
        self.assertEqual(input.bbb, bbb)
        self.assertTrue(input.ccc)
        self.assertEqual(input.ddd, '')

        self.assertIsInstance(input.eee, datetime)
        self.assertEqual(input.eee.year, 1999)
        self.assertEqual(input.eee.month, 12)
        self.assertEqual(input.eee.day, 31)

        self.assertIsInstance(input.fff, datetime)
        self.assertEqual(input.fff.year, 1988)
        self.assertEqual(input.fff.month, 1)
        self.assertEqual(input.fff.day, 29)

        self.assertEqual(input.ggg, decimal_Decimal(ggg))
        self.assertEqual(input.jjj, float(jjj))
        self.assertEqual(input.mmm, int(mmm))
        self.assertEqual(input.ooo, ooo)
        self.assertEqual(input.ppp, ppp)
        self.assertEqual(input.qqq, uuid_UUID(qqq))

# ################################################################################################################################

    def test_parse_invalid_input(self):

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', 'bbb'

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        aaa = 'aaa-111'
        bbb = '222'
        ccc = '333'

        # Note that we are using an unexpected separator so that the expected values cannot be found
        data = '{}^{}^{}'.format(aaa, bbb, ccc)

        with self.assertRaises(ValueError) as ctx:
            MyService._sio.parse_input(data, DATA_FORMAT.CSV)

        e = ctx.exception # type: ValueError
        self.assertEqual(e.args[0], "Could not find input value at index `1` in `['aaa-111^222^333']` (dialect:excel, config:{})")

# ################################################################################################################################
# ################################################################################################################################
