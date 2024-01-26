# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# pylint: disable=attribute-defined-outside-init

# stdlib
from contextlib import closing
from datetime import datetime
from logging import DEBUG, getLogger

# SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound

# Python 2/3 compatibility
from six import add_metaclass

# Zato
from zato.common.api import NOTIF as COMMON_NOTIF, SECRET_SHADOW
from zato.common.broker_message import NOTIF
from zato.common.odb.model import Cluster, NotificationSQL, SQLConnectionPool, Service
from zato.common.odb.query import notif_sql_list
from zato.server.service.internal import AdminService
from zato.server.service.internal.notif import NotifierService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################

logger_notif = getLogger('zato_notif_sql')
has_debug = logger_notif.isEnabledFor(DEBUG)

# ################################################################################################################################

elem = 'notif_sql'
model = NotificationSQL
label = 'an SQL notification'
get_list_docs = 'SQL notifications'
broker_message = NOTIF
broker_message_prefix = 'SQL_'
list_func = notif_sql_list
output_required_extra = ['service_name']
create_edit_input_required_extra = ['service_name']
create_edit_rewrite = ['service_name']
skip_input_params = ('notif_type', 'service_id', 'get_data_patt', 'get_data', 'get_data_patt_neg',
    'name_pattern_neg', 'name_pattern')
skip_output_params = ('get_data', 'get_data_patt_neg', 'get_data_patt', 'name_pattern_neg', 'name_pattern', 'service_name')

# ################################################################################################################################

def instance_hook(service, input, instance, attrs):
    instance.notif_type = COMMON_NOTIF.TYPE.SQL

    if attrs.is_create_edit:
        with closing(service.odb.session()) as session:
            instance.service_id = session.query(Service).\
                filter(Service.name==input.service_name).\
                filter(Service.cluster_id==Cluster.id).\
                filter(Service.cluster_id==input.cluster_id).\
                one().id

# ################################################################################################################################

def broker_message_hook(service, input, instance, attrs, service_type):
    if service_type == 'create_edit':
        input.notif_type = COMMON_NOTIF.TYPE.SQL

# ################################################################################################################################

@add_metaclass(GetListMeta)
class GetList(AdminService):
    _filter_by = NotificationSQL.name,

# ################################################################################################################################

@add_metaclass(CreateEditMeta)
class Create(AdminService):
    pass

# ################################################################################################################################

@add_metaclass(CreateEditMeta)
class Edit(AdminService):
    pass

# ################################################################################################################################

@add_metaclass(DeleteMeta)
class Delete(AdminService):
    pass

# ################################################################################################################################

class RunNotifier(NotifierService):
    notif_type = COMMON_NOTIF.TYPE.SQL

    def run_notifier_impl(self, config):

        # To make it possible to save it to logs directly
        config['password'] = SECRET_SHADOW
        out = []

        try:
            with closing(self.odb.session()) as session:
                def_name = session.query(SQLConnectionPool).\
                    filter(SQLConnectionPool.id==config.def_id).\
                    filter(SQLConnectionPool.cluster_id==self.server.cluster_id).\
                    one().name
        except NoResultFound:
            logger_notif('Stopping notifier, could not find an SQL pool for config `%s`', config)
            self.keep_running = False
            return

        with closing(self.outgoing.sql[def_name].session()) as session:
            rows = session.execute(config.query).fetchall()
            for row in rows:
                dict_row = dict(row.items())
                for k, v in dict_row.items():
                    if isinstance(v, datetime):
                        dict_row[k] = v.isoformat()
                out.append(dict_row)

            if out:
                msg = 'Executing `%s` in background with %d %s'
                if has_debug:
                    msg += ' ({})'.format(out)

                len_out = len(out)
                row_noun = 'row' if len_out == 1 else 'rows'
                logger_notif.info(msg, config.service_name, len_out, row_noun)
                self.invoke_async(config.service_name, {'data':out})

# ################################################################################################################################
