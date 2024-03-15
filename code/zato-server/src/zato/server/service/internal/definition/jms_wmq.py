# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from datetime import datetime
from traceback import format_exc
from uuid import uuid4

# Zato
from zato.common.broker_message import DEFINITION
from zato.common.odb.model import Cluster, ConnDefWMQ
from zato.common.odb.query import definition_wmq, definition_wmq_list
from zato.server.service import Boolean, Int
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase, GetListAdminSIO

# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of IBM MQ definitions available.
    """
    _filter_by = ConnDefWMQ.name,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_definition_jms_wmq_get_list_request'
        response_elem = 'zato_definition_jms_wmq_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'host', 'port', 'channel', Boolean('cache_open_send_queues'),
            Boolean('cache_open_receive_queues'), Boolean('use_shared_connections'), Boolean('ssl'), 'needs_mcd',
            Int('max_chars_printed'), Boolean('use_jms'))
        output_optional = ('ssl_cipher_spec', 'ssl_key_repository', 'queue_manager', 'username')

    def get_data(self, session):
        return self._search(definition_wmq_list, session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################

class GetByID(AdminService):
    """ Returns a particular IBM MQ definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_definition_jms_wmq_get_by_id_request'
        response_elem = 'zato_definition_jms_wmq_get_by_id_response'
        input_required = ('id', 'cluster_id',)
        output_required = ('id', 'name', 'host', 'port', 'channel', Boolean('cache_open_send_queues'),
            Boolean('cache_open_receive_queues'), Boolean('use_shared_connections'), Boolean('ssl'), 'needs_mcd',
            Int('max_chars_printed'))
        output_optional = ('ssl_cipher_spec', 'ssl_key_repository', 'queue_manager', 'username', Boolean('use_jms'))

    def get_data(self, session):
        return definition_wmq(session, self.request.input.cluster_id, self.request.input.id)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload = self.get_data(session)

# ################################################################################################################################

class Create(AdminService):
    """ Creates a new IBM MQ definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_definition_jms_wmq_create_request'
        response_elem = 'zato_definition_jms_wmq_create_response'
        input_required = ('cluster_id', 'name', 'host', 'port', 'channel', Boolean('cache_open_send_queues'),
            Boolean('cache_open_receive_queues'), Boolean('use_shared_connections'), Boolean('ssl'), 'needs_mcd',
            Int('max_chars_printed'), Boolean('use_jms'))
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
                raise Exception('IBM MQ definition `{}` already exists on this cluster'.format(input.name))

            try:
                input.password = uuid4().hex
                input.use_jms = input.use_jms or False

                definition = self._new_zato_instance_with_cluster(ConnDefWMQ)
                definition.name = input.name
                definition.host = input.host
                definition.port = input.port
                definition.queue_manager = input.queue_manager
                definition.channel = input.channel
                definition.cache_open_send_queues = input.cache_open_send_queues
                definition.cache_open_receive_queues = input.cache_open_receive_queues
                definition.use_shared_connections = input.use_shared_connections
                definition.ssl = input.ssl
                definition.ssl_cipher_spec = input.ssl_cipher_spec
                definition.ssl_key_repository = input.ssl_key_repository
                definition.needs_mcd = input.needs_mcd
                definition.max_chars_printed = input.max_chars_printed
                definition.cluster_id = input.cluster_id
                definition.username = input.username
                definition.password = input.password
                definition.use_jms = input.use_jms

                session.add(definition)
                session.commit()

                input.id = definition.id
                input.action = DEFINITION.WMQ_CREATE.value
                self.broker_client.publish(input)

                self.response.payload.id = definition.id
                self.response.payload.name = definition.name

            except Exception:
                self.logger.error('Could not create an IBM MQ definition, e:`%s`', format_exc())
                session.rollback()

                raise

# ################################################################################################################################

class Edit(AdminService):
    """ Updates an IBM MQ definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_definition_jms_wmq_edit_request'
        response_elem = 'zato_definition_jms_wmq_edit_response'
        input_required = (Int('id'), 'cluster_id', 'name', 'host', 'port', 'channel',
            Boolean('cache_open_send_queues'), Boolean('cache_open_receive_queues'), Boolean('use_shared_connections'),
            Boolean('ssl'), 'needs_mcd', Int('max_chars_printed'), Boolean('use_jms'))
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
                raise Exception('IBM MQ definition `{}` already exists on this cluster'.format(input.name))

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
                def_.username = input.username
                def_.use_jms = input.use_jms or False

                session.add(def_)
                session.commit()

                input.id = def_.id
                input.action = DEFINITION.WMQ_EDIT.value
                input.old_name = old_name
                self.broker_client.publish(input)

                self.response.payload.id = def_.id
                self.response.payload.name = def_.name

            except Exception:
                self.logger.error('Could not update IBM MQ definition, e:`%s`', format_exc())
                session.rollback()

                raise

# ################################################################################################################################

class Delete(AdminService):
    """ Deletes an IBM MQ definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_definition_jms_wmq_delete_request'
        response_elem = 'zato_definition_jms_wmq_delete_response'
        input_required = (Int('id'),)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                def_ = session.query(ConnDefWMQ).\
                    filter(ConnDefWMQ.id==self.request.input.id).\
                    one()

                session.delete(def_)
                session.commit()

                msg = {'action': DEFINITION.WMQ_DELETE.value, 'id': self.request.input.id}
                self.broker_client.publish(msg)

            except Exception:
                session.rollback()
                self.logger.error('Could not delete IBM MQ definition, e:`%s`', format_exc())

                raise

# ################################################################################################################################

class ChangePassword(ChangePasswordBase):
    """ Changes the password of an IBM MQ connection definition.
    """
    password_required = False

    class SimpleIO(ChangePasswordBase.SimpleIO):
        request_elem = 'zato_definition_jms_wmq_change_password_request'
        response_elem = 'zato_definition_jms_wmq_change_password_response'

    def handle(self):
        def _auth(instance, password):
            instance.password = password
        return self._handle(ConnDefWMQ, _auth, DEFINITION.WMQ_CHANGE_PASSWORD.value)

# ################################################################################################################################

class Ping(AdminService):
    """ Pings a remote queue manager a given connection definition ID points to.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_definition_jms_wmq_ping_request'
        response_elem = 'zato_definition_jms_wmq_ping_response'
        input_required = (Int('id'),)
        output_optional = ('info',)

    def handle(self):

        start_time = datetime.utcnow()
        self.server.connector_ibm_mq.ping_wmq(self.request.input.id)
        response_time = datetime.utcnow() - start_time

        self.response.payload.info = 'Ping OK, took:`{}` s'.format(response_time.total_seconds())

# ################################################################################################################################
