# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# Python 2/3 compatibility
from six import add_metaclass

# Zato
from zato.common.broker_message import RBAC
from zato.common.odb.model import RBACRole, RBACPermission, RBACRolePermission, Service
from zato.common.odb.query import rbac_role_permission_list
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################

elem = 'security_rbac_role_permission'
model = RBACRolePermission
label = 'an RBAC role permission'
get_list_docs = 'RBAC role permissions'
broker_message = RBAC
broker_message_prefix = 'ROLE_PERMISSION_'
list_func = rbac_role_permission_list
output_optional_extra = ['role_name', 'service_name', 'perm_name']
create_edit_rewrite = ['id']
skip_input_params = ['name']
extra_delete_attrs = ['role_id', 'service_id', 'perm_id']
check_existing_one = False

# ################################################################################################################################

def get_extra(service, role_id, service_id, perm_id):

    with closing(service.odb.session()) as session:

        role = session.query(RBACRole).\
            filter(RBACRole.id==role_id).one()

        _service = session.query(Service).\
            filter(Service.id==service_id).one()

        perm = session.query(RBACPermission).\
            filter(RBACPermission.id==perm_id).one()

        return '{}:::{}::{}'.format(role.name, _service.name, perm.name), role.name, _service.name, perm.name

# ################################################################################################################################

def instance_hook(self, input, instance, attrs):

    if attrs.is_create_edit:
        with closing(self.odb.session()) as session:

            role = session.query(RBACRole).\
                filter(RBACRole.id==input.role_id).one()

            _service = session.query(Service).\
                filter(Service.id==input.service_id).one()

            perm = session.query(RBACPermission).\
                filter(RBACPermission.id==input.perm_id).one()

        instance.name = '{}:::{}::{}'.format(role.name, _service.name, perm.name)

# ################################################################################################################################

def response_hook(self, input, instance, attrs, service_type):

    if service_type == 'get_list':
        for item in self.response.payload:

            item_name, role_name, service_name, perm_name = get_extra(self, item.role_id, item.service_id, item.perm_id)

            item.name = item_name
            item.role_name = role_name
            item.service_name = service_name
            item.perm_name = perm_name

    elif service_type == 'create_edit':

        with closing(self.odb.session()) as session:

            role = session.query(RBACRole).\
                filter(RBACRole.id==instance.role_id).one()

            _service = session.query(Service).\
                filter(Service.id==instance.service_id).one()

            perm = session.query(RBACPermission).\
                filter(RBACPermission.id==input.perm_id).one()

        self.response.payload.role_name = role.name
        self.response.payload.service_name = _service.name
        self.response.payload.perm_name = perm.name

# ################################################################################################################################

@add_metaclass(GetListMeta)
class GetList(AdminService):
    _filter_by = RBACRole.name,

# ################################################################################################################################

@add_metaclass(CreateEditMeta)
class Create(AdminService):
    pass

# ################################################################################################################################

class Edit(AdminService):
    """ This service is a no-op added only for API completeness.
    """
    def handle(self):
        pass

# ################################################################################################################################

@add_metaclass(DeleteMeta)
class Delete(AdminService):
    pass

# ################################################################################################################################
