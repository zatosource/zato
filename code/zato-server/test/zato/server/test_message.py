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
from zato.common.test import rand_string
from zato.server.message import JSONPointerStore, Mapper, XPathStore

# ################################################################################################################################

class TestJSONPointerStore(TestCase):

    def test_add(self):
        jps = JSONPointerStore()

        name1, expr1 = '1', '/{}/{}'.format(*rand_string(2))
        name2, expr2 = '2', '/aaa/{}/{}'.format(*rand_string(2))
        name3, expr3 = '3', '/aaa/{}/{}'.format(*rand_string(2))
        name4, expr4 = '2', '/aaa/{}/{}'.format(*rand_string(2))

        jps.add(name1, expr1)
        self.assertIn(name1, jps.data)
        self.assertEquals(expr1, jps.data[name1].path)

        jps.add(name2, expr2)
        self.assertIn(name2, jps.data)
        self.assertEquals(expr2, jps.data[name2].path)

        jps.add(name3, expr3)
        self.assertIn(name3, jps.data)
        self.assertEquals(expr3, jps.data[name3].path)

        # name4's value is '2' so it overrides 2

        jps.add(name4, expr4)
        self.assertIn(name4, jps.data)

        self.assertEquals(expr4, jps.data[name2].path)
        self.assertEquals(expr4, jps.data[name4].path)

    def test_get(self):
        jps = JSONPointerStore()

        c_value, d_value = rand_string(2)

        doc = {
            'a': {
                'b': [
                    {'c': c_value},
                    {'d': d_value},
                ]
            },
            'e': None,
            'f': 0
        }

        name1, expr1 = '1', '/a'
        name2, expr2 = '2', '/a/b'
        name3, expr3 = '3', '/a/b/0'
        name4, expr4 = '4', '/a/b/1'
        name5, expr5 = '5', '/a/b/0/c'

        # This will return default because the path points to None
        name6, expr6 = '6', '/e'

        # This will return default because there is no such path
        name7, expr7 = '7', '/e/e2/e3'

        # This will not return None because 0 is not None even though it's False in boolean sense
        name8, expr8 = '8', '/f'

        jps.add(name1, expr1)
        value = jps.get(name1, doc)
        self.assertListEqual(value.keys(), ['b'])

        jps.add(name2, expr2)
        value = jps.get(name2, doc)
        self.assertDictEqual(value[0], {'c':c_value})
        self.assertDictEqual(value[1], {'d':d_value})

        jps.add(name3, expr3)
        value = jps.get(name3, doc)
        self.assertDictEqual(value, {'c':c_value})

        jps.add(name4, expr4)
        value = jps.get(name4, doc)
        self.assertDictEqual(value, {'d':d_value})

        jps.add(name5, expr5)
        value = jps.get(name5, doc)
        self.assertEquals(value, c_value)

        default1 = rand_string()
        default2 = rand_string()

        jps.add(name6, expr6)
        value = jps.get(name6, doc, default1)
        self.assertEquals(value, default1)

        jps.add(name7, expr7)
        value = jps.get(name7, doc, default2)
        self.assertEquals(value, default2)

        jps.add(name8, expr8)
        value = jps.get(name8, doc)
        self.assertEquals(value, 0)

    def test_set_defaults(self):
        jps = JSONPointerStore()

        value1 = {'b':{}}
        value2 = {'c':{}}

        doc = {}

        name1, expr1 = '1', '/a'
        name2, expr2 = '2', '/a/b'

        jps.add(name1, expr1)
        jps.add(name2, expr2)

        jps.set(name1, doc, value1)
        value = jps.get(name1, doc)
        self.assertEquals(value, value1)

        jps.set(name2, doc, value2)
        value = jps.get(name2, doc)
        self.assertDictEqual(value, value2)

    def test_set_in_place(self):
        jps = JSONPointerStore()

        doc = {'a':'b'}
        value_random = rand_string()

        name1, expr1 = '1', '/a'

        jps.add(name1, expr1)

        # in_place is False so a new doc is created and the previous one should be retained
        new_doc = jps.set(name1, doc, value_random, True, in_place=False)

        value = jps.get(name1, new_doc)
        self.assertEquals(value, value_random)

        value = jps.get(name1, doc)
        self.assertEquals(value, 'b')

    def test_set_skip_missing(self):
        jps = JSONPointerStore()
        doc = {}

        name1, expr1 = '1', '/a'
        name2, expr2 = '2', '/b'

        value1, value2 = rand_string(2)
        default1, default2 = rand_string(2)

        jps.add(name1, expr1)
        jps.add(name2, expr2)

        # value is equal to default1 because it is never set by jps.set
        jps.set(name1, doc, value1, True)
        value = jps.get(name1, doc, default1)
        self.assertEquals(value, default1)
        self.assertDictEqual(doc, {})

        jps.set(name2, doc, value2)
        value = jps.get(name2, doc, default2)
        self.assertEquals(value, value2)
        self.assertDictEqual(doc, {'b':value2})

# ################################################################################################################################

class TestXPathStore(TestCase):
    def test_replace(self):
        msg = """
            <root>
              <elem1>elem1</elem1>
              <elem2 xmlns="just-testing">elem2</elem2>
              <list1>
                  <item1>item</item1>
                  <item1>item</item1>
                  <item2>
                      <key>key</key>
                  </item2>
              </list1>
            </root>
        """.encode('utf-8')

        expr1 = '/root/elem1'
        expr2 = '//jt:elem2'
        expr3 = '//list1/item1'
        expr4 = '//item2/key'

        for idx, expr in enumerate([expr1, expr2, expr3, expr4]):

            new_value = uuid4().hex

            config = Bunch()
            config.name = str(idx)
            config.value = expr

            xps = XPathStore()
            xps.add(config.name, config, ns_map={'jt':'just-testing'})

            replaced = xps.set(msg, config.name, new_value)
            result = xps.invoke(replaced, config.name, False)

            self.assertTrue(len(result) > 0)

            for item in result:
                self.assertEquals(item.text, new_value)

# ################################################################################################################################

class TestMapper(TestCase):
    def test_map(self):
        source = {
            'a': {
                'b': [1, 2, '3', 4],
                'c': {'d':'123'}
        }}

        m = Mapper(source)

        # 1:1 mappings
        m.map('/a/b', '/aa')
        m.map('/a/c/d', '/bb')

        # Force conversion to int
        m.map('int:/a/c/d', '/cc/dd')

        # Manually signal /cc/ee/ff should be a list here ..
        m.set([], '/cc/ee/ff')
        m.map('int:/a/c/d', '/cc/ee/ff/19')

        target = bunchify(m.target)

        self.assertListEqual(target.aa, [1, 2, '3', 4])
        self.assertEquals(target.bb, '123')
        self.assertEquals(target.cc.dd, 123)
        self.assertEquals(target.cc.ee.ff, [None] * 19 + [123])
