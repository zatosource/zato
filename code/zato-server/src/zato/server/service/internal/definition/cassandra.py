# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Python 2/3 compatibility
from six import add_metaclass

# Zato
from zato.common.broker_message import DEFINITION
from zato.common.odb.model import CassandraConn
from zato.common.odb.query import cassandra_conn_list
from zato.server.service.internal import AdminService, ChangePasswordBase
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

elem = 'definition_cassandra'
model = CassandraConn
label = 'a Cassandra connection'
get_list_docs = 'Cassandra connections'
broker_message = DEFINITION
broker_message_prefix = 'CASSANDRA_'
list_func = cassandra_conn_list

# ################################################################################################################################

@add_metaclass(GetListMeta)
class GetList(AdminService):
    _filter_by = CassandraConn.name,

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

class ChangePassword(ChangePasswordBase):
    """ Changes the password of a Cassandra connection definition.
    """
    password_required = False

    class SimpleIO(ChangePasswordBase.SimpleIO):
        request_elem = 'zato_definition_cassandra_change_password_request'
        response_elem = 'zato_definition_cassandra_change_password_response'

    def handle(self):
        def _auth(instance, password):
            instance.password = password

        return self._handle(CassandraConn, _auth, DEFINITION.CASSANDRA_CHANGE_PASSWORD.value)

# ################################################################################################################################
