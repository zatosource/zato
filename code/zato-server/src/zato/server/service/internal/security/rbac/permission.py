# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.broker_message import RBAC
from zato.common.odb.model import RBACPermission
from zato.common.odb.query import rbac_permission_list
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

elem = 'security_rbac_permission'
model = RBACPermission
label = 'an RBAC permission'
get_list_docs = 'RBAC permissions'
broker_message = RBAC
broker_message_prefix = 'PERMISSION_'
list_func = rbac_permission_list

def broker_message_hook(service, input, instance, attrs, service_type):
    if service_type == 'create_edit':
        input.id = instance.id

class GetList(AdminService):
    _filter_by = RBACPermission.name,
    __metaclass__ = GetListMeta

class Create(AdminService):
    __metaclass__ = CreateEditMeta

class Edit(AdminService):
    __metaclass__ = CreateEditMeta

class Delete(AdminService):
    __metaclass__ = DeleteMeta
