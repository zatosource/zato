# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from unittest import TestCase

# Bunch
from bunch import bunchify

# Zato
from zato.common import APISPEC
from zato.common.test import rand_string
from zato.server.apispec import Generator
from zato.server.apispec._docstring import Docstring, Docstring2, Docstring3
from zato.server.apispec._name import Name, Name2, Name3
from zato.server.apispec._invokes_list import InvokesList, InvokesList2, InvokesList3
from zato.server.apispec._invokes_string import InvokesString, InvokesString2, InvokesString3
from zato.server.apispec._ns1 import Namespace1, Namespace2, Namespace3
from zato.server.apispec._ns2 import Namespace11, Namespace22, Namespace33
from zato.server.apispec._ns3 import NoNamespace
from zato.server.apispec._simple_io import BoolInt, ForceTypeService, RequestResponse, String, String2, String3

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

simple_io_config = bunchify({
    'int': {'exact':['id'], 'suffix':['_id', '_count', '_size', '_timeout']},
    'bool': {'prefix':['is_', 'needs_', 'should_', 'by_', 'has_']},
    'secret': {'exact':['password', 'secret_key']},
})

# ################################################################################################################################

def get_service_store_services(*service_classes):
    out = {}
    for service_class in service_classes:
        out[service_class.get_impl_name()] = {'name':service_class.get_name(), 'service_class':service_class}
    return out

# ################################################################################################################################

def get_services_from_info(key, value, data, as_bunch=True):
    for dict_ in data['services']:
        if dict_.get(key) == value:
            return bunchify(dict_) if as_bunch else dict_
    else:
        raise ValueError('No such key/value {}/{} in {}'.format(key, value, data))

# ################################################################################################################################

class APISpecTestCase(TestCase):

# ################################################################################################################################

    def _sort_sio(self, elems):
        return [elem.items() for elem in sorted(elems, key=lambda k:k['name'])]

# ################################################################################################################################

    def test_name(self):
        gen = Generator(get_service_store_services(Name, Name2, Name3), simple_io_config)
        info = gen.get_info(rand_string())

        name1 = get_services_from_info('name', '_test.name', info)
        name2 = get_services_from_info('name', '_test.name2', info)
        name3 = get_services_from_info('name', '_test.name3', info)

        self.assertEquals(name1.name, '_test.name')
        self.assertEquals(name2.name, '_test.name2')
        self.assertEquals(name3.name, '_test.name3')

# ################################################################################################################################

    def test_docstring(self):
        gen = Generator(get_service_store_services(Docstring, Docstring2, Docstring3), simple_io_config)
        info = gen.get_info(rand_string())

        docstring1 = get_services_from_info('name', '_test.docstring', info)
        docstring2 = get_services_from_info('name', '_test.docstring2', info)
        docstring3 = get_services_from_info('name', '_test.docstring3', info)

        self.assertEquals(docstring1.name, '_test.docstring')
        self.assertEquals(docstring1.docs.summary, 'Docstring Summary')
        self.assertEquals(docstring1.docs.description, 'Docstring Summary')
        self.assertEquals(docstring1.docs.full, 'Docstring Summary')

        self.assertEquals(docstring2.name, '_test.docstring2')
        self.assertEquals(docstring2.docs.summary, 'Docstring2 Summary')
        self.assertEquals(docstring2.docs.description, 'Docstring2 Description')
        self.assertEquals(docstring2.docs.full, 'Docstring2 Summary.\n\nDocstring2 Description')

        self.assertEquals(docstring3.name, '_test.docstring3')
        self.assertEquals(docstring3.docs.summary, 'Docstring3 Summary')
        self.assertEquals(docstring3.docs.description, 'Docstring3 Description\n\nDocstring3 Description2')
        self.assertEquals(docstring3.docs.full, 'Docstring3 Summary.\n\nDocstring3 Description\n\nDocstring3 Description2')

# ################################################################################################################################

    def test_invokes_string(self):
        gen = Generator(get_service_store_services(InvokesString, InvokesString2, InvokesString3), simple_io_config)
        info = gen.get_info(rand_string())

        invokes_string1 = get_services_from_info('name', '_test.invokes-string', info)
        invokes_string2 = get_services_from_info('name', '_test.invokes-string2', info)
        invokes_string3 = get_services_from_info('name', '_test.invokes-string3', info)

        self.assertEquals(invokes_string1.name, '_test.invokes-string')
        self.assertListEqual(invokes_string1.invokes, ['_test.invokes-string2'])
        self.assertListEqual(invokes_string1.invoked_by, [])

        self.assertEquals(invokes_string2.name, '_test.invokes-string2')
        self.assertListEqual(invokes_string2.invokes, ['_test.invokes-string3'])
        self.assertListEqual(invokes_string2.invoked_by, ['_test.invokes-string', '_test.invokes-string3'])

        self.assertEquals(invokes_string3.name, '_test.invokes-string3')
        self.assertListEqual(invokes_string3.invokes, ['_test.invokes-string2'])
        self.assertListEqual(invokes_string3.invoked_by, ['_test.invokes-string2'])

