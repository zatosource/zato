# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common.broker_message import CHANNEL, MESSAGE_TYPE
from zato.common.odb.model import ChannelWMQ, Cluster, ConnDefWMQ, Service
from zato.common.odb.query import channel_jms_wmq_list
from zato.server.connection.jms_wmq.channel import start_connector
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

class GetList(AdminService):
    """ Returns a list of JMS WebSphere MQ channels.
    """
    _filter_by = ChannelWMQ.name,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_channel_jms_wmq_get_list_request'
        response_elem = 'zato_channel_jms_wmq_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'def_id', 'def_name', 'queue', 'service_name')
        output_optional = ('data_format',)

    def get_data(self, session):
        return self._search(channel_jms_wmq_list, session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

class Create(AdminService):
    """ Creates a new WebSphere MQ channel.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_channel_jms_wmq_create_request'
        response_elem = 'zato_channel_jms_wmq_create_response'
        input_required = ('cluster_id', 'name', 'is_active', 'def_id', 'queue', 'service')
        input_optional = ('data_format',)
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input

        with closing(self.odb.session()) as session:
            # Let's see if we already have a channel of that name before committing
            # any stuff into the database.
            existing_one = session.query(ChannelWMQ.id).\
                filter(ConnDefWMQ.cluster_id==input.cluster_id).\
                filter(ChannelWMQ.def_id==ConnDefWMQ.id).\
                filter(ChannelWMQ.name==input.name).\
                first()

            if existing_one:
                raise Exception('A WebSphere MQ channel [{0}] already exists on this cluster'.format(input.name))

            # Is the service's name correct?
            service = session.query(Service).\
                filter(Cluster.id==input.cluster_id).\
                filter(Service.cluster_id==Cluster.id).\
                filter(Service.name==input.service).first()

            if not service:
                msg = 'Service [{0}] does not exist on this cluster'.format(input.service)
                self.logger.error(msg)
                raise Exception(msg)

            try:

                item = ChannelWMQ()
                item.name = input.name
                item.is_active = input.is_active
                item.queue = input.queue
                item.def_id = input.def_id
                item.service = service
                item.data_format = input.data_format

                session.add(item)
                session.commit()

                if item.is_active:
                    start_connector(self.server.repo_location, item.id, item.def_id)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception, e:
                msg = 'Could not create a WebSphere MQ channel, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise

class Edit(AdminService):
    """ Updates a JMS WebSphere MQ channel.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_channel_jms_wmq_edit_request'
        response_elem = 'zato_channel_jms_wmq_edit_response'
        input_required = ('id', 'cluster_id', 'name', 'is_active', 'def_id', 'queue', 'service')
        input_optional = ('data_format',)
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input

        with closing(self.odb.session()) as session:
            # Let's see if we already have an account of that name before committing
            # any stuff into the database.
            existing_one = session.query(ChannelWMQ.id).\
                filter(ConnDefWMQ.cluster_id==input.cluster_id).\
                filter(ChannelWMQ.def_id==ConnDefWMQ.id).\
                filter(ChannelWMQ.name==input.name).\
                filter(ChannelWMQ.id!=input.id).\
                first()

            if existing_one:
                raise Exception('A JMS WebSphere MQ channel [{0}] already exists on this cluster'.format(input.name))

            # Is the service's name correct?
            service = session.query(Service).\
                filter(Cluster.id==input.cluster_id).\
                filter(Service.cluster_id==Cluster.id).\
                filter(Service.name==input.service).first()

            if not service:
                msg = 'Service [{0}] does not exist on this cluster'.format(input.service)
                raise Exception(msg)

            try:
                item = session.query(ChannelWMQ).filter_by(id=input.id).one()
                old_name = item.name
                item.name = input.name
                item.is_active = input.is_active
                item.queue = input.queue
                item.def_id = input.def_id
                item.service = service
                item.data_format = input.data_format

                session.add(item)
                session.commit()

                input.action = CHANNEL.JMS_WMQ_EDIT.value
                input.old_name = old_name
                input.service = service.impl_name
                self.broker_client.publish(input, msg_type=MESSAGE_TYPE.TO_JMS_WMQ_CONSUMING_CONNECTOR_ALL)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception, e:
                msg = 'Could not update the JMS WebSphere MQ definition, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise

class Delete(AdminService):
    """ Deletes an JMS WebSphere MQ channel.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_channel_jms_wmq_delete_request'
        response_elem = 'zato_channel_jms_wmq_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                def_ = session.query(ChannelWMQ).\
                    filter(ChannelWMQ.id==self.request.input.id).\
                    one()

                session.delete(def_)
                session.commit()

                msg = {'action': CHANNEL.JMS_WMQ_DELETE.value, 'name': def_.name, 'id':def_.id}
                self.broker_client.publish(msg, MESSAGE_TYPE.TO_JMS_WMQ_CONSUMING_CONNECTOR_ALL)

            except Exception, e:
                session.rollback()
                msg = 'Could not delete the JMS WebSphere MQ channel, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)

                raise
