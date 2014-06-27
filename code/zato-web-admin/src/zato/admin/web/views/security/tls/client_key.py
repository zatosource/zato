# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'security-tls-client-key'
    template = 'zato/security/tls/client-key.html'
    service_name = 'zato.security.tls.client-key.get-list'

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name')
        output_repeated = True

    def handle(self):
        pass

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name',)
        output_required = ('id', 'name')

    def success_message(self, item):
        return 'Successfully {0} the client key [{1}]'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'security-tls-client-key-create'
    service_name = 'zato.security.tls.client-key.create'

class Edit(_CreateEdit):
    url_name = 'security-tls-client-key-edit'
    form_prefix = 'edit-'
    service_name = 'zato.security.tls.client-key.edit'

class Delete(_Delete):
    url_name = 'security-tls-client-key-delete'
    error_message = 'Could not delete the client key'
    service_name = 'zato.security.tls.client-key.delete'
