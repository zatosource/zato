# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from decimal import Decimal as decimal_Decimal
from uuid import UUID as uuid_UUID

# lxml
from lxml.etree import fromstring as lxml_fromstring, tostring as lxml_tostring

# Zato
from zato.common.api import DATA_FORMAT
from zato.common.test import BaseSIOTestCase
from zato.server.service import Service

# Zato - Cython
from zato.bunch import Bunch
from zato.simpleio import backward_compat_default_value, AsIs, Bool, CSV, CySimpleIO, Date, DateTime, Decimal, \
     Float, Int, Opaque, Text, UUID

# ################################################################################################################################

if 0:
    lxml_tostring = lxml_tostring

# ################################################################################################################################
# ################################################################################################################################

class XMLInputParsing(BaseSIOTestCase):

# ################################################################################################################################

    def test_parse_basic_request(self):

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', Int('bbb'), Opaque('ccc'), '-ddd', '-eee'

        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        aaa = 'aaa-111'
        bbb = '222'
        ccc = 'ccc-ccc-ccc'
        eee = 'eee-444'

        # Note that 'ddd' is optional and we are free to skip it
        data = lxml_fromstring("""<?xml version="1.0"?><root>
            <aaa>{}</aaa>
            <bbb>{}</bbb>
            <ccc>{}</ccc>
            <eee>{}</eee>
        </root>
        """.format(
            aaa, bbb, ccc, eee
        ))

        input = MyService._sio.parse_input(data, DATA_FORMAT.XML)

        self.assertIsInstance(input, Bunch)

        self.assertEquals(input.aaa, aaa)
        self.assertEquals(input.bbb, int(bbb))
        self.assertEquals(input.ccc, ccc)
        self.assertEquals(input.ddd, backward_compat_default_value)
        self.assertEquals(input.eee, eee)

# ################################################################################################################################

    def test_parse_all_elem_types_non_list(self):

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', AsIs('bbb'), Bool('ccc'), CSV('ddd'), Date('eee'), DateTime('fff'), Decimal('ggg'), \
                    Float('jjj'), Int('mmm'), Opaque('ooo'), Text('ppp'), UUID('qqq')

        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        aaa = 'aaa-111'
        bbb = 'bbb-222-bbb'
        ccc = True
        ddd = '1,2,3,4'
        eee = '1999-12-31'
        fff = '1988-01-29T11:22:33.0000Z'
        ggg = '123.456'

        jjj = '111.222'
        mmm = '9090'

        ooo = 'ZZZ-ZZZ-ZZZ'
        ppp = 'mytext'
        qqq = 'd011d054-db4b-4320-9e24-7f4c217af673'

        # Note that 'ddd' is optional and we are free to skip it
        data = lxml_fromstring("""<?xml version="1.0"?><root>
            <aaa>{}</aaa>
            <bbb>{}</bbb>
            <ccc>{}</ccc>
            <ddd>{}</ddd>
            <eee>{}</eee>
            <fff>{}</fff>
            <ggg>{}</ggg>
            <jjj>{}</jjj>
            <mmm>{}</mmm>
            <ooo>{}</ooo>
            <ppp>{}</ppp>
            <qqq>{}</qqq>
        </root>
        """.format(
            aaa, bbb, ccc, ddd, eee, fff, ggg, jjj, mmm, ooo, ppp, qqq
        ))

        input = MyService._sio.parse_input(data, DATA_FORMAT.XML)
        self.assertIsInstance(input, Bunch)

        self.assertEquals(input.aaa, aaa)
        self.assertEquals(input.bbb, bbb)
        self.assertTrue(input.ccc)
        self.assertListEqual(input.ddd, ['1', '2', '3', '4'])

        self.assertIsInstance(input.eee, datetime)
        self.assertEquals(input.eee.year, 1999)
        self.assertEquals(input.eee.month, 12)
        self.assertEquals(input.eee.day, 31)

        self.assertIsInstance(input.fff, datetime)
        self.assertEquals(input.fff.year, 1988)
        self.assertEquals(input.fff.month, 1)
        self.assertEquals(input.fff.day, 29)

        self.assertEquals(input.ggg, decimal_Decimal(ggg))
        self.assertEquals(input.jjj, float(jjj))
        self.assertEquals(input.mmm, int(mmm))
        self.assertEquals(input.ooo, ooo)
        self.assertEquals(input.ppp, ppp)
        self.assertEquals(input.qqq, uuid_UUID(qqq))

# ################################################################################################################################
# ################################################################################################################################
