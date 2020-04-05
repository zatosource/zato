# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from decimal import Decimal as decimal_Decimal
from uuid import UUID as uuid_UUID, uuid4

# dateutil
from dateutil.parser import parse as dt_parse

# lxml
from lxml.etree import fromstring as lxml_fromstring

# Zato
from zato.common import DATA_FORMAT
from zato.server.service import Service
from zato.simpleio import backward_compat_default_value, AsIs, Bool, CSV, CySimpleIO, Date, DateTime, Decimal, \
     Dict, DictList, Float, Int, List, NotGiven, Opaque, Text, UUID

# Zato - Cython
from test.zato.cy.simpleio_ import BaseTestCase
from zato.bunch import Bunch

# ################################################################################################################################
# ################################################################################################################################

class XMLInputParsing(BaseTestCase):

# ################################################################################################################################

    def test_parse_basic_request(self):

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', Int('bbb'), Opaque('ccc'), '-ddd', '-eee'

        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        aaa = 'aaa-111'
        bbb = '222'
        ccc = 'ccc'
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
# ################################################################################################################################