# ################################################################################################################################

    def test_invokes_list(self):
        gen = Generator(get_service_store_services(InvokesList, InvokesList2, InvokesList3), simple_io_config)
        info = gen.get_info(rand_string())

        invokes_list1 = get_services_from_info('name', '_test.invokes-list', info)
        invokes_list2 = get_services_from_info('name', '_test.invokes-list2', info)
        invokes_list3 = get_services_from_info('name', '_test.invokes-list3', info)

        self.assertEquals(invokes_list1.name, '_test.invokes-list')
        self.assertListEqual(invokes_list1.invokes, ['_test.invokes-list2', '_test.invokes-list3'])
        self.assertListEqual(invokes_list1.invoked_by, [])

        self.assertEquals(invokes_list2.name, '_test.invokes-list2')
        self.assertListEqual(invokes_list2.invokes, ['_test.invokes-list3'])
        self.assertListEqual(invokes_list2.invoked_by, ['_test.invokes-list', '_test.invokes-list3'])

        self.assertEquals(invokes_list3.name, '_test.invokes-list3')
        self.assertListEqual(invokes_list3.invokes, ['_test.invokes-list2'])
        self.assertListEqual(invokes_list3.invoked_by, ['_test.invokes-list', '_test.invokes-list2'])

# ################################################################################################################################

    def test_sio_string1_open_api_v2(self):
        gen = Generator(get_service_store_services(String), simple_io_config)
        info = gen.get_info(rand_string())
        req = get_services_from_info('name', '_test.string', info)

        sio = req.simple_io[APISPEC.OPEN_API_V2]
        sio_ireq = self._sort_sio(sio.input_required)
        sio_oreq = self._sort_sio(sio.output_required)

        self.assertEquals(sio.spec_name, APISPEC.OPEN_API_V2)
        self.assertEquals(sio.request_elem, None)
        self.assertEquals(sio.response_elem, None)

        self.assertListEqual(sio_ireq, [
            [('subtype', None), ('is_required', True), ('type', 'string'), ('name', 'a')],
            [('subtype', None), ('is_required', True), ('type', 'string'), ('name', 'b')],
            [('subtype', None), ('is_required', True), ('type', 'string'), ('name', 'c')]
        ])

        self.assertListEqual(sio_oreq, [
            [('subtype', None), ('is_required', True), ('type', 'string'), ('name', 'aa')],
            [('subtype', None), ('is_required', True), ('type', 'string'), ('name', 'bb')],
            [('subtype', None), ('is_required', True), ('type', 'string'), ('name', 'cc')]
        ])

        self.assertListEqual(sio.input_optional, [])
        self.assertListEqual(sio.output_optional, [])

# ################################################################################################################################

    def test_sio_string1_zato(self):
        gen = Generator(get_service_store_services(String), simple_io_config)
        info = gen.get_info(rand_string())
        req = get_services_from_info('name', '_test.string', info)

        sio = req.simple_io['zato']
        sio_ireq = self._sort_sio(sio.input_required)
        sio_oreq = self._sort_sio(sio.output_required)

        self.assertEquals(sio.spec_name, 'zato')
        self.assertEquals(sio.request_elem, None)
        self.assertEquals(sio.response_elem, None)

        self.assertListEqual(sio_ireq, [
            [('subtype', 'string'), ('is_required', True), ('type', 'string'), ('name', 'a')],
            [('subtype', 'string'), ('is_required', True), ('type', 'string'), ('name', 'b')],
            [('subtype', 'string'), ('is_required', True), ('type', 'string'), ('name', 'c')]
        ])

        self.assertListEqual(sio_oreq, [
            [('subtype', 'string'), ('is_required', True), ('type', 'string'), ('name', 'aa')],
            [('subtype', 'string'), ('is_required', True), ('type', 'string'), ('name', 'bb')],
            [('subtype', 'string'), ('is_required', True), ('type', 'string'), ('name', 'cc')]
        ])

        self.assertListEqual(sio.input_optional, [])
        self.assertListEqual(sio.output_optional, [])

# ################################################################################################################################

    def test_sio_string2_open_api_v2(self):
        gen = Generator(get_service_store_services(String2), simple_io_config)
        info = gen.get_info(rand_string())
        req = get_services_from_info('name', '_test.string2', info)

        sio = req.simple_io[APISPEC.OPEN_API_V2]
        sio_ireq = self._sort_sio(sio.input_required)
        sio_iopt = self._sort_sio(sio.input_optional)
        sio_oopt = self._sort_sio(sio.output_optional)

        self.assertEquals(sio.spec_name, APISPEC.OPEN_API_V2)
        self.assertEquals(sio.request_elem, None)
        self.assertEquals(sio.response_elem, None)

        self.assertListEqual(sio_ireq, [
            [('subtype', None), ('is_required', True), ('type', 'string'), ('name', 'a2')],
            [('subtype', None), ('is_required', True), ('type', 'string'), ('name', 'b2')],
            [('subtype', None), ('is_required', True), ('type', 'string'), ('name', 'c2')]
        ])

        self.assertListEqual(sio_iopt, [
            [('subtype', None), ('is_required', False), ('type', 'string'), ('name', 'a2a')],
            [('subtype', None), ('is_required', False), ('type', 'string'), ('name', 'b2b')],
            [('subtype', None), ('is_required', False), ('type', 'string'), ('name', 'c2c')]
        ])

        self.assertListEqual(sio_oopt, [
            [('subtype', None), ('is_required', False), ('type', 'string'), ('name', 'aa')],
            [('subtype', None), ('is_required', False), ('type', 'string'), ('name', 'bb')],
            [('subtype', None), ('is_required', False), ('type', 'string'), ('name', 'cc')]
        ])

        self.assertListEqual(sio.output_required, [])

