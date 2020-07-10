# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from copy import deepcopy
from http.client import OK
from json import loads as json_loads
from io import StringIO

# lxml
from lxml.etree import _Element as EtreeElement
from lxml.objectify import fromstring as objectify_from_string, ObjectifiedElement

# Zato
from zato.common import DATA_FORMAT, ZATO_OK
from zato.common.test import ODBTestCase, test_odb_data
from zato.server.service import Service

# Zato - Cython
from test.zato.cy.simpleio_ import BaseTestCase
from zato.cy.reqresp.payload import SimpleIOPayload
from zato.cy.reqresp.response import Response
from zato.simpleio import CySimpleIO

# ################################################################################################################################
# ################################################################################################################################

class MyBaseService(Service):
    class SimpleIO:
        input = 'aaa', 'bbb', 'ccc', '-ddd', '-eee'
        output = 'qqq', 'www', '-eee', '-fff'

class MyODBService(Service):
    class SimpleIO:
        output = 'cluster_id', 'is_active', 'name'


class MyZatoClass:
    def to_zato(self):
        return {
            'cluster_id': test_odb_data.cluster_id,
            'is_active':  test_odb_data.is_active,
            'name':       test_odb_data.name,
        }

# ################################################################################################################################
# ################################################################################################################################

class ResponseTestCase(BaseTestCase):

    def xtest_defaults(self):
        response = Response()

        self.assertIsNone(response.cid)
        self.assertIsNone(response.content_encoding)
        self.assertEqual(response.content_type, 'text/plain')
        self.assertFalse(response.content_type_changed)
        self.assertIsNone(response.data_format)
        self.assertDictEqual(response.headers, {})
        self.assertEqual(response.payload, '')
        self.assertEqual(response.result, ZATO_OK)
        self.assertEqual(response.result_details, '')
        self.assertEqual(response.status_code, OK)
        self.assertEqual(response.status_message, 'OK')

# ################################################################################################################################

    def xtest_len(self):
        response = Response()
        response._payload = 'abcdef'

        self.assertEqual(len(response), 6)

# ################################################################################################################################

    def xtest_content_type(self):
        response = Response()
        response.content_type = 'abc'

        self.assertTrue(response.content_type_changed)
        self.assertEqual(response.content_type, 'abc')

# ################################################################################################################################

    def xtest_init_no_sio(self):
        response = Response()
        response.init('abc', None, DATA_FORMAT.CSV)

        self.assertEqual(response.cid, 'abc')
        self.assertEqual(response.data_format, DATA_FORMAT.CSV)
        self.assertEqual(response.payload, '')

# ################################################################################################################################

    def xtest_init_has_sio(self):

        MyService = deepcopy(MyBaseService)
        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        response = Response()
        response.init('abc', MyService._sio, DATA_FORMAT.CSV)

        self.assertIsInstance(response.payload, SimpleIOPayload)

# ################################################################################################################################

    def xtest_setslice(self):

        MyService = deepcopy(MyBaseService)
        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        response = Response()
        response.init('abc', MyService._sio, DATA_FORMAT.CSV)

        data = [{'a':'aa', 'b':'bb'}, {'a':'aa2', 'b':'bb2'}]
        response.payload[:] = data

        for idx, elem in enumerate(data):
            self.assertDictEqual(data[idx], response.payload.user_attrs_list[idx])

# ################################################################################################################################

    def xtest_set_payload_dict_has_sio_case_1a(self):

        MyService = deepcopy(MyBaseService)
        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        response = Response()
        response.init('abc', MyService._sio, DATA_FORMAT.XML)

        # Note that 'ddd' is optional so it can be missing
        # and that 'fff' is not in SIO so it should be ignored.
        data = {'aaa':'111', 'bbb':'222', 'ccc':'333', 'eee':'555', 'fff':'666', 'qqq':777, 'www':888}
        response.payload = data

# ################################################################################################################################

    def xtest_set_payload_dict_no_sio_case_1b(self):

        response = Response()
        response.init('abc', None, DATA_FORMAT.CSV)

        data = {'a':'aa', 'b':'bb'}
        response.payload = data

        self.assertDictEqual(response.payload, data)

# ################################################################################################################################

    def xtest_set_payload_direct_payload_case_2a(self):
        # basestring, dict, list, tuple, bool, Number + (EtreeElement, ObjectifiedElement)

        data_01 = b'abc'
        data_02 = u'def'
        data_03 = [1, 2, 3]
        data_04 = (5, 6, 7)
        data_05 = True
        data_06 = False
        data_07 = 1
        data_08 = 2.0
        data_09 = EtreeElement()
        data_10 = ObjectifiedElement()

        elems = [data_01, data_02, data_03, data_04, data_05, data_06, data_07, data_08, data_09, data_10]

        response = Response()
        response.init('abc', None, DATA_FORMAT.CSV)

        for elem in elems:
            response.payload = elem
            self.assertIs(response.payload, elem)

