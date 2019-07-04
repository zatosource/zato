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
from zato.common.odb.model import RBACRole
from zato.common.odb.query import rbac_role_list
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################

elem = 'security_rbac_role'
model = RBACRole
label = 'an RBAC role'
get_list_docs = 'RBAC roles'
broker_message = RBAC
broker_message_prefix = 'ROLE_'
list_func = rbac_role_list
output_optional_extra = ['parent_id', 'parent_name']
create_edit_rewrite = ['id']

# ################################################################################################################################

def instance_hook(service, input, instance, attrs):

    if attrs.is_create_edit:
        is_root = input.name.lower() == 'root'

        if is_root:
            raise ValueError('Root role cannot be changed')

        if input.parent_id == instance.id:
            raise ValueError('A role cannot be its own parent')

# ################################################################################################################################

def response_hook(service, input, instance, attrs, service_type):
    if service_type == 'create_edit':
        service.response.payload.parent_id = instance.parent_id

        with closing(service.odb.session()) as session:
            parent = session.query(attrs.model).\
                filter(attrs.model.id==instance.parent_id).one()

        service.response.payload.parent_name = parent.name

# ################################################################################################################################

def broker_message_hook(service, input, instance, attrs, service_type):
    input.id = instance.id

# ################################################################################################################################

@add_metaclass(GetListMeta)
class GetList(AdminService):
    _filter_by = RBACRole.name,

# ################################################################################################################################

@add_metaclass(CreateEditMeta)
class Create(AdminService):
    pass

# ################################################################################################################################

@add_metaclass(CreateEditMeta)
class Edit(AdminService):
    pass

# ################################################################################################################################

@add_metaclass(DeleteMeta)
class Delete(AdminService):
    pass

# ################################################################################################################################
