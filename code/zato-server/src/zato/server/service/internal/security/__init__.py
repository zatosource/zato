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
from contextlib import closing

# Zato
from zato.common.odb.query import basic_auth_list, tech_acc_list, wss_list
from zato.server.service import Boolean, Integer
from zato.server.service.internal import AdminService, AdminSIO

class GetList(AdminService):
    """ Returns a list of all security definitions available.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_get_list_request'
        response_elem = 'zato_security_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'sec_type')
        output_optional = ('username', 'realm', 'password_type', Boolean('reject_empty_nonce_creat'), 
            Boolean('reject_stale_tokens'), Integer('reject_expiry_limit'), Integer('nonce_freshness_time'))

    def handle(self):
        with closing(self.odb.session()) as session:
            pairs = (('basic_auth', basic_auth_list), 
                     ('tech_acc', tech_acc_list), 
                     ('wss', wss_list))
            for def_type, func in pairs:
                for definition in func(session, self.request.input.cluster_id, False):
                    self.response.payload.append(definition)
