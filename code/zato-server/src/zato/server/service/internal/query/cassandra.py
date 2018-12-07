# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.broker_message import QUERY
from zato.common.odb.model import CassandraConn, CassandraQuery
from zato.common.odb.query import cassandra_query_list
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

elem = 'query_cassandra'
model = CassandraQuery
output_optional_extra = ['def_name']
label = 'a Cassandra query'
get_list_docs = 'Cassandra queries'
broker_message = QUERY
broker_message_prefix = 'CASSANDRA_'
list_func = cassandra_query_list
def_needed = CassandraConn

class GetList(AdminService):
    _filter_by = CassandraQuery.name,
    __metaclass__ = GetListMeta

class Create(AdminService):
    __metaclass__ = CreateEditMeta

class Edit(AdminService):
    __metaclass__ = CreateEditMeta

class Delete(AdminService):
    __metaclass__ = DeleteMeta