# ################################################################################################################################

    def test_sio_string2_zato(self):
        gen = Generator(get_service_store_services(String2), simple_io_config)
        info = gen.get_info(rand_string())
        req = get_services_from_info('name', '_test.string2', info)

        sio = req.simple_io['zato']
        sio_ireq = self._sort_sio(sio.input_required)
        sio_iopt = self._sort_sio(sio.input_optional)
        sio_oopt = self._sort_sio(sio.output_optional)

        self.assertEquals(sio.spec_name, 'zato')
        self.assertEquals(sio.request_elem, None)
        self.assertEquals(sio.response_elem, None)

        self.assertListEqual(sio_ireq, [
            [('subtype', 'string'), ('is_required', True), ('type', 'string'), ('name', 'a2')],
            [('subtype', 'string'), ('is_required', True), ('type', 'string'), ('name', 'b2')],
            [('subtype', 'string'), ('is_required', True), ('type', 'string'), ('name', 'c2')]
        ])

        self.assertListEqual(sio_iopt, [
            [('subtype', 'string'), ('is_required', False), ('type', 'string'), ('name', 'a2a')],
            [('subtype', 'string'), ('is_required', False), ('type', 'string'), ('name', 'b2b')],
            [('subtype', 'string'), ('is_required', False), ('type', 'string'), ('name', 'c2c')]
        ])

        self.assertListEqual(sio_oopt, [
            [('subtype', 'string'), ('is_required', False), ('type', 'string'), ('name', 'aa')],
            [('subtype', 'string'), ('is_required', False), ('type', 'string'), ('name', 'bb')],
            [('subtype', 'string'), ('is_required', False), ('type', 'string'), ('name', 'cc')]
        ])

        self.assertListEqual(sio.output_required, [])

# ################################################################################################################################

    def test_sio_string3_open_api_v2(self):
        gen = Generator(get_service_store_services(String3), simple_io_config)
        info = gen.get_info(rand_string())
        req = get_services_from_info('name', '_test.string3', info)

        sio = req.simple_io[APISPEC.OPEN_API_V2]
        sio_iopt = self._sort_sio(sio.input_optional)
        sio_oreq = self._sort_sio(sio.output_required)
        sio_oopt = self._sort_sio(sio.output_optional)

        self.assertEquals(sio.spec_name, APISPEC.OPEN_API_V2)
        self.assertEquals(sio.request_elem, None)
        self.assertEquals(sio.response_elem, None)

        self.assertListEqual(sio_iopt, [
            [('subtype', None), ('is_required', False), ('type', 'string'), ('name', 'a2a')],
            [('subtype', None), ('is_required', False), ('type', 'string'), ('name', 'b2b')],
            [('subtype', None), ('is_required', False), ('type', 'string'), ('name', 'c2c')]
        ])

        self.assertListEqual(sio_oreq, [
            [('subtype', None), ('is_required', True), ('type', 'string'), ('name', 'aa')],
            [('subtype', None), ('is_required', True), ('type', 'string'), ('name', 'bb')],
            [('subtype', None), ('is_required', True), ('type', 'string'), ('name', 'cc')]
        ])

        self.assertListEqual(sio_oopt, [
            [('subtype', None), ('is_required', False), ('type', 'string'), ('name', 'aaa')],
            [('subtype', None), ('is_required', False), ('type', 'string'), ('name', 'bbb')],
            [('subtype', None), ('is_required', False), ('type', 'string'), ('name', 'ccc')]
        ])

        self.assertListEqual(sio.input_required, [])

# ################################################################################################################################

    def test_sio_string3_zato(self):
        gen = Generator(get_service_store_services(String3), simple_io_config)
        info = gen.get_info(rand_string())
        req = get_services_from_info('name', '_test.string3', info)

        sio = req.simple_io['zato']
        sio_iopt = self._sort_sio(sio.input_optional)
        sio_oreq = self._sort_sio(sio.output_required)
        sio_oopt = self._sort_sio(sio.output_optional)

        self.assertEquals(sio.spec_name, 'zato')
        self.assertEquals(sio.request_elem, None)
        self.assertEquals(sio.response_elem, None)

        self.assertListEqual(sio_iopt, [
            [('subtype', 'string'), ('is_required', False), ('type', 'string'), ('name', 'a2a')],
            [('subtype', 'string'), ('is_required', False), ('type', 'string'), ('name', 'b2b')],
            [('subtype', 'string'), ('is_required', False), ('type', 'string'), ('name', 'c2c')]
        ])

        self.assertListEqual(sio_oreq, [
            [('subtype', 'string'), ('is_required', True), ('type', 'string'), ('name', 'aa')],
            [('subtype', 'string'), ('is_required', True), ('type', 'string'), ('name', 'bb')],
            [('subtype', 'string'), ('is_required', True), ('type', 'string'), ('name', 'cc')]
        ])

        self.assertListEqual(sio_oopt, [
            [('subtype', 'string'), ('is_required', False), ('type', 'string'), ('name', 'aaa')],
            [('subtype', 'string'), ('is_required', False), ('type', 'string'), ('name', 'bbb')],
            [('subtype', 'string'), ('is_required', False), ('type', 'string'), ('name', 'ccc')]
        ])

        self.assertListEqual(sio.input_required, [])

