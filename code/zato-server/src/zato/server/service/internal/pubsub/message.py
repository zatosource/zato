# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from datetime import datetime

# SQLAlchemy
from sqlalchemy import and_, exists

# Zato
from zato.common import DATA_FORMAT
from zato.common.exception import NotFound
from zato.common.odb.model import PubSubTopic, PubSubEndpoint, PubSubEndpointEnqueuedMessage, PubSubEndpointTopic, PubSubMessage
from zato.common.odb.query import pubsub_message, pubsub_queue_message
from zato.common.util.time_ import datetime_from_ms, utcnow_as_ms
from zato.server.pubsub import get_expiration, get_priority
from zato.server.service import AsIs, Bool, Int
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

_JSON = DATA_FORMAT.JSON

MsgInsert = PubSubMessage.__table__.insert
EndpointTopicInsert = PubSubEndpointTopic.__table__.insert
EnqueuedMsgInsert = PubSubEndpointEnqueuedMessage.__table__.insert

Topic = PubSubTopic.__table__
Endpoint = PubSubEndpoint.__table__
EndpointTopic = PubSubEndpointTopic.__table__

# ################################################################################################################################

class GetFromTopic(AdminService):
    """ Returns a pub/sub topic message by its ID.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', AsIs('msg_id'))
        output_optional = ('topic_id', 'topic_name', AsIs('msg_id'), AsIs('correl_id'), 'in_reply_to', 'pub_time', \
            'ext_pub_time', 'pattern_matched', 'priority', 'data_format', 'mime_type', 'size', 'data',
            'expiration', 'expiration_time', 'endpoint_id', 'endpoint_name', Bool('has_gd'),
            'pub_hook_service_id', 'pub_hook_service_name', AsIs('ext_client_id'))

    def handle(self):
        with closing(self.odb.session()) as session:

            item = pubsub_message(session, self.request.input.cluster_id, self.request.input.msg_id).\
                first()

            if item:
                item.pub_time = datetime_from_ms(item.pub_time * 1000)
                item.ext_pub_time = datetime_from_ms(item.ext_pub_time * 1000) if item.ext_pub_time else ''
                item.expiration_time = datetime_from_ms(item.expiration_time * 1000) if item.expiration_time else ''
                self.response.payload = item
            else:
                raise NotFound(self.cid, 'No such message `{}`'.format(self.request.input.msg_id))

# ################################################################################################################################

class Has(AdminService):
    """ Returns a boolean flag to indicate whether a given message by ID exists in pub/sub.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', AsIs('msg_id'))
        output_required = (Bool('found'),)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload.found = session.query(
                exists().where(and_(
                    PubSubMessage.pub_msg_id==self.request.input.msg_id,
                    PubSubMessage.cluster_id==self.server.cluster_id,
                    ))).\
                scalar()

# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a message by its ID. Cascades to all related SQL objects, e.g. subscriber queues.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', AsIs('msg_id'))

    def handle(self):
        with closing(self.odb.session()) as session:
            ps_msg = session.query(PubSubMessage).\
                filter(PubSubMessage.cluster_id==self.request.input.cluster_id).\
                filter(PubSubMessage.pub_msg_id==self.request.input.msg_id).\
                first()

            if not ps_msg:
                raise NotFound(self.cid, 'Message not found `{}`'.format(self.request.input.msg_id))

            ps_topic = session.query(PubSubTopic).\
                filter(PubSubTopic.cluster_id==self.request.input.cluster_id).\
                filter(PubSubTopic.id==ps_msg.topic_id).\
                one()

            # Delete the message  but do it under a global lock because other transactions
            # may want to update the topic in parallel.
            with self.lock('zato.pubsub.publish.%s' % ps_topic.name):
                session.delete(ps_msg)
                session.commit()

# ################################################################################################################################

class Update(AdminService):
    """ Updates details of an individual message.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', AsIs('msg_id'), 'mime_type')
        input_optional = ('data', Int('expiration'), AsIs('correl_id'), AsIs('in_reply_to'), Int('priority'),
            Bool('exp_from_now'))
        output_required = (Bool('found'),)
        output_optional = ('expiration_time', Int('size'))

    def handle(self, _utcnow=datetime.utcnow):
        input = self.request.input

        with closing(self.odb.session()) as session:
            item = session.query(PubSubMessage).\
                filter(PubSubMessage.cluster_id==input.cluster_id).\
                filter(PubSubMessage.pub_msg_id==input.msg_id).\
                first()

            if not item:
                self.response.payload.found = False
                return

            item.data = input.data.encode('utf8')
            item.data_prefix = input.data[:2048].encode('utf8')
            item.data_prefix_short = input.data[:64].encode('utf8')
            item.size = len(input.data)
            item.expiration = get_expiration(self.cid, input)
            item.priority = get_priority(self.cid, input)

            item.pub_correl_id = input.correl_id
            item.in_reply_to = input.in_reply_to
            item.mime_type = input.mime_type

            if item.expiration:
                if self.request.input.exp_from_now:
                    from_ = utcnow_as_ms()
                else:
                    from_ = item.pub_time
                item.expiration_time = from_ + (item.expiration / 1000.0)
            else:
                item.expiration_time = None

            session.add(item)
            session.commit()

            self.response.payload.found = True
            self.response.payload.size = item.size
            self.response.payload.expiration_time = datetime_from_ms(
                item.expiration_time * 1000.0) if item.expiration_time else None

# ################################################################################################################################

class GetFromQueue(AdminService):
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', AsIs('msg_id'))
        output_optional = (AsIs('msg_id'), 'recv_time', 'data', Int('delivery_count'), 'last_delivery_time',
            'is_in_staging', 'has_gd', 'queue_name', 'endpoint_id', 'endpoint_name', 'size', 'priority', 'mime_type',
            'sub_pattern_matched', AsIs('correl_id'), 'in_reply_to', 'expiration', 'expiration_time',
            AsIs('sub_hook_service_id'), 'sub_hook_service_name', AsIs('ext_client_id'))

    def handle(self):

        with closing(self.odb.session()) as session:

            item = pubsub_queue_message(session, self.request.input.cluster_id, self.request.input.msg_id).\
                first()

            if item:
                item.expiration = item.expiration or None
                for name in('expiration_time', 'recv_time', 'ext_pub_time', 'last_delivery_time'):
                    value = getattr(item, name, None)
                    if value:
                        setattr(item, name, datetime_from_ms(value))

                self.response.payload = item
            else:
                raise NotFound(self.cid, 'No such message `{}`'.format(self.request.input.msg_id))

# ################################################################################################################################



# ################################################################################################################################
