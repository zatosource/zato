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

# Zato stuff needs to be imported first because of its doing the monkey-patching.
from zato.broker import BaseBroker
from zato.common.util import TRACE1

# stdlib
from logging import getLogger
from urllib2 import build_opener, Request

# anyjson
from anyjson import loads

# Zato
from zato.common.broker_message import MESSAGE, MESSAGE_TYPE

logger = getLogger(__name__)

CONFIG_MESSAGE_PREFIX = 'ZATO_CONFIG'

msg_socket = {
    MESSAGE_TYPE.TO_PARALLEL: 'parallel',
    MESSAGE_TYPE.TO_SINGLETON: 'singleton',
}

msg_types = msg_socket.keys()

config = loads(open('./config.json').read())
token_expected = config['token']
log_invalid_tokens = config['log_invalid_tokens']

class Broker(BaseBroker):
    def on_message(self, msg):
        
        if logger.isEnabledFor(TRACE1):
            logger.log(TRACE1, 'Got message [{0}]'.format(msg))
            
        msg_type = msg[:MESSAGE.MESSAGE_TYPE_LENGTH]

        # OK, it's something ours.
        if msg_type < MESSAGE_TYPE.USER_DEFINED_START:
        
            if msg_type not in msg_types:
                log_msg = ''.join([msg_type, '*'*32, msg[MESSAGE.PAYLOAD_START:]])
                err_msg = 'Unrecognized msg_type [{0}], msg [{1}]'.format(msg_type, log_msg)
                logger.error(err_msg)
                raise Exception(err_msg)
            
            token = msg[MESSAGE.MESSAGE_TYPE_LENGTH:MESSAGE.PAYLOAD_START]
            if token != token_expected:
                err_msg = 'Invalid token received, msg_type [{0}]'.format(msg_type)
                if log_invalid_tokens:
                    err_msg += ', token [{0}]'.format(token)
                logger.error(err_msg)
                raise Exception(err_msg)
            
            socket = self.sockets[msg_socket[msg_type]].pub
        else:
            # User-defined messages always go to parallel servers.
            socket = self.sockets[msg_socket[MESSAGE_TYPE.TO_PARALLEL]].pub
        
        socket.send(msg)
        