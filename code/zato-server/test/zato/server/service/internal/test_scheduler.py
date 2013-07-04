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
from zato.common.test import rand_bool, rand_datetime, rand_int, rand_string, ServiceTestCase
from zato.server.service.internal.scheduler import GetList, GetByName, Create, Edit, Delete, Execute

################################################################################

class GetListTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = GetList
        self.sio = self.service_class.SimpleIO
    
    def get_request_data(self):
        return {'cluster_id': rand_int()}
    
    def get_response_data(self):
        return Bunch({'id':rand_int(), 'name':self.name, 'is_active':rand_bool(), 'job_type':rand_string(),
                      'start_date':rand_datetime(), 'service_id':rand_int(), 'service_name':rand_string(),
                      'extra':rand_string(), 'weeks':rand_int(), 'days':rand_int(), 'minutes':rand_int(), 'seconds':rand_int(),
                      'repeats':rand_int(), 'cron_definition':rand_string(), '':True}
        )
    
    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_scheduler_job_get_list_request')
        self.assertEquals(self.sio.response_elem, 'zato_scheduler_job_get_list_response')
        self.assertEquals(self.sio.input_required, ('cluster_id',))
        self.assertEquals(self.sio.output_required, ('id', 'name', 'is_active', 'job_type', 'start_date', 'service_id', 'service_name'))
        self.assertEquals(self.sio.output_optional, ('extra', 'weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats', 'cron_definition'))
        self.assertEquals(self.sio.output_repeated, (True))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.scheduler.job.get-list')
        
###############################################################################   


class GetByNameTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = GetByName
        self.sio = self.service_class.SimpleIO
    
    def get_request_data(self):
        return {'cluster_id': rand_int(), 'name':rand_string()}
    
    def get_response_data(self):
        return Bunch({'id':rand_int(), 'name':self.name, 'is_active':rand_bool(), 'job_type':rand_string(),
                      'start_date':rand_datetime(), 'service_id':rand_int(), 'service_name':rand_string(),
                      'extra':rand_string(), 'weeks':rand_int(), 'days':rand_int(), 'minutes':rand_int(), 'seconds':rand_int(),
                      'repeats':rand_int(), 'cron_definition':rand_string(), '':True}
        )
    
    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_scheduler_job_get_by_name_request')
        self.assertEquals(self.sio.response_elem, 'zato_scheduler_job_get_by_name_response')
        self.assertEquals(self.sio.input_required, ('cluster_id', 'name'))
        self.assertEquals(self.sio.output_required, ('id', 'name', 'is_active', 'job_type', 'start_date', 'service_id', 'service_name'))
        self.assertEquals(self.sio.output_optional, ('extra', 'weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats', 'cron_definition'))
        self.assertEquals(self.sio.output_repeated, (False))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.scheduler.job.get-by-name')
        
###############################################################################

class CreateTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = Create
        self.sio = self.service_class.SimpleIO
    
    def get_request_data(self):
        return ({'cluster_id':rand_int(), 'name':rand_string(), 'is_active':rand_bool(), 'job_type':rand_string(),
                 'service':rand_string(), 'start_date':rand_datetime(), 'id':rand_int(), 'extra':rand_string(),
                 'weeks':rand_int(), 'days':rand_int(), 'hours':rand_int(), 'minutes':rand_int(),
                 'seconds':rand_int(), 'repeats':rand_int(), 'cron_definition':rand_string()}
                )
        
    def get_response_data(self):
        return Bunch({'id':rand_int(), 'name':rand_string(), 'cron_definition':rand_string()})        
    
    def test_sio(self):
        
        self.assertEquals(self.sio.request_elem, 'zato_scheduler_job_create_request')
        self.assertEquals(self.sio.response_elem, 'zato_scheduler_job_create_response')
        self.assertEquals(self.sio.input_required, ('cluster_id', 'name', 'is_active', 'job_type', 'service', 'start_date'))
        self.assertEquals(self.sio.input_optional, ('id', 'extra', 'weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats', 'cron_definition'))
        self.assertEquals(self.sio.output_required, ('id', 'name'))
        self.assertEquals(self.sio.output_optional, ('cron_definition',))
        self.assertEquals(self.sio.default_value, (''))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.scheduler.job.create')
        
###############################################################################

class EditTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = Edit
        self.sio = self.service_class.SimpleIO
    
    def get_request_data(self):
        return ({'cluster_id':rand_int(), 'name':rand_string(), 'is_active':rand_bool(), 'job_type':rand_string(),
                 'service':rand_string(), 'start_date':rand_datetime(), 'id':rand_int(), 'extra':rand_string(),
                 'weeks':rand_int(), 'days':rand_int(), 'hours':rand_int(), 'minutes':rand_int(),
                 'seconds':rand_int(), 'repeats':rand_int(), 'cron_definition':rand_string()}
                )
        
    def get_response_data(self):
        return Bunch({'id':rand_int(), 'name':rand_string(), 'cron_definition':rand_string()})
    
    def test_sio(self):
        
        self.assertEquals(self.sio.request_elem, 'zato_scheduler_job_edit_request')
        self.assertEquals(self.sio.response_elem, 'zato_scheduler_job_edit_response')
        self.assertEquals(self.sio.input_required, ('cluster_id', 'name', 'is_active', 'job_type', 'service', 'start_date'))
        self.assertEquals(self.sio.input_optional, ('id', 'extra', 'weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats', 'cron_definition'))
        self.assertEquals(self.sio.output_required, ('id', 'name'))
        self.assertEquals(self.sio.output_optional, ('cron_definition',))
        self.assertEquals(self.sio.default_value, (''))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.scheduler.job.edit')

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
        self.assertEquals(self.sio.request_elem, 'zato_scheduler_job_delete_request')
        self.assertEquals(self.sio.response_elem, 'zato_scheduler_job_delete_response')
        self.assertEquals(self.sio.input_required, ('id',))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_required')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.scheduler.job.delete')
        
##############################################################################

class ExecuteTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = Execute
        self.sio = self.service_class.SimpleIO
  
    def get_request_data(self):
        return {'id': rand_int()}
    
    def get_response_data(self):
        return Bunch()
    
    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_scheduler_job_execute_request')
        self.assertEquals(self.sio.response_elem, 'zato_scheduler_job_execute_response')
        self.assertEquals(self.sio.input_required, ('id',))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_required')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.scheduler.job.execute')