# ################################################################################################################################

    def xtest_set_payload_not_direct_payload_no_sio_case_2b2(self):

        class MyCustomPayloadType:
            def __repr__(self):
                return '<MyCustomPayloadType>'

        response = Response()
        response.init('abc', None, DATA_FORMAT.CSV)

        try:
            response.payload = MyCustomPayloadType()
        except Exception as e:
            self.assertEqual(e.args[0], 'Cannot serialise value without SimpleIO ouput declaration (<MyCustomPayloadType>)')
        else:
            self.fail('Expected for an exception to be raised')

# ################################################################################################################################
# ################################################################################################################################

class PayloadFromSQLAlchemy(BaseTestCase, ODBTestCase):

    def setUp(self):
        super(BaseTestCase, self).setUp()
        super(ODBTestCase, self).setUp()

    def tearDown(self):
        super(BaseTestCase, self).tearDown()
        super(ODBTestCase, self).tearDown()

# ################################################################################################################################

    def _prepare_sio_response(self, data, data_format, is_list):
        # type: (object, str, bool) -> str

        MyService = deepcopy(MyODBService)
        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        response = Response()
        response.init('abc', MyService._sio, data_format)

        if is_list:
            response.payload[:] = data
        else:
            response.payload = data

        return response.payload.getvalue()

# ################################################################################################################################

    def _prepare_sio_response_from_orm(self, data_format, is_list):
        # type: (str, bool) -> str
        data = self.get_sample_odb_orm_result(is_list)
        return self._prepare_sio_response(data, data_format, is_list)

# ################################################################################################################################

    def _prepare_sio_response_from_zato(self, data_format, is_list):
        # type: (str, bool) -> str
        data = MyZatoClass()
        data = [data] if is_list else data
        return self._prepare_sio_response(data, data_format, is_list)

# ################################################################################################################################

    def xtest_sio_response_from_sqlalchemy_orm_single_json(self):

        result = self._prepare_sio_response_from_orm(DATA_FORMAT.JSON, False)
        result = json_loads(result)

        self.assertEqual(result['cluster_id'], test_odb_data.cluster_id)
        self.assertEqual(result['name'], test_odb_data.name)
        self.assertIs(result['is_active'], test_odb_data.is_active)

# ################################################################################################################################

    def xtest_sio_response_from_sqlalchemy_orm_single_xml(self):

        result = self._prepare_sio_response_from_orm(DATA_FORMAT.XML, False)
        result = result.encode('utf8')
        root = objectify_from_string(result)

        self.assertEqual(root.cluster_id, test_odb_data.cluster_id)
        self.assertEqual(root.name, test_odb_data.name)
        self.assertTrue(root.is_active)

# ################################################################################################################################

    def xtest_sio_response_from_sqlalchemy_orm_single_csv(self):

        result = self._prepare_sio_response_from_orm(DATA_FORMAT.CSV, False)
        result = result.splitlines()

        data_row_expected = '{},{},{}'.format(test_odb_data.cluster_id, test_odb_data.is_active, test_odb_data.name)

        self.assertEqual(result[0], 'cluster_id,is_active,name')
        self.assertEqual(result[1], data_row_expected)

# ################################################################################################################################

    def xtest_sio_response_from_sqlalchemy_orm_single_dict(self):

        result = self._prepare_sio_response_from_orm(DATA_FORMAT.DICT, False)

        self.assertDictEqual(result, {
            'cluster_id': test_odb_data.cluster_id,
            'is_active': test_odb_data.is_active,
            'name': test_odb_data.name,
        })

# ################################################################################################################################

    def xtest_sio_response_from_sqlalchemy_orm_list_json(self):

        result = self._prepare_sio_response_from_orm(DATA_FORMAT.JSON, True)
        result = json_loads(result)
        result = result[0]

        self.assertEqual(result['cluster_id'], test_odb_data.cluster_id)
        self.assertEqual(result['name'], test_odb_data.name)
        self.assertIs(result['is_active'], test_odb_data.is_active)

# ################################################################################################################################

    def xtest_sio_response_from_sqlalchemy_orm_list_xml(self):

        result = self._prepare_sio_response_from_orm(DATA_FORMAT.XML, True)
        result = result.encode('utf8')
        root = objectify_from_string(result)

        self.assertEqual(root.item.cluster_id, test_odb_data.cluster_id)
        self.assertEqual(root.item.name, test_odb_data.name)
        self.assertTrue(root.item.is_active)

