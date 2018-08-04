# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.odb.query.generic import connection_list
from zato.server.generic.connection import GenericConnection
from zato.server.service.internal import AdminService, ChangePasswordBase, GetListAdminSIO

# ################################################################################################################################

class Create(AdminService):
    def handle(self):
        """ Creates a new generic connection in ODB.
        """
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
