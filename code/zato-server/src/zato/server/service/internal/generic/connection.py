# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from copy import deepcopy

# Bunch
from bunch import Bunch

# Zato
from zato.common.odb.model import GenericConn as ModelGenericConn
from zato.common.odb.query.generic import connection_list
from zato.server.generic.connection import attrs_gen_conn, GenericConnection
from zato.server.service import Bool, Int
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase, GetListAdminSIO
from zato.server.service.internal.generic import _BaseService

# ################################################################################################################################

class _CreateEditSIO(AdminSIO):
    input_required = ('name', 'type_', 'is_active', 'is_internal', 'is_channel', 'is_outconn', Int('pool_size'),
        Bool('sec_use_rbac'), 'cluster_id')
    input_optional = ('id', Int('cache_expiry'), 'address', Int('port'), Int('timeout'), 'data_format', 'version',
        'extra', 'username', 'username_type', 'secret', 'secret_type', 'conn_def_id', 'cache_id')
    force_empty_keys = True

# ################################################################################################################################

class Create(_BaseService):
    class SimpleIO(_CreateEditSIO):
        output_required = ('id', 'name')
        default_value = None
        response_elem = None

    def handle(self, _force_null=('conn_def_id', 'cache_id', 'timeout', 'port', 'cache_expiry')):
        """ Creates a new generic connection in ODB.
        """
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

        model = self._new_zato_instance_with_cluster(ModelGenericConn)
        for key, value in conn_dict.items():
            setattr(model, key, value)

        with closing(self.server.odb.session()) as session:
            session.add(model)
            session.commit()

            instance = self._get_instance(session, ModelGenericConn, data.type_, data.name)

            self.response.payload.id = instance.id
            self.response.payload.name = instance.name

# ################################################################################################################################

class Update(AdminService):
    pass

# ################################################################################################################################

class Delete(AdminService):
    pass

# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of generic connections by their type. Includes pagination.
    """
    _filter_by = GenericConnection.name,

    class SimpleIO(GetListAdminSIO):
        input_required = ('cluster_id', 'type_')
        output_optional = attrs_gen_conn
        output_repeated = True

    def get_data(self, session):
        return self._search(connection_list, session, self.request.input.cluster_id, self.request.input.type_, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################

class Get(AdminService):

    def handle(self):
        with closing(self.server.odb.session()) as session:
            item = session.query(ModelGenericConn).\
                filter(ModelGenericConn.id==id).\
                one()

        return GenericConnection.from_model(item)

# ################################################################################################################################

class ChangePassword(ChangePasswordBase):
    pass

# ################################################################################################################################