# ################################################################################################################################

    def test_sio_bool_int_open_api_v2(self):
        gen = Generator(get_service_store_services(BoolInt), simple_io_config)
        info = gen.get_info(rand_string())
        req = get_services_from_info('name', '_test.bool-int', info)

        sio = req.simple_io[APISPEC.OPEN_API_V2]

        sio_ireq = self._sort_sio(sio.input_required)
        sio_iopt = self._sort_sio(sio.input_optional)
        sio_oreq = self._sort_sio(sio.output_required)
        sio_oopt = self._sort_sio(sio.output_optional)

        self.assertEquals(sio.spec_name, APISPEC.OPEN_API_V2)
        self.assertEquals(sio.request_elem, None)
        self.assertEquals(sio.response_elem, None)

        self.assertEquals(sio_ireq[0], [('subtype', 'int32'), ('is_required', True), ('type', 'integer'), ('name', 'a_count')])
        self.assertEquals(sio_ireq[1], [('subtype', 'int32'), ('is_required', True), ('type', 'integer'), ('name', 'a_id')])
        self.assertEquals(sio_ireq[2], [('subtype', 'int32'), ('is_required', True), ('type', 'integer'), ('name', 'a_size')])
        self.assertEquals(sio_ireq[3], [('subtype', 'int32'), ('is_required', True), ('type', 'integer'), ('name', 'a_timeout')])
        self.assertEquals(sio_ireq[4], [('subtype', 'int32'), ('is_required', True), ('type', 'integer'), ('name', 'id')])
        self.assertEquals(sio_ireq[5], [('subtype', None),    ('is_required', True), ('type', 'boolean'), ('name', 'is_a')])
        self.assertEquals(sio_ireq[6], [('subtype', None),    ('is_required', True), ('type', 'boolean'), ('name', 'needs_a')])
        self.assertEquals(sio_ireq[7], [('subtype', None),    ('is_required', True), ('type', 'boolean'), ('name', 'should_a')])

        self.assertEquals(sio_iopt[0], [('subtype', 'int32'), ('is_required', False), ('type', 'integer'), ('name', 'b_count')])
        self.assertEquals(sio_iopt[1], [('subtype', 'int32'), ('is_required', False), ('type', 'integer'), ('name', 'b_id')])
        self.assertEquals(sio_iopt[2], [('subtype', 'int32'), ('is_required', False), ('type', 'integer'), ('name', 'b_size')])
        self.assertEquals(sio_iopt[3], [('subtype', 'int32'), ('is_required', False), ('type', 'integer'), ('name', 'b_timeout')])
        self.assertEquals(sio_iopt[4], [('subtype', 'int32'), ('is_required', False), ('type', 'integer'), ('name', 'id')])
        self.assertEquals(sio_iopt[5], [('subtype', None),    ('is_required', False), ('type', 'boolean'), ('name', 'is_b')])
        self.assertEquals(sio_iopt[6], [('subtype', None),    ('is_required', False), ('type', 'boolean'), ('name', 'needs_b')])
        self.assertEquals(sio_iopt[7], [('subtype', None),    ('is_required', False), ('type', 'boolean'), ('name', 'should_b')])

        self.assertEquals(sio_oreq[0], [('subtype', 'int32'), ('is_required', True), ('type', 'integer'), ('name', 'c_count')])
        self.assertEquals(sio_oreq[1], [('subtype', 'int32'), ('is_required', True), ('type', 'integer'), ('name', 'c_id')])
        self.assertEquals(sio_oreq[2], [('subtype', 'int32'), ('is_required', True), ('type', 'integer'), ('name', 'c_size')])
        self.assertEquals(sio_oreq[3], [('subtype', 'int32'), ('is_required', True), ('type', 'integer'), ('name', 'c_timeout')])
        self.assertEquals(sio_oreq[4], [('subtype', 'int32'), ('is_required', True), ('type', 'integer'), ('name', 'id')])
        self.assertEquals(sio_oreq[5], [('subtype', None),    ('is_required', True), ('type', 'boolean'), ('name', 'is_c')])
        self.assertEquals(sio_oreq[6], [('subtype', None),    ('is_required', True), ('type', 'boolean'), ('name', 'needs_c')])
        self.assertEquals(sio_oreq[7], [('subtype', None),    ('is_required', True), ('type', 'boolean'), ('name', 'should_c')])

        self.assertEquals(sio_oopt[0], [('subtype', 'int32'), ('is_required', False), ('type', 'integer'), ('name', 'd_count')])
        self.assertEquals(sio_oopt[1], [('subtype', 'int32'), ('is_required', False), ('type', 'integer'), ('name', 'd_id')])
        self.assertEquals(sio_oopt[2], [('subtype', 'int32'), ('is_required', False), ('type', 'integer'), ('name', 'd_size')])
        self.assertEquals(sio_oopt[3], [('subtype', 'int32'), ('is_required', False), ('type', 'integer'), ('name', 'd_timeout')])
        self.assertEquals(sio_oopt[4], [('subtype', 'int32'), ('is_required', False), ('type', 'integer'), ('name', 'id')])
        self.assertEquals(sio_oopt[5], [('subtype', None),    ('is_required', False), ('type', 'boolean'), ('name', 'is_d')])
        self.assertEquals(sio_oopt[6], [('subtype', None),    ('is_required', False), ('type', 'boolean'), ('name', 'needs_d')])
        self.assertEquals(sio_oopt[7], [('subtype', None),    ('is_required', False), ('type', 'boolean'), ('name', 'should_d')])

