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
from django.template.response import TemplateResponse

# anyjson
from anyjson import dumps

# Zato
from zato.admin.web import invoke_admin_service
from zato.admin.web.forms import ChooseClusterForm
from zato.admin.web.forms.kvdb import RemoteCommandForm
from zato.admin.web.views import meth_allowed

logger = logging.getLogger(__name__)

@meth_allowed('GET')
def remote_command(req):
    
    return_data = {'form':RemoteCommandForm(), 
                   'cluster':req.zato.get('cluster'),
                   'choose_cluster_form':ChooseClusterForm(req.zato.clusters, req.GET),
                   'zato_clusters':req.zato.clusters,
                   'cluster_id':req.zato.cluster_id,
                   }
    
    return TemplateResponse(req, 'zato/kvdb/remote-command.html', return_data)

@meth_allowed('POST')
def remote_command_execute(req):
    """ Executes a command against the key/value DB.
    """
    try:
        zato_message, soap_response  = invoke_admin_service(req.zato.cluster, 'zato.kvdb.remote-command.execute', {'command': req.POST['command']})
        return_data = {'message': zato_message.item.result.text}
        
        return HttpResponse(dumps(return_data), mimetype='application/javascript')
    except Exception, e:
        return HttpResponseServerError(format_exc(e))
