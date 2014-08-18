# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# Zato
from zato.common.broker_message import RBAC
from zato.common.odb.model import RBACRolePermission
from zato.common.odb.query import rbac_client_role_list
from zato.server.service.internal import AdminService, AdminSIO
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

elem = 'security_rbac_role_permission'
model = RBACRolePermission
label = 'an RBAC role permission'
broker_message = RBAC
broker_message_prefix = 'ROLE_PERMISSION_'
list_func = rbac_client_role_list
output_optional_extra = ['client_name', 'role_name', 'service_name'] husd fdes'pfds ;f pkisd'f'
create_edit_rewrite = ['id']
skip_input_params = ['name']
extra_delete_attrs = ['client_def', 'role_id']
check_existing_one = False

def instance_hook(service, input, instance, attrs):
    with closing(service.odb.session()) as session:
        role = session.query(RBACRole).\
            filter(RBACRole.id==input.role_id).one()

    instance.name = '{}:::{}'.format(instance.client_def, role.name)

def response_hook(service, input, instance, attrs, service_type):
    if service_type == 'get_list':
        for item in service.response.payload:
            with closing(service.odb.session()) as session:
                role = session.query(RBACRole).\
                    filter(RBACRole.id==item.role_id).one()
                item.client_name = item.client_def
                item.role_name = role.name

    elif service_type == 'create_edit':
        with closing(service.odb.session()) as session:
            role = session.query(RBACRole).\
                filter(RBACRole.id==instance.role_id).one()

        service.response.payload.client_name = instance.client_def
        service.response.payload.role_name = role.name

class GetList(AdminService):
    __metaclass__ = GetListMeta

class Create(AdminService):
    __metaclass__ = CreateEditMeta

class Delete(AdminService):
    __metaclass__ = DeleteMeta
