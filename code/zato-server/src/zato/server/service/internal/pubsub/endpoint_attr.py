# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.broker_message import PUB_SUB
from zato.common.odb.model import PubSubEndpointAttr
from zato.common.odb.query import pubsub_endpoint_attr_list
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################

elem = 'pubsub_endpoint_attr'
model = PubSubEndpointAttr
label = 'a publish/subscribe endpoint attribute'
broker_message = PUB_SUB
broker_message_prefix = 'ENDPOINT_ATTR_'
list_func = pubsub_endpoint_attr_list

# ################################################################################################################################

class Get(AdminService):
    name = 'zato.pubsub.endpoint-attr.get'

    def handle(self):
        raise NotImplemented()

# ################################################################################################################################

class GetList(AdminService):
    name = 'zato.pubsub.endpoint-attr.get-list'
    _filter_by = PubSubEndpointAttr.key,
    __metaclass__ = GetListMeta

# ################################################################################################################################

class Create(AdminService):
    name = 'zato.pubsub.endpoint-attr.create'
    __metaclass__ = CreateEditMeta

# ################################################################################################################################

class Edit(AdminService):
    name = 'zato.pubsub.endpoint-attr.edit'
    __metaclass__ = CreateEditMeta

# ################################################################################################################################

class Delete(AdminService):
    name = 'zato.pubsub.endpoint-attr.delete'
    __metaclass__ = DeleteMeta

# ################################################################################################################################
