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
from zato.common.util import get_validate_tls_key_cert
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
