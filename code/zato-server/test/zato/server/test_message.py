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
from bunch import Bunch

# Zato
from zato.server.message import ElemPathStore

class TestElemPathStore(TestCase):
    def test_invoke(self):

        cust_id = uuid4().hex

        street_name1 = uuid4().hex
        street_name2 = uuid4().hex

        street_elems1_1 = uuid4().hex
        street_elems1_2 = uuid4().hex

        street_elems2_1 = uuid4().hex
        street_elems2_2 = uuid4().hex

        msg = Bunch()
        msg.request = Bunch()
        msg.request.customer = Bunch()
        msg.request.customer.id = cust_id
        msg.request.customer.address = []

        msg.request.customer.address.append(
            {'street_name': street_name1,
             'elems': [street_elems1_1, street_elems1_2],
            }
        )

        msg.request.customer.address.append(
            {'street_name': street_name2,
             'elems': [street_elems2_1, street_elems2_2],
            }
        )

        eps = ElemPathStore()

        # Note that 3-7 return the same information
        expr1 = 'request.customer.id'
        expr2 = '*.id'
        expr3 = 'request.customer.id.text'
        expr4 = 'request.customer.address.list.street_name'
        expr5 = '*.address.list.street_name'
        expr6 = 'request.customer.*.street_name'
        expr7 = 'request.customer.address.list.street_name[1]'
        expr8 = 'request.customer.address.list.street_name'
        expr9 = 'request.customer.address.list.elems.list'

        expected = {
            '1': [cust_id],
            '2': [cust_id],
            '3': cust_id,
            '4': [street_name1, street_name2],
            '5': [street_name1, street_name2],
            '6': [street_name1, street_name2],
            '7': [street_name1, street_name2],
            '8': [street_name1, street_name2],
            '9': [street_elems1_1, street_elems1_2, street_elems2_1, street_elems2_2],
        }

        for idx, expr in enumerate(
            [expr1, expr2, expr3, expr4, expr5, expr6, expr7, expr8]):

            config = Bunch()
            config.name = str(idx+1)
            config.value = expr

            eps.create(config.name, config, {})
            result = eps.invoke(msg, config.name)

            self.assertEquals(expected[config.name], result)
