# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms.security.tls.channel import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.odb.model import TLSChannelSecurity

logger = logging.getLogger(__name__)

class Index(_Index):
    output_class = TLSChannelSecurity
    url_name = 'security-tls-channel'
    template = 'zato/security/tls/channel.html'
    service_name = 'zato.security.tls.channel.get-list'
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'value', 'is_active')
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'value', 'is_active')
        output_required = ('id', 'name')

    def success_message(self, item):
        return 'Successfully {} the TLS channel security definition [{}]'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'security-tls-channel-create'
    service_name = 'zato.security.tls.channel.create'

class Edit(_CreateEdit):
    url_name = 'security-tls-channel-edit'
    form_prefix = 'edit-'
    service_name = 'zato.security.tls.channel.edit'

class Delete(_Delete):
    url_name = 'security-tls-channel-delete'
    error_message = 'Could not delete the TLS channel security definition'
    service_name = 'zato.security.tls.channel.delete'
