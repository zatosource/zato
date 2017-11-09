# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Bunch
from bunch import Bunch

# Zato
from zato.common import zato_namespace
from zato.common.test import rand_int, rand_string, ServiceTestCase
from zato.server.service.internal import GetListAdminSIO
from zato.server.service.internal.kvdb.data_dict.dictionary import GetList, Create, Edit, GetSystemList, GetKeyList, GetValueList, GetLastID, Delete

################################################################################

class GetListTestCase(ServiceTestCase):

    def setUp(self):
        self.service_class = GetList
        self.sio = self.service_class.SimpleIO

    def get_request_data(self):
        return {}

    def get_response_data(self):
        return Bunch({'id': rand_int(), 'system':rand_string(), 'key':rand_string(), 'value':rand_string()})

    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_kvdb_data_dict_dictionary_get_list_request')
        self.assertEquals(self.sio.response_elem, 'zato_kvdb_data_dict_dictionary_get_list_response')
        self.assertEquals(self.sio.output_required, ('id', 'system', 'key'))
        self.assertEquals(self.sio.output_optional, ('value',))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertEquals(self.sio.input_optional, GetListAdminSIO.input_optional)
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')

    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.kvdb.data-dict.dictionary.get-list')

##############################################################################

class CreateTestCase(ServiceTestCase):

    def setUp(self):
        self.service_class = Create
        self.sio = self.service_class.SimpleIO

        def get_request_data(self):
            return {'system':rand_string(), 'key':rand_string(), 'value':rand_string(), 'id': rand_int()}

        def get_response_data(self):
            return Bunch({'id':rand_int()})

    def test_sio(self):

        self.assertEquals(self.sio.request_elem, 'zato_kvdb_data_dict_dictionary_create_request')
        self.assertEquals(self.sio.response_elem, 'zato_kvdb_data_dict_dictionary_create_response')
        self.assertEquals(self.sio.input_required, ('system', 'key'))
        self.assertEquals(self.sio.input_optional, ('id', 'value'))
        self.assertEquals(self.sio.output_required, ('id',))
        self.assertEquals(self.sio.namespace, zato_namespace)

    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.kvdb.data-dict.dictionary.create')

# ##############################################################################

class EditTestCase(ServiceTestCase):

    def setUp(self):
        self.service_class = Edit
        self.sio = self.service_class.SimpleIO

        def get_request_data(self):
            return {'system':rand_string(), 'key':rand_string(), 'value':rand_string(), 'id': rand_int()}

        def get_response_data(self):
            return Bunch({'id':rand_int()})

    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_kvdb_data_dict_dictionary_edit_request')
        self.assertEquals(self.sio.response_elem, 'zato_kvdb_data_dict_dictionary_edit_response')
        self.assertEquals(self.sio.input_required, ('system', 'key')
        self.assertEquals(self.sio.input_optional, ('id', 'value')))
        self.assertEquals(self.sio.output_required, ('id',))
        self.assertEquals(self.sio.namespace, zato_namespace)

    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.kvdb.data-dict.dictionary.edit')

##############################################################################

class DeleteTestCase(ServiceTestCase):

    def setUp(self):
        self.service_class = Delete
        self.sio = self.service_class.SimpleIO

    def get_request_data(self):
        return {'id': rand_int()}

    def get_response_data(self):
        return Bunch({'id':rand_int()})

    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_kvdb_data_dict_dictionary_delete_request')
        self.assertEquals(self.sio.response_elem, 'zato_kvdb_data_dict_dictionary_delete_response')
        self.assertEquals(self.sio.input_required, ('id',))
        self.assertEquals(self.sio.output_required, ('id',))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')

    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.kvdb.data-dict.dictionary.delete')

##############################################################################

class GetSystemListTestCase(ServiceTestCase):

    def setUp(self):
        self.service_class = GetSystemList
        self.sio = self.service_class.SimpleIO

    def get_request_data(self):
        return {}

    def get_response_data(self):
        return Bunch({'name': rand_string()})

    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_kvdb_data_dict_dictionary_get_system_list_request')
        self.assertEquals(self.sio.response_elem, 'zato_kvdb_data_dict_dictionary_get_system_list_response')
        self.assertEquals(self.sio.output_required, ('name',))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')

    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.kvdb.data-dict.dictionary.get-system-list')

##############################################################################

class GetKeyListTestCase(ServiceTestCase):

    def setUp(self):
        self.service_class = GetKeyList
        self.sio = self.service_class.SimpleIO

    def get_request_data(self):
        return {'system': rand_string()}

    def get_response_data(self):
        return Bunch({'name':rand_string()})

    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_kvdb_data_dict_dictionary_get_key_list_request')
        self.assertEquals(self.sio.response_elem, 'zato_kvdb_data_dict_dictionary_get_key_list_response')
        self.assertEquals(self.sio.input_required, ('system',))
        self.assertEquals(self.sio.output_required, ('name',))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')

    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.kvdb.data-dict.dictionary.get-key-list')

##############################################################################

class GetValueListTestCase(ServiceTestCase):

    def setUp(self):
        self.service_class = GetValueList
        self.sio = self.service_class.SimpleIO

    def get_request_data(self):
        return {'system': rand_string(), 'key':rand_string()}

    def get_response_data(self):
        return Bunch({'name':rand_string()})

    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_kvdb_data_dict_dictionary_get_value_list_request')
        self.assertEquals(self.sio.response_elem, 'zato_kvdb_data_dict_dictionary_get_value_list_response')
        self.assertEquals(self.sio.input_required, ('system', 'key'))
        self.assertEquals(self.sio.output_required, ('name',))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')

    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.kvdb.data-dict.dictionary.get-value-list')

class GetLastIDTestCase(ServiceTestCase):

    def setUp(self):
        self.service_class = GetLastID
        self.sio = self.service_class.SimpleIO

    def get_request_data(self):
        return {}, ''

    def get_response_data(self):
        return Bunch({'value':rand_int()})

    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_kvdb_data_dict_dictionary_get_last_id_request')
        self.assertEquals(self.sio.response_elem, 'zato_kvdb_data_dict_dictionary_get_last_id_response')
        self.assertEquals(self.sio.output_optional, ('value',))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_required')
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_required')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')

    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.kvdb.data-dict.dictionary.get-last-id')
