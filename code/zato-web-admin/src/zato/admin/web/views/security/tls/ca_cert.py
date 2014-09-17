# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms.security.tls.ca_cert import CreateForm, EditForm
from zato.admin.web.views import method_allowed, upload_to_server
from zato.admin.web.views.security.tls import CreateEdit as _CreateEdit, Delete as _Delete, Index as _Index
from zato.common.odb.model import TLSCACert

logger = logging.getLogger(__name__)

class Index(_Index):
    output_class = TLSCACert
    url_name = 'security-tls-ca-cert'
    template = 'zato/security/tls/ca-cert.html'
    service_name = 'zato.security.tls.ca-cert.get-list'
    create_form = CreateForm
    edit_form = EditForm

@method_allowed('POST')
def upload(req, cluster_id):
    return upload_to_server(req, cluster_id, 'zato.security.tls.ca-cert.upload', 'Could not upload the CA certificate, e:`{}`')

class Delete(_Delete):
    url_name = 'security-tls-ca-cert-delete'
    error_message = 'Could not delete the CA cert'
    service_name = 'zato.security.tls.ca-cert.delete'
