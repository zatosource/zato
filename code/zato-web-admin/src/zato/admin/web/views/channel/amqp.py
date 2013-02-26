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

# anyjson
from anyjson import dumps

# Zato
from zato.admin.web.forms.channel.amqp import CreateForm, EditForm
from zato.admin.web.views import Delete as _Delete, get_definition_list, \
     Index as _Index, method_allowed
from zato.common.odb.model import ChannelAMQP
from zato.common import zato_path

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
        'service': params[prefix + 'service'],
        'data_format': params.get(prefix + 'data_format'),
    }

def _edit_create_response(cluster, verb, id, name, def_id):
    response = req.zato.client.invoke('zato.definition.amqp.get-by-id', {'id':def_id})
    return_data = {'id': id,
                   'message': 'Successfully {0} the AMQP channel [{1}]'.format(verb, name),
                   'def_name': response.name
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
            'def_name', 'def_id', 'service_name', 'data_format')
        output_repeated = True
    
    def handle(self):
        create_form = CreateForm()
        edit_form = EditForm(prefix='edit')
        
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
        return _edit_create_response(req.zato.cluster, 'created', response.id, 
            req.POST['name'], req.POST['def_id'])
    except Exception, e:
        msg = 'Could not create an AMQP channel, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

    
@method_allowed('POST')
def edit(req):
    try:
        req.zato.client.invoke('zato.channel.amqp.edit', _get_edit_create_message(req.POST, 'edit-'))
        return _edit_create_response(req.zato.cluster, 'updated', req.POST['id'], req.POST['edit-name'], req.POST['edit-def_id'])
        
    except Exception, e:
        msg = 'Could not update the AMQP channel, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    
class Delete(_Delete):
    url_name = 'channel-amqp-delete'
    error_message = 'Could not delete the AMQP channel'
    service_name = 'zato.channel.amqp.delete'
