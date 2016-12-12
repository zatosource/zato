# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from uuid import uuid4

# SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound

# Zato
from zato.common.broker_message import VAULT
from zato.common.odb.model import VaultConnection
from zato.common.odb.query import service, vault_connection_list
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

elem = 'security_vault_connection'
model = VaultConnection
label = 'a Vault connection'
broker_message = VAULT
broker_message_prefix = 'CONNECTION_'
list_func = vault_connection_list
output_optional_extra = ['service_id', 'service_name']
extra_delete_attrs = ['cluster_id', 'service_id']

def instance_hook(self, input, instance, attrs):
    instance.username = uuid4().hex

def broker_message_hook(self, input, instance, attrs, service_type):

    with closing(self.odb.session()) as session:
        try:
            input.service_name = service(session, input.cluster_id, input.service_id).name
        except NoResultFound:
            input.service_name = '' # That is fine, service is optional for Vault connections

class GetList(AdminService):
    _filter_by = VaultConnection.name,
    __metaclass__ = GetListMeta

class Create(AdminService):
    __metaclass__ = CreateEditMeta

class Edit(AdminService):
    __metaclass__ = CreateEditMeta

class Delete(AdminService):
    __metaclass__ = DeleteMeta
