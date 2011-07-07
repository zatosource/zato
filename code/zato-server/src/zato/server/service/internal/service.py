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
import re

# lxml
from lxml import etree
from lxml.objectify import Element

# Zato
from zato.common import ZatoException
from zato.common import ZATO_OK, ZATO_NOT_GIVEN
from zato.server.service.internal import _get_params, AdminService

class GetServiceList(AdminService):
    """ Returns a list of all services matching a given regexp, which may be
    ZATO_NOT_GIVEN, in which case all existing services will be returned.
    If 'ignore_zato_services' is True then only user-defined services will be returned.
    """
    def handle(self, *args, **kwargs):

        payload = kwargs.get("payload")
        request_params = ["name_pattern", "pattern_type", "ignore_zato_services"]
        request_params = _get_params(payload, request_params, "data.service.",
                                     force_type=bool, force_type_params=["ignore_zato_services"])
        name_pattern = request_params["name_pattern"]
        pattern_type = request_params["pattern_type"]
        ignore_zato_services = request_params["ignore_zato_services"]

        supported_pattern_types = "re", "simple"
        if pattern_type not in(supported_pattern_types):
            raise ZatoException("pattern_type must be one of [%s]" % (supported_pattern_types,))

        # Parallel servers are always are up to date with regards to services
        # available so we don't need to query the singleton server.

        service_list = Element("service_list")
        services = self.server.service_store.services

        if name_pattern != ZATO_NOT_GIVEN:
            if pattern_type == "simple":
                name_pattern = name_pattern.replace("*", ".*")
            regexp = re.compile(name_pattern)
        else:
            regexp = None


        for service_name in services:
            if ignore_zato_services and service_name.startswith("zato"):
                continue

            if regexp and not re.search(regexp, service_name):
                continue

            service = Element("service")
            service.name = service_name
            service.egg_path = services[service_name]["egg_path"]
            service.usage_count = 0
            service_list.append(service)

        return ZATO_OK, etree.tostring(service_list)

class GetServiceDetails(AdminService):
    """ Returns detailed information on a given service.
    """
    def handle(self, *args, **kwargs):

        payload = kwargs.get("payload")
        request_params = _get_params(payload, ["name"], "data.service.")
        service_name = request_params["name"]

        service_elem = Element("service")
        services = self.server.service_store.services

        if service_name in services:
            service = services[service_name]

            service_elem.name = service_name
            service_elem.usage_count = 0
            service_elem.deployment_time = service["deployment_time"]
            service_elem.deployment_user = service["deployment_user"]
            service_elem.egg_path = service["egg_path"]
        else:
            msg = "Service [%s] doesn't exist." % service_name
            self.logger.error(msg)
            raise ZatoException(msg)

        return ZATO_OK, etree.tostring(service_elem)