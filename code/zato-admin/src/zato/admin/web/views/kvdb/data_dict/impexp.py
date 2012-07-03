# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at gefira.pl>

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
from bz2 import compress
from datetime import datetime
from json import dumps

# Django
from django.template import RequestContext
from django.shortcuts import render_to_response, HttpResponse

# Zato
from zato.admin.web import invoke_admin_service
from zato.admin.web.views import meth_allowed
from zato.admin.web.forms.kvdb.data_dict.dictionary import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common import zato_path
from zato.common.util import current_host, translation_name

logger = logging.getLogger(__name__)

@meth_allowed('GET')
def index(req):
    
    return_data = {
        'zato_clusters':req.zato.clusters,
        'cluster_id':req.zato.cluster_id,
        'choose_cluster_form':req.zato.choose_cluster_form,
    }
    
    return render_to_response('zato/kvdb/data_dict/impexp.html', return_data, context_instance=RequestContext(req))

@meth_allowed('POST')
def import_(req, cluster_id):
    return HttpResponse(dumps({'success': True}))

@meth_allowed('GET')
def export(req, cluster_id):
    
    def _get_last_id(service):
        zato_message, _  = invoke_admin_service(req.zato.cluster, service, {})
        if zato_path('response.item').get_from(zato_message) is not None:
            return zato_message.response.item.value.text
        
    def _get_last_dict_id():
        return _get_last_id('zato:kvdb.data-dict.dictionary.get-last-id')
    
    def _get_last_translation_id():
        return _get_last_id('zato:kvdb.data-dict.translation.get-last-id')

    def _get_dict_list():
        zato_message, _  = invoke_admin_service(req.zato.cluster, 'zato:kvdb.data-dict.dictionary.get-list', {})
        if zato_path('response.item_list.item').get_from(zato_message) is not None:
            for item in zato_message.response.item_list.item:
                yield item.id.text, item.system.text, item.key.text, item.value.text
    
    def _get_translation_list():
        zato_message, _  = invoke_admin_service(req.zato.cluster, 'zato:kvdb.data-dict.translation.get-list', {})
        if zato_path('response.item_list.item').get_from(zato_message) is not None:
            for item in zato_message.response.item_list.item:
                yield item.id.text, item.system1.text, item.key1.text, item.value1.text, item.system2.text, \
                      item.key2.text, item.value2.text, item.id1.text, item.id2.text
    
    return_data = {'meta': {'current_host':current_host(), 'timestamp_utc':datetime.utcnow().isoformat(), 'user':req.user.username}}
    return_data['data'] = {'dict_list':[], 'translation_list':[]}
    
    return_data['data']['last_dict_id'] = _get_last_dict_id()
    return_data['data']['last_translation_id'] = _get_last_translation_id()
    
    for id, system, key, value in _get_dict_list():
        return_data['data']['dict_list'].append({'id':id, 'system':system, 'key':key, 'value':value})
        
    for id, system1, key1, value1, system2, key2, value2, id1, id2 in _get_translation_list():
        return_data['data']['translation_list'].append(
            {translation_name(system1, key1, value1, system2, key2): {'id':id, 'value2':value2, 'id1':id1, 'id2':id2}})
    
    response = HttpResponse(compress(dumps(return_data, indent=4)), mimetype='application/x-bzip2')
    response['Content-Disposition'] = 'attachment; filename={}'.format('zato-data-dict-export.json.bz2')

    return response
