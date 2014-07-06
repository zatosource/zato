# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from uuid import uuid4

# Zato
from zato.common.broker_message import SECURITY
from zato.common.odb.model import TLSKeyCertSecurity
from zato.common.odb.query import tls_key_cert_list
from zato.server.service.internal import AdminService, ChangePasswordBase
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

elem = 'security_tls_key_cert'
model = TLSKeyCertSecurity
label = 'a TLS key/cert pair'
broker_message = SECURITY
broker_message_prefix = 'TLS_KEY_CERT_'
list_func = tls_key_cert_list
skip_input_params = ('sec_type', 'cert_fp', 'cert_cn')

def instance_hook(service, input, instance, attrs):
    input, instance, attrs
    instance.cert_fp = 'bbb'
    instance.cert_cn = 'ccc'
    instance.username = service.cid # Required by model

class GetList(AdminService):
    __metaclass__ = GetListMeta

class Create(AdminService):
    __metaclass__ = CreateEditMeta

class Edit(AdminService):
    __metaclass__ = CreateEditMeta

class Delete(AdminService):
    __metaclass__ = DeleteMeta
