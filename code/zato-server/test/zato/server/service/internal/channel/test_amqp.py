# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Bunch
from bunch import Bunch

# Zato
from zato.common import zato_namespace
from zato.common.test import rand_bool, rand_int, rand_string, ServiceTestCase
from zato.server.service.internal import GetListAdminSIO
from zato.server.service.internal.channel.amqp_ import Create, Edit, Delete, GetList

# ##############################################################################

class _Base(ServiceTestCase):
    def get_fake_channel_amqp(self):
        class FakeChannelAMQP(object):
            id = self.id
            def_id = self.def_id
            name = self.name

        return FakeChannelAMQP

    def get_fake_start_connector(self, request_data):
        def fake_start_connector(repo_location, id, def_id):
            self.assertTrue(isinstance(repo_location, basestring))
            self.assertEquals(id, self.id)
            self.assertEquals(def_id, request_data['def_id'])

        return fake_start_connector

# ################################################################################################################################

class GetListTestCase(ServiceTestCase):

    def setUp(self):
        self.service_class = GetList
        self.sio = self.service_class.SimpleIO

    def get_request_data(self):
        return {
            'cluster_id': rand_int(),
            'paginate': 'True',
            'query': '',
            'cur_page': '1',
        }

    def get_response_data(self):
        return Bunch(
            {'id':rand_int(), 'name':rand_string(), 'is_active':rand_bool(), 'queue':rand_string(),
             'consumer_tag_prefix':rand_string(), 'def_name':rand_string(), 'def_id':rand_int(),
             'service_name':rand_string(), 'data_format':rand_string()}
        )

    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_channel_amqp_get_list_request')
        self.assertEquals(self.sio.response_elem, 'zato_channel_amqp_get_list_response')
        self.assertEquals(self.sio.input_required, ('cluster_id',))
        self.assertEquals(self.sio.input_optional, GetListAdminSIO.input_optional)
        self.assertEquals(self.sio.output_required, ('id', 'name', 'is_active', 'queue', 'consumer_tag_prefix',
            'def_name', 'def_id', 'service_name', 'pool_size', 'ack_mode'))
        self.assertEquals(self.sio.output_optional, ('data_format',))
        self.assertEquals(self.sio.namespace, zato_namespace)

# ################################################################################################################################

class CreateTestCase(_Base):

    def setUp(self):
        self.service_class = Create
        self.sio = self.service_class.SimpleIO
        self.id = rand_int()
        self.def_id = rand_int()
        self.name = rand_string()

    def get_request_data(self):
        return {'cluster_id':rand_int(), 'name':self.name, 'is_active':rand_bool(), 'def_id':self.def_id,
                'queue':rand_string(), 'consumer_tag_prefix':rand_string(), 'service':rand_string(),
                'data_format':rand_string()}

    def get_response_data(self):
        return Bunch({'id':self.id, 'name':self.name})

    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_channel_amqp_create_request')
        self.assertEquals(self.sio.response_elem, 'zato_channel_amqp_create_response')
        self.assertEquals(self.sio.input_required,
            ('cluster_id', 'name', 'is_active', 'def_id', 'queue', 'consumer_tag_prefix', 'service', 'pool_size', 'ack_mode'))
        self.assertEquals(self.sio.input_optional, ('data_format',))
        self.assertEquals(self.sio.output_required, ('id', 'name'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')

# ################################################################################################################################

class EditTestCase(_Base):

    def setUp(self):
        self.service_class = Edit
        self.sio = self.service_class.SimpleIO
        self.id = rand_int()
        self.def_id = rand_int()
        self.name = rand_string()

    def get_request_data(self):
        return {'id': self.id, 'cluster_id':rand_int(), 'name':self.name, 'is_active':rand_bool(), 'queue':rand_string(),
             'consumer_tag_prefix':rand_string(), 'def_id':self.def_id, 'service':rand_string(), 'data_format':rand_string()}

    def get_response_data(self):
        return Bunch({'id':self.id, 'name':self.name})

    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_channel_amqp_edit_request')
        self.assertEquals(self.sio.response_elem, 'zato_channel_amqp_edit_response')
        self.assertEquals(self.sio.input_required,
            ('id', 'cluster_id', 'name', 'is_active', 'def_id', 'queue', 'consumer_tag_prefix', 'service', 'pool_size',
             'ack_mode'))
        self.assertEquals(self.sio.input_optional, ('data_format',))
        self.assertEquals(self.sio.output_required, ('id', 'name'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')

# ################################################################################################################################

class DeleteTestCase(_Base):

    def setUp(self):
        self.service_class = Delete
        self.sio = self.service_class.SimpleIO
        self.id = rand_int()
        self.name = rand_string()

    def get_request_data(self):
        return {'id': self.id}

    def get_response_data(self):
        return Bunch()

    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_channel_amqp_delete_request')
        self.assertEquals(self.sio.response_elem, 'zato_channel_amqp_delete_response')
        self.assertEquals(self.sio.input_required, ('id',))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'output_required')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')

# ################################################################################################################################
