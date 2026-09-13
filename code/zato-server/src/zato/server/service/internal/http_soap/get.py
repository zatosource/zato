# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""


# stdlib
from contextlib import closing

# Zato
from zato.common.api import Groups, query_parameters
from zato.common.ext_db.api import get_ext_db_session, is_ext_db_configured, \
     is_ext_object_id, merge_ext_channel_items, needs_ext_db, to_local_id, to_public_id
from zato.common.odb.model import HTTPSOAP
from zato.common.odb.query import http_soap, http_soap_list
from zato.common.typing_ import cast_
from zato.common.util.api import as_bool
from zato.common.util.sql import elems_with_opaque, get_dict_with_opaque
from zato.server.service import AsIs, Boolean
from zato.server.service.internal.http_soap.alert_settings import alert_input, apply_list_defaults
from zato.server.service.internal.http_soap.common import _as2_input, _as4_input, _BaseGet, _invocation_input, \
    _pem_secret_fields, _retry_input

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

    input = '-cluster_id', '-id', '-name'

    def handle(self):
        self.request.input.require_any('id', 'name')
        cluster_id = self.request.input.get('cluster_id') or self.server.cluster_id

        # Ids arrive as strings and the external database check needs an integer
        if input_id := self.request.input.id:
            input_id = int(input_id)
        else:
            input_id = 0

        # Objects from the external AS2/AS4 database are looked up under their local ids there
        is_ext = is_ext_object_id(input_id)

        if is_ext:
            local_id = to_local_id(input_id)
        else:
            local_id = input_id

        with closing(self.server.get_config_session(object_id=input_id)) as session:
            item = http_soap(session, cluster_id, local_id, self.request.input.name)
            out = cast_('anydict', get_dict_with_opaque(item))

        # Secrets never leave the server, not even encrypted.
        for name in _pem_secret_fields:
            _ = out.pop(name, None)

        # The object is known everywhere else under its offset id
        if is_ext:
            out['id'] = to_public_id(out['id'])

        self.response.payload = out

# ################################################################################################################################

class GetList(_BaseGet):
    """ Returns a list of HTTP/SOAP connections.
    """
    name = 'zato.http-soap.get-list'

    _filter_by = HTTPSOAP.name,

    input = '-include_wrapper', '-cluster_id', '-connection', '-transport', '-data_format', '-needs_security_group_names', \
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
        *_as4_input, \
        *_as2_input, \
        *alert_input

    def get_data(self, session):

        # Local aliases
        out:'anylist' = []
        cluster_id = self.request.input.get('cluster_id') or self.server.cluster_id
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
        result = self._search(http_soap_list, session, cluster_id,
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

            # .. secrets never leave the server, not even encrypted ..
            for name in _pem_secret_fields:
                _ = item.pop(name, None)

            # .. a channel or an outgoing REST connection created before a setting existed reads the same
            # .. as one created after it ..
            apply_list_defaults(item)

            # .. if we are here, it means that this element is to be returned ..
            out.append(item)

        # .. now, return the result to our caller.
        return out

    def handle(self):
        transport = self.request.input.transport

        # AS2/AS4 objects come from the external database when one is configured ..
        if needs_ext_db(transport):
            with closing(get_ext_db_session()) as session:
                data = self.get_data(session)

            for item in data:
                item['id'] = to_public_id(item['id'])

        else:
            with closing(self.odb.session()) as session:
                data = self.get_data(session)

            # .. lists without a transport filter combine both databases,
            # .. with the external one winning on name conflicts.
            if is_ext_db_configured():
                if not transport:
                    with closing(get_ext_db_session()) as session:
                        ext_data = self.get_data(session)

                    for item in ext_data:
                        item['id'] = to_public_id(item['id'])

                    merge_ext_channel_items(data, ext_data)

        self.response.payload[:] = data

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################
