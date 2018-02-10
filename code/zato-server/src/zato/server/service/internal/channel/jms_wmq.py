# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from binascii import unhexlify
from contextlib import closing
from json import loads
from traceback import format_exc

# Arrow
from arrow import get as arrow_get

# Zato
from zato.common import CHANNEL
from zato.common.broker_message import CHANNEL as BROKER_MSG_CHANNEL
from zato.common.odb.model import ChannelWMQ, Cluster, ConnDefWMQ, Service
from zato.common.odb.query import channel_wmq_list
from zato.common.time_util import datetime_from_ms
from zato.common.util import payload_from_request
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of IBM MQ channels.
    """
    _filter_by = ChannelWMQ.name,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_channel_jms_wmq_get_list_request'
        response_elem = 'zato_channel_jms_wmq_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'def_id', 'def_name', 'queue', 'service_name')
        output_optional = ('data_format',)

    def get_data(self, session):
        return self._search(channel_wmq_list, session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################

class Create(AdminService):
    """ Creates a new IBM MQ channel.
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
                raise Exception('A IBM MQ channel `{}` already exists on this cluster'.format(input.name))

            # Is the service's name correct?
            service = session.query(Service).\
                filter(Cluster.id==input.cluster_id).\
                filter(Service.cluster_id==Cluster.id).\
                filter(Service.name==input.service).first()

            if not service:
                msg = 'Service `{}` does not exist on this cluster'.format(input.service)
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

                input.id = item.id
                input.service_name = service.name
                input.action = BROKER_MSG_CHANNEL.WMQ_CREATE.value
                self.broker_client.publish(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception:
                self.logger.error('Could not create an IBM MQ MQ channel, e:`%s`', format_exc())
                session.rollback()

                raise

# ################################################################################################################################

class Edit(AdminService):
    """ Updates an IBM MQ MQ channel.
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
                raise Exception('A IBM MQ channel `{}` already exists on this cluster'.format(input.name))

            # Is the service's name correct?
            service = session.query(Service).\
                filter(Cluster.id==input.cluster_id).\
                filter(Service.cluster_id==Cluster.id).\
                filter(Service.name==input.service).first()

            if not service:
                msg = 'Service `{}` does not exist on this cluster'.format(input.service)
                raise Exception(msg)

            try:
                item = session.query(ChannelWMQ).filter_by(id=input.id).one()
                item.name = input.name
                item.is_active = input.is_active
                item.queue = input.queue
                item.def_id = input.def_id
                item.service = service
                item.data_format = input.data_format

                session.add(item)
                session.commit()

                input.id = item.id
                input.service_name = service.name
                input.action = BROKER_MSG_CHANNEL.WMQ_EDIT.value
                self.broker_client.publish(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception:
                self.logger.error('Could not update IBM MQ definition, e:`%s`', format_exc())
                session.rollback()

                raise

# ################################################################################################################################

class Delete(AdminService):
    """ Deletes an IBM MQ MQ channel.
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

                self.broker_client.publish({
                    'action': BROKER_MSG_CHANNEL.WMQ_DELETE.value, 'id':def_.id
                })

            except Exception:
                session.rollback()
                self.logger.error('Could not delete IBM MQ channel, e:`%s`', format_exc())

                raise

# ################################################################################################################################

class OnMessageReceived(AdminService):
    """ A callback service invoked by WebSphere connectors for each taken off a queue.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_channel_jms_wmq_on_message_received_request'
        response_elem = 'zato_channel_jms_wmq_on_message_received_response'

    def handle(self, _channel=CHANNEL.WEBSPHERE_MQ, ts_format='YYYYMMDDHHmmssSS'):
        request = loads(self.request.raw_request)
        msg = request['msg']
        service_name = request['service_name']

        # Make MQ-level attributes easier to handle
        correlation_id = unhexlify(msg['correlation_id']) if msg['correlation_id'] else None
        expiration = datetime_from_ms(msg['expiration']) if msg['expiration'] else None

        timestamp = '{}{}'.format(msg['put_date'], msg['put_time'])
        timestamp = arrow_get(timestamp, ts_format).replace(tzinfo='UTC').datetime

        data = payload_from_request(self.cid, msg['text'], request['data_format'], None)

        self.invoke(service_name, data, _channel, wmq_ctx={
            'msg_id': unhexlify(msg['msg_id']),
            'correlation_id': correlation_id,
            'timestamp': timestamp,
            'put_time': msg['put_time'],
            'put_date': msg['put_date'],
            'expiration': expiration,
            'reply_to': msg['reply_to'],
        })

# ################################################################################################################################
