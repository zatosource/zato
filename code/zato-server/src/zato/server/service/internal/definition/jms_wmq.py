# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common.broker_message import MESSAGE_TYPE, DEFINITION
from zato.common.odb.model import Cluster, ConnDefWMQ
from zato.common.odb.query import def_jms_wmq, def_jms_wmq_list
from zato.server.service import Boolean, Integer
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase, GetListAdminSIO

# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of WebSphere MQ definitions available.
    """
    _filter_by = ConnDefWMQ.name,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_definition_jms_wmq_get_list_request'
        response_elem = 'zato_definition_jms_wmq_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'host', 'port', 'channel', Boolean('cache_open_send_queues'),
            Boolean('cache_open_receive_queues'), Boolean('use_shared_connections'), Boolean('ssl'), 'needs_mcd',
            Integer('max_chars_printed'))
        output_optional = ('ssl_cipher_spec', 'ssl_key_repository', 'queue_manager', 'username')

    def get_data(self, session):
        return self._search(def_jms_wmq_list, session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################

class GetByID(AdminService):
    """ Returns a particular WebSphere MQ definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_definition_jms_wmq_get_by_id_request'
        response_elem = 'zato_definition_jms_wmq_get_by_id_response'
        input_required = ('id', 'cluster_id',)
        output_required = ('id', 'name', 'host', 'port', 'channel', Boolean('cache_open_send_queues'),
            Boolean('cache_open_receive_queues'), Boolean('use_shared_connections'), Boolean('ssl'), 'needs_mcd',
            Integer('max_chars_printed'))
        output_optional = ('ssl_cipher_spec', 'ssl_key_repository', 'queue_manager', 'username')

    def get_data(self, session):
        return def_jms_wmq(session, self.request.input.cluster_id, self.request.input.id)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload = self.get_data(session)

# ################################################################################################################################

class Create(AdminService):
    """ Creates a new WebSphere MQ definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_definition_jms_wmq_create_request'
        response_elem = 'zato_definition_jms_wmq_create_response'
        input_required = ('cluster_id', 'name', 'host', 'port', 'channel', Boolean('cache_open_send_queues'),
            Boolean('cache_open_receive_queues'), Boolean('use_shared_connections'), Boolean('ssl'), 'needs_mcd',
            Integer('max_chars_printed'))
        input_optional = ('ssl_cipher_spec', 'ssl_key_repository', 'queue_manager', 'username')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input

        with closing(self.odb.session()) as session:

            # Let's see if we already have an object of that name before committing
            # any stuff into the database.
            existing_one = session.query(ConnDefWMQ).\
                filter(ConnDefWMQ.cluster_id==Cluster.id).\
                filter(ConnDefWMQ.name==input.name).\
                first()

            if existing_one:
                raise Exception('WebSphere MQ definition `{}` already exists on this cluster'.format(input.name))

            try:
                def_ = ConnDefWMQ(None, input.name, input.host, input.port, input.queue_manager,
                    input.channel, input.cache_open_send_queues, input.cache_open_receive_queues,
                    input.use_shared_connections, input.ssl, input.ssl_cipher_spec,
                    input.ssl_key_repository, input.needs_mcd, input.max_chars_printed,
                    input.cluster_id)
                session.add(def_)
                session.commit()

                input.id = def_.id
                input.action = DEFINITION.JMS_WMQ_CREATE.value
                self.broker_client.publish(input)

                self.response.payload.id = def_.id
                self.response.payload.name = def_.name

            except Exception, e:
                self.logger.error('Could not create a WebSphere MQ definition, e:`%s`' % format_exc())
                session.rollback()

                raise

# ################################################################################################################################

class Edit(AdminService):
    """ Updates a WMQ definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_definition_jms_wmq_edit_request'
        response_elem = 'zato_definition_jms_wmq_edit_response'
        input_required = ('id', 'cluster_id', 'name', 'host', 'port', 'channel',
            Boolean('cache_open_send_queues'), Boolean('cache_open_receive_queues'), Boolean('use_shared_connections'),
            Boolean('ssl'), 'needs_mcd', Integer('max_chars_printed'))
        input_optional = ('queue_manager', 'username')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input

        with closing(self.odb.session()) as session:

            # Let's see if we already have an object of that name before committing any stuff into the database.
            existing_one = session.query(ConnDefWMQ).\
                filter(ConnDefWMQ.cluster_id==Cluster.id).\
                filter(ConnDefWMQ.id!=input.id).\
                filter(ConnDefWMQ.name==input.name).\
                first()

            if existing_one:
                raise Exception('WebSphere MQ definition `{}` already exists on this cluster'.format(input.name))

            try:
                def_ = session.query(ConnDefWMQ).filter_by(id=input.id).one()
                old_name = def_.name
                def_.name = input.name
                def_.host = input.host
                def_.port = input.port
                def_.queue_manager = input.queue_manager
                def_.channel = input.channel
                def_.cache_open_send_queues = input.cache_open_send_queues
                def_.cache_open_receive_queues = input.cache_open_receive_queues
                def_.use_shared_connections = input.use_shared_connections
                def_.ssl = input.ssl
                def_.ssl_cipher_spec = input.get('ssl_cipher_spec')
                def_.ssl_key_repository = input.get('ssl_key_repository')
                def_.needs_mcd = input.needs_mcd
                def_.max_chars_printed = input.max_chars_printed

                session.add(def_)
                session.commit()

                input.id = def_.id
                input.action = DEFINITION.JMS_WMQ_EDIT.value
                input.old_name = old_name
                self.broker_client.publish(input)

                self.response.payload.id = def_.id
                self.response.payload.name = def_.name

            except Exception, e:
                self.logger.error('Could not update WebSphere MQ definition, e:`%s`' % format_exc())
                session.rollback()

                raise

# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a WebSphere MQ definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_definition_jms_wmq_delete_request'
        response_elem = 'zato_definition_jms_wmq_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                def_ = session.query(ConnDefWMQ).\
                    filter(ConnDefWMQ.id==self.request.input.id).\
                    one()

                session.delete(def_)
                session.commit()

                msg = {'action': DEFINITION.JMS_WMQ_DELETE.value, 'id': self.request.input.id}
                self.broker_client.publish(msg)

            except Exception, e:
                session.rollback()
                self.logger.error('Could not delete WebSphere MQ definition, e:`%s`' % format_exc())

                raise

# ################################################################################################################################

class ChangePassword(ChangePasswordBase):
    """ Changes the password of a WebSphere MQ connection definition.
    """
    password_required = False

    class SimpleIO(ChangePasswordBase.SimpleIO):
        request_elem = 'zato_definition_jms_wmq_change_password_request'
        response_elem = 'zato_definition_jms_wmq_change_password_response'

    def handle(self):
        def _auth(instance, password):
            instance.password = password

        return self._handle(CassandraConn, _auth, DEFINITION.CASSANDRA_CHANGE_PASSWORD.value)

# ################################################################################################################################