# ################################################################################################################################

    def test_sio_bool_zato(self):
        gen = Generator(get_service_store_services(BoolInt), simple_io_config)
        info = gen.get_info(rand_string())
        req = get_services_from_info('name', '_test.bool-int', info)

        sio = req.simple_io['zato']

        sio_ireq = self._sort_sio(sio.input_required)
        sio_iopt = self._sort_sio(sio.input_optional)
        sio_oreq = self._sort_sio(sio.output_required)
        sio_oopt = self._sort_sio(sio.output_optional)

        self.assertEquals(sio.spec_name, 'zato')
        self.assertEquals(sio.request_elem, None)
        self.assertEquals(sio.response_elem, None)

        self.assertEquals(sio_ireq[0], [('subtype', 'integer'), ('is_required', True), ('type', 'integer'), ('name', 'a_count')])
        self.assertEquals(sio_ireq[1], [('subtype', 'integer'), ('is_required', True), ('type', 'integer'), ('name', 'a_id')])
        self.assertEquals(sio_ireq[2], [('subtype', 'integer'), ('is_required', True), ('type', 'integer'), ('name', 'a_size')])
        self.assertEquals(sio_ireq[3], [('subtype', 'integer'), ('is_required', True), ('type', 'integer'), ('name', 'a_timeout')])
        self.assertEquals(sio_ireq[4], [('subtype', 'integer'), ('is_required', True), ('type', 'integer'), ('name', 'id')])
        self.assertEquals(sio_ireq[5], [('subtype', 'boolean'), ('is_required', True), ('type', 'boolean'), ('name', 'is_a')])
        self.assertEquals(sio_ireq[6], [('subtype', 'boolean'), ('is_required', True), ('type', 'boolean'), ('name', 'needs_a')])
        self.assertEquals(sio_ireq[7], [('subtype', 'boolean'), ('is_required', True), ('type', 'boolean'), ('name', 'should_a')])

        self.assertEquals(sio_iopt[0], [('subtype', 'integer'), ('is_required', False), ('type', 'integer'), ('name', 'b_count')])
        self.assertEquals(sio_iopt[1], [('subtype', 'integer'), ('is_required', False), ('type', 'integer'), ('name', 'b_id')])
        self.assertEquals(sio_iopt[2], [('subtype', 'integer'), ('is_required', False), ('type', 'integer'), ('name', 'b_size')])
        self.assertEquals(sio_iopt[3], [('subtype', 'integer'), ('is_required', False), ('type', 'integer'), ('name', 'b_timeout')])
        self.assertEquals(sio_iopt[4], [('subtype', 'integer'), ('is_required', False), ('type', 'integer'), ('name', 'id')])
        self.assertEquals(sio_iopt[5], [('subtype', 'boolean'), ('is_required', False), ('type', 'boolean'), ('name', 'is_b')])
        self.assertEquals(sio_iopt[6], [('subtype', 'boolean'), ('is_required', False), ('type', 'boolean'), ('name', 'needs_b')])
        self.assertEquals(sio_iopt[7], [('subtype', 'boolean'), ('is_required', False), ('type', 'boolean'), ('name', 'should_b')])

        self.assertEquals(sio_oreq[0], [('subtype', 'integer'), ('is_required', True), ('type', 'integer'), ('name', 'c_count')])
        self.assertEquals(sio_oreq[1], [('subtype', 'integer'), ('is_required', True), ('type', 'integer'), ('name', 'c_id')])
        self.assertEquals(sio_oreq[2], [('subtype', 'integer'), ('is_required', True), ('type', 'integer'), ('name', 'c_size')])
        self.assertEquals(sio_oreq[3], [('subtype', 'integer'), ('is_required', True), ('type', 'integer'), ('name', 'c_timeout')])
        self.assertEquals(sio_oreq[4], [('subtype', 'integer'), ('is_required', True), ('type', 'integer'), ('name', 'id')])
        self.assertEquals(sio_oreq[5], [('subtype', 'boolean'), ('is_required', True), ('type', 'boolean'), ('name', 'is_c')])
        self.assertEquals(sio_oreq[6], [('subtype', 'boolean'), ('is_required', True), ('type', 'boolean'), ('name', 'needs_c')])
        self.assertEquals(sio_oreq[7], [('subtype', 'boolean'), ('is_required', True), ('type', 'boolean'), ('name', 'should_c')])

        self.assertEquals(sio_oopt[0], [('subtype', 'integer'), ('is_required', False), ('type', 'integer'), ('name', 'd_count')])
        self.assertEquals(sio_oopt[1], [('subtype', 'integer'), ('is_required', False), ('type', 'integer'), ('name', 'd_id')])
        self.assertEquals(sio_oopt[2], [('subtype', 'integer'), ('is_required', False), ('type', 'integer'), ('name', 'd_size')])
        self.assertEquals(sio_oopt[3], [('subtype', 'integer'), ('is_required', False), ('type', 'integer'), ('name', 'd_timeout')])
        self.assertEquals(sio_oopt[4], [('subtype', 'integer'), ('is_required', False), ('type', 'integer'), ('name', 'id')])
        self.assertEquals(sio_oopt[5], [('subtype', 'boolean'), ('is_required', False), ('type', 'boolean'), ('name', 'is_d')])
        self.assertEquals(sio_oopt[6], [('subtype', 'boolean'), ('is_required', False), ('type', 'boolean'), ('name', 'needs_d')])
        self.assertEquals(sio_oopt[7], [('subtype', 'boolean'), ('is_required', False), ('type', 'boolean'), ('name', 'should_d')])

