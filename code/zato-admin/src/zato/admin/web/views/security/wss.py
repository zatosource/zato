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

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render_to_response

# lxml
from lxml import etree
from lxml.objectify import Element

# Zato
from zato.admin.settings import ssl_key_file, ssl_cert_file, ssl_ca_certs
from zato.admin.web.forms import ChooseClusterForm
from zato.admin.web.server_model import WSSUsernameTokenDefinition
from zato.admin.web.forms.security.wss import WSSUsernameTokenDefinitionForm
from zato.admin.web.views import meth_allowed
from zato.common import zato_namespace, zato_path, ZatoException, ZATO_NOT_GIVEN
from zato.admin.web import invoke_admin_service
from zato.common.odb.model import Cluster
from zato.common.util import TRACE1, to_form

logger = logging.getLogger(__name__)

def _get_edit_create_message(params):
    """ Creates a base document which can be used by both 'edit' and 'create' actions.
    """
    zato_message = Element("{%s}zato_message" % zato_namespace)
    zato_message.definition = Element("definition")
    zato_message.definition.id = params["id"]
    zato_message.definition.name = params["name"]
    zato_message.definition.username = params["username"]
    zato_message.definition.reject_empty_nonce_ts = True if params.get("reject_empty_nonce_ts") == "on" else False
    zato_message.definition.reject_stale_username = True if params.get("reject_stale_username") == "on" else False
    zato_message.definition.expiry_limit = params["expiry_limit"]
    zato_message.definition.nonce_freshness = params["nonce_freshness"]

    return zato_message

@meth_allowed("GET")
def index(req):

    zato_clusters = req.odb.query(Cluster).order_by("name").all()
    choose_cluster_form = ChooseClusterForm(zato_clusters, req.GET)
    cluster_id = req.GET.get("cluster")
    definitions = []

    if cluster_id and req.method == "GET":
        cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()

        zato_message = Element("{%s}zato_message" % zato_namespace)

        _ignored, zato_message, soap_response  = invoke_admin_service(cluster,
                "zato:security.wss.get-list", zato_message, req.session)

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

    return_data = {"zato_clusters":zato_clusters,
        "cluster_id":cluster_id,
        "choose_cluster_form":choose_cluster_form,
        "definitions":definitions
        }

    # TODO: Should really be done by a decorator.
    if logger.isEnabledFor(TRACE1):
        logger.log(TRACE1, "Returning render_to_response [%s]" % return_data)

    return render_to_response("zato/security/wss/index.html", return_data)

@meth_allowed("GET")
def details(req, server_id, def_id):

    server = Server.objects.get(id=server_id)
    zato_servers = Server.objects.all().order_by("name")
    choose_server_form = ChooseClusterForm(zato_servers, {"server":server_id})

    definition = WSSUsernameTokenDefinition(def_id, original_name=None)

    zato_message = Element("{%s}zato_message" % zato_namespace)
    zato_message.definition = Element("definition")
    zato_message.definition.id = def_id

    _ignored, zato_message, soap_response  = invoke_admin_service(server.address,
            "zato:security.wss.get-details", etree.tostring(zato_message))

    if zato_path("data.definition").get_from(zato_message) is not None:
        definition_elem = zato_message.data.definition

        def_name = unicode(definition_elem.name.text)

        definition.name = def_name
        definition.original_name = def_name
        definition.username = unicode(definition_elem.username.text)
        definition.reject_empty_nonce_ts = definition_elem.reject_empty_nonce_ts
        definition.reject_stale_username = definition_elem.reject_stale_username
        definition.expiry_limit = definition_elem.expiry_limit
        definition.nonce_freshness = definition_elem.nonce_freshness

    definition_form = WSSUsernameTokenDefinitionForm(to_form(definition))

    return_data = {"server":server, "choose_server_form":choose_server_form,
                   "definition":definition, "definition_form":definition_form}

    # TODO: Should really be done by a decorator.
    if logger.isEnabledFor(TRACE1):
        logger.log(TRACE1, "Returning render_to_response [%s]" % return_data)

    return render_to_response("zato/security/wss/details.html", return_data)

@meth_allowed("POST")
def edit(req, server_id, def_id):
    """ Updates WS-S definitions's parameters (everything except for the password).
    """
    try:
        params = req.POST
        server = Server.objects.get(id=server_id)

        logger.info("About to change a WS-S definition, server_address=[%s], params=[%s]" % (server.address, params))
        zato_message = _get_edit_create_message(params)

        # original_definition_name is needed only by 'edit'.
        zato_message.definition.original_name = params.get("original_name")
        invoke_admin_service(server.address, "zato:security.wss.edit", etree.tostring(zato_message))

        logger.info("Saved changes to WS-S definition, server_address=[%s], params=[%s]" % (server.address, params))
    except Exception, e:
        return HttpResponseServerError(e)
    else:
        return HttpResponse()
