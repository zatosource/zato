# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from unittest import TestCase
from uuid import uuid4

# Bunch
from bunch import Bunch, bunchify

# lxml
from lxml import etree

# Zato
from zato.common.test import rand_string
from zato.server.message import JSONPointerStore, Mapper, XPathStore

logger = getLogger(__name__)

def config_value(value):
    return Bunch({'value':value})

# ################################################################################################################################

class TestJSONPointerStore(TestCase):

    def test_add(self):
        jps = JSONPointerStore()

        name1, expr1 = '1', config_value('/{}/{}'.format(*rand_string(2)))
        name2, expr2 = '2', config_value('/aaa/{}/{}'.format(*rand_string(2)))
        name3, expr3 = '3', config_value('/aaa/{}/{}'.format(*rand_string(2)))
        name4, expr4 = '2', config_value('/aaa/{}/{}'.format(*rand_string(2)))

        jps.add(name1, Bunch(value=expr1.value))
        self.assertIn(name1, jps.data)
        self.assertEquals(expr1.value, jps.data[name1].path)

        jps.add(name2, Bunch(value=expr2.value))
        self.assertIn(name2, jps.data)
        self.assertEquals(expr2.value, jps.data[name2].path)

        jps.add(name3, Bunch(value=expr3.value))
        self.assertIn(name3, jps.data)
        self.assertEquals(expr3.value, jps.data[name3].path)

        # name4's value is '2' so it overrides 2

        jps.add(name4, Bunch(value=expr4.value))
        self.assertIn(name4, jps.data)

        self.assertEquals(expr4.value, jps.data[name2].path)
        self.assertEquals(expr4.value, jps.data[name4].path)

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

        name1, expr1 = '1', config_value('/a')
        name2, expr2 = '2', config_value('/a/b')
        name3, expr3 = '3', config_value('/a/b/0')
        name4, expr4 = '4', config_value('/a/b/1')
        name5, expr5 = '5', config_value('/a/b/0/c')

        # This will return default because the path points to None
        name6, expr6 = '6', config_value('/e')

        # This will return default because there is no such path
        name7, expr7 = '7', config_value('/e/e2/e3')

        # This will not return None because 0 is not None even though it's False in boolean sense
        name8, expr8 = '8', config_value('/f')

        jps.add(name1, Bunch(value=expr1.value))
        value = jps.get(name1, doc)
        self.assertListEqual(value.keys(), ['b'])

        jps.add(name2, Bunch(value=expr2.value))
        value = jps.get(name2, doc)
        self.assertDictEqual(value[0], {'c':c_value})
        self.assertDictEqual(value[1], {'d':d_value})

        jps.add(name3, Bunch(value=expr3.value))
        value = jps.get(name3, doc)
        self.assertDictEqual(value, {'c':c_value})

        jps.add(name4, Bunch(value=expr4.value))
        value = jps.get(name4, doc)
        self.assertDictEqual(value, {'d':d_value})

        jps.add(name5, Bunch(value=expr5.value))
        value = jps.get(name5, doc)
        self.assertEquals(value, c_value)

        default1 = rand_string()
        default2 = rand_string()

        jps.add(name6, Bunch(value=expr6.value))
        value = jps.get(name6, doc, default1)
        self.assertEquals(value, default1)

        jps.add(name7, Bunch(value=expr7.value))
        value = jps.get(name7, doc, default2)
        self.assertEquals(value, default2)

        jps.add(name8, Bunch(value=expr8.value))
        value = jps.get(name8, doc)
        self.assertEquals(value, 0)

    def test_set_defaults(self):
        jps = JSONPointerStore()

        value1 = {'b':{}}
        value2 = {'c':{}}

        doc = {}

        name1, expr1 = '1', config_value('/a')
        name2, expr2 = '2', config_value('/a/b')

        jps.add(name1, Bunch(value=expr1.value))
        jps.add(name2, Bunch(value=expr2.value))

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

        name1, expr1 = '1', config_value('/a')

        jps.add(name1, Bunch(value=expr1.value))

        # in_place is False so a new doc is created and the previous one should be retained
        new_doc = jps.set(name1, doc, value_random, True, in_place=False)

        value = jps.get(name1, new_doc)
        self.assertEquals(value, value_random)

        value = jps.get(name1, doc)
        self.assertEquals(value, 'b')

    def test_set_skip_missing(self):
        jps = JSONPointerStore()
        doc = {}

        name1, expr1 = '1', config_value('/a')
        name2, expr2 = '2', config_value('/b')

        value1, value2 = rand_string(2)
        default1, default2 = rand_string(2)

        jps.add(name1, Bunch(value=expr1.value))
        jps.add(name2, Bunch(value=expr2.value))

        # value is equal to default1 because it is never set by jps.set
        jps.set(name1, doc, value1, True)
        value = jps.get(name1, doc, default1)
        self.assertEquals(value, default1)
        self.assertDictEqual(doc, {})

        jps.set(name2, doc, value2)
        value = jps.get(name2, doc, default2)
        self.assertEquals(value, value2)
        self.assertDictEqual(doc, {'b':value2})

    def test_set_create_missing(self):
        jps = JSONPointerStore()
        doc = {}

        name1, expr1, value1 = '1', config_value('/a/b/c/d'), rand_string()
        name2, expr2, value2 = '2', config_value('/a/b/c/dd'), rand_string()
        name3, expr3, value3 = '3', config_value('/a/b/cc/d'), rand_string()

        jps.add(name1, Bunch(value=expr1.value))
        jps.add(name2, Bunch(value=expr2.value))
        jps.add(name3, Bunch(value=expr3.value))

        # Creates all the missing path parts in the empty document
        jps.set(name1, doc, value1)
        jps.set(name2, doc, value2)
        jps.set(name3, doc, value3)

        doc = bunchify(doc)

        self.assertEquals(doc.a.b.c.d, value1)
        self.assertEquals(doc.a.b.c.dd, value2)
        self.assertEquals(doc.a.b.cc.d, value3)

