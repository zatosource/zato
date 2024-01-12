# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms.security.rbac.client_role import CreateForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.odb.model import RBACRole

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    output_class = RBACRole
    url_name = 'security-rbac-client-role'
    template = 'zato/security/rbac/client-role.html'
    service_name = 'zato.security.rbac.client-role.get-list'
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'client_def', 'client_name', 'role_id', 'role_name')
        output_repeated = True

    def handle(self):

        client_def_list = []
        role_id_list = []

        if self.req.zato.cluster_id:

            service_name = 'zato.security.rbac.client-role.get-client-def-list'
            response = self.req.zato.client.invoke(service_name, {'cluster_id':self.req.zato.cluster_id})
            if response.has_data:
                client_def_list = response.data

            service_name = 'zato.security.rbac.role.get-list'
            response = self.req.zato.client.invoke(service_name, {'cluster_id':self.req.zato.cluster_id})
            if response.has_data:
                role_id_list = response.data

        return {
            'create_form': CreateForm(client_def_list, role_id_list)
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('client_def', 'role_id')
        output_required = ('id', 'client_name', 'role_name')

    def success_message(self, item):
        return 'Successfully {} the client role `{}`'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'security-rbac-client-role-create'
    service_name = 'zato.security.rbac.client-role.create'

class Delete(_Delete):
    url_name = 'security-rbac-client-role-delete'
    error_message = 'Could not delete the client role'
    service_name = 'zato.security.rbac.client-role.delete'
