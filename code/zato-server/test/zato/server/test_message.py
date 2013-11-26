# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from unittest import TestCase
from uuid import uuid4

# Bunch
from bunch import Bunch, bunchify, unbunchify

# lxml
from lxml import etree

# xmldict
from xmltodict import parse, unparse

# Zato
from zato.server.message import ElemPathStore

class TestElemPathStore(TestCase):
    def setUp(self):
        self.cust_id = uuid4().hex

        self.street_name1 = 'street-1-{}'.format(uuid4().hex)
        self.street_name2 = 'street-2-{}'.format(uuid4().hex)

        self.street_elems1_1 = 'street-1_1-{}'.format(uuid4().hex)
        self.street_elems1_2 = 'street-1_2-{}'.format(uuid4().hex)

        self.street_elems2_1 = 'street-2_1-{}'.format(uuid4().hex)
        self.street_elems2_2 = 'street-2_2-{}'.format(uuid4().hex)

        self.msg = Bunch()
        self.msg.request = Bunch()
        self.msg.request.customer = Bunch()
        self.msg.request.customer.id = self.cust_id
        self.msg.request.customer.address = []

        self.msg.request.customer.address.append(
            {'street_name': self.street_name1,
             'elems': [self.street_elems1_1, self.street_elems1_2],
            }
        )

        self.msg.request.customer.address.append(
            {'street_name': self.street_name2,
             'elems': [self.street_elems2_1, self.street_elems2_2],
            }
        )

    def test_invoke(self):
        eps = ElemPathStore()

        # Note that 3-7 return the same information
        expr1 = 'request.customer.id'
        expr2 = '*.id'
        expr3 = 'request.customer.id.text'
        expr4 = 'request.customer.address.street_name'
        expr5 = '*.address.street_name'
        expr6 = 'request.customer.*.street_name'
        expr7 = 'request.customer.address.street_name[1]'
        expr8 = 'request.customer.address.street_name'
        expr9 = 'request.customer.address.elems'

        expected = {
            '1': [self.cust_id],
            '2': [self.cust_id],
            '3': self.cust_id,
            '4': [self.street_name1, self.street_name2],
            '5': [self.street_name1, self.street_name2],
            '6': [self.street_name1, self.street_name2],
            '7': [self.street_name1, self.street_name2],
            '8': [self.street_name1, self.street_name2],
            '9': [self.street_elems1_1, self.street_elems1_2,
                  self.street_elems2_1, self.street_elems2_2],
        }

        for idx, expr in enumerate(
            [expr1, expr2, expr3, expr4, expr5, expr6, expr7, expr8]):

            config = Bunch()
            config.name = str(idx+1)
            config.value = expr

            eps.create(config.name, config, {})
            result = eps.invoke(self.msg, config.name)

            self.assertEquals(expected[config.name], result)

    def test_conversion_roundtrip(self):
        eps = ElemPathStore()
        xml = eps.convert_dict_to_xml(self.msg)
        msg = eps.convert_xml_to_dict(xml)

        self.assertEquals(msg, self.msg)
