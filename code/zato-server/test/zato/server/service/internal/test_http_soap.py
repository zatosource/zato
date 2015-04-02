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
from zato.common.test import ForceTypeWrapper, rand_bool, rand_int, rand_string, ServiceTestCase
from zato.server.service import Bool
from zato.server.service.internal.http_soap import GetList, Create, Edit, Delete, Ping

################################################################################

class GetListTestCase(ServiceTestCase):

    def setUp(self):
        self.service_class = GetList
        self.sio = self.service_class.SimpleIO

    def get_request_data(self):
        return {'cluster_id': rand_int(), 'connection':rand_string(), 'transport':rand_string()}

    def get_response_data(self):
        return Bunch({'id':rand_int(), 'name':self.name, 'is_active':rand_bool(), 'is_internal':rand_bool(),
            'url_path':rand_string(), 'service_id':rand_int(), 'service_name':rand_string(), 'security_id':rand_int(),
            'security_name':rand_int(), 'sec_type':rand_string(), 'method':rand_string(), 'soap_action':rand_string(),
            'soap_version':rand_string(), 'data_format':rand_string(), 'host':rand_string(), 'ping_method':rand_string(),
            'pool_size':rand_int()}
        )

    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_http_soap_get_list_request')
        self.assertEquals(self.sio.response_elem, 'zato_http_soap_get_list_response')
        self.assertEquals(self.sio.input_required, ('cluster_id', 'connection', 'transport'))
        self.assertEquals(self.sio.output_required, ('id', 'name', 'is_active', 'is_internal', 'url_path'))
        self.assertEquals(self.sio.output_optional, ('service_id', 'service_name', 'security_id', 'security_name', 'sec_type',
            'method', 'soap_action', 'soap_version', 'data_format', 'host', 
            'ping_method', 'pool_size', 'merge_url_params_req', 'url_params_pri', 'params_pri', 'serialization_type', 'timeout',
            'sec_tls_ca_cert_id', Bool('has_rbac'), 'content_type'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')

    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.http-soap.get-list')

###############################################################################

class CreateTestCase(ServiceTestCase):

    def setUp(self):
        self.service_class = Create
        self.sio = self.service_class.SimpleIO

    def get_request_data(self):
        return ({'cluster_id':rand_int(), 'name':rand_string(), 'is_active':rand_bool(), 'connection':rand_string(),
                 'transport':rand_string(), 'is_internal':rand_bool(), 'url_path':rand_string(), 'service':rand_string(),
                 'security_id':rand_int(), 'method':rand_string(), 'soap_action':rand_string(), 'soap_version':rand_string(),
                 'data_format':rand_string(), 'host':rand_string()}
                )

    def get_response_data(self):
        return Bunch({'id':rand_int(), 'name':rand_string()})        

    def test_sio(self):

        self.assertEquals(self.sio.request_elem, 'zato_http_soap_create_request')
        self.assertEquals(self.sio.response_elem, 'zato_http_soap_create_response')
        self.assertEquals(self.sio.input_required, ('cluster_id', 'name', 'is_active', 'connection', 'transport', 'is_internal', 'url_path'))
        self.assertEquals(self.sio.input_optional, ('service', 'security_id', 'method', 'soap_action', 'soap_version', 'data_format', 'host', 
            'ping_method', 'pool_size', ForceTypeWrapper(Bool('merge_url_params_req')), 'url_params_pri', 'params_pri',
            'serialization_type', 'timeout', 'sec_tls_ca_cert_id', ForceTypeWrapper(Bool('has_rbac')), 'content_type'))
        self.assertEquals(self.sio.output_required, ('id', 'name'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')

    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.http-soap.create')

###############################################################################

class EditTestCase(ServiceTestCase):

    def setUp(self):
        self.service_class = Edit
        self.sio = self.service_class.SimpleIO

    def get_request_data(self):
        return ({'cluster_id':rand_int(), 'name':rand_string(), 'is_active':rand_bool(), 'connection':rand_string(),
                 'transport':rand_string(), 'url_path':rand_string(), 'service':rand_string(), 'security':rand_string(),
                 'security_id':rand_int(), 'method':rand_string(), 'soap_action':rand_string(), 'soap_version':rand_string(),
                 'data_format':rand_string(), 'host':rand_string(), 'content_type':rand_string()}
                )

    def get_response_data(self):
        return Bunch({'id':rand_int(), 'name':rand_string(), })          

    def test_sio(self):        
        self.assertEquals(self.sio.request_elem, 'zato_http_soap_edit_request')
        self.assertEquals(self.sio.response_elem, 'zato_http_soap_edit_response')
        self.assertEquals(self.sio.input_required, ('id', 'cluster_id', 'name', 'is_active', 'connection', 'transport', 'url_path'))
        self.assertEquals(self.sio.input_optional, ('service', 'security_id', 'method', 'soap_action', 'soap_version',
            'data_format', 'host', 'ping_method', 'pool_size', ForceTypeWrapper(Bool('merge_url_params_req')), 'url_params_pri',
            'params_pri', 'serialization_type', 'timeout', 'sec_tls_ca_cert_id', ForceTypeWrapper(Bool('has_rbac')),
            'content_type')) 
        self.assertEquals(self.sio.output_required, ('id', 'name'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')

    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.http-soap.edit')

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
        self.assertEquals(self.sio.request_elem, 'zato_http_soap_delete_request')
        self.assertEquals(self.sio.response_elem, 'zato_http_soap_delete_response')
        self.assertEquals(self.sio.input_required, ('id',))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_required')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')

    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.http-soap.delete')

##############################################################################

class PingTestCase(ServiceTestCase):

    def setUp(self):
        self.service_class = Ping
        self.sio = self.service_class.SimpleIO

    def get_request_data(self):
        return {'id': rand_int()}

    def get_response_data(self):
        return Bunch({'info':rand_string()})

    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_http_soap_ping_request')
        self.assertEquals(self.sio.response_elem, 'zato_http_soap_ping_response')
        self.assertEquals(self.sio.input_required, ('id',))
        self.assertEquals(self.sio.output_required, ('info',))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')

    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.http-soap.ping')
