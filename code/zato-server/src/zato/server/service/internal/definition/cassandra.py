# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from itertools import chain
from traceback import format_exc
from uuid import uuid4

# Zato
from zato.common.broker_message import DEFINITION
from zato.common.odb.model import Cluster, CassandraConn
from zato.common.odb.query import cassandra_conn_list
from zato.server.service import Int, ForceType
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase

class GetList(AdminService):
    """ Returns a list of definitions available.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_definition_cassandra_get_list_request'
        response_elem = 'zato_definition_cassandra_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'contact_points', Int('port'), Int('exec_size'), 'proto_version',
            'cql_version', 'default_keyspace')
        output_optional = ('username',)

    def get_data(self, session):
        return cassandra_conn_list(session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

class _CreateEdit(AdminService):
    def populate_definition(self, definition):
        for name in chain(self.SimpleIO.input_required, self.SimpleIO.input_optional):
            if isinstance(name, ForceType):
                name = name.name
            value = self.request.input.get(name)
            setattr(definition, name, value)

class Create(_CreateEdit):
    """ Creates a new definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_definition_cassandra_create_request'
        response_elem = 'zato_definition_cassandra_create_response'
        input_required = ('cluster_id', 'name', 'is_active', 'contact_points', Int('port'), Int('exec_size'),
                'proto_version', 'default_keyspace')
        input_optional = ('username', 'cql_version')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input

        with closing(self.odb.session()) as session:
            try:

                # Let's see if we already have a definition of that name before committing
                # any stuff into the database.
                existing_one = session.query(CassandraConn).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(CassandraConn.name==input.name).first()

                if existing_one:
                    raise Exception('Definition `{}` already exists on this cluster'.format(input.name))

                password = uuid4().hex

                definition = CassandraConn()
                definition.password = password
                self.populate_definition(definition)

                session.add(definition)
                session.commit()

            except Exception, e:
                msg = 'Could not create a definition, e:`%s`'
                self.logger.error(msg, format_exc(e))
                session.rollback()

                raise
            else:
                input.action = DEFINITION.CASSANDRA_CREATE
                input.password = password
                self.broker_client.publish(input)

            self.response.payload.id = definition.id
            self.response.payload.name = definition.name

class Edit(_CreateEdit):
    """ Updates a definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_definition_cassandra_edit_request'
        response_elem = 'zato_definition_cassandra_edit_response'
        input_required = ('id', 'cluster_id', 'name', 'is_active', 'contact_points', Int('port'), Int('exec_size'),
            'proto_version', 'default_keyspace')
        input_optional = ('username', 'cql_version')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            try:
                existing_one = session.query(CassandraConn).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(CassandraConn.name==input.name).\
                    filter(CassandraConn.id!=input.id).\
                    first()

                if existing_one:
                    raise Exception('Definition `{}` already exists on this cluster'.format(input.name))

                definition = session.query(CassandraConn).filter_by(id=input.id).one()
                old_name = definition.name
                self.populate_definition(definition)

                session.add(definition)
                session.commit()

            except Exception, e:
                msg = 'Could not update the definition, e:[%s]'
                self.logger.error(msg, format_exc(e))
                session.rollback()

                raise
            else:
                input.action = DEFINITION.CASSANDRA_EDIT
                input.old_name = old_name
                input.password = definition.password
                self.broker_client.publish(input)

                self.response.payload.id = definition.id
                self.response.payload.name = definition.name

class ChangePassword(ChangePasswordBase):
    """ Changes the password of a Cassandra connection definition.
    """
    password_required = False
    
    class SimpleIO(ChangePasswordBase.SimpleIO):
        request_elem = 'zato_definition_cassandra_change_password_request'
        response_elem = 'zato_definition_cassandra_change_password_response'
    
    def handle(self):
        def _auth(instance, password):
            instance.password = password
            
        return self._handle(CassandraConn, _auth, DEFINITION.CASSANDRA_CHANGE_PASSWORD)

class Delete(AdminService):
    """ Deletes a definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_definition_cassandra_delete_request'
        response_elem = 'zato_definition_cassandra_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                auth = session.query(CassandraConn).\
                    filter(CassandraConn.id==self.request.input.id).\
                    one()

                session.delete(auth)
                session.commit()
            except Exception, e:
                msg = 'Could not delete the definition, e:[%s]'
                self.logger.error(msg, format_exc(e))
                session.rollback()

                raise
            else:
                self.request.input.action = DEFINITION.CASSANDRA_DELETE
                self.request.input.name = auth.name
                self.broker_client.publish(self.request.input)
