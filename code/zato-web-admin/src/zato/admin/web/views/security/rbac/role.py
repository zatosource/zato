# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms.security.rbac.role import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.odb.model import RBACRole

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    output_class = RBACRole
    url_name = 'security-rbac-role'
    template = 'zato/security/rbac/role.html'
    service_name = 'zato.security.rbac.role.get-list'

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'parent_id', 'parent_name')
        output_repeated = True

    def handle(self):

        items = []
        if self.req.zato.cluster_id:
            service_name = 'zato.security.rbac.role.get-list'
            response = self.req.zato.client.invoke(service_name, {'cluster_id':self.req.zato.cluster_id})
            if response.has_data:
                items = response.data

        return {
            'create_form': CreateForm(items),
            'edit_form': EditForm(items, prefix='edit')
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'parent_id')
        output_required = ('id', 'name', 'parent_id', 'parent_name')

    def success_message(self, item):
        return 'Successfully {} the role `{}`'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'security-rbac-role-create'
    service_name = 'zato.security.rbac.role.create'

class Edit(_CreateEdit):
    url_name = 'security-rbac-role-edit'
    form_prefix = 'edit-'
    service_name = 'zato.security.rbac.role.edit'

class Delete(_Delete):
    url_name = 'security-rbac-role-delete'
    error_message = 'Could not delete the role'
    service_name = 'zato.security.rbac.role.delete'
