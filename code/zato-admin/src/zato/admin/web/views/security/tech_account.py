# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError

# Validate
from validate import is_boolean

# Zato
from zato.admin.settings import TECH_ACCOUNT_NAME
from zato.admin.web import invoke_admin_service
from zato.admin.web.views import change_password as _change_password
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.security.tech_account import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, meth_allowed
from zato.common.odb.model import TechnicalAccount

logger = logging.getLogger(__name__)
    
@meth_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.security.tech-account.change-password')
    
    
@meth_allowed('GET')
def get_by_id(req, tech_account_id, cluster_id):
    try:
        zato_message, soap_response = invoke_admin_service(req.zato.cluster, 'zato.security.tech-account.get-by-id', {'tech_account_id': tech_account_id})
    except Exception, e:
        msg = 'Could not fetch the technical account, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    else:
        tech_account = TechnicalAccount()
        tech_account_elem = zato_message.item
        
        tech_account.id = tech_account_elem.id.text
        tech_account.name = tech_account_elem.name.text
        tech_account.is_active = is_boolean(tech_account_elem.is_active.text)

        return HttpResponse(tech_account.to_json(), mimetype='application/javascript')
    
class Index(_Index):
    meth_allowed = 'GET'
    url_name = 'security-tech-account'
    template = 'zato/security/tech-account.html'
    
    soap_action = 'zato.security.tech-account.get-list'
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
    meth_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_active')
        output_required = ('id', 'name')
        
    def success_message(self, item):
        return 'Successfully {0} the technical account [{1}]'.format(self.verb, item.name.text)

class Create(_CreateEdit):
    url_name = 'security-tech-account-create'
    soap_action = 'zato.security.tech-account.create'

class Edit(_CreateEdit):
    url_name = 'security-tech-account-edit'
    form_prefix = 'edit-'
    soap_action = 'zato.security.tech-account.edit'

@meth_allowed('POST')
def delete(req, id, cluster_id):
    try:
        invoke_admin_service(req.zato.cluster, 'zato.security.tech-account.delete', {'id': id, 'zato_admin_tech_account_name':TECH_ACCOUNT_NAME})
    except Exception, e:
        msg = 'Could not delete the technical account, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    else:
        return HttpResponse()
