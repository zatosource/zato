# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Python 2/3 compatibility
from zato.common.py23_.past.builtins import unicode
from six import add_metaclass

# Zato
from zato.common.api import SEC_DEF_TYPE
from zato.common.broker_message import SECURITY
from zato.common.odb.model import TLSKeyCertSecurity
from zato.common.odb.query import tls_key_cert_list
from zato.common.util.api import delete_tls_material_from_fs, get_tls_ca_cert_full_path, get_tls_from_payload, store_tls
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################

elem = 'security_tls_key_cert'
model = TLSKeyCertSecurity
label = 'a TLS key/cert pair'
get_list_docs = 'TLS key/cert pairs'
broker_message = SECURITY
broker_message_prefix = 'TLS_KEY_CERT_'
list_func = tls_key_cert_list
create_edit_input_required_extra = ['auth_data']
skip_input_params = ['info', 'sec_type']
output_optional_extra = ['info']

# ################################################################################################################################

def instance_hook(self, input, instance, attrs):

    if attrs.is_delete:
        return

    decrypted = self.server.decrypt(input.auth_data).encode('utf8')

    instance.username = self.cid # Required by model
    instance.sec_type = SEC_DEF_TYPE.TLS_KEY_CERT
    instance.info = get_tls_from_payload(decrypted, True).encode('utf8')
    instance.auth_data = input.auth_data.encode('utf8')

    with self.lock():
        full_path = store_tls(self.server.tls_dir, decrypted, True)
        self.logger.info('Key/cert pair saved under `%s`', full_path)

# ################################################################################################################################

def response_hook(self, input, instance, attrs, service_type):
    if service_type == 'create_edit':
        self.response.payload.info = instance.info

    elif service_type == 'get_list':
        for elem in self.response.payload:
            if not isinstance(elem.auth_data, unicode):
                elem.auth_data = elem.auth_data.decode('utf8')
            elem.auth_data = self.server.decrypt(elem.auth_data)

# ################################################################################################################################

def broker_message_hook(self, input, instance, attrs, service_type):
    input.sec_type = SEC_DEF_TYPE.TLS_KEY_CERT
    if service_type == 'delete':
        input.auth_data = instance.auth_data

# ################################################################################################################################

def delete_hook(self, input, instance, attrs):
    delete_tls_material_from_fs(self.server, instance.info, get_tls_ca_cert_full_path)

# ################################################################################################################################

@add_metaclass(GetListMeta)
class GetList(AdminService):
    _filter_by = TLSKeyCertSecurity.name,

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
