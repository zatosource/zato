# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Django
from django.http import HttpResponse, HttpResponseServerError

# Zato
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.email.imap import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, id_only_service, \
     Index as _Index, method_allowed
from zato.common.api import EMAIL
from zato.common.odb.model import IMAP

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'email-imap'
    template = 'zato/email/imap.html'
    service_name = 'zato.email.imap.get-list'
    output_class = IMAP
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id',
        output_required = 'id', 'name', 'is_active', 'host', 'port', 'timeout', 'username', 'debug_level', 'mode', \
             'get_criteria', 'server_type', 'server_type_human'
        output_optional = 'username', 'tenant_id', 'client_id', 'search_criteria', 'filter_criteria'
        output_repeated = True

    def handle(self):
        return {
            'default_debug_level': EMAIL.DEFAULT.IMAP_DEBUG_LEVEL,
            'default_get_criteria': EMAIL.DEFAULT.GET_CRITERIA,
            'default_filter_criteria': EMAIL.DEFAULT.FILTER_CRITERIA,
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'change_password_form': ChangePasswordForm()
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = 'name', 'is_active', 'host', 'port', 'timeout', 'username', 'debug_level', 'mode', 'get_criteria', \
            'server_type', 'tenant_id', 'client_id', 'search_criteria', 'filter_criteria'
        output_required = 'id', 'name'

    def success_message(self, item):
        return 'Successfully {} IMAP connection `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'email-imap-create'
    service_name = 'zato.email.imap.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'email-imap-edit'
    form_prefix = 'edit-'
    service_name = 'zato.email.imap.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'email-imap-delete'
    error_message = 'Could not delete the IMAP connection'
    service_name = 'zato.email.imap.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def ping(req, id, cluster_id):
    ret = id_only_service(req, 'zato.email.imap.ping', id, 'IMAP ping error: {}')
    if isinstance(ret, HttpResponseServerError):
        return ret
    return HttpResponse(ret.data.info)

# ################################################################################################################################

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.email.imap.change-password')

# ################################################################################################################################
