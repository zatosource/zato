# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy

# Zato
from zato.common.api import DATA_FORMAT
from zato.common.json_internal import loads as json_loads
from zato.common.test import BaseSIOTestCase, MyODBServiceWithResponseElem, MyZatoClass, ODBTestCase, test_odb_data

# Zato - Cython
from zato.cy.reqresp.response import Response
from zato.simpleio import CySimpleIO

# ################################################################################################################################

response_elem = MyODBServiceWithResponseElem.SimpleIO.response_elem

# ################################################################################################################################
# ################################################################################################################################

class ResponseSerialiseNoResponseElem(BaseSIOTestCase, ODBTestCase):

    def setUp(self):
        super(BaseSIOTestCase, self).setUp()
        super(ODBTestCase, self).setUp()

    def tearDown(self):
        super(BaseSIOTestCase, self).tearDown()
        super(ODBTestCase, self).tearDown()

# ################################################################################################################################

    def _prepare_sio_response(self, data, data_format, is_list):
        # type: (object, str, bool) -> str

        MyService = deepcopy(MyODBServiceWithResponseElem)
        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

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

    def test_sio_response_from_sqlalchemy_orm_single_json(self):

        result = self._prepare_sio_response_from_orm(DATA_FORMAT.JSON, False)
        result = json_loads(result)
        result = result[response_elem]

        self.assertEqual(result['cluster_id'], test_odb_data.cluster_id)
        self.assertEqual(result['name'], test_odb_data.name)
        self.assertIs(result['is_active'], test_odb_data.is_active)

# ################################################################################################################################

    def test_sio_response_from_sqlalchemy_orm_single_csv(self):

        result = self._prepare_sio_response_from_orm(DATA_FORMAT.CSV, False)
        result = result.splitlines()

        data_row_expected = '{},{},{}'.format(test_odb_data.cluster_id, test_odb_data.is_active, test_odb_data.name)

        self.assertEqual(result[0], 'cluster_id,is_active,name')
        self.assertEqual(result[1], data_row_expected)

# ################################################################################################################################

    def test_sio_response_from_sqlalchemy_orm_single_dict(self):

        result = self._prepare_sio_response_from_orm(DATA_FORMAT.DICT, False)
        result = result[response_elem]

        self.assertDictEqual(result, {
            'cluster_id': test_odb_data.cluster_id,
            'is_active': test_odb_data.is_active,
            'name': test_odb_data.name,
        })

# ################################################################################################################################

    def test_sio_response_from_sqlalchemy_orm_list_json(self):

        result = self._prepare_sio_response_from_orm(DATA_FORMAT.JSON, True)
        result = json_loads(result)
        result = result[response_elem]
        result = result[0]

        self.assertEqual(result['cluster_id'], test_odb_data.cluster_id)
        self.assertEqual(result['name'], test_odb_data.name)
        self.assertIs(result['is_active'], test_odb_data.is_active)

# ################################################################################################################################

    def test_sio_response_from_sqlalchemy_orm_list_csv(self):

        result = self._prepare_sio_response_from_orm(DATA_FORMAT.CSV, True)
        result = result.splitlines()

        data_row_expected = '{},{},{}'.format(test_odb_data.cluster_id, test_odb_data.is_active, test_odb_data.name)

        self.assertEqual(result[0], 'cluster_id,is_active,name')
        self.assertEqual(result[1], data_row_expected)

# ################################################################################################################################

    def test_sio_response_from_sqlalchemy_orm_list_dict(self):

        result = self._prepare_sio_response_from_orm(DATA_FORMAT.DICT, True)
        result = result[response_elem]
        result = result[0]

        self.assertDictEqual(result, {
            'cluster_id': test_odb_data.cluster_id,
            'name': test_odb_data.name,
            'is_active': test_odb_data.is_active,
        })

# ################################################################################################################################

    def test_sio_response_from_zato_single_json(self):

        result = self._prepare_sio_response_from_zato(DATA_FORMAT.JSON, False)
        result = json_loads(result)
        result = result[response_elem]

        self.assertEqual(result['cluster_id'], test_odb_data.cluster_id)
        self.assertEqual(result['name'], test_odb_data.name)
        self.assertTrue(result['is_active'])

# ################################################################################################################################

    def test_sio_response_from_zato_single_csv(self):

        result = self._prepare_sio_response_from_zato(DATA_FORMAT.CSV, False)
        result = result.splitlines()

        data_row_expected = '{},{},{}'.format(test_odb_data.cluster_id, test_odb_data.is_active, test_odb_data.name)

        self.assertEqual(result[0], 'cluster_id,is_active,name')
        self.assertEqual(result[1], data_row_expected)

# ################################################################################################################################

    def test_sio_response_from_zato_single_dict(self):

        result = self._prepare_sio_response_from_orm(DATA_FORMAT.DICT, False)
        result = result[response_elem]

        self.assertDictEqual(result, {
            'cluster_id': test_odb_data.cluster_id,
            'is_active': test_odb_data.is_active,
            'name': test_odb_data.name,
        })

# ################################################################################################################################

    def test_sio_response_from_zato_list_json(self):

        result = self._prepare_sio_response_from_zato(DATA_FORMAT.JSON, True)
        result = json_loads(result)
        result = result[response_elem]
        result = result[0]

        self.assertEqual(result['cluster_id'], test_odb_data.cluster_id)
        self.assertEqual(result['name'], test_odb_data.name)
        self.assertIs(result['is_active'], test_odb_data.is_active)

# ################################################################################################################################

    def test_sio_response_from_zato_list_csv(self):

        result = self._prepare_sio_response_from_zato(DATA_FORMAT.CSV, True)
        result = result.splitlines()

        data_row_expected = '{},{},{}'.format(test_odb_data.cluster_id, test_odb_data.is_active, test_odb_data.name)

        self.assertEqual(result[0], 'cluster_id,is_active,name')
        self.assertEqual(result[1], data_row_expected)

# ################################################################################################################################

    def test_sio_response_from_zato_list_dict(self):

        result = self._prepare_sio_response_from_zato(DATA_FORMAT.DICT, True)
        result = result[response_elem]
        result = result[0]

        self.assertEqual(result['cluster_id'], test_odb_data.cluster_id)
        self.assertEqual(result['name'], test_odb_data.name)
        self.assertIs(result['is_active'], test_odb_data.is_active)

# ################################################################################################################################
# ################################################################################################################################
