# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.exception import ZatoException
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

class GetList(AdminService):
    """ Returns the list of servers (this server only in the new architecture).
    """

    class SimpleIO(AdminSIO):
        request_elem = 'zato_server_get_list_request'
        response_elem = 'zato_server_get_list_response'
        input_required = 'cluster_id',
        output_required = 'id', 'cluster_id', 'name', 'host'
        output_optional = 'bind_host', 'bind_port', 'last_join_status', \
            'last_join_mod_date', 'last_join_mod_by', 'up_status', 'up_mod_date'
        output_repeated = True

    def handle(self):
        self.response.payload[:] = [self._get_server_data()]

    def _get_server_data(self):
        return {
            'id': self.server.id,
            'cluster_id': self.server.cluster_id,
            'name': self.server.name,
            'host': '',
            'bind_host': '',
            'bind_port': '',
            'last_join_status': 'accepted',
            'last_join_mod_date': '',
            'last_join_mod_by': '',
            'up_status': 'running',
            'up_mod_date': '',
        }

# ################################################################################################################################

class Edit(AdminService):
    """ Updates a server.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_server_edit_request'
        response_elem = 'zato_server_edit_response'
        input_required = ('id', 'name')
        output_required = ('id', 'cluster_id', 'name', 'host')
        output_optional = ('bind_host', 'bind_port', 'last_join_status',
            'last_join_mod_date', 'last_join_mod_by', 'up_status', 'up_mod_date')

    def handle(self):
        self.server.name = self.request.input.name

        self.response.payload.id = self.server.id
        self.response.payload.cluster_id = self.server.cluster_id
        self.response.payload.name = self.server.name
        self.response.payload.host = ''

# ################################################################################################################################

class GetByID(AdminService):
    """ Returns a particular server.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_server_get_by_id_request'
        response_elem = 'zato_server_get_by_id_response'
        input_required = ('id',)
        output_required = ('id', 'cluster_id', 'name', 'host')
        output_optional = ('bind_host', 'bind_port', 'last_join_status',
            'last_join_mod_date', 'last_join_mod_by', 'up_status', 'up_mod_date')

    def handle(self):
        self.response.payload.id = self.server.id
        self.response.payload.cluster_id = self.server.cluster_id
        self.response.payload.name = self.server.name
        self.response.payload.host = ''

# ################################################################################################################################

class Delete(AdminService):
    """ A server cannot delete itself.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_server_delete_request'
        response_elem = 'zato_server_delete_response'
        input_required = ('id',)

    def handle(self):
        msg = 'A server cannot delete itself, id:`{}`, name:`{}`'.format(self.server.id, self.server.name)
        self.logger.error(msg)
        raise ZatoException(self.cid, msg)

# ################################################################################################################################
