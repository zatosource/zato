# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""


# stdlib
from contextlib import closing

# Zato
from zato.common.api import Groups, query_parameters
from zato.common.odb.model import HTTPSOAP
from zato.common.odb.query import http_soap, http_soap_list
from zato.common.util.api import as_bool
from zato.common.util.sql import elems_with_opaque, get_dict_with_opaque
from zato.server.service import AsIs, Boolean
from zato.server.service.internal.http_soap.alert_settings import alert_input, apply_list_defaults
from zato.server.service.internal.http_soap.common import _BaseGet, _invocation_input, _retry_input
from zato.server.service.internal.http_soap.delivery_settings import apply_delivery_list_defaults, delivery_input

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

class Get(_BaseGet):
    """ Returns information about an individual HTTP/SOAP object by its ID.
    """
    name = 'zato.http-soap.get'

    input = '-id', '-name'

    def handle(self):
        self.request.input.require_any('id', 'name')

        with closing(self.odb.session()) as session:
            item = http_soap(session, self.request.input.id, self.request.input.name)
            out = get_dict_with_opaque(item)

        self.response.payload = out

# ################################################################################################################################

class GetList(_BaseGet):
    """ Returns a list of HTTP/SOAP connections.
    """
    name = 'zato.http-soap.get-list'

    _filter_by = HTTPSOAP.name,

    input = '-include_wrapper', '-connection', '-transport', '-data_format', '-needs_security_group_names', \
        *query_parameters
    output = 'id', 'name', 'is_active', 'is_internal', 'url_path', \
        '-service_id', '-service_name', '-security_id', '-security_name', '-sec_type', \
        '-method', '-soap_action', '-soap_version', '-data_format', '-host', '-ping_method', '-pool_size', \
        '-merge_url_params_req', '-url_params_pri', '-params_pri', '-timeout', \
        '-content_type', \
        Boolean('-match_slash'), '-http_accept', \
        '-should_parse_on_input', '-should_validate', '-should_return_errors', \
        '-data_encoding', '-username', '-is_wrapper', '-wrapper_type', AsIs('-security_groups'), '-security_group_count', \
        '-security_group_member_count', '-needs_security_group_names', Boolean('-validate_tls'), '-gateway_service_list', \
        '-connection', '-transport', Boolean('-is_audit_log_active'), \
        Boolean('-use_ws_addressing'), Boolean('-use_mtom'), '-body_credentials', '-tls_client_cert', '-tls_client_key', \
        *_invocation_input, \
        *_retry_input, \
        *alert_input, \
        *delivery_input

    def get_data(self, session):

        # Local aliases
        out:'anylist' = []
        needs_security_group_names = self.request.input.get('needs_security_group_names') or False
        include_wrapper = self.request.input.get('include_wrapper') or False
        should_ignore_wrapper = not include_wrapper

        # Get information about security groups which may be used later on
        security_groups_member_count = self.invoke('zato.groups.get-member-count', group_type=Groups.Type.API_Clients)

        if needs_security_group_names:
            all_security_groups = self.invoke('zato.groups.get-list', group_type=Groups.Type.API_Clients)
        else:
            all_security_groups = []

        # Obtain the basic result ..
        result = self._search(http_soap_list, session,
            self.request.input.connection, self.request.input.transport,
            as_bool(self.server.fs_server_config.misc.return_internal_objects),
            self.request.input.get('data_format'),
            False,
            )

        # .. extract all the opaque elements ..
        data:'anylist' = elems_with_opaque(result)

        # .. go through everything we have so far ..
        for item in data:

            # .. build a dictionary of information about groups ..
            security_groups_for_item_info = self._get_security_groups_info(item, security_groups_member_count)

            item['security_group_count'] = security_groups_for_item_info['group_count']
            item['security_group_member_count'] = security_groups_for_item_info['member_count']

            # .. optionally, we may need to turn security group IDs into their names ..
            if needs_security_group_names:
                if security_groups_for_item := item.get('security_groups'):
                    new_security_groups = []
                    for item_group_id in security_groups_for_item:
                        for group in all_security_groups:
                            if item_group_id == group['id']:
                                new_security_groups.append(group['name'])
                                break
                    item['security_groups'] = sorted(new_security_groups)

            # .. ignore wrapper elements if told do ..
            if should_ignore_wrapper and item.get('is_wrapper'):
                continue

            # .. a channel or an outgoing REST connection created before a setting existed reads the same
            # .. as one created after it ..
            apply_list_defaults(item)

            # .. and so does an outgoing REST connection created before a delivery setting existed ..
            apply_delivery_list_defaults(item)

            # .. if we are here, it means that this element is to be returned ..
            out.append(item)

        # .. now, return the result to our caller.
        return out

    def handle(self):
        with closing(self.odb.session()) as session:
            data = self.get_data(session)
            self.response.payload[:] = data

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################
