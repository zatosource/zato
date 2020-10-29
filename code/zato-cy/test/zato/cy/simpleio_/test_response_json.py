# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from uuid import UUID as uuid_UUID

# Bunch
from bunch import bunchify

# dateparser
from dateparser import parse as dt_parse

# Zato
from zato.common.api import DATA_FORMAT
from zato.common.json_internal import loads as json_loads
from zato.common.test import BaseSIOTestCase
from zato.server.service import Service

# Zato - Cython
from zato.simpleio import AsIs, Bool, CySimpleIO, Date, DateTime, Decimal, \
     Float, Int, Opaque, SerialisationError, Text, UUID

# ################################################################################################################################
# ################################################################################################################################

class JSONResponse(BaseSIOTestCase):

# ################################################################################################################################

    def test_response_basic(self):

        class MyService(Service):
            class SimpleIO:
                output = 'aaa', Int('bbb'), Opaque('ccc'), '-ddd', '-eee'

        CySimpleIO.attach_sio(self.get_server_config(), MyService)

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

        result = MyService._sio.get_output(data, DATA_FORMAT.JSON)
        json_data = json_loads(result)

        self.assertEquals(json_data['aaa'], aaa)
        self.assertEquals(json_data['bbb'], int(bbb))
        self.assertEquals(json_data['ccc'], ccc)
        self.assertEquals(json_data['eee'], eee)

# ################################################################################################################################

    def test_response_with_response_elem(self):

        class MyService(Service):
            class SimpleIO:
                output = 'aaa', Int('bbb'), Opaque('ccc'), '-ddd', '-eee'
                response_elem = 'my_response_elem'

        CySimpleIO.attach_sio(self.get_server_config(), MyService)

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

        result = MyService._sio.get_output(data, DATA_FORMAT.JSON)

        json_data = json_loads(result)
        json_data = bunchify(json_data)

        self.assertEquals(json_data.my_response_elem.aaa, aaa)
        self.assertEquals(json_data.my_response_elem.bbb, int(bbb))
        self.assertEquals(json_data.my_response_elem.ccc, ccc)
        self.assertEquals(json_data.my_response_elem.eee, eee)

# ################################################################################################################################

    def test_response_multiline(self):

        class MyService(Service):
            class SimpleIO:
                output = 'aaa', Int('bbb'), Opaque('ccc'), '-ddd', '-eee'
                csv_delimiter = ':'

        CySimpleIO.attach_sio(self.get_server_config(), MyService)

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

        result = MyService._sio.get_output(data, DATA_FORMAT.JSON)
        json_data = json_loads(result)

        self.assertEquals(json_data[0]['aaa'], aaa1)
        self.assertEquals(json_data[0]['bbb'], int(bbb1))
        self.assertEquals(json_data[0]['ccc'], ccc1)
        self.assertEquals(json_data[0]['eee'], eee1)

        self.assertEquals(json_data[1]['aaa'], aaa2)
        self.assertEquals(json_data[1]['bbb'], int(bbb2))
        self.assertEquals(json_data[1]['ccc'], ccc2)
        self.assertEquals(json_data[1]['eee'], eee2)

# ################################################################################################################################

    def test_response_all_elem_types(self):

        class MyService(Service):
            class SimpleIO:
                output = 'aaa', AsIs('bbb'), Bool('ccc'), 'ddd', Date('eee'), DateTime('fff'), Decimal('ggg'), \
                    Float('jjj'), Int('mmm'), Opaque('ooo'), Text('ppp'), UUID('qqq')

        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        aaa = 'aaa-111'
        bbb = 'bbb-222-bbb'
        ccc = True
        ddd = ''
        eee = dt_parse('1999-12-31')
        fff = dt_parse('1988-01-29T11:22:33.0000Z')
        ggg = '123.456'

        jjj = '111.222'
        mmm = '9090'

        ooo = 'ZZZ-ZZZ-ZZZ'
        ppp = 'mytext'
        qqq = uuid_UUID('d011d054-db4b-4320-9e24-7f4c217af673')

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

        result = MyService._sio.get_output(data, DATA_FORMAT.JSON)
        json_data = json_loads(result)

        self.assertEquals(json_data['aaa'], aaa)
        self.assertEquals(json_data['bbb'], bbb)
        self.assertEquals(json_data['ccc'], ccc)
        self.assertEquals(json_data['eee'], '1999-12-31')
        self.assertEquals(json_data['fff'], '1988-01-29T11:22:33+00:00')
        self.assertEquals(json_data['ggg'], ggg)
        self.assertEquals(json_data['jjj'], float(jjj))
        self.assertEquals(json_data['mmm'], int(mmm))
        self.assertEquals(json_data['ooo'], ooo)
        self.assertEquals(json_data['ppp'], ppp)
        self.assertEquals(json_data['qqq'], qqq.hex)

# ################################################################################################################################

    def test_response_invalid_input(self):

        class MyService(Service):
            class SimpleIO:
                output = Int('aaa'), 'bbb'

        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        aaa = 'aaa'
        bbb = '222'

        # Note that the value of 'aaa' is not an integer
        data = {
            'aaa': aaa,
            'bbb': bbb
        }

        with self.assertRaises(SerialisationError) as ctx:
            MyService._sio.get_output(data, DATA_FORMAT.JSON)

        e = ctx.exception # type: SerialisationError
        self.assertTrue(e.args[0].startswith(
            """Exception `ValueError("invalid literal for int() with base 10: 'aaa'",)` while serialising `aaa` (<class 'test.zato.cy.simpleio_.test_response_json.JSONResponse.test_response_invalid_input.<locals>.MyService'>) ({'aaa': 'aaa', 'bbb': '222'})"""))

# ################################################################################################################################
# ################################################################################################################################
