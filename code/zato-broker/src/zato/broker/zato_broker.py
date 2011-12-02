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
import sys
from logging import getLogger

# Zato
from zato.common.broker_message import MESSAGE, MESSAGE_TYPE

logger = getLogger(__name__)

CONFIG_MESSAGE_PREFIX = 'ZATO_CONFIG'

msg_socket = {
    MESSAGE_TYPE.TO_PARALLEL_PULL: 'worker-thread/pull-push',
    MESSAGE_TYPE.TO_PARALLEL_SUB: 'worker-thread/sub',
    MESSAGE_TYPE.TO_SINGLETON: 'singleton',
    MESSAGE_TYPE.TO_AMQP_PUBLISHING_CONNECTOR_PULL: 'amqp-publishing-connector/pull-push',
    MESSAGE_TYPE.TO_AMQP_CONSUMING_CONNECTOR_PULL: 'amqp-consuming-connector/pull-push',
    MESSAGE_TYPE.TO_AMQP_CONNECTOR_SUB: 'amqp-publishing-connector/sub',
}

msg_types = msg_socket.keys()


class Broker(BaseBroker):
    def __init__(self, token, log_invalid_tokens, *socket_data):
        super(Broker, self).__init__(*socket_data)
        self.token = token
        self.log_invalid_tokens = log_invalid_tokens
        
    def on_message(self, msg):
        
        if logger.isEnabledFor(TRACE1):
            logger.log(TRACE1, 'Got message [{0}]'.format(msg))
            
        msg_type = msg[:MESSAGE.MESSAGE_TYPE_LENGTH]

        # OK, it's something ours.
        if msg_type < MESSAGE_TYPE.USER_DEFINED_START:
            
            msg_shadowed = ''.join([msg_type, MESSAGE.NULL_TOKEN, msg[MESSAGE.PAYLOAD_START:]]) 
        
            if msg_type not in msg_types:
                err_msg = 'Unrecognized msg_type [{0}], msg [{1}]'.format(
                    msg_type, msg_shadowed)
                logger.error(err_msg)
                raise Exception(err_msg)
            
            token = msg[MESSAGE.TOKEN_START:MESSAGE.TOKEN_END]
            if token != self.token:
                err_msg = 'Invalid token received, msg_type [{0}]'.format(msg_type)
                if log_invalid_tokens:
                    err_msg += ', token [{0}]'.format(token)
                logger.error(err_msg)
                raise Exception(err_msg)

            _msg_socket = msg_socket[msg_type]
            if logger.isEnabledFor(TRACE1):
                logger.log(TRACE1, '_msg_socket [{0}]'.format(_msg_socket))

            if msg_type in(MESSAGE_TYPE.TO_SINGLETON, MESSAGE_TYPE.TO_PARALLEL_PULL, \
                           MESSAGE_TYPE.TO_AMQP_CONNECTOR_PULL):
                socket = self.sockets[_msg_socket].push
            else:
                socket = self.sockets[_msg_socket].pub
            
            # We don't want the subscribers to know what the original token was.
            msg = bytes(msg_shadowed)
        else:
            # User-defined messages always go to parallel servers.
            _msg_socket = msg_socket[MESSAGE_TYPE.TO_PARALLEL_PULL]
            socket = self.sockets[_msg_socket].push
        
        socket.send(msg)
