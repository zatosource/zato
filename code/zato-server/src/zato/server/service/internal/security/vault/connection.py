# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from uuid import uuid4

# SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound

# Python 2/3 compatibility
from six import add_metaclass

# Zato
from zato.common.broker_message import VAULT
from zato.common.odb.model import VaultConnection
from zato.common.odb.query import service, vault_connection_list
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

elem = 'security_vault_connection'
model = VaultConnection
label = 'a Vault connection'
get_list_docs = 'Vault connections'
broker_message = VAULT
broker_message_prefix = 'CONNECTION_'
list_func = vault_connection_list
output_optional_extra = ['service_id', 'service_name']
extra_delete_attrs = ['cluster_id', 'service_id']

# ################################################################################################################################

def instance_hook(self, input, instance, attrs):
    instance.tls_key_cert_id = instance.tls_key_cert_id or None
    instance.tls_ca_cert_id = instance.tls_ca_cert_id or None
    instance.username = uuid4().hex

# ################################################################################################################################

def broker_message_hook(self, input, instance, attrs, service_type):

    if input.service_id:
        with closing(self.odb.session()) as session:
            try:
                input.service_name = service(session, input.cluster_id, input.service_id).name
            except NoResultFound:
                input.service_name = '' # That is fine, service is optional for Vault connections

# ################################################################################################################################

@add_metaclass(GetListMeta)
class GetList(AdminService):
    _filter_by = VaultConnection.name,

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
