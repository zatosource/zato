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
from httplib import HTTPConnection

# Zato

# TODO: Clean it up, it's not needed anymore
soap_pool = SOAPPool("http://localhost:17080/soap")

logger = logging.getLogger(__name__)

def soap_invoke(url, postdata, soap_action):
    headers = {"content-type": "text/xml", "SOAPAction": soap_action}
    payload = soap_doc.safe_substitute(body=postdata)

    response = http_pool.urlopen("POST", "/soap", payload, headers)
    return response.data