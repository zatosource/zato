# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Django
from django.http import HttpResponse, HttpResponseServerError

# Zato
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.outgoing.odoo import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, id_only_service, \
     Index as _Index, method_allowed
from zato.common.api import ODOO
from zato.common.odb.model import OutgoingOdoo

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'out-odoo'
    template = 'zato/outgoing/odoo.html'
    service_name = 'zato.outgoing.odoo.get-list'
    output_class = OutgoingOdoo
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'host', 'port', 'user', 'database', 'protocol', 'pool_size')
        output_repeated = True

    def handle(self):

        for item in self.items:
            for protocol in ODOO.PROTOCOL():
                if item.protocol == protocol.id:
                    item.protocol_name = protocol.name

        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'change_password_form': ChangePasswordForm(),
            'default_port': ODOO.DEFAULT.PORT,
            'default_pool_size': ODOO.DEFAULT.POOL_SIZE,
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_active', 'host', 'port', 'user', 'database', 'protocol', 'pool_size')
        output_required = ('id', 'name')

    def success_message(self, item):
        return 'Successfully {} the outgoing Odoo connection [{}]'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'out-odoo-create'
    service_name = 'zato.outgoing.odoo.create'

class Edit(_CreateEdit):
    url_name = 'out-odoo-edit'
    form_prefix = 'edit-'
    service_name = 'zato.outgoing.odoo.edit'

class Delete(_Delete):
    url_name = 'out-odoo-delete'
    error_message = 'Could not delete the outgoing Odoo connection'
    service_name = 'zato.outgoing.odoo.delete'

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.outgoing.odoo.change-password')

@method_allowed('POST')
def ping(req, id, cluster_id):
    ret = id_only_service(req, 'zato.outgoing.odoo.ping', id, 'Could not ping the Odoo connection, e:`{}`')
    if isinstance(ret, HttpResponseServerError):
        return ret
    return HttpResponse(ret.data.info)
