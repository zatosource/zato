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
from zato.common.odb.model import RBACRole
from zato.common.odb.query import rbac_role, rbac_role_list
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.server.service import Service

    Bunch = Bunch
    Service = Service

# ################################################################################################################################

elem = 'security_rbac_role'
model = RBACRole
label = 'an RBAC role'
get_list_docs = 'RBAC roles'
broker_message = RBAC
broker_message_prefix = 'ROLE_'
list_func = rbac_role_list
input_optional_extra = ['parent_name']
output_optional_extra = ['parent_id', 'parent_name']
create_edit_rewrite = ['id']

# ################################################################################################################################

def instance_hook(self, input, instance, attrs):
    # type: (Service, Bunch, RBACRole, Bunch)

    if attrs.is_create_edit:
        is_root = input.name.lower() == 'root'

        if is_root:
            raise ValueError('Root role cannot be changed')

        with closing(self.odb.session()) as session:
            parent = rbac_role(session, self.server.cluster_id, input.parent_id, input.parent_name)
            input.parent_id = parent.id

        if input.parent_id == instance.id:
            raise ValueError('A role cannot be its own parent')
        else:
            instance.parent_id = input.parent_id

# ################################################################################################################################

def response_hook(self, input, instance, attrs, service_type):
    # type: (Service, Bunch, RBACRole, Bunch, str)

    if service_type == 'create_edit':
        self.response.payload.parent_id = instance.parent_id

        if instance.parent_id:

            with closing(self.odb.session()) as session:
                parent = session.query(attrs.model).\
                    filter(attrs.model.id==instance.parent_id).one()

            self.response.payload.parent_name = parent.name

# ################################################################################################################################

def broker_message_hook(self, input, instance, attrs, service_type):
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
