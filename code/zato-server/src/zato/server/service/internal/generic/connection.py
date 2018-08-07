# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from copy import deepcopy
from json import dumps

# Bunch
from bunch import Bunch

# Zato
from zato.common.broker_message import GENERIC
from zato.common.odb.model import GenericConn as ModelGenericConn
from zato.common.odb.query.generic import connection_list
from zato.server.generic.connection import attrs_gen_conn, GenericConnection
from zato.server.service import Bool, Int
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase, GetListAdminSIO
from zato.server.service.internal.generic import _BaseService
from zato.server.service.meta import DeleteMeta

# ################################################################################################################################

elem = 'generic_connection'
model = ModelGenericConn
label = 'a connection'
broker_message = GENERIC
broker_message_prefix = 'CONNECTION_'
list_func = None

# ################################################################################################################################

class _CreateEditSIO(AdminSIO):
    input_required = ('name', 'type_', 'is_active', 'is_internal', 'is_channel', 'is_outconn', Int('pool_size'),
        Bool('sec_use_rbac'), 'cluster_id')
    input_optional = ('id', Int('cache_expiry'), 'address', Int('port'), Int('timeout'), 'data_format', 'version',
        'extra', 'username', 'username_type', 'secret', 'secret_type', 'conn_def_id', 'cache_id')
    force_empty_keys = True

# ################################################################################################################################

class _CreateEdit(_BaseService):
    """ Creates a new or updates an existing generic connection in ODB.
    """
    class SimpleIO(_CreateEditSIO):
        output_required = ('id', 'name')
        default_value = None
        response_elem = None

    def handle(self, _force_null=('conn_def_id', 'cache_id', 'timeout', 'port', 'cache_expiry')):
        data = deepcopy(self.request.input)
        for key, value in self.request.raw_request.items():
            if key not in data:
                data[key] = self._convert_sio_elem(key, value)

        for name in _force_null:
            value = data.get(name)
            if not value:
                data[name] = None

        conn = GenericConnection.from_dict(data)
        conn_dict = conn.to_sql_dict()

        with closing(self.server.odb.session()) as session:

            if self.is_edit:
                model = self._get_instance(session, ModelGenericConn, data.type_, data.name)
            else:
                model = self._new_zato_instance_with_cluster(ModelGenericConn)

            for key, value in conn_dict.items():
                setattr(model, key, value)

            session.add(model)
            session.commit()

            instance = self._get_instance(session, ModelGenericConn, data.type_, data.name)

            self.response.payload.id = instance.id
            self.response.payload.name = instance.name

        data['action'] = GENERIC.CONNECTION_EDIT.value if self.is_edit else GENERIC.CONNECTION_CREATE.value
        self.broker_client.publish(data)

# ################################################################################################################################

class Create(_CreateEdit):
    is_edit = False

# ################################################################################################################################

class Edit(_CreateEdit):
    is_edit = True

# ################################################################################################################################

class Delete(AdminService):
    __metaclass__ = DeleteMeta

# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of generic connections by their type. Includes pagination.
    """
    _filter_by = GenericConnection.name,

    class SimpleIO(GetListAdminSIO):
        input_required = ('cluster_id', 'type_')

# ################################################################################################################################

    def get_data(self, session):
        return self._search(connection_list, session, self.request.input.cluster_id, self.request.input.type_, False)

# ################################################################################################################################

    def _enrich_conn_dict(self, conn_dict):
        for key, service_id in conn_dict.items():
            if service_id:
                if key.endswith('_service_id'):
                    prefix = key.split('_service_id')[0]
                    service_attr = prefix + '_service_name'
                    try:
                        service_name = self.invoke('zato.service.get-by-id', {
                            'cluster_id': self.request.input.cluster_id,
                            'id': service_id,
                        })['zato_service_get_by_name_response']['name']
                    except Exception:
                        pass
                    else:
                        conn_dict[service_attr] = service_name

# ################################################################################################################################

    def handle(self):
        out = {'_meta':{}, 'response':[]}

        with closing(self.odb.session()) as session:

            search_result = self.get_data(session)
            out['_meta'].update(search_result.to_dict())

            for item in search_result:
                conn = GenericConnection.from_model(item)
                conn_dict = conn.to_dict()
                self._enrich_conn_dict(conn_dict)
                out['response'].append(conn_dict)

        self.response.payload = dumps(out)

# ################################################################################################################################

class ChangePassword(ChangePasswordBase):
    pass

# ################################################################################################################################
