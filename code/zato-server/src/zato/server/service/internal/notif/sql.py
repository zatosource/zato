# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# 

# Zato
from zato.common.broker_message import NOTIF
from zato.common import NOTIF as COMMON_NOTIF
from zato.common.odb.model import NotificationSQL
from zato.common.odb.query import notif_sql_list
from zato.server.service.internal import AdminService
from zato.server.service.internal.notif import NotifierService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

elem = 'notif_sql'
model = NotificationSQL
label = 'an SQL notification'
broker_message = NOTIF
broker_message_prefix = 'SQL_'
list_func = notif_sql_list
input_required_extra = ['service_name']
skip_input_params = ('notif_type', 'service_id',)
skip_output_params = ('get_data', 'get_data_patt_neg', 'get_data_patt', 'name_pattern_neg', 'name_pattern')
default_value = None

def instance_hook(service, input, instance, attrs):
    instance.notif_type = COMMON_NOTIF.TYPE.SQL

    with closing(service.odb.session()) as session:
        service.logger.warn(input)

class GetList(AdminService):
    __metaclass__ = GetListMeta

class Create(AdminService):
    __metaclass__ = CreateEditMeta

class Edit(AdminService):
    __metaclass__ = CreateEditMeta

class Delete(AdminService):
    __metaclass__ = DeleteMeta

class RunNotifier(NotifierService):
    notif_type = COMMON_NOTIF.TYPE.SQL

    def run_notifier_impl(self, config):
        with closing(self.outgoing.sql[config.def_name].session()) as session:
            self.invoke_async(config.service_name, {'data':session.execute(config.query)})
