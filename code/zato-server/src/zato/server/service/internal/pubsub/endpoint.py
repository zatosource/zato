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
from zato.common.odb.model import PubSubEndpoint
from zato.common.odb.query import pubsub_endpoint_list
from zato.server.service.internal import AdminService, AdminSIO
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################

elem = 'pubsub_endpoint'
model = PubSubEndpoint
label = 'a publish/subscribe endpoint'
broker_message = PUB_SUB
broker_message_prefix = 'ENDPOINT_'
list_func = pubsub_endpoint_list
check_existing_one = False # Endpoints objects as such have no attributes except for is_internal
skip_output_params = ['name']

# ################################################################################################################################

class Get(AdminService):
    name = 'zato.pubsub.endpoint.get'

    def handle(self):
        raise NotImplemented()

# ################################################################################################################################

class GetList(AdminService):
    name = 'zato.pubsub.endpoint.get-list'
    _filter_by = PubSubEndpoint.id,
    __metaclass__ = GetListMeta

# ################################################################################################################################

class Create(AdminService):
    name = 'zato.pubsub.endpoint.create'
    __metaclass__ = CreateEditMeta

# ################################################################################################################################

class Edit(AdminService):
    name = 'zato.pubsub.endpoint.edit'
    __metaclass__ = CreateEditMeta

# ################################################################################################################################

class Delete(AdminService):
    name = 'zato.pubsub.endpoint.delete'
    __metaclass__ = DeleteMeta

# ################################################################################################################################