# ################################################################################################################################

    def test_force_type_open_api_v2(self):
        gen = Generator(get_service_store_services(ForceTypeService), simple_io_config)
        info = gen.get_info(rand_string())
        req = get_services_from_info('name', '_test.force-type', info)

        sio = req.simple_io[APISPEC.OPEN_API_V2]

        sio_ireq = self._sort_sio(sio.input_required)
        sio_iopt = self._sort_sio(sio.input_optional)
        sio_oreq = self._sort_sio(sio.output_required)
        sio_oopt = self._sort_sio(sio.output_optional)

        self.assertEquals(sio.spec_name, APISPEC.OPEN_API_V2)
        self.assertEquals(sio.request_elem, None)
        self.assertEquals(sio.response_elem, None)

        self.assertListEqual(sio_ireq, [
            [('subtype', None),        ('is_required', True), ('type', 'boolean'), ('name', 'b')],
            [('subtype', None),        ('is_required', True), ('type', 'boolean'), ('name', 'c')],
            [('subtype', None),        ('is_required', True), ('type', 'string'),  ('name', 'd')],
            [('subtype', None),        ('is_required', True), ('type', None),      ('name', 'e')],
            [('subtype', 'float'),     ('is_required', True), ('type', 'number'),  ('name', 'f')],
            [('subtype', 'int32'),     ('is_required', True), ('type', 'integer'), ('name', 'g')],
            [('subtype', 'int32'),     ('is_required', True), ('type', 'integer'), ('name', 'h')],
            [('subtype', None),        ('is_required', True), ('type', None),      ('name', 'i')],
            [('subtype', None),        ('is_required', True), ('type', 'string'),  ('name', 'is_a')],
            [('subtype', None),        ('is_required', True), ('type', None),      ('name', 'j')],
            [('subtype', None),        ('is_required', True), ('type', None),      ('name', 'k')],
            [('subtype', None),        ('is_required', True), ('type', None),      ('name', 'l')],
            [('subtype', None),        ('is_required', True), ('type', 'string'),  ('name', 'm')],
            [('subtype', 'date-time'), ('is_required', True), ('type', 'string'),  ('name', 'n')]
        ])

        self.assertListEqual(sio_iopt, [
            [('subtype', None),        ('is_required', False), ('type', 'boolean'), ('name', 'bb')],
            [('subtype', None),        ('is_required', False), ('type', 'boolean'), ('name', 'cc')],
            [('subtype', None),        ('is_required', False), ('type', 'string'),  ('name', 'dd')],
            [('subtype', None),        ('is_required', False), ('type', None),      ('name', 'ee')],
            [('subtype', 'float'),     ('is_required', False), ('type', 'number'),  ('name', 'ff')],
            [('subtype', 'int32'),     ('is_required', False), ('type', 'integer'), ('name', 'gg')],
            [('subtype', 'int32'),     ('is_required', False), ('type', 'integer'), ('name', 'hh')],
            [('subtype', None),        ('is_required', False), ('type', None),      ('name', 'ii')],
            [('subtype', None),        ('is_required', False), ('type', 'string'),  ('name', 'is_aa')],
            [('subtype', None),        ('is_required', False), ('type', None),      ('name', 'jj')],
            [('subtype', None),        ('is_required', False), ('type', None),      ('name', 'kk')],
            [('subtype', None),        ('is_required', False), ('type', None),      ('name', 'll')],
            [('subtype', None),        ('is_required', False), ('type', 'string'),  ('name', 'mm')],
            [('subtype', 'date-time'), ('is_required', False), ('type', 'string'),  ('name', 'nn')]
        ])

        self.assertListEqual(sio_oreq, [
            [('subtype', None),        ('is_required', True), ('type', 'boolean'), ('name', 'bbb')],
            [('subtype', None),        ('is_required', True), ('type', 'boolean'), ('name', 'ccc')],
            [('subtype', None),        ('is_required', True), ('type', 'string'),  ('name', 'ddd')],
            [('subtype', None),        ('is_required', True), ('type', None),      ('name', 'eee')],
            [('subtype', 'float'),     ('is_required', True), ('type', 'number'),  ('name', 'fff')],
            [('subtype', 'int32'),     ('is_required', True), ('type', 'integer'), ('name', 'ggg')],
            [('subtype', 'int32'),     ('is_required', True), ('type', 'integer'), ('name', 'hhh')],
            [('subtype', None),        ('is_required', True), ('type', None),      ('name', 'iii')],
            [('subtype', None),        ('is_required', True), ('type', 'string'),  ('name', 'is_aaa')],
            [('subtype', None),        ('is_required', True), ('type', None),      ('name', 'jjj')],
            [('subtype', None),        ('is_required', True), ('type', None),      ('name', 'kkk')],
            [('subtype', None),        ('is_required', True), ('type', None),      ('name', 'lll')],
            [('subtype', None),        ('is_required', True), ('type', 'string'),  ('name', 'mmm')],
            [('subtype', 'date-time'), ('is_required', True), ('type', 'string'),  ('name', 'nnn')]
        ])

        self.assertListEqual(sio_oopt, [
            [('subtype', None),        ('is_required', False), ('type', 'boolean'), ('name', 'bbbb')],
            [('subtype', None),        ('is_required', False), ('type', 'boolean'), ('name', 'cccc')],
            [('subtype', None),        ('is_required', False), ('type', 'string'),  ('name', 'dddd')],
            [('subtype', None),        ('is_required', False), ('type', None),      ('name', 'eeee')],
            [('subtype', 'float'),     ('is_required', False), ('type', 'number'),  ('name', 'ffff')],
            [('subtype', 'int32'),     ('is_required', False), ('type', 'integer'), ('name', 'gggg')],
            [('subtype', 'int32'),     ('is_required', False), ('type', 'integer'), ('name', 'hhhh')],
            [('subtype', None),        ('is_required', False), ('type', None),      ('name', 'iiii')],
            [('subtype', None),        ('is_required', False), ('type', 'string'),  ('name', 'is_aaaa')],
            [('subtype', None),        ('is_required', False), ('type', None),      ('name', 'jjjj')],
            [('subtype', None),        ('is_required', False), ('type', None),      ('name', 'kkkk')],
            [('subtype', None),        ('is_required', False), ('type', None),      ('name', 'llll')],
            [('subtype', None),        ('is_required', False), ('type', 'string'),  ('name', 'mmmm')],
            [('subtype', 'date-time'), ('is_required', False), ('type', 'string'),  ('name', 'nnnn')]
        ])

