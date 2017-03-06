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
from zato.common.test import rand_bool, rand_int, rand_string, ServiceTestCase
from zato.server.service.internal import GetListAdminSIO
from zato.server.service.internal.definition.amqp_ import GetList, GetByID, Create, Edit, Delete, ChangePassword

# ################################################################################################################################

class GetListTestCase(ServiceTestCase):

    def setUp(self):
        self.service_class = GetList
        self.sio = self.service_class.SimpleIO

    def get_request_data(self):
        return {'cluster_id': rand_int()}

    def get_response_data(self):
        return Bunch(
            {'id':rand_int(), 'name':rand_string(), 'host':rand_string(), 'port':rand_int(),
             'vhost':rand_string(), 'username':rand_string(), 'frame_max':rand_int(),
             'heartbeat':rand_int(), 'output_repeated':rand_bool()}
        )

    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_definition_amqp_get_list_request')
        self.assertEquals(self.sio.response_elem, 'zato_definition_amqp_get_list_response')
        self.assertEquals(self.sio.input_required, ('cluster_id',))
        self.assertEquals(self.sio.input_optional, GetListAdminSIO.input_optional)
        self.assertEquals(self.sio.output_required, ('frame_max', 'heartbeat', 'host', 'id', 'name', 'port', 'username', 'vhost'))
        self.assertEquals(self.sio.namespace, zato_namespace)

    def xtest_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.definition.amqp.get-list')

# ################################################################################################################################

class GetByIDTestCase(ServiceTestCase):

    def setUp(self):
        self.service_class = GetByID
        self.sio = self.service_class.SimpleIO

    def get_request_data(self):
        return {'id':self.id, 'cluster_id':self.cluster_id}

    def get_response_data(self):
        return Bunch({'id':rand_int(), 'name':self.name, 'host':rand_string(), 'port':rand_int(),
             'vhost':rand_string(),'username':rand_string(),
             'frame_max':rand_int(),'heartbeat':rand_int()})

    def xtest_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_definition_amqp_get_by_id_request')
        self.assertEquals(self.sio.response_elem, 'zato_definition_amqp_get_by_id_response')
        self.assertEquals(self.sio.input_required, ('id', 'cluster_id'))
        self.assertEquals(self.sio.output_required, ('id', 'name', 'host', 'port', 'vhost', 'username', 'frame_max', 'heartbeat'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')

        def xtest_impl(self):
            self.assertEquals(self.service_class.get_name(), 'zato.definition.amqp.get_by_id')

# ################################################################################################################################
class CreateTestCase(ServiceTestCase):

    def setUp(self):
        self.service_class = Create
        self.sio = self.service_class.SimpleIO

    def get_request_data(self):
        return {'cluster_id':rand_int(), 'name':self.name, 'host':rand_string(),
                'port':rand_int(), 'vhost':rand_string(), 'username':rand_string(),
                'frame_max':rand_int(), 'heartbeat':rand_int()}

    def get_response_data(self):
        return Bunch({'id':self.id, 'name':self.name})

    def xtest_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_definition_amqp_create_request')
        self.assertEquals(self.sio.response_elem, 'zato_definition_amqp_create_response')
        self.assertEquals(
            self.sio.input_required, ('cluster_id', 'name', 'host', 'port', 'vhost', 'username', 'frame_max', 'heartbeat'))
        self.assertEquals(self.sio.output_required, ('id', 'name'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')

    def xtest_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.definition.amqp.create')

# ################################################################################################################################

class EditTestCase(ServiceTestCase):

    def setUp(self):
        self.service_class = Edit
        self.sio = self.service_class.SimpleIO

    def get_request_data(self):
        return {'id': rand_int(), 'cluster_id':rand_int(), 'name':self.name, 'host':rand_string(),
            'port':rand_int(), 'vhost':rand_string(), 'username':rand_string(), 'frame_max':rand_int(), 'heartbeat':rand_int()}

    def get_response_data(self):
        return Bunch({'id':self.id, 'name':self.name})

    def xtest_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_definition_amqp_edit_request')
        self.assertEquals(self.sio.response_elem, 'zato_definition_amqp_edit_response')
        self.assertEquals(
            self.sio.input_required, ('id', 'cluster_id', 'name', 'host', 'port', 'vhost', 'username', 'frame_max', 'heartbeat'))
        self.assertEquals(self.sio.output_required, ('id', 'name'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')

    def xtest_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.definition.amqp.edit')

# ################################################################################################################################

class DeleteTestCase(ServiceTestCase):

    def setUp(self):
        self.service_class = Delete
        self.sio = self.service_class.SimpleIO

    def get_request_data(self):
        return {'id': rand_int()}

    def get_response_data(self):
        return Bunch()

    def xtest_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_definition_amqp_delete_request')
        self.assertEquals(self.sio.response_elem, 'zato_definition_amqp_delete_response')
        self.assertEquals(self.sio.input_required, ('id',))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_required')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')

    def xtest_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.definition.amqp.delete')

# ################################################################################################################################

class ChangePasswordCase(ServiceTestCase):

    def setUp(self):
        self.service_class = ChangePassword
        self.sio = self.service_class.SimpleIO

    def get_request_data(self):
        return({'id':rand_int(), 'password1':rand_string(), 'password2':rand_string()})

    def get_response_data(self):
        return Bunch()

    def xtest_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_definition_amqp_change_password_request')
        self.assertEquals(self.sio.response_elem, 'zato_definition_amqp_change_password_response')
        self.assertEquals(self.sio.input_required, ('id', 'password1', 'password2'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_required')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')

    def xtest_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.definition.amqp.change-password')

# ################################################################################################################################
