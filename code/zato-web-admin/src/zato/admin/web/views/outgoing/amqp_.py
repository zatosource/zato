# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse

# Zato
from zato.admin.settings import delivery_friendly_name
from zato.admin.web.forms.outgoing.amqp_ import CreateForm, EditForm
from zato.admin.web.views import Delete as _Delete, Index as _Index, invoke_action_handler, method_allowed
from zato.common.api import AMQP_Subtype
from zato.common.json_internal import dumps
# Bunch
from zato.common.ext.bunch import Bunch

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The ODB stores delivery modes as AMQP integers, the forms use these string names
_delivery_mode_by_id = {
    1: 'non_persistent',
    2: 'persistent',
}

# ################################################################################################################################
# ################################################################################################################################

def _get_edit_create_message(params:'any_', subtype:'str', prefix:'str'='') -> 'stranydict':
    """ Creates a base dictionary which can be used by both 'edit' and 'create' actions.
    """
    return {
        'id': params.get('id'),
        'cluster_id': params['cluster_id'],
        'name': params[prefix + 'name'],
        'is_active': bool(params.get(prefix + 'is_active')),
        'address': params.get(prefix + 'address'),
        'username': params.get(prefix + 'username'),
        'password': params.get(prefix + 'password'),
        'delivery_mode': params[prefix + 'delivery_mode'],
        'priority': params[prefix + 'priority'],
        'content_type': params.get(prefix + 'content_type'),
        'content_encoding': params.get(prefix + 'content_encoding'),
        'expiration': params.get(prefix + 'expiration'),
        'pool_size': params.get(prefix + 'pool_size'),
        'user_id': params.get(prefix + 'user_id'),
        'app_id': params.get(prefix + 'app_id'),
        'subtype': subtype,
    }

# ################################################################################################################################
# ################################################################################################################################

def _edit_create_response(verb:'str', id:'any_', name:'str', delivery_mode_text:'str', label:'str') -> 'HttpResponse':
    return_data = {'id': id,
                   'message': 'Successfully {} outgoing {} connection `{}`'.format(verb, label, name),
                   'delivery_mode_text': delivery_mode_text,
                }
    return HttpResponse(dumps(return_data), content_type='application/javascript')

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    """ One index view serves every subtype of the AMQP implementation - urls.py mounts it once per subtype,
    e.g. as the AMQP page and as the Azure Service Bus page.
    """
    method_allowed = 'GET'
    template = 'zato/outgoing/amqp.html'
    service_name = 'zato.outgoing.amqp.get-list'
    output_class = Bunch
    paginate = True

    input_required = 'cluster_id',
    output_required = ('id', 'name', 'address', 'username', 'password', 'is_active', 'delivery_mode', 'priority',
        'content_type', 'content_encoding', 'expiration', 'pool_size', 'user_id', 'app_id', 'delivery_mode_text')
    output_repeated = True

    def __init__(self, subtype:'str') -> 'None':
        super().__init__()
        self.subtype_key = subtype
        self.subtype = AMQP_Subtype[subtype]
        self.url_name = self.subtype['url_prefix_outgoing']

    def get_initial_input(self):
        # The get-list service narrows the results down to this page's subtype
        return {'subtype': self.subtype_key}

    def handle(self):
        create_form = CreateForm()
        edit_form = EditForm(prefix='edit')

        for item in self.items:

            # The get-list service returns the AMQP integer, map it back to the string name first
            item.delivery_mode = _delivery_mode_by_id[item.delivery_mode]
            item.delivery_mode_text = delivery_friendly_name[item.delivery_mode]

        # The url names the template's forms and links point to
        url_prefix = self.subtype['url_prefix_outgoing']

        return {
            'show_search_form': True,
            'create_form': create_form,
            'edit_form': edit_form,
            'subtype': self.subtype,
            'path_segment': self.subtype_key,
            'create_url': f'{url_prefix}-create',
            'edit_url': f'{url_prefix}-edit',
            'invoke_url': f'{url_prefix}-invoke',
        }

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def create(req:'any_', subtype:'str') -> 'HttpResponse':
    label = AMQP_Subtype[subtype]['label']
    try:
        request = _get_edit_create_message(req.POST, subtype)
        response = req.zato.client.invoke('zato.outgoing.amqp.create', request)
        delivery_mode_text = delivery_friendly_name[req.POST['delivery_mode']]

        return _edit_create_response('created', response.data.id, req.POST['name'], delivery_mode_text, label)
    except Exception:
        msg = 'Outgoing {} connection could not be created, e:`{}`'.format(label, format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def edit(req:'any_', subtype:'str') -> 'HttpResponse':
    label = AMQP_Subtype[subtype]['label']
    try:
        request = _get_edit_create_message(req.POST, subtype, 'edit-')
        req.zato.client.invoke('zato.outgoing.amqp.edit', request)
        delivery_mode_text = delivery_friendly_name[req.POST['edit-delivery_mode']]

        return _edit_create_response('updated', req.POST['id'], req.POST['edit-name'], delivery_mode_text, label)
    except Exception:
        msg = 'Outgoing {} connection could not be updated, e:`{}`'.format(label, format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    service_name = 'zato.outgoing.amqp.delete'

    def __init__(self, subtype:'str') -> 'None':
        super().__init__()
        self.subtype = AMQP_Subtype[subtype]
        self.url_name = '{}-delete'.format(self.subtype['url_prefix_outgoing'])
        self.error_message = 'Could not delete outgoing {} connection'.format(self.subtype['label'])

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def invoke(req:'any_', conn_id:'str', conn_name:'str', conn_slug:'str', subtype:'str') -> 'TemplateResponse':

    subtype_config = AMQP_Subtype[subtype]
    url_prefix = subtype_config['url_prefix_outgoing']

    return_data = {
        'conn_id': conn_id,
        'conn_name': conn_name,
        'cluster_id': req.zato.cluster_id,
        'subtype': subtype_config,
        'index_url': url_prefix,
        'invoke_action_url': f'{url_prefix}-invoke-action',
    }

    return TemplateResponse(req, 'zato/outgoing/amqp-invoke.html', return_data)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def invoke_action(req:'any_', conn_name:'str') -> 'any_':
    out = invoke_action_handler(req, 'zato.outgoing.amqp.publish', ('conn_name', 'request_data', 'exchange', 'routing_key'))
    return out

# ################################################################################################################################
# ################################################################################################################################
