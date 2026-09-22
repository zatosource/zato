# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Bunch
from zato.common.ext.bunch import Bunch

# Django
from django.http import HttpResponse, HttpResponseServerError

# Zato
from zato.admin.web.forms.on_prem_gateway import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, id_only_service, Index as _Index, method_allowed
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from django.http import HttpRequest
    from zato.common.typing_ import any_, strdict

    # Dummy assignments to satisfy type checkers
    HttpRequest = HttpRequest
    strdict = strdict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

_service_prefix = 'zato.on-prem-gateway.'

# ################################################################################################################################
# ################################################################################################################################

class _Status:
    """ The values reported in the Status column.
    """
    Connected = 'Connected'
    Offline = 'Enrolled, offline'
    Not_Enrolled = 'Not enrolled'
    Not_Active = 'Not active'

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'on-prem-gateway'
    template = 'zato/on-prem-gateway.html'
    service_name = _service_prefix + 'get-list'
    output_class = Bunch
    paginate = True

    input_required = ('cluster_id',)
    output_required = 'id', 'name', 'is_active', 'is_key_reset_required'
    output_optional = 'hosts', 'host_count', 'is_connected', 'has_key', 'connected_since', 'remote_address', \
        'gateway_version', 'platform'
    output_repeated = True

    def on_before_append_item(self, item:'Bunch') -> 'Bunch':

        # The current state of the gateway ..
        if not item.is_active:
            status = _Status.Not_Active
        elif item.is_connected:
            status = _Status.Connected
        elif item.has_key:
            status = _Status.Offline
        else:
            status = _Status.Not_Enrolled

        # .. and its addresses, which the edit form reads from a hidden cell. A gateway
        # .. configured with no addresses does not carry the key at all.
        if 'hosts' in item:
            hosts = item.hosts
        else:
            hosts = []

        item.status = status
        item.hosts = '\n'.join(hosts)

        return item

    def handle(self) -> 'strdict':
        return {
            'show_search_form': True,
            'create_form': CreateForm(req=self.req),
            'edit_form': EditForm(prefix='edit', req=self.req),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name', 'is_active', 'is_key_reset_required'
    input_optional = ('hosts',)
    output_required = 'id', 'name'

    def pre_process_item(self, name:'str', value:'any_') -> 'any_':

        # The form submits one address per line whereas the service expects a list
        if name == 'hosts':
            value = value.splitlines()

        return value

    def success_message(self, item:'any_') -> 'str':
        return f'Successfully {self.verb} on-premises gateway `{item.name}`'

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'on-prem-gateway-create'
    service_name = _service_prefix + 'create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'on-prem-gateway-edit'
    form_prefix = 'edit-'
    service_name = _service_prefix + 'edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'on-prem-gateway-delete'
    error_message = 'Could not delete the on-premises gateway'
    service_name = _service_prefix + 'delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def enrollment_token(req:'HttpRequest', id:'str', cluster_id:'str') -> 'any_':
    """ Issues a single-use enrollment token for one gateway.
    """
    initial = {'dashboard_host': req.get_host()}
    response = id_only_service(req, _service_prefix + 'get-enrollment-token', id,
        'Could not obtain an enrollment token, e:`{}`', initial)

    if isinstance(response, HttpResponseServerError):
        return response

    out = {
        'token': response.data.token,
        'expires_at': response.data.expires_at,
    }

    return HttpResponse(dumps(out), content_type='application/javascript')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def reset_key(req:'HttpRequest', id:'str', cluster_id:'str') -> 'any_':
    """ Revokes the key of a gateway, which requires the gateway to enroll again.
    """
    response = id_only_service(req, _service_prefix + 'reset-key', id, 'Could not reset the key, e:`{}`')

    if isinstance(response, HttpResponseServerError):
        return response

    out = {'message': 'Key reset, the gateway is required to enroll again'}

    return HttpResponse(dumps(out), content_type='application/javascript')

# ################################################################################################################################
# ################################################################################################################################
