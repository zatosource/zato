# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import ast
from logging import INFO
from uuid import uuid4

# nose
from nose.tools import eq_

# Zato
from zato.common import CHANNEL, SCHEDULER_JOB_TYPE
from zato.common.test import ServiceTestCase
from zato.server.service import Service

# ##############################################################################

class HooksTestCase(ServiceTestCase):
    def xtest_hooks(self):
        
        class MyJob(Service):
            def handle(self):
                pass
            
            def before_handle(self):
                self.environ['before_handle_called'] = True
            
            def before_job(self):
                self.environ['before_job_called'] = True
            
            def before_one_time_job(self):
                self.environ['before_one_time_job_called'] = True
            
            def after_handle(self):
                self.environ['after_handle_called'] = True
            
            def after_job(self):
                self.environ['after_job_called'] = True
            
            def after_one_time_job(self):
                self.environ['after_one_time_job_called'] = True
            
        instance = self.invoke(MyJob, {}, {}, channel=CHANNEL.SCHEDULER, job_type=SCHEDULER_JOB_TYPE.ONE_TIME)
        
        for name in('before_handle', 'before_job', 'before_one_time_job', 'after_handle', 'after_job', 'after_one_time_job'):
            eq_(instance.environ['{}_called'.format(name)], True)

class TestLogInputOutput(ServiceTestCase):
    def test_log_input_output(self):
        
        class MyLogger(object):
            def __init__(self):
                self.level = None
                self.msg = None
                
            def log(self, level, msg):
                self.level = level
                self.msg = msg
                
        class DummyService(Service):
            def handle(self):
                self.logger = MyLogger()
        
        instance = self.invoke(DummyService, {}, {})
        
        level = uuid4().hex
        user_msg = uuid4().hex
        
        instance._log_input_output(user_msg, level, {}, True)
        eq_(instance.logger.level, level)
        self.assertTrue(instance.logger.msg.startswith('{} '.format(user_msg)))
        
        instance.log_input()
        eq_(instance.logger.level, INFO)
        msg = ast.literal_eval(instance.logger.msg)
        eq_(sorted(msg), ['channel', 'cid', 'data_format', 'environ', 
                           'impl_name', 'invocation_time', 'job_type', 'name', 
                           'request.payload', 'slow_threshold', u'usage', 
                           'wsgi_environ'])

        instance.log_output()
        eq_(instance.logger.level, INFO)
        msg = ast.literal_eval(instance.logger.msg)
        eq_(sorted(msg), ['channel', 'cid', 'data_format', 'environ', 
                           'handle_return_time', 'impl_name', 'invocation_time', 
                           'job_type', 'name', 'processing_time', 'processing_time_raw', 
                           'response.payload', 'slow_threshold', 'usage', 
                           'wsgi_environ', 'zato.http.response.headers'])
