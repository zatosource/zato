# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The read services of generic connections - the list by type and the lookup by id, each with the secrets
# left out. Their names spell out the module the write services live in, which is where they used to live
# and what every caller knows them by.

# stdlib
from contextlib import closing

# Zato
from zato.common.alerting.object_config import apply_defaults, conn_type_to_alert_type
from zato.common.api import query_parameters
from zato.common.ext_db.api import get_ext_db_session, is_ext_db_configured, is_ext_object_id, needs_ext_db, \
     to_local_id, to_public_id
from zato.common.json_internal import dumps
from zato.common.odb.model import GenericConn as ModelGenericConn
from zato.common.odb.query.generic import connection_list
from zato.common.util.config import replace_query_string_items_in_dict
from zato.server.generic.api.outconn_sdk import get_secret_field_names
from zato.server.generic.connection import GenericConnection
from zato.server.service import Int
from zato.server.service.internal import AdminService
from zato.server.service.internal.generic.connection import never_returned_keys

# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of generic connections by their type; includes pagination.
    """
    name = 'zato.generic.connection.get-list'
    _filter_by = ModelGenericConn.name,

    input = 'cluster_id', '-type_', *query_parameters

# ################################################################################################################################

    def get_data(self, session:'any_') -> 'any_':
        cluster_id = self.request.input.get('cluster_id') or self.server.cluster_id
        self.logger.info('GenericConn GetList.get_data: cluster_id=%s, type_=%s', cluster_id, self.request.input.type_)
        data:'any_' = self._search(connection_list, session, cluster_id, self.request.input.type_, False)
        self.logger.info('GenericConn GetList.get_data: result count=%s', data.count() if hasattr(data, 'count') else 'N/A')
        return data

# ################################################################################################################################

    def _add_custom_conn_dict_fields(self, conn_dict:'anydict') -> 'None':
        pass

# ################################################################################################################################

    def _enrich_conn_dict(self, conn_dict:'anydict') -> 'None':

        # Local aliases
        cluster_id = self.request.input.get('cluster_id') or self.server.cluster_id

        # Secrets never leave the server in listings ..
        for key in never_returned_keys:
            _ = conn_dict.pop(key, None)

        # .. neither do secret fields declared by hot-deployed connector types ..
        for key in get_secret_field_names(self.server.config_manager, conn_dict['type_']):
            _ = conn_dict.pop(key, None)

        # .. mask out all the relevant attributes.
        replace_query_string_items_in_dict(self.server, conn_dict)

        # Process all the items found in the database.
        for key, value in conn_dict.items():

            if value:

                if key.endswith('_service_id'):
                    prefix = key.split('_service_id')[0]
                    service_attr = prefix + '_service_name'
                    try:
                        service_name = self.invoke('zato.service.get-by-id', {
                            'cluster_id': cluster_id,
                            'id': value,
                        })['zato_service_get_by_name_response']['name']
                    except Exception:
                        pass
                    else:
                        conn_dict[service_attr] = service_name

        # .. add custom fields that do not exist in the database ..
        self._add_custom_conn_dict_fields(conn_dict)

        # .. and an object whose type has alert settings carries every one of them, the ones it was
        # never given at their defaults, so that the Dashboard and enmasse read a complete picture.
        conn_type = conn_dict['type_']
        if conn_type in conn_type_to_alert_type:
            apply_defaults(conn_type_to_alert_type[conn_type], conn_dict)

# ################################################################################################################################
# ################################################################################################################################

    def _append_conn_dicts(self, session:'any_', out:'anylist', needs_id_offset:'bool') -> 'None':

        search_result = self.get_data(session)

        for item in search_result:
            conn = GenericConnection.from_model(item)
            conn_dict = conn.to_dict()

            # Everyone else knows objects from the external database under their offset ids
            if needs_id_offset:
                conn_dict['id'] = to_public_id(conn_dict['id'])

            self._enrich_conn_dict(conn_dict)
            out.append(conn_dict)

# ################################################################################################################################

    def handle(self) -> 'None':
        out:'anylist' = []
        type_ = self.request.input.type_

        self.logger.info('GenericConn GetList.handle: type_=%s', type_)

        # AS2 outgoing connections come from the external database when one is configured ..
        is_ext = needs_ext_db(type_)

        with closing(self.server.get_config_session(object_type=type_)) as session:
            self._append_conn_dicts(session, out, is_ext)

        # .. lists without a type filter combine both databases.
        if is_ext_db_configured():
            if not type_:
                with closing(get_ext_db_session()) as session:
                    self._append_conn_dicts(session, out, True)

        self.logger.info('GenericConn GetList.handle: returning %s items for type_=%s', len(out), type_)

        self.response.payload = dumps(out)

# ################################################################################################################################
# ################################################################################################################################

class GetByID(AdminService):
    """ Returns a single generic connection by its ID.
    """
    name = 'zato.generic.connection.get-by-id'
    input = Int('id')

    def handle(self) -> 'None':

        input_id = self.request.input.id

        # Objects from the external AS2/AS4 database are stored under their local ids there ..
        if is_ext_object_id(input_id):
            local_id = to_local_id(input_id)
        else:
            local_id = input_id

        # .. look the connection up in the correct database ..
        with closing(self.server.get_config_session(object_id=input_id)) as session:
            query = session.query(ModelGenericConn)
            query = query.filter(ModelGenericConn.id==local_id)
            item = query.one()

            # .. turn the model into a dict ..
            conn = GenericConnection.from_model(item)
            conn_dict = conn.to_dict()

        # .. everyone else knows objects from the external database under their offset ids ..
        conn_dict['id'] = input_id

        # .. secrets never leave the server ..
        for key in never_returned_keys:
            _ = conn_dict.pop(key, None)

        # .. neither do secret fields declared by hot-deployed connector types ..
        for key in get_secret_field_names(self.server.config_manager, conn_dict['type_']):
            _ = conn_dict.pop(key, None)

        # .. mask out all the relevant secret attributes ..
        replace_query_string_items_in_dict(self.server, conn_dict)

        # .. and return the connection to our caller.
        self.response.payload = dumps(conn_dict)

# ################################################################################################################################
# ################################################################################################################################
