# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# Zato
from zato.common.odb import query
from zato.server.service import Boolean, Integer, List
from zato.server.service.internal import AdminService, AdminSIO

class GetList(AdminService):
    """ Returns a list of all security definitions available.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_get_list_request'
        response_elem = 'zato_security_get_list_response'
        input_required = ('cluster_id',)
        input_optional = (List('sec_type'),)
        output_required = ('id', 'name', 'is_active', 'sec_type')
        output_optional = ('username', 'realm', 'password_type',
            Boolean('reject_empty_nonce_creat'), Boolean('reject_stale_tokens'), Integer('reject_expiry_limit'),
            Integer('nonce_freshness_time'), 'proto_version', 'sig_method', Integer('max_nonce_log'))
        output_repeated = True

    def handle(self):
        with closing(self.odb.session()) as session:
            pairs = (('apikey', query.apikey_security_list),
                     ('aws', query.aws_security_list),
                     ('basic_auth', query.basic_auth_list),
                     ('ntlm', query.ntlm_list),
                     ('oauth', query.oauth_list),
                     ('openstack', query.openstack_security_list),
                     ('tech_acc', query.tech_acc_list),
                     ('wss', query.wss_list))

            for def_type, func in pairs:

                filter_by = self.request.input.get('sec_type', [])
                if filter_by and def_type not in filter_by:
                    continue

                for definition in func(session, self.request.input.cluster_id, False):
                    self.response.payload.append(definition)
