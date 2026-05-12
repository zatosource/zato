# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from json import dumps, loads
from traceback import format_exc

# Django
from django.http import HttpResponse

# Zato
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.security.oauth.outconn_client_credentials import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, \
     CreateEdit, Delete as _Delete, Index as _Index, method_allowed
# Bunch
from zato.common.ext.bunch import Bunch

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'security-oauth-outconn-client-credentials'
    template = 'zato/security/oauth/outconn-client-credentials.html'
    service_name = 'zato.security.oauth.get-list'
    output_class = Bunch
    paginate = True

    input_required = 'cluster_id',
    output_required = 'id', 'name', 'is_active', 'username', 'auth_server_url', 'scopes', \
        'client_id_field', 'client_secret_field', 'grant_type', 'extra_fields', 'data_format', \
        'static_header', 'static_value', 'static_prefix'
    output_repeated = True

    def handle(self):
        return {
            'show_search_form': True,
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'change_password_form': ChangePasswordForm(),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name', 'is_active', 'username', 'auth_server_url', 'scopes', \
        'client_id_field', 'client_secret_field', 'grant_type', 'extra_fields', 'data_format', \
        'static_header', 'static_value', 'static_prefix'
    output_required = 'id', 'name'

    def success_message(self, item):
        return 'Bearer token definition `{}` {} successfully'.format(item.name, self.verb)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'security-oauth-outconn-client-credentials-create'
    service_name = 'zato.security.oauth.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'security-oauth-outconn-client-credentials-edit'
    form_prefix = 'edit-'
    service_name = 'zato.security.oauth.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'security-oauth-outconn-client-credentials-delete'
    error_message = 'Bearer token definition could not be deleted'
    service_name = 'zato.security.oauth.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def change_secret(req):
    return _change_password(req, 'zato.security.oauth.change-password', success_msg='Secret updated')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def get_token(req):

    logger.info('get_token: called, method=%s, content_type=%s, body_length=%d',
        req.method, req.content_type, len(req.body or b''))

    try:
        request_data = loads(req.body)
        logger.info('get_token: parsed request_data keys=%s', list(request_data.keys()))
    except Exception as e:
        logger.warning('get_token: failed to parse body: %s', e)
        request_data = {}

    security_id = request_data.get('id') or ''
    raw_params = request_data.get('raw_params')

    logger.info('get_token: security_id=%s, has_raw_params=%s', security_id, bool(raw_params))

    if not security_id and not raw_params:
        logger.warning('get_token: no id or raw_params provided')
        return HttpResponse(dumps({
            'is_success': False,
            'exception_message': 'Either a definition ID or raw parameters are required',
            'info': 'No ID or parameters were provided in the request.',
        }), content_type='application/json')

    try:
        invoke_data = {
            'func_name': 'get_bearer_token',
            'security_id': security_id,
        }

        if raw_params:
            invoke_data['raw_params_json'] = dumps(raw_params)
            logger.info('get_token: using raw_params, auth_server_url=%s', raw_params.get('auth_server_url', ''))

        logger.info('get_token: invoking zato.server.invoker')
        response = req.zato.client.invoke('zato.server.invoker', invoke_data)

        response_data = response.data
        logger.info('get_token: response.data type=%s', type(response_data).__name__)

        if isinstance(response_data, str):
            logger.info('get_token: response.data (str) = %s', response_data[:300])
            response_data = loads(response_data)

        logger.info('get_token: is_ok=%s', response_data.get('is_ok'))

        if response_data.get('is_ok'):
            token = response_data['token']
            logger.info('get_token: success, token length=%d', len(token))
            return HttpResponse(dumps({
                'is_success': True,
                'token': token,
            }), content_type='application/json')
        else:
            error_msg = response_data.get('error', 'Error while obtaining token')
            status_code = response_data.get('status_code', 0)
            response_body = response_data.get('response_body', '')
            response_content_type = response_data.get('response_content_type', '')
            logger.warning('get_token: error: %s', error_msg)
            return HttpResponse(dumps({
                'is_success': False,
                'exception_message': 'Error while obtaining token',
                'status_code': status_code,
                'info': response_body or error_msg,
                'response_content_type': response_content_type,
            }), content_type='application/json')

    except Exception as e:
        tb = format_exc()
        logger.error('get_token: exception: %s', tb)
        return HttpResponse(dumps({
            'is_success': False,
            'exception_message': 'Error while obtaining token',
            'info': str(e),
            'response_content_type': 'text/plain',
        }), content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################
