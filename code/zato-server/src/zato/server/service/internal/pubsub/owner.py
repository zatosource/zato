# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from uuid import uuid4

# Zato
from zato.common.broker_message import PUB_SUB
from zato.common.odb.model import PubSubOwner
from zato.common.odb.query import pubsub_owner_list
from zato.server.service.internal import AdminService, AdminSIO
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################

elem = 'pubsub_owner'
model = PubSubOwner
label = 'a publish/subscribe owner'
broker_message = PUB_SUB
broker_message_prefix = 'OWNER_'
list_func = pubsub_owner_list

# ################################################################################################################################

class Get(AdminService):
    name = 'zato.pubsub.owner.get'

    def handle(self):
        raise NotImplemented()

# ################################################################################################################################

class GetList(AdminService):
    name = 'zato.pubsub.owner.get-list'
    _filter_by = PubSubOwner.name,
    __metaclass__ = GetListMeta

# ################################################################################################################################

class Create(AdminService):
    name = 'zato.pubsub.owner.create'
    __metaclass__ = CreateEditMeta

# ################################################################################################################################

class Edit(AdminService):
    name = 'zato.pubsub.owner.edit'
    __metaclass__ = CreateEditMeta

# ################################################################################################################################

class Delete(AdminService):
    name = 'zato.pubsub.owner.delete'
    __metaclass__ = DeleteMeta

# ################################################################################################################################
