# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common.broker_message import MSG_NS
from zato.common.odb.model import Cluster, MsgNamespace
from zato.common.odb.query import namespace_list
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

class GetList(AdminService):
    """ Returns a list of namespaces available.
    """
    _filter_by = MsgNamespace.name,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_message_namespace_get_list_request'
        response_elem = 'zato_message_namespace_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'value')

    def get_data(self, session):
        return self._search(namespace_list, session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

class Create(AdminService):
    """ Creates a new namespace.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_message_namespace_create_request'
        response_elem = 'zato_message_namespace_create_response'
        input_required = ('cluster_id', 'name', 'value')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input

        with closing(self.odb.session()) as session:
            try:
                cluster = session.query(Cluster).filter_by(id=input.cluster_id).first()

                # Let's see if we already have a definition of that name before committing
                # any stuff into the database.
                existing_one = session.query(MsgNamespace).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(MsgNamespace.name==input.name).first()

                if existing_one:
                    raise Exception('Namespace [{0}] already exists on this cluster'.format(input.name))

                definition = MsgNamespace(None, input.name, input.value, cluster.id)

                session.add(definition)
                session.commit()

            except Exception:
                self.logger.error('Could not create a namespace, e:`%s`', format_exc())
                session.rollback()

                raise
            else:
                input.action = MSG_NS.CREATE.value
                self.broker_client.publish(input)

            self.response.payload.id = definition.id
            self.response.payload.name = definition.name

class Edit(AdminService):
    """ Updates a namespace.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_message_namespace_edit_request'
        response_elem = 'zato_message_namespace_edit_response'
        input_required = ('id', 'cluster_id', 'name', 'value')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            try:
                existing_one = session.query(MsgNamespace).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(MsgNamespace.name==input.name).\
                    filter(MsgNamespace.id!=input.id).\
                    first()

                if existing_one:
                    raise Exception('Namespace [{0}] already exists on this cluster'.format(input.name))

                definition = session.query(MsgNamespace).filter_by(id=input.id).one()
                old_name = definition.name

                definition.name = input.name
                definition.value = input.value

                session.add(definition)
                session.commit()

            except Exception:
                self.logger.error('Could not update the namespace, e:`%s`', format_exc())
                session.rollback()

                raise
            else:
                input.action = MSG_NS.EDIT.value
                input.old_name = old_name
                self.broker_client.publish(input)

                self.response.payload.id = definition.id
                self.response.payload.name = definition.name

class Delete(AdminService):
    """ Deletes a namespace.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_message_namespace_delete_request'
        response_elem = 'zato_message_namespace_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                auth = session.query(MsgNamespace).\
                    filter(MsgNamespace.id==self.request.input.id).\
                    one()

                session.delete(auth)
                session.commit()
            except Exception:
                self.logger.error('Could not delete the namespace, e:`%s`', format_exc())
                session.rollback()

                raise
            else:
                self.request.input.action = MSG_NS.DELETE.value
                self.request.input.name = auth.name
                self.broker_client.publish(self.request.input)
