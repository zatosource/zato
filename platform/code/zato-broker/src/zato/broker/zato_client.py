# -*- coding: utf-8 -*-

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

# anyjson
from anyjson import dumps

# Zato
from zato.broker.client import BrokerClient as _BrokerClient
from zato.common.broker_message import MESSAGE_TYPE


class BrokerClient(_BrokerClient):
    """ A ZeroMQ broker client which knows how to subscribe to messages and push
    the messages onto the broker.
    """
    def __init__(self, **kwargs):
        super(BrokerClient, self).__init__(**kwargs)
        self.token = kwargs.get('token')
        
    def send(self, msg, msg_type=MESSAGE_TYPE.TO_PARALLEL_PULL):
        msg = '{0}{1}{2}'.format(msg_type, self.token, msg)
        return self._push.send(msg)
        
    def send_json(self, msg, msg_type=MESSAGE_TYPE.TO_PARALLEL_PULL):
        msg = dumps(msg)
        return self.send(msg, msg_type)
    
    def send_raw(self, msg):
        return self._push.send(msg)
        