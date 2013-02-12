# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at gefira.pl>

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

# nose
from nose.tools import eq_

# Zato
from zato.common import CHANNEL, SCHEDULER_JOB_TYPE
from zato.common.test import ServiceTestCase
from zato.server.service import Service

# ##############################################################################

class HooksTestCase(ServiceTestCase):
    def test_hooks(self):
        
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