# ################################################################################################################################

    def test_force_type_zato(self):
        gen = Generator(get_service_store_services(ForceTypeService), simple_io_config)
        info = gen.get_info(rand_string())
        req = get_services_from_info('name', '_test.force-type', info)

        sio = req.simple_io['zato']

        sio_ireq = self._sort_sio(sio.input_required)
        sio_iopt = self._sort_sio(sio.input_optional)
        sio_oreq = self._sort_sio(sio.output_required)
        sio_oopt = self._sort_sio(sio.output_optional)

        self.assertEquals(sio.spec_name, 'zato')
        self.assertEquals(sio.request_elem, None)
        self.assertEquals(sio.response_elem, None)

        self.assertListEqual(sio_ireq, [
            [('subtype', 'boolean'),       ('is_required', True), ('type', 'boolean'), ('name', 'b')],
            [('subtype', 'boolean'),       ('is_required', True), ('type', 'boolean'), ('name', 'c')],
            [('subtype', 'string'),        ('is_required', True), ('type', 'string'),  ('name', 'd')],
            [('subtype', 'dict'),          ('is_required', True), ('type', 'dict'),    ('name', 'e')],
            [('subtype', 'float'),         ('is_required', True), ('type', 'number'),  ('name', 'f')],
            [('subtype', 'integer'),       ('is_required', True), ('type', 'integer'), ('name', 'g')],
            [('subtype', 'integer'),       ('is_required', True), ('type', 'integer'), ('name', 'h')],
            [('subtype', 'list'),          ('is_required', True), ('type', 'list'),    ('name', 'i')],
            [('subtype', 'string'),        ('is_required', True), ('type', 'string'),  ('name', 'is_a')],
            [('subtype', 'list-of-dicts'), ('is_required', True), ('type', 'list'),    ('name', 'j')],
            [('subtype', 'opaque'),        ('is_required', True), ('type', 'opaque'),  ('name', 'k')],
            [('subtype', 'opaque'),        ('is_required', True), ('type', 'opaque'),  ('name', 'l')],
            [('subtype', 'string'),        ('is_required', True), ('type', 'string'),  ('name', 'm')],
            [('subtype', 'date-time-utc'), ('is_required', True), ('type', 'string'),  ('name', 'n')]
        ])

        self.assertListEqual(sio_iopt, [
            [('subtype', 'boolean'),       ('is_required', False), ('type', 'boolean'), ('name', 'bb')],
            [('subtype', 'boolean'),       ('is_required', False), ('type', 'boolean'), ('name', 'cc')],
            [('subtype', 'string'),        ('is_required', False), ('type', 'string'),  ('name', 'dd')],
            [('subtype', 'dict'),          ('is_required', False), ('type', 'dict'),    ('name', 'ee')],
            [('subtype', 'float'),         ('is_required', False), ('type', 'number'),  ('name', 'ff')],
            [('subtype', 'integer'),       ('is_required', False), ('type', 'integer'), ('name', 'gg')],
            [('subtype', 'integer'),       ('is_required', False), ('type', 'integer'), ('name', 'hh')],
            [('subtype', 'list'),          ('is_required', False), ('type', 'list'),    ('name', 'ii')],
            [('subtype', 'string'),        ('is_required', False), ('type', 'string'),  ('name', 'is_aa')],
            [('subtype', 'list-of-dicts'), ('is_required', False), ('type', 'list'),    ('name', 'jj')],
            [('subtype', 'opaque'),        ('is_required', False), ('type', 'opaque'),  ('name', 'kk')],
            [('subtype', 'opaque'),        ('is_required', False), ('type', 'opaque'),  ('name', 'll')],
            [('subtype', 'string'),        ('is_required', False), ('type', 'string'),  ('name', 'mm')],
            [('subtype', 'date-time-utc'), ('is_required', False), ('type', 'string'),  ('name', 'nn')]
        ])

        self.assertListEqual(sio_oreq, [
            [('subtype', 'boolean'),       ('is_required', True), ('type', 'boolean'), ('name', 'bbb')],
            [('subtype', 'boolean'),       ('is_required', True), ('type', 'boolean'), ('name', 'ccc')],
            [('subtype', 'string'),        ('is_required', True), ('type', 'string'),  ('name', 'ddd')],
            [('subtype', 'dict'),          ('is_required', True), ('type', 'dict'),    ('name', 'eee')],
            [('subtype', 'float'),         ('is_required', True), ('type', 'number'),  ('name', 'fff')],
            [('subtype', 'integer'),       ('is_required', True), ('type', 'integer'), ('name', 'ggg')],
            [('subtype', 'integer'),       ('is_required', True), ('type', 'integer'), ('name', 'hhh')],
            [('subtype', 'list'),          ('is_required', True), ('type', 'list'),    ('name', 'iii')],
            [('subtype', 'string'),        ('is_required', True), ('type', 'string'),  ('name', 'is_aaa')],
            [('subtype', 'list-of-dicts'), ('is_required', True), ('type', 'list'),    ('name', 'jjj')],
            [('subtype', 'opaque'),        ('is_required', True), ('type', 'opaque'),  ('name', 'kkk')],
            [('subtype', 'opaque'),        ('is_required', True), ('type', 'opaque'),  ('name', 'lll')],
            [('subtype', 'string'),        ('is_required', True), ('type', 'string'),  ('name', 'mmm')],
            [('subtype', 'date-time-utc'), ('is_required', True), ('type', 'string'),  ('name', 'nnn')]
        ])

        self.assertListEqual(sio_oopt, [
            [('subtype', 'boolean'),       ('is_required', False), ('type', 'boolean'), ('name', 'bbbb')],
            [('subtype', 'boolean'),       ('is_required', False), ('type', 'boolean'), ('name', 'cccc')],
            [('subtype', 'string'),        ('is_required', False), ('type', 'string'),  ('name', 'dddd')],
            [('subtype', 'dict'),          ('is_required', False), ('type', 'dict'),    ('name', 'eeee')],
            [('subtype', 'float'),         ('is_required', False), ('type', 'number'),  ('name', 'ffff')],
            [('subtype', 'integer'),       ('is_required', False), ('type', 'integer'), ('name', 'gggg')],
            [('subtype', 'integer'),       ('is_required', False), ('type', 'integer'), ('name', 'hhhh')],
            [('subtype', 'list'),          ('is_required', False), ('type', 'list'),    ('name', 'iiii')],
            [('subtype', 'string'),        ('is_required', False), ('type', 'string'),  ('name', 'is_aaaa')],
            [('subtype', 'list-of-dicts'), ('is_required', False), ('type', 'list'),    ('name', 'jjjj')],
            [('subtype', 'opaque'),        ('is_required', False), ('type', 'opaque'),  ('name', 'kkkk')],
            [('subtype', 'opaque'),        ('is_required', False), ('type', 'opaque'),  ('name', 'llll')],
            [('subtype', 'string'),        ('is_required', False), ('type', 'string'),  ('name', 'mmmm')],
            [('subtype', 'date-time-utc'), ('is_required', False), ('type', 'string'),  ('name', 'nnnn')]
        ])

