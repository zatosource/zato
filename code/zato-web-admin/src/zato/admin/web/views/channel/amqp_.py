# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError

# Zato
from zato.admin.web.forms.channel.amqp_ import CreateForm, EditForm
from zato.admin.web.views import Delete as _Delete, Index as _Index, method_allowed
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

def _get_edit_create_message(params:'any_', subtype:'str', prefix:'str'='') -> 'stranydict':
    """ Creates a base dictionary which can be used by both 'edit' and 'create' actions.
    """
    return {
        'id': params.get('id'),
        'cluster_id': params['cluster_id'],
        'name': params[prefix + 'name'],
        'is_active': bool(params.get(prefix + 'is_active')),
        'queue': params[prefix + 'queue'],
        'address': params[prefix + 'address'],
        'username': params.get(prefix + 'username'),
        'password': params.get(prefix + 'password'),
        'consumer_tag_prefix': params[prefix + 'consumer_tag_prefix'],
        'service': params[prefix + 'service'],
        'pool_size': params.get(prefix + 'pool_size'),
        'ack_mode': params.get(prefix + 'ack_mode'),
        'prefetch_count': params.get(prefix + 'prefetch_count'),
        'data_format': params.get(prefix + 'data_format'),
        'subtype': subtype,
    }

def _edit_create_response(client:'any_', verb:'str', id:'any_', name:'str', label:'str') -> 'HttpResponse':
    return_data = {'id': id, 'message': 'Successfully {} {} channel `{}`'.format(verb, label, name)}
    return HttpResponse(dumps(return_data), content_type='application/javascript')

class Index(_Index):
    """ One index view serves every subtype of the AMQP implementation - urls.py mounts it once per subtype,
    e.g. as the AMQP page and as the Azure Service Bus page.
    """
    method_allowed = 'GET'
    template = 'zato/channel/amqp.html'
    service_name = 'zato.channel.amqp.get-list'
    output_class = Bunch
    paginate = True

    input_required = 'cluster_id',
    output_required = 'id', 'name', 'is_active', 'address', 'username', 'password', 'queue', 'consumer_tag_prefix', 'service_name', \
        'pool_size', 'ack_mode', 'prefetch_count', 'data_format'
    output_repeated = True

    def __init__(self, subtype:'str') -> 'None':
        super().__init__()
        self.subtype_key = subtype
        self.subtype = AMQP_Subtype[subtype]
        self.url_name = self.subtype['url_prefix_channel']

    def get_initial_input(self):
        # The get-list service narrows the results down to this page's subtype
        return {'subtype': self.subtype_key}

    def handle(self):
        create_form = CreateForm(req=self.req)
        edit_form = EditForm(prefix='edit', req=self.req)

        # The url names the template's forms point to
        url_prefix = self.subtype['url_prefix_channel']

        return {
            'show_search_form': True,
            'create_form': create_form,
            'edit_form': edit_form,
            'subtype': self.subtype,
            'create_url': f'{url_prefix}-create',
            'edit_url': f'{url_prefix}-edit',
        }

@method_allowed('POST')
def create(req:'any_', subtype:'str') -> 'HttpResponse':
    label = AMQP_Subtype[subtype]['label']
    try:
        response = req.zato.client.invoke('zato.channel.amqp.create', _get_edit_create_message(req.POST, subtype))
        return _edit_create_response(req.zato.client, 'created', response.data.id, req.POST['name'], label)
    except Exception:
        msg = 'Could not create {} channel, e:`{}`'.format(label, format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)


@method_allowed('POST')
def edit(req:'any_', subtype:'str') -> 'HttpResponse':
    label = AMQP_Subtype[subtype]['label']
    try:
        req.zato.client.invoke('zato.channel.amqp.edit', _get_edit_create_message(req.POST, subtype, 'edit-'))
        return _edit_create_response(req.zato.client, 'updated', req.POST['id'], req.POST['edit-name'], label)

    except Exception:
        msg = 'Could not update {} channel, e:`{}`'.format(label, format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

class Delete(_Delete):
    service_name = 'zato.channel.amqp.delete'

    def __init__(self, subtype:'str') -> 'None':
        super().__init__()
        self.subtype = AMQP_Subtype[subtype]
        self.url_name = '{}-delete'.format(self.subtype['url_prefix_channel'])
        self.error_message = 'Could not delete {} channel'.format(self.subtype['label'])
