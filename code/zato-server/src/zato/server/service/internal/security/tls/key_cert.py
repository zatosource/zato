# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common import SEC_DEF_TYPE
from zato.common.broker_message import SECURITY
from zato.common.odb.model import TLSKeyCertSecurity
from zato.common.odb.query import tls_key_cert_list
from zato.common.util import delete_tls_material_from_fs, get_tls_ca_cert_full_path, get_tls_from_payload, store_tls
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

elem = 'security_tls_key_cert'
model = TLSKeyCertSecurity
label = 'a TLS key/cert pair'
broker_message = SECURITY
broker_message_prefix = 'TLS_KEY_CERT_'
list_func = tls_key_cert_list
create_edit_input_required_extra = ['auth_data']
skip_input_params = ['info', 'sec_type']
output_optional_extra = ['info']

def instance_hook(self, input, instance, attrs):

    decrypted = self.server.decrypt(input.auth_data).encode('utf8')

    instance.username = self.cid # Required by model
    instance.sec_type = SEC_DEF_TYPE.TLS_KEY_CERT
    instance.info = get_tls_from_payload(decrypted, True).encode('utf8')
    instance.auth_data = input.auth_data.encode('utf8')

    with self.lock():
        full_path = store_tls(self.server.tls_dir, decrypted, True)
        self.logger.info('Key/cert pair saved under `%s`', full_path)

def response_hook(self, input, instance, attrs, service_type):
    if service_type == 'create_edit':
        self.response.payload.info = instance.info

def broker_message_hook(self, input, instance, attrs, service_type):
    if service_type == 'delete':
        input.auth_data = instance.auth_data

def delete_hook(self, input, instance, attrs):
    delete_tls_material_from_fs(self.server, instance.info, get_tls_ca_cert_full_path)

class GetList(AdminService):
    _filter_by = TLSKeyCertSecurity.name,
    __metaclass__ = GetListMeta

class Delete(AdminService):
    __metaclass__ = DeleteMeta

class Create(AdminService):
    __metaclass__ = CreateEditMeta

class Edit(AdminService):
    __metaclass__ = CreateEditMeta
