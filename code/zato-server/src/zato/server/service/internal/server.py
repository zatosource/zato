# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.exception import ZatoException
from zato.server.service.internal import AdminService

# ################################################################################################################################

class GetList(AdminService):
    """ Returns the list of servers (this server only in the new architecture).
    """
    input = 'cluster_id',
    output = 'id', 'cluster_id', 'name', 'host', '-bind_host', '-bind_port', '-last_join_status', \
        '-last_join_mod_date', '-last_join_mod_by', '-up_status', '-up_mod_date'
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
    input = 'id', 'name'
    output = 'id', 'cluster_id', 'name', 'host', '-bind_host', '-bind_port', '-last_join_status', \
        '-last_join_mod_date', '-last_join_mod_by', '-up_status', '-up_mod_date'

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
    input = 'id',
    output = 'id', 'cluster_id', 'name', 'host', '-bind_host', '-bind_port', '-last_join_status', \
        '-last_join_mod_date', '-last_join_mod_by', '-up_status', '-up_mod_date'

    def handle(self):
        self.response.payload.id = self.server.id
        self.response.payload.cluster_id = self.server.cluster_id
        self.response.payload.name = self.server.name
        self.response.payload.host = ''

# ################################################################################################################################

class Delete(AdminService):
    """ A server cannot delete itself.
    """
    input = 'id',

    def handle(self):
        msg = 'A server cannot delete itself, id:`{}`, name:`{}`'.format(self.server.id, self.server.name)
        self.logger.error(msg)
        raise ZatoException(self.cid, msg)

# ################################################################################################################################
