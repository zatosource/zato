# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse

# anyjson
from anyjson import dumps

# Zato
from zato.admin.web.forms import SearchForm
from zato.admin.web.forms.kvdb import RemoteCommandForm
from zato.admin.web.views import method_allowed
from zato.common import ZatoException

@method_allowed('GET')
def remote_command(req):

    return_data = {'form':RemoteCommandForm(),
                   'cluster':req.zato.get('cluster'),
                   'search_form':SearchForm(req.zato.clusters, req.GET),
                   'zato_clusters':req.zato.clusters,
                   'cluster_id':req.zato.cluster_id,
                   }

    return TemplateResponse(req, 'zato/kvdb/remote-command.html', return_data)

@method_allowed('POST')
def remote_command_execute(req):
    """ Executes a command against the key/value DB.
    """
    try:
        response = req.zato.client.invoke('zato.kvdb.remote-command.execute', {'command': req.POST['command']})
        if response.has_data:
            return HttpResponse(dumps({'message': dumps(response.data.result)}), content_type='application/javascript')
        else:
            raise ZatoException(msg=response.details)
    except Exception:
        return HttpResponseServerError(format_exc())
