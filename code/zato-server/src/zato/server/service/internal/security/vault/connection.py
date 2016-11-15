# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from uuid import uuid4

# Zato
from zato.common.broker_message import VAULT
from zato.common.odb.model import Service, VaultConnection
from zato.common.odb.query import vault_connection, vault_connection_list
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

elem = 'security_vault_connection'
model = VaultConnection
label = 'a Vault connection'
broker_message = VAULT
broker_message_prefix = 'CONNECTION_'
list_func = vault_connection_list
output_optional_extra = ['service_id', 'service_name']

def instance_hook(self, input, instance, attrs):
    instance.username = uuid4().hex

def broker_message_hook(self, input, instance, attrs, service_type):

    with closing(self.odb.session()) as session:
        input.service_name = vault_connection(session, input.cluster_id, input.id).service_name

class GetList(AdminService):
    _filter_by = VaultConnection.name,
    __metaclass__ = GetListMeta

class Create(AdminService):
    __metaclass__ = CreateEditMeta

class Edit(AdminService):
    __metaclass__ = CreateEditMeta

class Delete(AdminService):
    __metaclass__ = DeleteMeta
