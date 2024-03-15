# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from copy import deepcopy

# Bunch
from bunch import Bunch

# SQLAlchemy
from sqlalchemy import and_, exists

# Zato
from zato.common.exception import NotFound
from zato.common.odb.model import PubSubTopic, PubSubEndpoint, PubSubEndpointEnqueuedMessage, PubSubEndpointTopic, PubSubMessage
from zato.common.odb.query import pubsub_message, pubsub_queue_message
from zato.common.typing_ import cast_
from zato.common.util.pubsub import get_expiration, get_priority
from zato.common.util.time_ import datetime_from_ms, utcnow_as_ms
from zato.server.service import AsIs, Bool, Int
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

MsgInsert = PubSubMessage.__table__.insert
EndpointTopicInsert = PubSubEndpointTopic.__table__.insert
EnqueuedMsgInsert = PubSubEndpointEnqueuedMessage.__table__.insert

Topic = PubSubTopic.__table__
Endpoint = PubSubEndpoint.__table__
EndpointTopic = PubSubEndpointTopic.__table__

# ################################################################################################################################

class _GetSIO(AdminSIO):
    input_required = (AsIs('msg_id'),)
    output_optional = ('topic_id', 'topic_name', AsIs('msg_id'), AsIs('correl_id'), 'in_reply_to', 'pub_time', \
        'ext_pub_time', 'pub_pattern_matched', 'sub_pattern_matched', 'priority', 'data_format', 'mime_type', 'size', 'data',
        'expiration', 'expiration_time', 'endpoint_id', 'endpoint_name', 'recv_time', 'pub_hook_service_id',
        'pub_hook_service_name', AsIs('ext_client_id'), 'server_name', 'server_pid', 'published_by_id', 'published_by_name',
        'subscriber_id', 'subscriber_name')

# ################################################################################################################################

class _UpdateSIO(AdminSIO):
    input_required = (AsIs('msg_id'), 'mime_type')
    input_optional = ('cluster_id', 'data', Int('expiration'), AsIs('correl_id'), AsIs('in_reply_to'), Int('priority'),
        Bool('exp_from_now'), 'server_name', 'server_pid', Int('size'), AsIs('pub_correl_id'), AsIs('expiration_time'))
    output_required = (Bool('found'), AsIs('msg_id'))
    output_optional = ('expiration_time', Int('size'))

# ################################################################################################################################

class GetFromTopicGD(AdminService):
    """ Returns a GD pub/sub topic message by its ID.
    """
    class SimpleIO(_GetSIO):
        input_required = _GetSIO.input_required + ('cluster_id',)
        input_optional = ('needs_sub_queue_check',)

    def handle(self, _not_given:'any_'=object()) -> 'None':
        with closing(self.odb.session()) as session:
            needs_sub_queue_check = self.request.input.get('needs_sub_queue_check', _not_given)
            needs_sub_queue_check = needs_sub_queue_check if needs_sub_queue_check is not _not_given else True
            item = pubsub_message(session, self.request.input.cluster_id, self.request.input.msg_id, needs_sub_queue_check).\
                first()

            if item:
                item.pub_time = datetime_from_ms(item.pub_time * 1000)
                item.ext_pub_time = datetime_from_ms(item.ext_pub_time * 1000) if item.ext_pub_time else ''
                item.expiration_time = datetime_from_ms(item.expiration_time * 1000) if item.expiration_time else ''
                self.response.payload = item
            else:
                raise NotFound(self.cid, 'No such message `{}`'.format(self.request.input.msg_id))

# ################################################################################################################################

class GetFromServerTopicNonGD(AdminService):
    """ Returns a non-GD message from current server.
    """
    SimpleIO = _GetSIO # type: ignore

    def handle(self) -> 'None':
        msg = self.pubsub.sync_backlog.get_message_by_id(self.request.input.msg_id)

        # We need to re-arrange attributes but we don't want to update the original message in place
        msg = deepcopy(msg)

        msg['msg_id'] = msg.pop('pub_msg_id')
        msg['correl_id'] = msg.pop('pub_correl_id', None)
        msg['pub_time'] = datetime_from_ms(msg['pub_time'] * 1000.0)

        expiration_time = msg.pop('expiration_time', None)
        if expiration_time:
            msg['expiration_time'] = datetime_from_ms(expiration_time * 1000.0)

        msg['endpoint_id'] = msg.pop('published_by_id')
        msg['endpoint_name'] = self.pubsub.get_endpoint_by_id(msg['endpoint_id']).name

        self.response.payload = msg

