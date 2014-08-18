# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms.security.rbac.role_permission import CreateForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.odb.model import RBACRolePermission

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    output_class = RBACRolePermission
    url_name = 'security-rbac-role-permission'
    template = 'zato/security/rbac/role-permission.html'
    service_name = 'zato.security.rbac.role-permission.get-list'

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'client_def', 'client_name', 'role_id', 'role_name', 'service_id', 'service_name')
        output_repeated = True

    def handle(self):

        client_def_list = []
        role_id_list = []
        service_id_list = []

        if self.req.zato.cluster_id:

            service_name = 'zato.security.rbac.role-permission.get-client-def-list'
            response = self.req.zato.client.invoke(service_name, {'cluster_id':self.req.zato.cluster_id})
            if response.has_data:
                client_def_list = response.data

            service_name = 'zato.security.rbac.role.get-list'
            response = self.req.zato.client.invoke(service_name, {'cluster_id':self.req.zato.cluster_id})
            if response.has_data:
                role_id_list = response.data

            service_name = 'zato.service.get-list'
            response = self.req.zato.client.invoke(service_name, {'cluster_id':self.req.zato.cluster_id})
            if response.has_data:
                service_id_list = response.data

        return {
            'create_form': CreateForm(client_def_list, role_id_list, service_id_list)
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('client_def', 'role_id')
        output_required = ('id', 'client_name', 'role_name')

    def success_message(self, item):
        return 'Successfully {} the role permission `{}`'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'security-rbac-role-permission-create'
    service_name = 'zato.security.rbac.role-permission.create'

class Delete(_Delete):
    url_name = 'security-rbac-role-permission-delete'
    error_message = 'Could not delete the role permission'
    service_name = 'zato.security.rbac.role-permission.delete'
