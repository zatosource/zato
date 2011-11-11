#!/usr/bin/env python

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at gefira.pl>

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

# stdlib
import sys

# anyjson
from anyjson import loads

# Zato
from zato.broker import SocketData
from zato.broker.zato_broker import Broker

if __name__ == '__main__':
    config = loads(open(sys.argv[1]).read())
    
    token = config['token']
    log_invalid_tokens = config['log_invalid_tokens']
    host = config['host']
    start_port = config['start_port']
    
    pull1 = 'tcp://{0}:{1}'.format(host, start_port)
    push1 = 'tcp://{0}:{1}'.format(host, start_port+1)
    pub1 = 'tcp://{0}:{1}'.format(host, start_port+2)
    
    pull3 = 'tcp://{0}:{1}'.format(host, start_port+50)
    push3 = 'tcp://{0}:{1}'.format(host, start_port+51)
    
    s1 = SocketData('parallel/pull', pull1, push1)
    s2 = SocketData('parallel/sub', None, None, pub1)
    s3 = SocketData('singleton', pull3, push3)
    
    Broker(token, log_invalid_tokens, s1, s2, s3).serve_forever()
