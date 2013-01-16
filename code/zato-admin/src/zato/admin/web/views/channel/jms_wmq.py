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
from zato.admin.web import invoke_admin_service
from zato.admin.web.forms.channel.jms_wmq import CreateForm, EditForm
from zato.admin.web.views import Delete as _Delete, Index as _Index, meth_allowed
from zato.common.odb.model import ChannelWMQ
from zato.common import zato_path

logger = logging.getLogger(__name__)

def _get_def_ids(cluster):
    out = {}
    zato_message, soap_response  = invoke_admin_service(cluster, 'zato.definition.jms_wmq.get-list', {'cluster_id':cluster.id})
    
    if zato_path('item_list.item').get_from(zato_message) is not None:
        for definition_elem in zato_message.item_list.item:
            id = definition_elem.id.text
            name = definition_elem.name.text
            out[id] = name
        
    return out
        
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
        'service': params[prefix + 'service'],
        'data_format': params.get(prefix + 'data_format'),
    }

def _edit_create_response(cluster, verb, id, name, cluster_id, def_id):
    zato_message, soap_response  = invoke_admin_service(cluster, 'zato.definition.jms_wmq.get-by-id', {'id':def_id, 'cluster_id': cluster_id})
    return_data = {'id': id,
                   'message': 'Successfully {0} the JMS WebSphere MQ channel [{1}]'.format(verb, name),
                   'def_name': zato_message.item.name.text
                }
    
    return HttpResponse(dumps(return_data), mimetype='application/javascript')

class Index(_Index):
    meth_allowed = 'GET'
    url_name = 'channel-jms-wmq'
    template = 'zato/channel/jms_wmq.html'
    
    soap_action = 'zato.channel.jms_wmq.get-list'
    output_class = ChannelWMQ
    
    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'queue', 'def_name', 'def_id', 'service_name', 'data_format')
        output_repeated = True
    
    def handle(self):
        create_form = CreateForm()
        edit_form = EditForm(prefix='edit')
        
        if self.req.zato.cluster_id:
            def_ids = _get_def_ids(self.req.zato.cluster)
            create_form.set_def_id(def_ids)
            edit_form.set_def_id(def_ids)
        
        return {
            'create_form': create_form,
            'edit_form': edit_form,
        }

@meth_allowed('POST')
def create(req):
    try:
        zato_message, soap_response = invoke_admin_service(req.zato.cluster, 'zato.channel.jms_wmq.create', _get_edit_create_message(req.POST))
        return _edit_create_response(req.zato.cluster, 'created', zato_message.item.id.text, req.POST['name'], req.POST['cluster_id'], req.POST['def_id'])
    except Exception, e:
        msg = 'Could not create a JMS WebSphere MQ channel, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

    
@meth_allowed('POST')
def edit(req):
    try:
        zato_message, soap_response = invoke_admin_service(req.zato.cluster, 'zato.channel.jms_wmq.edit', _get_edit_create_message(req.POST, 'edit-'))
        return _edit_create_response(req.zato.cluster, 'updated', req.POST['id'], req.POST['edit-name'], req.POST['cluster_id'], req.POST['edit-def_id'])
    except Exception, e:
        msg = 'Could not update the JMS WebSphere MQ channel, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    
class Delete(_Delete):
    url_name = 'channel-jms-wmq-delete'
    error_message = 'Could not delete the JMS WebSphere MQ channel'
    soap_action = 'zato.channel.jms_wmq.delete'
