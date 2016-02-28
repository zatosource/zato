# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError

# Zato
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.security.tech_account import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Index as _Index, method_allowed
from zato.common.odb.model import TechnicalAccount

logger = logging.getLogger(__name__)

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.security.tech-account.change-password')


@method_allowed('GET')
def get_by_id(req, id_, cluster_id):
    try:
        response = req.zato.client.invoke('zato.security.tech-account.get-by-id', {'id':id_})
    except Exception, e:
        msg = 'Could not fetch the technical account, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    else:
        tech_account = TechnicalAccount()
        tech_account.id = response.data.id
        tech_account.name = response.data.name
        tech_account.is_active = response.data.is_active

        return HttpResponse(tech_account.to_json(), content_type='application/javascript')

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'security-tech-account'
    template = 'zato/security/tech-account.html'

    service_name = 'zato.security.tech-account.get-list'
    output_class = TechnicalAccount

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active')
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'change_password_form': ChangePasswordForm()
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_active')
        output_required = ('id', 'name')

    def success_message(self, item):
        return 'Successfully {0} the technical account [{1}]'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'security-tech-account-create'
    service_name = 'zato.security.tech-account.create'

class Edit(_CreateEdit):
    url_name = 'security-tech-account-edit'
    form_prefix = 'edit-'
    service_name = 'zato.security.tech-account.edit'

@method_allowed('POST')
def delete(req, id, cluster_id):
    try:
        req.zato.client.invoke('zato.security.tech-account.delete', {'id': id})
    except Exception, e:
        msg = 'Could not delete the technical account, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    else:
        return HttpResponse()
