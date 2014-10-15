# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import errno, os

# Zato
from zato.common import SEC_DEF_TYPE
from zato.common.broker_message import SECURITY
from zato.common.odb.model import TLSKeyCertSecurity
from zato.common.odb.query import tls_key_cert_list
from zato.common.util import delete_tls_material_from_fs, get_tls_cert_full_path, get_tls_cert_info_from_payload, \
     store_tls_ca_cert
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

elem = 'security_tls_ca_cert'
model = TLSKeyCertSecurity
label = 'a TLS key/cert pair'
broker_message = SECURITY
broker_message_prefix = 'TLS_KEY_CERT_'
list_func = tls_key_cert_list
create_edit_input_required_extra = ['value']
skip_input_params = ['info', 'sec_type']
output_optional_extra = ['info',]

def instance_hook(service, input, instance, attrs):

    service.logger.warn(input)
    instance.username = service.cid # Required by model
    instance.sec_type = SEC_DEF_TYPE.TLS_KEY_CERT
    instance.info = get_tls_cert_info_from_payload(input.value)

    with service.lock():
        full_path = store_tls_ca_cert(service.server.tls_dir, service.request.input.value)
        service.logger.info('CA certificate saved under `%s`', full_path)

def response_hook(service, input, instance, attrs, service_type):
    if service_type == 'create_edit':
        service.response.payload.info = instance.info

def broker_message_hook(service, input, instance, attrs, service_type):
    if service_type == 'delete':
        input.value = instance.value

def delete_hook(service, input, instance, attrs):
    delete_tls_material_from_fs(service.server, instance.info, get_tls_cert_full_path)

class GetList(AdminService):
    __metaclass__ = GetListMeta

class Delete(AdminService):
    __metaclass__ = DeleteMeta

class Create(AdminService):
    __metaclass__ = CreateEditMeta

class Edit(AdminService):
    __metaclass__ = CreateEditMeta

'''
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
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

elem = 'security_tls_key_cert'
model = TLSKeyCertSecurity
label = 'a TLS key/cert pair'
broker_message = SECURITY
broker_message_prefix = 'TLS_KEY_CERT_'
list_func = tls_key_cert_list
skip_input_params = ('sec_type', 'cert_fp', 'cert_subject')
extra_delete_attrs = ('fs_name',)

def instance_hook(service, input, instance, attrs):
    cert_fp, cert_subject, _ = get_validate_tls_key_cert(service.server.tls_dir, input.fs_name)

    input.cert_fp = instance.cert_fp = cert_fp
    input.cert_subject = instance.cert_subject = cert_subject
    input.sec_type = SEC_DEF_TYPE.TLS_KEY_CERT

    instance.username = service.cid # Required by model

class GetList(AdminService):
    __metaclass__ = GetListMeta

class Create(AdminService):
    __metaclass__ = CreateEditMeta

class Edit(AdminService):
    __metaclass__ = CreateEditMeta

class Delete(AdminService):
    __metaclass__ = DeleteMeta
'''