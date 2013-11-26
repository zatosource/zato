# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from copy import deepcopy
from json import dumps
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
        self.eps = ElemPathStore()

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

        self.expr1 = 'request.customer.id.text'
        self.expr2 = '*.id'
        self.expr3 = 'request.customer.id'
        self.expr4 = 'request.customer.address.street_name'
        self.expr5 = '*.address.street_name'
        self.expr6 = 'request.customer.*.street_name'
        self.expr7 = 'request.customer.address.street_name[1]'
        self.expr8 = 'request.customer.address.street_name'
        self.expr9 = 'request.customer.address.elems'

        self.expressions = [self.expr1, self.expr2, self.expr3, self.expr4,
            self.expr5, self.expr6, self.expr7, self.expr8, self.expr9]

        for idx, expr in enumerate(self.expressions, 1):

            config = Bunch()
            config.name = str(idx)
            config.value = expr

            self.eps.create(config.name, config, {})

    def test_invoke(self):
        expected = {
            '1': self.cust_id,
            '2': [self.cust_id],
            '3': [self.cust_id],
            '4': [self.street_name1, self.street_name2],
            '5': [self.street_name1, self.street_name2],
            '6': [self.street_name1, self.street_name2],
            '7': [self.street_name1, self.street_name2],
            '8': [self.street_name1, self.street_name2],
            '9': [self.street_elems1_1, self.street_elems1_2,
                  self.street_elems2_1, self.street_elems2_2],
        }

        for idx, expr in enumerate(self.expressions, 1):
            name = str(idx)
            result = self.eps.invoke(self.msg, name)
            self.assertEquals(expected[name], result)

    def test_conversion_roundtrip(self):
        xml = self.eps.convert_dict_to_xml(self.msg)
        msg = self.eps.convert_xml_to_dict(xml)

        self.assertEquals(msg, self.msg)

    def test_replace(self):

        for idx, expr in enumerate(self.expressions, 1):

            msg = deepcopy(self.msg)
            new_value = uuid4().hex
            name = str(idx)

            replaced = self.eps.replace(msg, name, new_value)
            result = self.eps.invoke(replaced, name)

            if isinstance(result, basestring):
                self.assertEquals(result, new_value)
            else:
                for item in result:
                    self.assertEquals(item, new_value)