# ################################################################################################################################

class GetFromTopicNonGD(AdminService):
    """ Returns a non-GD pub/sub topic message by its ID.
    """
    class SimpleIO(_GetSIO):
        input_required = _GetSIO.input_required + ('server_name', 'server_pid')

    def handle(self) -> 'None':
        invoker = self.server.rpc.get_invoker_by_server_name(self.request.input.server_name)
        response = invoker.invoke(GetFromServerTopicNonGD.get_name(), {
            'msg_id': self.request.input.msg_id,
        }, pid=self.request.input.server_pid)

        if response:
            self.response.payload = response['response']

# ################################################################################################################################

class Has(AdminService):
    """ Returns a boolean flag to indicate whether a given message by ID exists in pub/sub.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', AsIs('msg_id'))
        output_required = (Bool('found'),)

    def handle(self) -> 'None':
        with closing(self.odb.session()) as session:
            self.response.payload.found = session.query(
                exists().where(and_(
                    PubSubMessage.pub_msg_id==self.request.input.msg_id,
                    PubSubMessage.cluster_id==self.server.cluster_id,
                    ))).\
                scalar()

# ################################################################################################################################

class TopicDeleteGD(AdminService):
    """ Deletes a GD topic message by its ID. Cascades to all related SQL objects, e.g. subscriber queues.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', AsIs('msg_id'))

    def handle(self) -> 'None':
        with closing(self.odb.session()) as session:
            ps_msg = session.query(PubSubMessage).\
                filter(PubSubMessage.cluster_id==self.request.input.cluster_id).\
                filter(PubSubMessage.pub_msg_id==self.request.input.msg_id).\
                first()

            if not ps_msg:
                raise NotFound(self.cid, 'Message not found `{}`'.format(self.request.input.msg_id))

            session.delete(ps_msg)
            session.commit()

        self.logger.info('GD topic message deleted `%s` (%s)', self.request.input.msg_id, ps_msg.data_prefix_short)

# ################################################################################################################################

class DeleteTopicNonGDMessage(AdminService):
    """ Deletes a non-GD message by its ID from current server.
    """
    class SimpleIO(AdminSIO):
        input_required = (AsIs('msg_id'),)

    def handle(self) -> 'None':
        self.pubsub.sync_backlog.delete_msg_by_id(self.request.input.msg_id)

# ################################################################################################################################

class TopicDeleteNonGD(AdminService):
    """ Deletes a non-GD message by its ID from a named server.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', 'server_name', 'server_pid', AsIs('msg_id'))

    def handle(self) -> 'None':
        invoker = self.server.rpc.get_invoker_by_server_name(self.request.input.server_name)
        invoker.invoke(DeleteTopicNonGDMessage.get_name(), {
            'msg_id': self.request.input.msg_id,
        }, pid=self.request.input.server_pid)

        self.logger.info('Deleted non-GD message `%s` from `%s:%s`',
            self.request.input.msg_id, self.request.input.server_name, self.request.input.server_pid)

# ################################################################################################################################

class QueueDeleteServerNonGD(AdminService):
    """ Deletes a non-GD messages from a selected queue which must exist on current server.
    """
    class SimpleIO(AdminSIO):
        input_required = ('sub_key', AsIs('msg_id'))

    def handle(self) -> 'None':
        if pubsub_tool := self.pubsub.get_pubsub_tool_by_sub_key(self.request.input.sub_key):
            pubsub_tool.delete_messages(self.request.input.sub_key, [self.request.input.msg_id])

# ################################################################################################################################

class QueueDeleteNonGD(AdminService):
    """ Deletes a non-GD messages from a selected queue.
    """
    class SimpleIO(AdminSIO):
        input_required = ('sub_key', AsIs('msg_id'), 'server_name', 'server_pid')

    def handle(self) -> 'None':
        sk_server = self.pubsub.get_delivery_server_by_sub_key(self.request.input.sub_key)

        if sk_server:
            invoker = self.server.rpc.get_invoker_by_server_name(sk_server.server_name)
            response = invoker.invoke(
                QueueDeleteServerNonGD.get_name(), {
                    'sub_key': sk_server.sub_key,
                    'msg_id': self.request.input.msg_id
                }, pid=sk_server.server_pid)

            if response:
                self.response.payload[:] = response['response']

# ################################################################################################################################

class QueueDeleteGD(AdminService):
    """ Deletes a GD message by its ID from the input subscription queue.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', AsIs('msg_id'), 'sub_key')

    def handle(self) -> 'None':
        with closing(self.odb.session()) as session:
            ps_msg = session.query(PubSubEndpointEnqueuedMessage).\
                filter(PubSubEndpointEnqueuedMessage.cluster_id==self.request.input.cluster_id).\
                filter(PubSubEndpointEnqueuedMessage.pub_msg_id==self.request.input.msg_id).\
                filter(PubSubEndpointEnqueuedMessage.sub_key==self.request.input.sub_key).\
                first()

            if not ps_msg:
                raise NotFound(self.cid, 'Message not found `{}` for sub_key `{}`'.format(
                    self.request.input.msg_id, self.request.input.sub_key))

            session.delete(ps_msg)
            session.commit()

            # Find the server that has the delivery task for this sub_key
            sk_server = self.pubsub.get_delivery_server_by_sub_key(self.request.input.sub_key)

            # It's possible that there is no such server in case of WSX clients that connected,
            # had their subscription created but then they disconnected and there is no delivery server for them.
            if sk_server:
                invoker = self.server.rpc.get_invoker_by_server_name(sk_server.server_name)
                invoker.invoke(DeleteDeliveryTaskMessage.get_name(), {
                    'msg_id': self.request.input.msg_id,
                    'sub_key': self.request.input.sub_key,
                }, pid=sk_server.server_pid)

        self.logger.info('Deleting GD queue message `%s` (%s)', self.request.input.msg_id, self.request.input.sub_key)

