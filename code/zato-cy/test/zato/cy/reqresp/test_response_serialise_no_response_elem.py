# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from copy import deepcopy
from json import loads as json_loads

# lxml
from lxml.objectify import fromstring as objectify_from_string

# Zato
from zato.common import DATA_FORMAT
from zato.common.test import MyODBService, MyZatoClass, ODBTestCase, test_odb_data

# Zato - Cython
from test.zato.cy.simpleio_ import BaseTestCase
from zato.cy.reqresp.response import Response
from zato.simpleio import CySimpleIO

# ################################################################################################################################
# ################################################################################################################################

class ResponseSerialiseNoResponseElem(BaseTestCase, ODBTestCase):

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

        self.assertEqual(root.tag, 'response')
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

        self.assertEqual(root.tag, 'response')
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

    def xtest_sio_response_from_zato_list_dict(self):

        result = self._prepare_sio_response_from_zato(DATA_FORMAT.DICT, True)
        result = result[0]

        self.assertIsInstance(result, MyZatoClass)

        to_zato = result.to_zato()

        self.assertEqual(to_zato['cluster_id'], test_odb_data.cluster_id)
        self.assertEqual(to_zato['name'], test_odb_data.name)
        self.assertIs(to_zato['is_active'], test_odb_data.is_active)

# ################################################################################################################################
# ################################################################################################################################
