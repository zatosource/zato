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
from django.shortcuts import render_to_response

# lxml
from lxml import etree
from lxml.objectify import Element

# ConfigObj
from validate import is_boolean

# Zato
from zato.admin.web import invoke_admin_service
from zato.admin.web.forms import ChooseClusterForm
from zato.admin.web.forms.security.tech_account import CreateTechnicalAccountForm
from zato.admin.web.views import meth_allowed
from zato.common.odb.model import Cluster, TechnicalAccount
from zato.common import zato_namespace, zato_path, ZatoException, ZATO_NOT_GIVEN
from zato.common.util import TRACE1, to_form

logger = logging.getLogger(__name__)

@meth_allowed('GET')
def index(req):
    zato_clusters = req.odb.query(Cluster).order_by('name').all()
    choose_cluster_form = ChooseClusterForm(zato_clusters, req.GET)
    cluster_id = req.GET.get('cluster')
    accounts = []
    
    create_form = CreateTechnicalAccountForm()

    if cluster_id and req.method == 'GET':
        
        cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()
        
        zato_message = Element('{%s}zato_message' % zato_namespace)
        zato_message.cluster = Element('cluster')
        zato_message.cluster.id = cluster_id
        
        _, zato_message, soap_response  = invoke_admin_service(cluster,
                'zato:security.tech-account.get-list', zato_message)
        
        if zato_path('data.definition_list.definition').get_from(zato_message) is not None:
            
            for definition_elem in zato_message.data.definition_list.definition:
                
                id = definition_elem.id.text
                name = definition_elem.name.text
                is_active = is_boolean(definition_elem.is_active.text)
                
                account = TechnicalAccount(id, name, is_active=is_active)
                accounts.append(account)
                

    return_data = {'zato_clusters':zato_clusters,
        'cluster_id':cluster_id,
        'choose_cluster_form':choose_cluster_form,
        'accounts':accounts,
        'create_form':create_form
        }
    
    # TODO: Should really be done by a decorator.
    if logger.isEnabledFor(TRACE1):
        logger.log(TRACE1, 'Returning render_to_response [{0}]'.format(return_data))

    return render_to_response('zato/security/tech-account/index.html', return_data)

@meth_allowed('POST')
def create(req):
    
    cluster_id = req.POST.get('cluster_id')
    name = req.POST.get('name')
    is_active = req.POST.get('is_active', False)
    
    cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()
    
    zato_message = Element('{%s}zato_message' % zato_namespace)
    zato_message.data = Element('data')
    zato_message.data.cluster_id = cluster_id
    zato_message.data.name = name
    zato_message.data.is_active = is_active
    
    try:
        _, zato_message, soap_response = invoke_admin_service(cluster,
        'zato:security.tech-account.create', zato_message)
    except Exception, e:
        msg = "Could not create a technical account, e=[{e}]".format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    else:
        # 200 OK
        return HttpResponse()