# ################################################################################################################################

class DeleteDeliveryTaskMessage(AdminService):
    """ Deletes a message from a delivery task which must exist on current server
    """
    class SimpleIO(AdminSIO):
        input_required = (AsIs('msg_id'), 'sub_key')

    def handle(self) -> 'None':
        if pubsub_tool := self.pubsub.get_pubsub_tool_by_sub_key(self.request.input.sub_key):
            pubsub_tool.delete_messages(self.request.input.sub_key, [self.request.input.msg_id])

# ################################################################################################################################

class UpdateServerNonGD(AdminService):
    """ Updates a non-GD message on current server.
    """
    SimpleIO = _UpdateSIO # type: ignore

    def handle(self) -> 'None':
        self.response.payload.msg_id = self.request.input.msg_id
        self.response.payload.found = self.pubsub.sync_backlog.update_msg(self.request.input)

# ################################################################################################################################

class _Update(AdminService):
    """ Base class for services updating GD or non-GD messages.
    """
    _message_update_has_gd:'bool'

    SimpleIO = _UpdateSIO # type: ignore

    def _get_item(self, *args:'any_', **kwargs:'any_') -> 'PubSubMessage':
        raise NotImplementedError('Must be overridden by subclasses')

    def _save_item(self, *args:'any_', **kwargs:'any_') -> 'None':
        raise NotImplementedError('Must be overridden by subclasses')

    def handle(self) -> 'None':
        input = self.request.input
        self.response.payload.msg_id = input.msg_id
        session = self.odb.session() if self._message_update_has_gd else None

        try:
            # Get that from its storage, no matter what it is
            item = self._get_item(input, session)

            if session and (not item):
                self.response.payload.found = False
                return

            item.data = input.data.encode('utf8')
            item.data_prefix = input.data[:self.pubsub.data_prefix_len].encode('utf8')
            item.data_prefix_short = input.data[:self.pubsub.data_prefix_short_len].encode('utf8')
            item.size = len(input.data)
            item.expiration = get_expiration(self.cid, input.get('expiration'), item.expiration)
            item.priority = get_priority(self.cid, input.get('priority'))

            item.msg_id = input.msg_id
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

            # Save data to its storage, SQL for GD and RAM for non-GD messages
            found = self._save_item(item, input, session)

            self.response.payload.found = found
            self.response.payload.size = item.size
            self.response.payload.expiration_time = datetime_from_ms(
                item.expiration_time * 1000.0) if item.expiration_time else None
        finally:
            if session:
                session.close() # type: ignore

# ################################################################################################################################

class UpdateGD(_Update):
    """ Updates details of an individual GD message.
    """
    _message_update_has_gd = True

    def _get_item(self, input:'stranydict', session:'SASession') -> 'PubSubMessage | None':
        return session.query(PubSubMessage).\
            filter(PubSubMessage.cluster_id==input['cluster_id']).\
            filter(PubSubMessage.pub_msg_id==input['msg_id']).\
            first()

    def _save_item(self, item:'any_', _ignored:'any_', session:'SASession') -> 'bool':
        session.add(item)
        session.commit()
        return True

