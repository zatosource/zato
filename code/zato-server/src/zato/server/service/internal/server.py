# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common import ZatoException
from zato.common.odb.model import Server
from zato.common.odb.query import server_list
from zato.server.service.internal import AdminService, AdminSIO
from zato.server.service.meta import GetListMeta

# ################################################################################################################################

elem = 'server'
model = Server
label = 'a Zato server'
list_func = server_list
skip_output_params = ['token']

def response_hook(self, input, _ignored_instance, attrs, service_type):
    if service_type == 'get_list':
        for item in self.response.payload:
            if item.last_join_mod_date:
                item.last_join_mod_date = item.last_join_mod_date.isoformat()
            if item.up_mod_date:
                item.up_mod_date = item.up_mod_date.isoformat()

# ################################################################################################################################

class GetList(AdminService):
    _filter_by = Server.name,
    __metaclass__ = GetListMeta

# ################################################################################################################################

class Edit(AdminService):
    """ Updates a server.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_server_edit_request'
        response_elem = 'zato_server_edit_response'
        input_required = ('id', 'name')
        output_required = ('id', 'cluster_id', 'name', 'host')
        output_optional = ('bind_host', 'bind_port', 'last_join_status',
            'last_join_mod_date', 'last_join_mod_by', 'up_status', 'up_mod_date')

    def handle(self):
        with closing(self.odb.session()) as session:
            existing_one = session.query(Server).\
                filter(Server.id!=self.request.input.id).\
                filter(Server.name==self.request.input.name).\
                first()

            if existing_one:
                raise Exception('A server of that name [{0}] already exists on this cluster'.format(self.request.input.name))

            try:
                item = session.query(Server).filter_by(id=self.request.input.id).one()
                item.name = self.request.input.name

                session.add(item)
                session.commit()

                self.response.payload = item

                for name in('last_join_mod_date', 'up_mod_date'):
                    attr = getattr(self.response.payload, name, None)
                    if attr:
                        setattr(self.response.payload, name, attr.isoformat())

            except Exception, e:
                msg = 'Could not update the server, id:[{}], e:[{}]'.format(self.request.input.id, format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise

# ################################################################################################################################

class GetByID(AdminService):
    """ Returns a particular server
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_server_get_by_id_request'
        response_elem = 'zato_server_get_by_id_response'
        input_required = ('id',)
        output_required = ('id', 'cluster_id', 'name', 'host')
        output_optional = ('bind_host', 'bind_port', 'last_join_status',
            'last_join_mod_date', 'last_join_mod_by', 'up_status', 'up_mod_date')

    def get_data(self, session):
        return session.query(Server).\
            filter(Server.id==self.request.input.id).\
            one()

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload = self.get_data(session)

            for name in('last_join_mod_date', 'up_mod_date'):
                attr = getattr(self.response.payload, name, None)
                if attr:
                    setattr(self.response.payload, name, attr.isoformat())

# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a server.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_server_delete_request'
        response_elem = 'zato_server_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                server = session.query(Server).\
                    filter(Server.id==self.request.input.id).\
                    one()

                # Sanity check
                if server.id == self.server.id:
                    msg = 'A server cannot delete itself, id:[{}], name:[{}]'.format(server.id, server.name)
                    self.logger.error(msg)
                    raise ZatoException(self.cid, msg)

                # This will cascade and delete every related object
                session.delete(server)
                session.commit()

            except Exception, e:
                session.rollback()
                msg = 'Could not delete the server, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)

                raise

# ################################################################################################################################
