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
from datetime import datetime

# anyjson
from anyjson import dumps

# Django
from django.template import RequestContext
from django.shortcuts import render_to_response, HttpResponse

# Zato
from zato.admin.web import invoke_admin_service
from zato.admin.web.views import meth_allowed
from zato.admin.web.forms.kvdb.data_dict.dictionary import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.util import current_host

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
    # 'zato:kvdb.data-dict.dictionary.get-next-id':'zato.server.service.internal.kvdb.data_dict.dictionary.GetNextID',
    # 'zato:kvdb.data-dict.dictionary.get-list':'zato.server.service.internal.kvdb.data_dict.dictionary.GetList',
    # # 'zato:kvdb.data-dict.translation.get-next-id':'zato.server.service.internal.kvdb.data_dict.translation.GetNextID',
    # 'zato:kvdb.data-dict.translation.get-list':'zato.server.service.internal.kvdb.data_dict.translation.GetList',
    #zato_message, _  = invoke_admin_service(req.zato.cluster, 'zato:kvdb.data-dict.impexp.export', {})
    
    return_data = {'meta': {'current_host':current_host(), 'timestamp_utc':datetime.utcnow().isoformat(), 'user':req.user.username}}
    
    response = HttpResponse(dumps(return_data), mimetype='application/javascript') # TODO: /json
    response['Content-Disposition'] = 'attachment; filename={}'.format('zato-data-dict-export.json')

    return response
