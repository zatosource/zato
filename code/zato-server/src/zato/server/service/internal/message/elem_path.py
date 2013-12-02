# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc
from uuid import uuid4

# Zato
from zato.common.broker_message import MSG_ELEM_PATH
from zato.common.odb.model import Cluster, ElemPath
from zato.common.odb.query import elem_path_list
from zato.server.service.internal import AdminService, AdminSIO

# ##############################################################################

class GetList(AdminService):
    """ Returns a list of ElemPaths available.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_message_elem_path_get_list_request'
        response_elem = 'zato_message_elem_path_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'value')

    def get_data(self, session):
        return elem_path_list(session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ##############################################################################

class _CreateEdit(AdminService):
    def check_elem_path(self, value):
        """ Check whether the expression can be evaluated at all,
        making sure all the namespaces needed, if any, are already defined.
        """
        self.msg.elem_path_store.compile(value, self.msg.ns.ns_map)

class Create(_CreateEdit):
    """ Creates a new ElemPath.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_message_elem_path_create_request'
        response_elem = 'zato_message_elem_path_create_response'
        input_required = ('cluster_id', 'name', 'value')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input

        # Sanity check
        self.check_elem_path(input.value)

        with closing(self.odb.session()) as session:
            try:
                cluster = session.query(Cluster).filter_by(id=input.cluster_id).first()

                # Let's see if we already have a definition of that name before committing
                # any stuff into the database.
                existing_one = session.query(ElemPath).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(ElemPath.name==input.name).first()

                if existing_one:
                    raise Exception('ElemPath [{0}] already exists on this cluster'.format(input.name))

                definition = ElemPath(None, input.name, input.value, cluster.id)

                session.add(definition)
                session.commit()

            except Exception, e:
                msg = 'Could not create an ElemPath, e:[%s]'
                self.logger.error(msg, format_exc(e))
                session.rollback()

                raise
            else:
                input.action = MSG_ELEM_PATH.CREATE
                self.broker_client.publish(input)

            self.response.payload.id = definition.id
            self.response.payload.name = definition.name

class Edit(_CreateEdit):
    """ Updates an ElemPath.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_message_elem_path_edit_request'
        response_elem = 'zato_message_elem_path_edit_response'
        input_required = ('id', 'cluster_id', 'name', 'value')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input

        # Sanity check
        self.check_elem_path(input.value)

        with closing(self.odb.session()) as session:
            try:
                existing_one = session.query(ElemPath).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(ElemPath.name==input.name).\
                    filter(ElemPath.id!=input.id).\
                    first()

                if existing_one:
                    raise Exception('ElemPath [{0}] already exists on this cluster'.format(input.name))

                definition = session.query(ElemPath).filter_by(id=input.id).one()
                old_name = definition.name

                definition.name = input.name
                definition.value = input.value

                session.add(definition)
                session.commit()

            except Exception, e:
                msg = 'Could not update the ElemPath, e:[%s]'
                self.logger.error(msg, format_exc(e))
                session.rollback()

                raise
            else:
                input.action = MSG_ELEM_PATH.EDIT
                input.old_name = old_name
                self.broker_client.publish(input)

                self.response.payload.id = definition.id
                self.response.payload.name = definition.name

class Delete(AdminService):
    """ Deletes an ElemPath.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_message_elem_path_delete_request'
        response_elem = 'zato_message_elem_path_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                auth = session.query(ElemPath).\
                    filter(ElemPath.id==self.request.input.id).\
                    one()

                session.delete(auth)
                session.commit()
            except Exception, e:
                msg = 'Could not delete the ElemPath, e:[%s]'
                self.logger.error(msg, format_exc(e))
                session.rollback()

                raise
            else:
                self.request.input.action = MSG_ELEM_PATH.DELETE
                self.request.input.name = auth.name
                self.broker_client.publish(self.request.input)
