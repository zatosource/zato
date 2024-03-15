# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# Python 2/3 compatibility
from six import add_metaclass

# Zato
from zato.common.broker_message import RBAC
from zato.common.odb.model import RBACRole, RBACPermission, RBACRolePermission, Service
from zato.common.odb.query import rbac_role, rbac_permission, rbac_role_permission_list, service
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.common.odb.model import RBACClientRole

    Bunch = Bunch
    RBACClientRole = RBACClientRole

# ################################################################################################################################

elem = 'security_rbac_role_permission'
model = RBACRolePermission
label = 'an RBAC role permission'
get_list_docs = 'RBAC role permissions'
broker_message = RBAC
broker_message_prefix = 'ROLE_PERMISSION_'
list_func = rbac_role_permission_list
input_optional_extra = ['role_name', 'service_name', 'perm_name']
output_optional_extra = ['role_name', 'service_name', 'perm_name']
create_edit_rewrite = ['id']
skip_input_params = ['name']
extra_delete_attrs = ['role_id', 'service_id', 'perm_id']
skip_create_integrity_error = True
check_existing_one = False

# ################################################################################################################################

def get_extra(service, role_id, service_id, perm_id):
    # type: (Service, int, int, int) -> str

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
    # type: (Service, Bunch, RBACRolePermission, Bunch)

    if attrs.is_create_edit:

        cluster_id = self.server.cluster_id

        with closing(self.odb.session()) as session:

            role = rbac_role(session, cluster_id, input.role_id, input.role_name)
            _service = service(session, cluster_id, input.service_id, input.service_name)
            perm = rbac_permission(session, cluster_id, input.perm_id, input.perm_name)

            instance.role_id = role.id
            instance.service_id = _service.id
            instance.perm_id = perm.id

            input.role_id = role.id
            input.service_id = _service.id
            input.perm_id = perm.id

        instance.name = '{}:::{}::{}'.format(role.name, _service.name, perm.name)

# ################################################################################################################################

def response_hook(self, input, instance, attrs, service_type):
    # type: (Service, Bunch, RBACClientRole, Bunch, str)

    if service_type == 'get_list':
        for item in self.response.payload:

            item_name, role_name, service_name, perm_name = get_extra(self, item.role_id, item.service_id, item.perm_id)

            item.name = item_name
            item.role_name = role_name
            item.service_name = service_name
            item.perm_name = perm_name

    elif service_type == 'create_edit':

        cluster_id = self.server.cluster_id

        with closing(self.odb.session()) as session:

            role = rbac_role(session, cluster_id, input.role_id, input.role_name)
            _service = service(session, cluster_id, input.service_id, input.service_name)
            perm = rbac_permission(session, cluster_id, input.perm_id, input.perm_name)

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
