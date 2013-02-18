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

# Zato
from zato.server.service.internal import AdminService

class Echo(AdminService):
    """ Copies request over to response.
    """
    def handle(self):
        self.response.payload = self.request.raw_request

class InputLogger(AdminService):
    """ Writes out all input data to server logs.
    """
    def handle(self):
        pass
    
    def finalize_handle(self):
        msg = {}
        msg['request.payload'] = self.request.payload
        
        attrs = ('channel', 'cid', 'data_format', 'environ', 'handle_return_time',
            'impl_name', 'invocation_time', 'job_type', 'name', 'processing_time', 
            'processing_time_raw', 'slow_threshold', 'usage', 'wsgi_environ')
        for attr in attrs:
            msg[attr] = getattr(self, attr, '(None)')

        self.logger.info(msg)
