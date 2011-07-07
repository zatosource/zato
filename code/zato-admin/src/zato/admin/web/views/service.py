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
from zato.admin.web.forms import ChooseClusterForm
from zato.admin.web.server_model import Service
from zato.admin.web.views import meth_allowed
from zato.common import zato_namespace, zato_path, ZatoException, ZATO_NOT_GIVEN
from zato.common.soap import invoke_admin_service
from zato.common.odb.model import Server
from zato.common.util import TRACE1

logger = logging.getLogger(__name__)

@meth_allowed("GET")
def index(req):

    zato_servers = Server.objects.all().order_by("name")
    choose_server_form = ChooseClusterForm(zato_servers, req.GET)
    server_id = None
    services = []

    # Build a list of services for a given Zato server.
    server_id = req.GET.get("server")

    if server_id and req.method == "GET":
        server = Server.objects.get(id=server_id)

        zato_message = Element("{%s}zato_message" % zato_namespace)
        zato_message.data = Element("data")
        zato_message.data.service = Element("service")
        zato_message.data.service.name_pattern = ZATO_NOT_GIVEN
        zato_message.data.service.pattern_type = "re"
        zato_message.data.service.ignore_zato_services = False

        _ignored, zato_message, soap_response  = invoke_admin_service(server.address,
                "zato:service.get-list", etree.tostring(zato_message))

        if zato_path("data.service_list.service").get_from(zato_message) is not None:
            for service_elem in zato_message.data.service_list.service:
                name = unicode(service_elem.name.text)
                egg_path = unicode(service_elem.egg_path.text)
                usage_count = int(service_elem.usage_count.text)

                service = Service(name, egg_path, usage_count)
                services.append(service)

            services.sort()

    return_data = {"zato_servers":zato_servers,
        "server_id":server_id,
        "choose_server_form":choose_server_form,
        "services":services
        }

    # TODO: Should really be done with a decorator
    if logger.isEnabledFor(TRACE1):
        logger.log(TRACE1, "Returning render_to_response [%s]" % return_data)

    return render_to_response("zato/service/index.html", return_data)

@meth_allowed("GET")
def details(req, server_id, service_name):

    server = Server.objects.get(id=server_id)
    service = Service()

    zato_message = Element("{%s}zato_message" % zato_namespace)
    zato_message.data = Element("data")
    zato_message.data.service = Element("service")
    zato_message.data.service.name = service_name

    _ignored, zato_message, soap_response  = invoke_admin_service(server.address,
            "zato:service.get-details", etree.tostring(zato_message))

    if zato_path("data.service").get_from(zato_message) is not None:
        service_elem = zato_message.data.service

        service.name = unicode(service_elem.name.text)
        service.egg_path = unicode(service_elem.egg_path.text)
        service.usage_count = int(service_elem.usage_count.text)
        service.deployment_time = datetime.strptime(service_elem.deployment_time.text, "%Y-%m-%dT%H:%M:%S.%f")
        service.deployment_user = service_elem.deployment_user.text

    return_data = {"server": server, "service":service}

    if logger.isEnabledFor(TRACE1):
        logger.log(TRACE1, "Returning render_to_response [%s]" % return_data)

    return render_to_response("zato/service/details.html", return_data)

@meth_allowed("TODO")
def invoke(req, server_id, service_name):
    pass
