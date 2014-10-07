# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.broker_message import SECURITY
from zato.common.odb.model import TLSCACert
from zato.common.odb.query import tls_ca_cert_list
from zato.common.util import validate_tls_cert_from_paths, store_tls_ca_cert
from zato.server.service.internal import AdminService, AdminSIO
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

elem = 'security_tls_ca_cert'
model = TLSCACert
label = 'a TLS CA cert'
broker_message = SECURITY
broker_message_prefix = 'TLS_CA_CERT_'
list_func = tls_ca_cert_list
extra_delete_attrs = ('fs_name',)

def instance_hook(service, input, instance, attrs):
    validate_tls_cert_from_paths(service.server.tls_dir, input.fs_name)
    instance.username = service.cid # Required by model

class GetList(AdminService):
    __metaclass__ = GetListMeta

class Delete(AdminService):
    __metaclass__ = DeleteMeta

class Upload(AdminService):

    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_tls_ca_cert_upload_request'
        response_elem = 'zato_security_tls_ca_cert_upload_response'
        input_required = ('cluster_id', 'payload', 'payload_name')

    def handle(self):
        self.log_input()
        store_tls_ca_cert(self.server.tls_dir, self.request.input.payload.decode('base64'), self.request.input.payload_name)