# ################################################################################################################################

    def test_request_response_open_api_v2(self):
        gen = Generator(get_service_store_services(RequestResponse), simple_io_config)
        info = gen.get_info(rand_string())
        req = get_services_from_info('name', '_test.request-response', info)
        sio = req.simple_io[APISPEC.OPEN_API_V2]

        self.assertEquals(sio.spec_name, APISPEC.OPEN_API_V2)
        self.assertEquals(sio.request_elem, 'my_request_elem')
        self.assertEquals(sio.response_elem, 'my_response_elem')

# ################################################################################################################################

    def test_namespace(self):
        gen = Generator(get_service_store_services(
            Namespace1, Namespace2, Namespace3, Namespace11, Namespace22, Namespace33, NoNamespace), simple_io_config)
        info = gen.get_info(rand_string())

        sns1 = get_services_from_info('name', '_test.namespace1', info)
        sns2 = get_services_from_info('name', '_test.namespace2', info)
        sns3 = get_services_from_info('name', '_test.namespace3', info)
        sns11 = get_services_from_info('name', '_test.namespace11', info)
        sns22 = get_services_from_info('name', '_test.namespace22', info)
        sns33 = get_services_from_info('name', '_test.namespace33', info)
        snons = get_services_from_info('name', '_test.no-namespace', info)

        namespaces = bunchify(info['namespaces'])
        myns = namespaces['myns']
        my_other_ns = namespaces['my-other-ns']
        my_other_ns_abc = namespaces['my-other-ns-abc']

        self.assertEquals(myns.name, 'myns')
        self.assertEquals(myns.docs, """This is my namespace.\nAs with regular docstrings it can contain multi-line documentation.\n\n* Documentation will be parsed as Markdown\n* Bullet lists *and* other non-obtrusive markup can be used\n""")
        self.assertEquals(myns.docs_md, """<p>This is my namespace.\nAs with regular docstrings it can contain multi-line documentation.</p>\n<ul>\n<li>Documentation will be parsed as Markdown</li>\n<li>Bullet lists <em>and</em> other non-obtrusive markup can be used</li>\n</ul>""")

        self.assertEquals(my_other_ns.name, 'my-other-ns')
        self.assertEquals(my_other_ns.docs, '')
        self.assertEquals(my_other_ns.docs_md, '')

        self.assertEquals(my_other_ns_abc.name, 'my-other-ns-abc')
        self.assertEquals(my_other_ns_abc.docs, '')
        self.assertEquals(my_other_ns_abc.docs_md, '')

        self.assertEquals(sns1.namespace_name, 'myns')
        self.assertEquals(sns2.namespace_name, 'my-other-ns')
        self.assertEquals(sns3.namespace_name, 'myns')
        self.assertEquals(sns11.namespace_name, 'myns')
        self.assertEquals(sns22.namespace_name, 'myns')
        self.assertEquals(sns33.namespace_name, 'my-other-ns-abc')
        self.assertEquals(snons.namespace_name, APISPEC.NAMESPACE_NULL)

# ################################################################################################################################
