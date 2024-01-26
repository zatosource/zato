# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms.security.rbac.permission import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.odb.model import RBACPermission

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    output_class = RBACPermission
    url_name = 'security-rbac-permission'
    template = 'zato/security/rbac/permission.html'
    service_name = 'zato.security.rbac.permission.get-list'
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name')
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit')
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name',)
        output_required = ('id', 'name')

    def success_message(self, item):
        return 'Successfully {} the permission `{}`'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'security-rbac-permission-create'
    service_name = 'zato.security.rbac.permission.create'

class Edit(_CreateEdit):
    url_name = 'security-rbac-permission-edit'
    form_prefix = 'edit-'
    service_name = 'zato.security.rbac.permission.edit'

class Delete(_Delete):
    url_name = 'security-rbac-permission-delete'
    error_message = 'Could not delete the permission'
    service_name = 'zato.security.rbac.permission.delete'
