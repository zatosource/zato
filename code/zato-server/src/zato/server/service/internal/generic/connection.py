# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing

# Bunch
from bunch import Bunch

# Zato
from zato.common.odb.query.generic import connection_list
from zato.server.generic.connection import attrs_gen_conn, GenericConnection
from zato.server.service.internal import AdminService, ChangePasswordBase, GetListAdminSIO

# ################################################################################################################################

class Create(AdminService):

    id = Column(Integer, Sequence('generic_conn_def_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    type_ = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)
    is_internal = Column(Boolean(), nullable=False, default=False)
    is_channel = Column(Boolean(), nullable=False)
    is_outconn = Column(Boolean(), nullable=False)
    pool_size = Column(Integer(), nullable=False)
    sec_use_rbac = Column(Boolean(), nullable=False, default=False)

    cache_expiry = Column(Integer, nullable=True, default=0)
    address = Column(Text(), nullable=True)
    port = Column(Integer, nullable=True)
    timeout = Column(Integer, nullable=True)
    data_format = Column(String(60), nullable=True)

    version = Column(String(200), nullable=True)
    extra = Column(Text(), nullable=True)
    username = Column(String(1000), nullable=True)
    username_type = Column(String(45), nullable=True)
    secret = Column(String(1000), nullable=True)
    secret_type = Column(String(45), nullable=True)
    conn_def_id = Column(Integer, ForeignKey('generic_conn_def.id', ondelete='CASCADE'), nullable=True)
    cache_id = Column(Integer, ForeignKey('cache.id', ondelete='CASCADE'), nullable=True)
    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)

    def handle(self):
        """ Creates a new generic connection in ODB.
        """
        self.logger.warn(self.request.raw_request)
        '''
        conn.cluster_id = self.server.cluster.id
        conn_dict = conn.to_sql_dict()

        model = ModelGenericConn()
        for key, value in conn_dict.items():
            setattr(model, key, value)

        with closing(self.server.odb.session()) as session:
            session.add(model)
            session.commit()
            session.refresh(model) # Needed because .from_model below needs to access all the attributes

        return GenericConnection.from_model(model)
        '''

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