# ################################################################################################################################

    def xtest_sio_response_from_sqlalchemy_orm_list_csv(self):

        result = self._prepare_sio_response_from_orm(DATA_FORMAT.CSV, True)
        result = result.splitlines()

        data_row_expected = '{},{},{}'.format(test_odb_data.cluster_id, test_odb_data.is_active, test_odb_data.name)

        self.assertEqual(result[0], 'cluster_id,is_active,name')
        self.assertEqual(result[1], data_row_expected)

# ################################################################################################################################

    def xtest_sio_response_from_sqlalchemy_orm_list_dict(self):

        result = self._prepare_sio_response_from_orm(DATA_FORMAT.DICT, True)
        result = result[0]

        self.assertIsInstance(result, self.ODBTestModelClass)

        result = result.asdict()

        # Note that the input format DICT acts, essentially, as pass-through.
        self.assertDictEqual(result, {

            # These were added by the database
            'id': 1,
            'opaque1': None,

            # These were specified explicitly
            'name': test_odb_data.name,
            'is_active': test_odb_data.is_active,
            'hosts': test_odb_data.es_hosts,
            'timeout': test_odb_data.es_timeout,
            'body_as': test_odb_data.es_body_as,
            'cluster_id': test_odb_data.cluster_id,
        })

# ################################################################################################################################

    def xtest_sio_response_from_zato_single_json(self):

        result = self._prepare_sio_response_from_zato(DATA_FORMAT.JSON, False)
        result = json_loads(result)

        self.assertEqual(result['cluster_id'], test_odb_data.cluster_id)
        self.assertEqual(result['name'], test_odb_data.name)
        self.assertTrue(result['is_active'])

# ################################################################################################################################

    def xtest_sio_response_from_zato_single_xml(self):

        result = self._prepare_sio_response_from_zato(DATA_FORMAT.XML, False)
        result = result.encode('utf8')
        root = objectify_from_string(result)

        self.assertEqual(root.cluster_id, test_odb_data.cluster_id)
        self.assertEqual(root.name, test_odb_data.name)
        self.assertTrue(root.is_active)

# ################################################################################################################################

    def xtest_sio_response_from_zato_single_csv(self):

        result = self._prepare_sio_response_from_zato(DATA_FORMAT.CSV, False)
        result = result.splitlines()

        data_row_expected = '{},{},{}'.format(test_odb_data.cluster_id, test_odb_data.is_active, test_odb_data.name)

        self.assertEqual(result[0], 'cluster_id,is_active,name')
        self.assertEqual(result[1], data_row_expected)

# ################################################################################################################################

    def xtest_sio_response_from_zato_single_dict(self):

        result = self._prepare_sio_response_from_orm(DATA_FORMAT.DICT, False)

        self.assertDictEqual(result, {
            'cluster_id': test_odb_data.cluster_id,
            'is_active': test_odb_data.is_active,
            'name': test_odb_data.name,
        })

# ################################################################################################################################

    def xtest_sio_response_from_zato_list_json(self):

        result = self._prepare_sio_response_from_zato(DATA_FORMAT.JSON, True)
        result = json_loads(result)
        result = result[0]

        self.assertEqual(result['cluster_id'], test_odb_data.cluster_id)
        self.assertEqual(result['name'], test_odb_data.name)
        self.assertIs(result['is_active'], test_odb_data.is_active)

# ################################################################################################################################

    def xtest_sio_response_from_zato_list_xml(self):

        result = self._prepare_sio_response_from_zato(DATA_FORMAT.XML, True)
        result = result.encode('utf8')
        root = objectify_from_string(result)

        self.assertEqual(root.item.cluster_id, test_odb_data.cluster_id)
        self.assertEqual(root.item.name, test_odb_data.name)
        self.assertTrue(root.item.is_active)

# ################################################################################################################################

    def xtest_sio_response_from_zato_list_csv(self):

        result = self._prepare_sio_response_from_zato(DATA_FORMAT.CSV, True)
        result = result.splitlines()

        data_row_expected = '{},{},{}'.format(test_odb_data.cluster_id, test_odb_data.is_active, test_odb_data.name)

        self.assertEqual(result[0], 'cluster_id,is_active,name')
        self.assertEqual(result[1], data_row_expected)

# ################################################################################################################################

    def test_sio_response_from_zato_list_dict(self):

        result = self._prepare_sio_response_from_zato(DATA_FORMAT.DICT, True)
        result = result[0]

        self.assertIsInstance(result, MyZatoClass)

        to_zato = result.to_zato()

        self.assertEqual(to_zato['cluster_id'], test_odb_data.cluster_id)
        self.assertEqual(to_zato['name'], test_odb_data.name)
        self.assertIs(to_zato['is_active'], test_odb_data.is_active)

# ################################################################################################################################
# ################################################################################################################################
