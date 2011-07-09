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

# lxml
from lxml import etree

# Zato
from zato.admin.settings import ssl_key_file, ssl_cert_file, ssl_ca_certs
from zato.common.soap import invoke_admin_service as _invoke_admin_service


def invoke_admin_service(cluster, service, zato_message, session):
    """ A thin wrapper around zato.common.soap.invoke_admin_service that adds
    Django session-related information to the request headers.
    """
    headers = {'session_type':'zato-admin/django', 'session_key': session.session_key}
    return _invoke_admin_service(cluster, service, etree.tostring(zato_message),
                                 headers)