# ################################################################################################################################

class UpdateNonGD(_Update):
    """ Updates details of an individual non-GD message.
    """
    _message_update_has_gd = False

    def _get_item(self, input:'any_', _ignored:'any_') -> 'Bunch':
        return Bunch()

    def _save_item(self, item:'any_', input:'any_', _ignored:'any_') -> 'bool':
        invoker = self.server.rpc.get_invoker_by_server_name(self.request.input.server_name)
        response = invoker.invoke(UpdateServerNonGD.get_name(), item, pid=self.request.input.server_pid)
        self.response.payload = response['response']
        return True

# ################################################################################################################################

class GetFromQueueGD(AdminService):
    """ Returns a GD pub/sub topic message by its ID.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', AsIs('msg_id'))
        output_optional = (AsIs('msg_id'), 'recv_time', 'data', Int('delivery_count'), 'last_delivery_time',
            'is_in_staging', 'queue_name', 'subscriber_id', 'subscriber_name', 'size', 'priority', 'mime_type',
            'sub_pattern_matched', AsIs('correl_id'), 'in_reply_to', 'expiration', 'expiration_time',
            AsIs('sub_hook_service_id'), 'sub_hook_service_name', AsIs('ext_client_id'), 'published_by_id',
            'published_by_name', 'pub_pattern_matched')

    def handle(self):
        with closing(self.odb.session()) as session:
            item = pubsub_queue_message(session, self.request.input.cluster_id, self.request.input.msg_id).\
                first()
            if item:
                item.expiration = item.expiration or None
                item_dict = item._asdict()
                for name in('expiration_time', 'recv_time', 'ext_pub_time', 'last_delivery_time'):
                    value = item_dict.get(name)
                    if value:
                        item_dict[name] = datetime_from_ms(value * 1000.0)
                self.response.payload = item_dict
                self.response.payload['published_by_name'] = self.pubsub.get_endpoint_by_id(item_dict['published_by_id']).name
            else:
                raise NotFound(self.cid, 'No such message `{}`'.format(self.request.input.msg_id))

# ################################################################################################################################

class GetFromQueueServerNonGD(AdminService):
    """ Returns details of a selected non-GD message from its queue which must exist on current server.
    """
    class SimpleIO(_GetSIO):
        input_required = _GetSIO.input_required + ('sub_key',)

    def handle(self) -> 'None':

        if pubsub_tool := self.pubsub.get_pubsub_tool_by_sub_key(self.request.input.sub_key):
            msg = pubsub_tool.get_message(self.request.input.sub_key, self.request.input.msg_id)

            if msg:
                msg = msg.to_dict()

                msg['msg_id'] = msg.pop('pub_msg_id')
                msg['correl_id'] = msg.pop('pub_correl_id', None)

                for name in ('pub_time', 'ext_pub_time', 'expiration_time', 'recv_time'):
                    value = msg.pop(name, None)
                    if value:
                        value = cast_('float', value)
                        msg[name] = datetime_from_ms(value * 1000.0)

                published_by_id = msg['published_by_id']
                published_by_id = cast_('int', published_by_id)

                msg['published_by_name'] = self.pubsub.get_endpoint_by_id(published_by_id).name

                sub = self.pubsub.get_subscription_by_sub_key(self.request.input.sub_key)
                if sub:
                    subscriber_id = sub.endpoint_id
                    subscriber_name = self.pubsub.get_endpoint_by_id(subscriber_id).name

                    msg['subscriber_id'] = subscriber_id
                    msg['subscriber_name'] = subscriber_name

                self.response.payload = msg

# ################################################################################################################################

class GetFromQueueNonGD(AdminService):
    """ Returns details of a selected non-GD message from its queue.
    """
    class SimpleIO(_GetSIO):
        input_required = _GetSIO.input_required + ('sub_key', 'server_name', 'server_pid')

    def handle(self) -> 'None':
        sk_server = self.pubsub.get_delivery_server_by_sub_key(self.request.input.sub_key)

        if sk_server:
            invoker = self.server.rpc.get_invoker_by_server_name(sk_server.server_name)
            response = invoker.invoke(
                GetFromQueueServerNonGD.get_name(), {
                    'sub_key': sk_server.sub_key,
                    'msg_id': self.request.input.msg_id
                }, pid=sk_server.server_pid)

            if response:
                self.response.payload = response['response']

# ################################################################################################################################
