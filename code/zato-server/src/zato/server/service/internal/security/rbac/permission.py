# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Python 2/3 compatibility
from six import add_metaclass

# Zato
from zato.common.broker_message import RBAC
from zato.common.odb.model import RBACPermission
from zato.common.odb.query import rbac_permission_list
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.server.service import Service

    Bunch = Bunch
    Service = Service

# ################################################################################################################################

elem = 'security_rbac_permission'
model = RBACPermission
label = 'an RBAC permission'
get_list_docs = 'RBAC permissions'
broker_message = RBAC
broker_message_prefix = 'PERMISSION_'
list_func = rbac_permission_list

# ################################################################################################################################

def broker_message_hook(service, input, instance, attrs, service_type):
    # type: (Service, Bunch, RBACPermission, Bunch, str)

    if service_type == 'create_edit':
        input.id = instance.id

# ################################################################################################################################

@add_metaclass(GetListMeta)
class GetList(AdminService):
    _filter_by = RBACPermission.name,

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
