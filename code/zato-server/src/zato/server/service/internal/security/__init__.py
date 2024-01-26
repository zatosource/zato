# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing

# Zato
from zato.common.api import SEC_DEF_TYPE
from zato.common.const import ServiceConst
from zato.common.odb import query
from zato.common.odb.model import SecurityBase
from zato.server.service import Boolean, Integer, List
from zato.server.service.internal import AdminService, GetListAdminSIO

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

output_required = 'id', 'name', 'is_active', 'sec_type'
output_optional:'any_' = 'username', 'realm', 'password_type', Boolean('reject_empty_nonce_creat'), \
    Boolean('reject_stale_tokens'), Integer('reject_expiry_limit'),  Integer('nonce_freshness_time'), 'proto_version', \
        'sig_method', Integer('max_nonce_log')

# ################################################################################################################################
# ################################################################################################################################

class GetByID(AdminService):
    """ Returns a single security definition by its ID.
    """
    class SimpleIO(GetListAdminSIO):
        response_elem = None
        input_required = 'cluster_id', 'id'
        output_required = output_required
        output_optional = output_optional

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload = query.sec_base(session, self.request.input.cluster_id, self.request.input.id)

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of all security definitions available.
    """
    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_security_get_list_request'
        response_elem = 'zato_security_get_list_response'
        input_optional = 'cluster_id'
        input_optional:'any_' = GetListAdminSIO.input_optional + (List('sec_type'), Boolean('needs_internal', default=True))
        output_required = output_required
        output_optional = output_optional
        output_repeated = True

    def handle(self):

        _cluster_id = self.request.input.get('cluster_id') or self.server.cluster_id
        _needs_internal = self.request.input.get('needs_internal') != ''
        _internal = {ServiceConst.API_Admin_Invoke_Username}

        if _needs_internal:
            needs_internal = True if self.request.input.get('needs_internal') is True else False
        else:
            needs_internal = True

        with closing(self.odb.session()) as session:
            pairs:'any_' = (
                (SEC_DEF_TYPE.APIKEY, query.apikey_security_list),
                (SEC_DEF_TYPE.AWS, query.aws_security_list),
                (SEC_DEF_TYPE.BASIC_AUTH, query.basic_auth_list),
                (SEC_DEF_TYPE.JWT, query.jwt_list),
                (SEC_DEF_TYPE.NTLM, query.ntlm_list),
                (SEC_DEF_TYPE.OAUTH, query.oauth_list),
                (SEC_DEF_TYPE.VAULT, query.vault_connection_list),
                (SEC_DEF_TYPE.TLS_CHANNEL_SEC, query.tls_channel_sec_list),
                (SEC_DEF_TYPE.TLS_KEY_CERT, query.tls_key_cert_list),
            )

            for def_type, func in pairs:

                filter_by = self.request.input.get('sec_type', [])
                if filter_by and def_type not in filter_by:
                    continue

                if func is query.basic_auth_list:
                    args = session, _cluster_id, None, False
                else:
                    args = session, _cluster_id, False

                # By default, we have nothing to filter by ..
                kwargs = {}

                # .. unless there is a query on input ..
                if query_criteria := self.request.input.get('query'):
                    kwargs['filter_by'] = SecurityBase.name
                    kwargs['query'] = query_criteria

                for definition in func(*args, **kwargs):

                    if definition.name.startswith('zato') or definition.name in _internal:
                        if not needs_internal:
                            continue

                    self.response.payload.append(definition)

# ################################################################################################################################
# ################################################################################################################################
