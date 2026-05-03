# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from json import loads
from traceback import format_exc

# Django
from django.http import HttpResponseServerError, JsonResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.security.apikey import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common.json_internal import dumps

# Bunch
from bunch import Bunch

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'security-apikey'
    template = 'zato/security/apikey.html'
    service_name = 'zato.security.apikey.get-list'
    output_class = Bunch
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id',
        output_required = 'id', 'name', 'is_active', 'username'
        output_optional = 'header'
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
        input_required = 'name', 'is_active', 'username'
        output_required = 'id', 'name'

    def success_message(self, item):
        return 'Successfully {} API key `{}`'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'security-apikey-create'
    service_name = 'zato.security.apikey.create'

    def __call__(self, req, *args, **kwargs):
        response = super().__call__(req, *args, **kwargs)
        if response.status_code == 200:
            data = loads(response.content)
            password = req.POST.get('password', '')
            if password:
                req.zato.client.invoke('zato.security.apikey.change-password', {
                    'id': data['id'],
                    'password': password,
                })
        return response

class Edit(_CreateEdit):
    url_name = 'security-apikey-edit'
    form_prefix = 'edit-'
    service_name = 'zato.security.apikey.edit'

class Delete(_Delete):
    url_name = 'security-apikey-delete'
    error_message = 'Could not delete the API key'
    service_name = 'zato.security.apikey.delete'

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.security.apikey.change-password', success_msg='API key updated')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def rate_limiting(req, id): # type: ignore

    rules_response = req.zato.client.invoke('zato.security.apikey.rate-limiting.get', {
        'id': id,
    })

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'entity_id': id,
        'entity_name': req.GET.get('name', ''),
        'rules_json': dumps(rules_response.data.rate_limiting),
    }

    return TemplateResponse(req, 'zato/security/apikey-rate-limiting.html', return_data)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def rate_limiting_save(req, id): # type: ignore
    try:
        rules_json = req.POST['rules_json']
        response = req.zato.client.invoke('zato.security.apikey.rate-limiting.save', {
            'id': id,
            'rules_json': rules_json,
        })
        if response.ok:
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'status': 'error', 'message': response.details}, status=400)
    except Exception:
        msg = 'Rate limiting rules could not be saved, e:`{}`'.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def rate_limiting_clear_counters(req, id): # type: ignore
    try:
        rule_index = req.POST['rule_index']
        response = req.zato.client.invoke('zato.security.apikey.rate-limiting.clear-counters', {
            'id': id,
            'rule_index': rule_index,
        })
        if response.ok:
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'status': 'error', 'message': response.details}, status=400)
    except Exception:
        msg = 'Rate limiting counters could not be cleared, e:`{}`'.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

# ################################################################################################################################
# ################################################################################################################################
