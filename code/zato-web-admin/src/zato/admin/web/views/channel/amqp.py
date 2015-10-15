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

# anyjson
from anyjson import dumps

# Zato
from zato.admin.web.forms.channel.amqp import CreateForm, EditForm
from zato.admin.web.views import Delete as _Delete, get_definition_list, \
     Index as _Index, method_allowed
from zato.common.odb.model import ChannelAMQP

logger = logging.getLogger(__name__)

def _get_edit_create_message(params, prefix=''):
    """ Creates a base dictionary which can be used by both 'edit' and 'create' actions.
    """
    return {
        'id': params.get('id'),
        'cluster_id': params['cluster_id'],
        'name': params[prefix + 'name'],
        'is_active': bool(params.get(prefix + 'is_active')),
        'def_id': params[prefix + 'def_id'],
        'queue': params[prefix + 'queue'],
        'consumer_tag_prefix': params[prefix + 'consumer_tag_prefix'],
        'is_sync': bool(params.get(prefix + 'is_sync')),
        'service': params[prefix + 'service'],
        'data_format': params.get(prefix + 'data_format'),
    }

def _edit_create_response(client, verb, id, name, def_id, cluster_id):
    response = client.invoke('zato.definition.amqp.get-by-id', {'id':def_id, 'cluster_id':cluster_id})
    return_data = {'id': id,
                   'message': 'Successfully {0} the AMQP channel [{1}]'.format(verb, name),
                   'def_name': response.data.name
                }
    return HttpResponse(dumps(return_data), mimetype='application/javascript')

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'channel-amqp'
    template = 'zato/channel/amqp.html'
    service_name = 'zato.channel.amqp.get-list'
    output_class = ChannelAMQP
    
    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'queue', 'consumer_tag_prefix', 
            'is_sync', 'def_name', 'def_id', 'service_name', 'data_format')
        output_repeated = True
    
    def handle(self):
        create_form = CreateForm(req=self.req)
        edit_form = EditForm(prefix='edit', req=self.req)
        
        if self.req.zato.cluster_id:
            def_ids = get_definition_list(self.req.zato.client, self.req.zato.cluster, 'amqp')
            create_form.set_def_id(def_ids)
            edit_form.set_def_id(def_ids)
        
        return {
            'create_form': create_form,
            'edit_form': edit_form,
        }

@method_allowed('POST')
def create(req):
    try:
        response = req.zato.client.invoke('zato.channel.amqp.create', _get_edit_create_message(req.POST))
        return _edit_create_response(req.zato.client, 'created', response.data.id, 
            req.POST['name'], req.POST['def_id'], req.POST['cluster_id'])
    except Exception, e:
        msg = 'Could not create an AMQP channel, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

    
@method_allowed('POST')
def edit(req):
    try:
        req.zato.client.invoke('zato.channel.amqp.edit', _get_edit_create_message(req.POST, 'edit-'))
        return _edit_create_response(req.zato.client, 'updated', req.POST['id'], req.POST['edit-name'], 
            req.POST['edit-def_id'], req.POST['cluster_id'])
        
    except Exception, e:
        msg = 'Could not update the AMQP channel, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    
class Delete(_Delete):
    url_name = 'channel-amqp-delete'
    error_message = 'Could not delete the AMQP channel'
    service_name = 'zato.channel.amqp.delete'
