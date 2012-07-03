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

# anyjson
from anyjson import dumps

# Django
from django.template import RequestContext
from django.shortcuts import render_to_response, HttpResponse

# Zato
from zato.admin.web.views import meth_allowed
from zato.admin.web.forms.kvdb.data_dict.dictionary import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index

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
    return HttpResponse()
