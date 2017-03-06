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
from zato.server.service import AsIs, Integer
from zato.server.service.internal import GetListAdminSIO
from zato.server.service.internal.outgoing.amqp_ import Create, Edit, Delete, GetList

##############################################################################

class GetListTestCase(ServiceTestCase):

    def setUp(self):
        self.service_class = GetList
        self.sio = self.service_class.SimpleIO

    def get_request_data(self):
        return {'cluster_id': rand_int()}

    def get_response_data(self):
        return Bunch(
            {'id':rand_int(), 'name':rand_string(), 'is_active':rand_bool(), 'def_id':rand_int(),
             'delivery_mode':rand_int(), 'priority':rand_int(), 'def_name':rand_string(),
             'content_type':rand_string(), 'content_encoding':rand_string(),
             'cexpiration':rand_int(), 'user_id':rand_string(),
             'app_id':rand_string()}
        )

    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_outgoing_amqp_get_list_request')
        self.assertEquals(self.sio.response_elem, 'zato_outgoing_amqp_get_list_response')
        self.assertEquals(self.sio.input_required, ('cluster_id',))
        self.assertEquals(self.sio.input_optional, GetListAdminSIO.input_optional)
        self.assertEquals(self.sio.output_required,
            ('id', 'name', 'is_active', 'def_id', 'delivery_mode', 'priority', 'def_name', 'pool_size'))
        self.assertEquals(self.sio.output_optional, ('content_type', 'content_encoding', 'expiration',
            self.wrap_force_type(AsIs('user_id')), self.wrap_force_type(AsIs('app_id'))))
        self.assertEquals(self.sio.namespace, zato_namespace)

    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.outgoing.amqp.get-list')

##############################################################################

class CreateTestCase(ServiceTestCase):

    def setUp(self):
        self.service_class = Create
        self.sio = self.service_class.SimpleIO

    def get_request_data(self):
        return {'cluster_id':rand_int(), 'name':rand_string(), 'is_active':rand_bool(), 'def_id':rand_int(),
                'delivery_mode':rand_int(),'priority':rand_int(), 'content_type':rand_string(), 'content_encoding':rand_string(),
                'expiration':rand_int(), 'user_id':rand_string(), 'app_id':rand_string()}

    def get_response_data(self):
        return Bunch({'id':self.id, 'name':self.name})

    def test_sio(self):

        self.assertEquals(self.sio.request_elem, 'zato_outgoing_amqp_create_request')
        self.assertEquals(self.sio.response_elem, 'zato_outgoing_amqp_create_response')
        self.assertEquals(self.sio.input_required,
            ('cluster_id', 'name', 'is_active', 'def_id', 'delivery_mode', 'priority', 'pool_size'))
        self.assertEquals(self.sio.input_optional, ('content_type', 'content_encoding', 'expiration',
            self.wrap_force_type(AsIs('user_id')), self.wrap_force_type(AsIs('app_id'))))
        self.assertEquals(self.sio.output_required, ('id', 'name'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')

    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.outgoing.amqp.create')


##############################################################################

class EditTestCase(ServiceTestCase):

    def setUp(self):
        self.service_class = Edit
        self.sio = self.service_class.SimpleIO

    def get_request_data(self):
        return {'id':rand_int(), 'cluster_id':rand_int(), 'name':rand_string(), 'is_active':rand_bool(), 'def_id':rand_int(),
                'delivery_mode':rand_string(),'priority':rand_int(), 'content_type':rand_string(), 'content_encoding':rand_string(),
                'expiration':rand_int(), 'user_id':rand_string(), 'app_id':rand_string()}

    def get_response_data(self):
        return Bunch({'id':rand_int(), 'name':rand_string()})

    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_outgoing_amqp_edit_request')
        self.assertEquals(self.sio.response_elem, 'zato_outgoing_amqp_edit_response')
        self.assertEquals(self.sio.input_required, ('id', 'cluster_id', 'name', 'is_active', 'def_id', 'delivery_mode',
            self.wrap_force_type(Integer('priority')), 'pool_size'))
        self.assertEquals(self.sio.input_optional, ('content_type', 'content_encoding', 'expiration',
            self.wrap_force_type(AsIs('user_id')), self.wrap_force_type(AsIs('app_id'))))
        self.assertEquals(self.sio.output_required, ('id', 'name'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')

    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.outgoing.amqp.edit')

##############################################################################

class DeleteTestCase(ServiceTestCase):

    def setUp(self):
        self.service_class = Delete
        self.sio = self.service_class.SimpleIO

    def get_request_data(self):
        return {'id': rand_int()}

    def get_response_data(self):
        return Bunch()

    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_outgoing_amqp_delete_request')
        self.assertEquals(self.sio.response_elem, 'zato_outgoing_amqp_delete_response')
        self.assertEquals(self.sio.input_required, ('id',))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_required')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')

    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.outgoing.amqp.delete')
