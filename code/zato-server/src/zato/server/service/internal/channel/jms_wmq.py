# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64decode
from binascii import unhexlify
from contextlib import closing
from traceback import format_exc

# Arrow
from arrow import get as arrow_get

# Python 2/3 compatibility
from zato.common.py23_ import pickle_loads

# Zato
from zato.common.api import CHANNEL
from zato.common.broker_message import CHANNEL as BROKER_MSG_CHANNEL
from zato.common.ccsid_ import CCSIDConfig
from zato.common.exception import ServiceMissingException
from zato.common.json_internal import loads
from zato.common.odb.model import ChannelWMQ, Cluster, ConnDefWMQ, Service as ModelService
from zato.common.odb.query import channel_wmq_list
from zato.common.util.api import payload_from_request
from zato.common.util.time_ import datetime_from_ms
from zato.server.service import Service
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
            service = session.query(ModelService).\
                filter(Cluster.id==input.cluster_id).\
                filter(ModelService.cluster_id==Cluster.id).\
                filter(ModelService.name==input.service).first()

            if not service:
                msg = 'Service `{}` does not exist in this cluster'.format(input.service)
                self.logger.info(msg)
                raise ServiceMissingException(msg)

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
        input_required = ('id', 'cluster_id', 'name', 'is_active', 'queue', 'service')
        input_optional = ('data_format', 'def_id', 'def_name')
        output_optional = ('id', 'name')

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
            service = session.query(ModelService).\
                filter(Cluster.id==input.cluster_id).\
                filter(ModelService.cluster_id==Cluster.id).\
                filter(ModelService.name==input.service).first()

            if not service:
                msg = 'Service `{}` does not exist in this cluster'.format(input.service)
                self.logger.info(msg)
                raise Exception(msg)

            try:

                # We will have def_id if the request comes through Dashboard
                # but not if is coming through enmasse.
                def_id = input.def_id

                if not def_id:
                    def_id = session.query(ConnDefWMQ.id).\
                        filter(ConnDefWMQ.cluster_id==input.cluster_id).\
                        filter(ConnDefWMQ.name==input.def_name).\
                        one_or_none()
                    def_id = def_id[0]

                item = session.query(ChannelWMQ).filter_by(id=input.id).one()
                item.name = input.name
                item.is_active = input.is_active
                item.queue = input.queue
                item.def_id = def_id
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

class OnMessageReceived(Service):
    """ A callback service invoked by WebSphere connectors for each taken off a queue.
    """
    def handle(self, _channel=CHANNEL.IBM_MQ, ts_format='YYYYMMDDHHmmssSS'):
        request = loads(self.request.raw_request)
        msg = request['msg']
        service_name = request['service_name']

        # Make MQ-level attributes easier to handle
        correlation_id = unhexlify(msg['correlation_id']) if msg['correlation_id'] else None
        expiration = datetime_from_ms(msg['expiration']) if msg['expiration'] else None

        timestamp = '{}{}'.format(msg['put_date'], msg['put_time'])
        timestamp = arrow_get(timestamp, ts_format).replace(tzinfo='UTC').datetime

        # Extract MQMD
        mqmd = msg['mqmd']
        mqmd = b64decode(mqmd)
        mqmd = pickle_loads(mqmd)

        # Find the message's CCSID
        request_ccsid = mqmd.CodedCharSetId

        # Try to find an encoding matching the CCSID,
        # if not found, use the default one.
        try:
            encoding = CCSIDConfig.encoding_map[request_ccsid]
        except KeyError:
            encoding = CCSIDConfig.default_encoding

        # Encode the input Unicode data into bytes
        msg['text'] = msg['text'].encode(encoding, errors='replace')

        # Extract the business payload
        data = payload_from_request(self.server.json_parser, self.cid, msg['text'], request['data_format'], None)

        # Invoke the target service
        self.invoke(service_name, data, _channel, wmq_ctx={
            'msg_id': unhexlify(msg['msg_id']),
            'correlation_id': correlation_id,
            'timestamp': timestamp,
            'put_time': msg['put_time'],
            'put_date': msg['put_date'],
            'expiration': expiration,
            'reply_to': msg['reply_to'],
            'data': data,
            'mqmd': mqmd
        })

# ################################################################################################################################