# ################################################################################################################################

class TestXPathStore(TestCase):
    def test_store_replace(self):

        expr1 = '/root/elem1'
        expr2 = '//jt:elem2'
        expr3 = '//list1/item1'
        expr4 = '//item2/key'

        ns_map={'jt':'just-testing'}

        for idx, expr in enumerate([expr1, expr2, expr3, expr4]):
            msg = """
                <root>
                  <elem1>elem1</elem1>
                  <elem2 xmlns="just-testing">elem2</elem2>
                  <list1>
                      <item1>item-a</item1>
                      <item1>item-b</item1>
                      <item2>
                          <key>key</key>
                      </item2>
                  </list1>
                </root>
            """.encode('utf-8')

            doc = etree.fromstring(msg)

            new_value = uuid4().hex

            config = Bunch()
            config.name = str(idx)
            config.value = expr

            xps = XPathStore()
            xps.add(config.name, config, ns_map=ns_map)

            xps.set(config.name, doc, new_value, ns_map)
            result = xps.get(config.name, doc)

            self.assertTrue(len(result) > 0)

            if isinstance(result, list):
                for item in result:
                    logger.warn('%r %r %r %r %s', idx, expr, item, result, etree.tostring(doc, pretty_print=1))
                    self.assertEquals(item, new_value)
            else:
                self.assertEquals(result, new_value)

    def test_get(self):
        msg = """
            <root>
                <a>123</a>
                <b>456</b>
            </root>
        """.encode('utf-8')

        config1 = Bunch()
        config1.name = '1'
        config1.value = '//a'

        config2 = Bunch()
        config2.name = '2'
        config2.value = '//zzz'
        default = rand_string()

        xps = XPathStore()
        xps.add(config1.name, config1)
        xps.add(config2.name, config2)

        doc = etree.fromstring(msg)

        value = xps.get('1', doc)
        self.assertEquals(value, '123')

        value = xps.get('2', doc, default)
        self.assertEquals(value, default)

    def test_set(self):
        msg = """
            <root>
                <a>123</a>
                <b>456</b>
            </root>
        """.encode('utf-8')

        config1 = Bunch()
        config1.name = '1'
        config1.value = '//a'
        new_value = rand_string()

        config2 = Bunch()
        config2.name = '2'
        config2.value = '/zzz'

        xps = XPathStore()
        xps.add(config1.name, config1)
        xps.add(config2.name, config2)

        doc = etree.fromstring(msg)

        xps.set('1', doc, new_value)
        value = xps.get('1', doc)
        self.assertEquals(value, new_value)

        xps.set('2', doc, new_value)
        value = xps.get('2', doc)
        self.assertEquals(value, None)

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
        m.map('int:/a/c/d', '/cc/ee/ff/19')

        target = bunchify(m.target)

        self.assertListEqual(target.aa, [1, 2, '3', 4])
        self.assertEquals(target.bb, '123')
        self.assertEquals(target.cc.dd, 123)
