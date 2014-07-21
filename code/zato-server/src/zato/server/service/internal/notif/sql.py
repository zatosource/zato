# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.broker_message import NOTIF
from zato.common import NOTIF as COMMON_NOTIF
from zato.common.odb.model import NotificationSQL
from zato.common.odb.query import notif_sql_list
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

elem = 'notif_sql'
model = NotificationSQL
label = 'an SQL notification'
broker_message = NOTIF
broker_message_prefix = 'SQL_'
list_func = notif_sql_list
skip_input_params = ('notif_type', 'service_id',)
default_value = None

def instance_hook(service, input, instance, attrs):
    instance.notif_type = COMMON_NOTIF.TYPE.SQL
    instance.service_id = 1

class GetList(AdminService):
    __metaclass__ = GetListMeta

class Create(AdminService):
    __metaclass__ = CreateEditMeta

class Edit(AdminService):
    __metaclass__ = CreateEditMeta

class Delete(AdminService):
    __metaclass__ = DeleteMeta
