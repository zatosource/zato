# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

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

# Django
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

# lxml
from lxml import etree
from lxml.objectify import Element

# Zato
from zato.admin.web import invoke_admin_service
from zato.admin.web.forms import ChooseClusterForm
from zato.admin.web.server_model import Service
from zato.admin.web.views import meth_allowed
from zato.common import zato_namespace, zato_path, ZatoException, ZATO_NOT_GIVEN
from zato.common.odb.model import Server
from zato.common.odb.model import Cluster
from zato.common.util import TRACE1

logger = logging.getLogger(__name__)

@meth_allowed('GET', 'POST')
def soap(req):

    zato_clusters = req.odb.query(Cluster).order_by('name').all()
    choose_cluster_form = ChooseClusterForm(zato_clusters, req.GET)
    cluster_id = req.GET.get('cluster')
    definitions = []

    if cluster_id and req.method == 'GET':
        cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()

        zato_message = Element('{%s}zato_message' % zato_namespace)
        zato_message.cluster = Element('cluster')
        zato_message.cluster.id = cluster_id

        _ignored, zato_message, soap_response  = invoke_admin_service(cluster,
                "zato:channel.soap.get-list", zato_message)

        '''zato_message = Element("{%s}zato_message" % zato_namespace)

        _ignored, zato_message, soap_response  = invoke_admin_service(cluster,
                "zato:security.wss.get-list", etree.tostring(zato_message),
                ssl_key_file=ssl_key_file, ssl_cert_file=ssl_cert_file, ssl_ca_certs=ssl_ca_certs)

        if zato_path("data.definition_list.definition").get_from(zato_message) is not None:
            for definition_elem in zato_message.data.definition_list.definition:

                id = definition_elem.id.text
                name = unicode(definition_elem.name.text)
                username = unicode(definition_elem.username.text)
                reject_empty_nonce_ts = definition_elem.reject_empty_nonce_ts
                reject_stale_username = definition_elem.reject_stale_username
                expiry_limit = definition_elem.expiry_limit
                nonce_freshness = definition_elem.nonce_freshness

                definition = WSSUsernameTokenDefinition(id, name, None, username,
                    reject_empty_nonce_ts, reject_stale_username,
                    expiry_limit, nonce_freshness)
                definitions.append(definition)

            definitions.sort()
            '''

    return_data = {"zato_clusters":zato_clusters,
        "cluster_id":cluster_id,
        "choose_cluster_form":choose_cluster_form,
        "definitions":definitions
        }

    # TODO: Should really be done by a decorator.
    if logger.isEnabledFor(TRACE1):
        logger.log(TRACE1, "Returning render_to_response [%s]" % return_data)

    return render_to_response("zato/channel/soap.html", return_data)
