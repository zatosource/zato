# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.broker_message import CHANNEL
from zato.common.odb.model import ChannelWebSocket
from zato.common.odb.query import channel_web_socket_list
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

elem = 'channel_web_socket'
model = ChannelWebSocket
label = 'a WebSocket channel'
broker_message = CHANNEL
broker_message_prefix = 'WEB_SOCKET_'
list_func = channel_web_socket_list

class GetList(AdminService):
    _filter_by = ChannelWebSocket.name,
    __metaclass__ = GetListMeta

class Create(AdminService):
    __metaclass__ = CreateEditMeta

class Edit(AdminService):
    __metaclass__ = CreateEditMeta

class Delete(AdminService):
    __metaclass__ = DeleteMeta

class GetToken(AdminService):
    pass

class InvalidateToken(AdminService):
    pass
