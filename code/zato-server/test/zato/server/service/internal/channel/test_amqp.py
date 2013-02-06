# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# anyjson
from anyjson import loads

# Bunch
from bunch import Bunch

# mock
from mock import Mock, patch

# nose
from nose.tools import eq_

# Zato
from zato.common import zato_namespace
from zato.common.broker_message import CHANNEL, MESSAGE_TYPE
from zato.common.odb.model import ChannelAMQP, Service
from zato.common.test import Expected, rand_bool, rand_int, rand_string, ServiceTestCase
from zato.server.service.internal.channel.amqp import Create, Edit, Delete, GetList

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

# ##############################################################################

class GetListTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = GetList
    
    def get_request_data(self):
        return {'cluster_id': rand_int()}
    
    def get_response_data(self):
        return Bunch(
            {'id':rand_int(), 'name':rand_string(), 'is_active':rand_bool(), 'queue':rand_string(), 
             'consumer_tag_prefix':rand_string(), 'def_name':rand_string(), 'def_id':rand_int(), 
             'service_name':rand_string(), 'data_format':rand_string()}
        )
    
    def test_service(self):
        sio = self.service_class.SimpleIO
        
        self.assertEquals(sio.request_elem, 'zato_channel_amqp_get_list_request')
        self.assertEquals(sio.response_elem, 'zato_channel_amqp_get_list_response')
        self.assertEquals(sio.input_required, ('cluster_id',))
        self.assertEquals(sio.output_required, ('id', 'name', 'is_active', 'queue', 'consumer_tag_prefix', 
            'def_name', 'def_id', 'service_name', 'data_format'))
        self.assertEquals(sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, sio, 'output_optional')
        
        self.check_sio_list_response(self.service_class, ChannelAMQP, 
            self.get_request_data(), self.get_response_data(), 
            sio.request_elem, sio.response_elem)
        
# ##############################################################################

class CreateTestCase(_Base):
    
    def setUp(self):
        self.service_class = Create
        self.id = rand_int()
        self.def_id = rand_int()
        self.name = rand_string()
        self.mock_data = {
            'odb': [{'session.query.filter.filter.filter.first': False},
                    {'session.query.filter.filter.first': Service()},
                    ],
            }
    
    def get_request_data(self):
        return {'cluster_id':rand_int(), 'name':self.name, 'is_active':rand_bool(), 'queue':rand_string(), 
             'consumer_tag_prefix':rand_string(), 'def_id':self.def_id, 'data_format':rand_string()}
    
    def get_response_data(self):
        return Bunch({'id':self.id, 'name':self.name})
    
    def test_service(self):
        sio = self.service_class.SimpleIO
        
        self.assertEquals(sio.request_elem, 'zato_channel_amqp_create_request')
        self.assertEquals(sio.response_elem, 'zato_channel_amqp_create_response')
        self.assertEquals(sio.input_required, ('cluster_id', 'name', 'is_active', 'def_id', 'queue', 'consumer_tag_prefix', 'service'))
        self.assertEquals(sio.input_optional, ('data_format',))
        self.assertEquals(sio.output_required, ('id', 'name'))
        self.assertEquals(sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, sio, 'output_repeated')
        
        request_data = self.get_request_data()

        with patch('zato.server.service.internal.channel.amqp.start_connector', self.get_fake_start_connector(request_data)):
            with patch('zato.server.service.internal.channel.amqp.ChannelAMQP', self.get_fake_channel_amqp()):
                self.check_sio(self.service_class, request_data, self.get_response_data(), 
                    sio.response_elem, self.mock_data)
                
# ##############################################################################
            
class EditTestCase(_Base):
    
    def setUp(self):
        self.service_class = Edit
        self.id = rand_int()
        self.def_id = rand_int()
        self.name = rand_string()
        self.mock_data = {
            'odb': [{'session.query.filter.filter.filter.filter.first': False},
                    {'session.query.filter.filter.first': Service()},
                    {'session.query.filter_by.one': ChannelAMQP(self.id)},
                    ]
            }
        
    def broker_client_publish(self, msg, msg_type):
        self.assertEquals(msg['action'], CHANNEL.AMQP_DELETE)
        self.assertEquals(msg['name'], self.name)
        self.assertEquals(msg_type, MESSAGE_TYPE.TO_AMQP_CONNECTOR_ALL)
    
    def get_request_data(self):
        return {'id': self.id, 'cluster_id':rand_int(), 'name':self.name, 'is_active':rand_bool(), 'queue':rand_string(), 
             'consumer_tag_prefix':rand_string(), 'def_id':self.def_id, 'data_format':rand_string()}
    
    def get_response_data(self):
        return Bunch({'id':rand_int(), 'name':self.name})
    
    def test_service(self):
        sio = self.service_class.SimpleIO
        
        self.assertEquals(sio.request_elem, 'zato_channel_amqp_edit_request')
        self.assertEquals(sio.response_elem, 'zato_channel_amqp_edit_response')
        self.assertEquals(sio.input_required, ('id', 'cluster_id', 'name', 'is_active', 'def_id', 'queue', 'consumer_tag_prefix', 'service'))
        self.assertEquals(sio.input_optional, ('data_format',))
        self.assertEquals(sio.output_required, ('id', 'name'))
        self.assertEquals(sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, sio, 'output_repeated')
        
        request_data = self.get_request_data()
        
        with patch('zato.server.service.internal.channel.amqp.start_connector', self.get_fake_start_connector(request_data)):
            with patch('zato.server.service.internal.channel.amqp.ChannelAMQP', self.get_fake_channel_amqp()):
                self.check_sio(self.service_class, request_data, self.get_response_data(), 
                    sio.response_elem, self.mock_data)

# ##############################################################################

class DeleteTestCase(_Base):
    
    def setUp(self):
        self.service_class = Delete
        self.id = rand_int()
        self.name = rand_string()
        self.mock_data = {
            'odb': [{'session.query.filter.one': ChannelAMQP(self.id, self.name)}
                    ]
            }
        
    def broker_client_publish(self, msg, msg_type):
        self.assertEquals(msg['action'], CHANNEL.AMQP_DELETE)
        self.assertEquals(msg['id'], self.id)
        self.assertEquals(msg['name'], self.name)
        self.assertEquals(msg_type, MESSAGE_TYPE.TO_AMQP_CONNECTOR_ALL)
    
    def get_request_data(self):
        return {'id': self.id}
    
    def get_response_data(self):
        return Bunch()
    
    def test_service(self):
        sio = self.service_class.SimpleIO
        
        self.assertEquals(sio.request_elem, 'zato_channel_amqp_delete_request')
        self.assertEquals(sio.response_elem, 'zato_channel_amqp_delete_response')
        self.assertEquals(sio.input_required, ('id',))
        self.assertEquals(sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, sio, 'output_required')
        self.assertRaises(AttributeError, getattr, sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, sio, 'output_repeated')

        self.check_sio(self.service_class, self.get_request_data(), self.get_response_data(), 
                            sio.response_elem, self.mock_data)
