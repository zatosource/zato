# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from traceback import format_exc

# Bunch
from zato.common.ext.bunch import Bunch

# Zato
from zato.common.api import PubSub, query_parameters
from zato.common.broker_message import PUBSUB
from zato.common.json_internal import dumps
from zato.common.odb.model import Cluster, PubSubTopic
from zato.common.odb.query import pubsub_subscription_topic_names, pubsub_topic_list
from zato.common.pubsub.matcher import PatternMatcher
from zato.common.pubsub.util import validate_topic_name
from zato.common.util.sql import elems_with_opaque, parse_instance_opaque_attr, set_instance_opaque_attrs
from zato.server.service import Boolean, Service
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

_backend_fields = ('backend_type', 'amqp_outconn_name', 'amqp_exchange', 'amqp_routing_key', 'amqp_channel_name')

# ################################################################################################################################
# ################################################################################################################################

def _ensure_backend_input(input:'any_') -> 'None':
    """ Fills in backend type defaults and validates AMQP requirements before the input is persisted.
    """
    if not input.backend_type:
        input.backend_type = PubSub.Backend_Type_Default

    if input.backend_type == PubSub.Backend_Type.AMQP:

        if not input.amqp_outconn_name:
            raise Exception('An outgoing AMQP connection is required for AMQP-backed topics')

        if not input.amqp_exchange:
            raise Exception('An exchange is required for AMQP-backed topics')

        # The routing key is optional and defaults to the topic name at write time,
        # so the stored value is always present and publish time reads it directly.
        if not input.amqp_routing_key:
            input.amqp_routing_key = input.name

# ################################################################################################################################

def _get_backend_config_from_opaque(opaque:'any_') -> 'Bunch':
    """ Extracts backend fields from a topic's opaque attributes, with built-in defaults for topics
    that were created before backend types existed.
    """
    out = Bunch()

    for name in _backend_fields:
        if name in opaque:
            out[name] = opaque[name]
        else:
            out[name] = PubSub.Backend_Type_Default if name == 'backend_type' else ''

    return out

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of pub/sub topics available.
    """
    _filter_by = PubSubTopic.name, PubSubTopic.description,

    input = 'cluster_id', *query_parameters
    output = 'id', 'name', 'is_active', '-description', '-publisher_count', '-subscriber_count', '-backend_type', \
        '-amqp_outconn_name', '-amqp_exchange', '-amqp_routing_key', '-amqp_channel_name', Boolean('-is_audit_log_active')

    def get_data(self, session:'any_') -> 'any_':
        result = self._search(pubsub_topic_list, session, self.request.input.cluster_id, None, False)
        data = []

        for item, publisher_count, subscriber_count in result:

            item_dict = item.asdict()
            item_dict['publisher_count'] = publisher_count
            item_dict['subscriber_count'] = subscriber_count

            data.append(item_dict)

        data = elems_with_opaque(data)

        # Topics created before backend types existed have no backend information in their
        # opaque attributes, which means they use the built-in backend.
        for item_dict in data:
            if 'backend_type' not in item_dict:
                item_dict['backend_type'] = PubSub.Backend_Type_Default

        return data

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new pub/sub topic.
    """
    input = 'name', 'is_active', '-cluster_id', '-description', '-backend_type', '-amqp_outconn_name', \
        '-amqp_exchange', '-amqp_routing_key', '-amqp_channel_name', Boolean('-is_audit_log_active')
    output = 'id', 'name'

    def handle(self):
        input = self.request.input
        cluster_id = self.server.cluster_id

        # The audit log is enabled unless it was turned off explicitly
        input.is_audit_log_active = input.get('is_audit_log_active', True)

        # Validate topic name
        validate_topic_name(input.name)

        # Fill in the backend type default and validate AMQP requirements
        _ensure_backend_input(input)

        with closing(self.odb.session()) as session:
            try:
                cluster = session.query(Cluster).filter_by(id=cluster_id).first()

                # Let's see if we already have a definition of that name before committing
                # any stuff into the database.
                existing_one = session.query(PubSubTopic).\
                    filter(Cluster.id==cluster_id).\
                    filter(PubSubTopic.name==input.name).first()

                if existing_one:
                    raise Exception('Pub/sub topic `{}` already exists in this cluster'.format(input.name))

                topic = PubSubTopic()
                topic.name = input.name
                topic.is_active = input.is_active
                topic.cluster = cluster
                topic.description = input.description

                set_instance_opaque_attrs(topic, input)

                session.add(topic)
                session.commit()

            except Exception:
                self.logger.error('Could not create a pub/sub topic, e:`%s`', format_exc())
                session.rollback()

                raise
            else:

                # All servers are notified about every new topic so they can register
                # its audit log state, and AMQP-backed topics additionally need
                # their publish calls routed to the AMQP broker along with
                # the inbound channel override, which is why the backend fields go out too.
                pubsub_msg = Bunch()
                pubsub_msg.cid = self.cid
                pubsub_msg.action = PUBSUB.TOPIC_CREATE.value
                pubsub_msg.topic_name = input.name
                pubsub_msg.is_audit_log_active = input.is_audit_log_active

                for name in _backend_fields:
                    pubsub_msg[name] = input[name]

                self.config_dispatcher.publish(pubsub_msg)

                self.response.payload.id = topic.id
                self.response.payload.name = topic.name

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates a pub/sub topic.
    """
    input = 'name', 'is_active', '-id', '-cluster_id', '-description', '-backend_type', '-amqp_outconn_name', \
        '-amqp_exchange', '-amqp_routing_key', '-amqp_channel_name', Boolean('-is_audit_log_active')
    output = 'id', 'name'

    def handle(self):
        input = self.request.input
        input_id = input.get('id')
        cluster_id = self.server.cluster_id

        # The audit log is enabled unless it was turned off explicitly
        input.is_audit_log_active = input.get('is_audit_log_active', True)

        # Validate topic name
        validate_topic_name(input.name)

        # Fill in the backend type default and validate AMQP requirements
        _ensure_backend_input(input)

        with closing(self.odb.session()) as session:
            try:
                existing_one = session.query(PubSubTopic).\
                    filter(Cluster.id==cluster_id).\
                    filter(PubSubTopic.name==input.name)

                if input_id:
                    existing_one = existing_one.filter(PubSubTopic.id!=input.id)
                    existing_one = existing_one.first()

                if existing_one:
                    raise Exception('Pub/sub topic `{}` already exists on this cluster'.format(input.name))

                topic = session.query(PubSubTopic)

                if input_id:
                    topic = topic.filter_by(id=input.id)
                else:
                    topic = topic.filter_by(name=input.name)
                topic = topic.one()

                old_name = topic.name
                old_is_active = topic.is_active

                # Snapshot backend fields before they are overwritten so the config event
                # can tell servers what to undo, e.g. which channel override to restore.
                old_opaque = parse_instance_opaque_attr(topic)
                old_backend = _get_backend_config_from_opaque(old_opaque)

                # The previous audit log state is needed to detect toggles
                old_is_audit_log_active = old_opaque.get('is_audit_log_active')

                set_instance_opaque_attrs(topic, input)

                topic.name = input.name
                topic.is_active = input.is_active
                topic.description = input.description

                session.add(topic)
                session.commit()

            except Exception:
                self.logger.error('Could not update pub/sub topic, e:`%s`', format_exc())
                session.rollback()

                raise
            else:

                # Notify the broker if the name, active status, audit log state or backend configuration changed ..
                name_changed = input.name != old_name
                active_changed = input.is_active != old_is_active
                audit_changed = input.is_audit_log_active != old_is_audit_log_active
                backend_changed = False

                for name in _backend_fields:
                    if input[name] != old_backend[name]:
                        backend_changed = True
                        break

                has_changes = name_changed or active_changed or audit_changed or backend_changed

                if has_changes:

                    pubsub_msg = Bunch()
                    pubsub_msg.cid = self.cid
                    pubsub_msg.action = PUBSUB.TOPIC_EDIT.value
                    pubsub_msg.new_topic_name = input.name
                    pubsub_msg.old_topic_name = old_name
                    pubsub_msg.is_active = input.is_active
                    pubsub_msg.is_audit_log_active = input.is_audit_log_active

                    # Carry both the new backend fields and the previous channel name
                    # so servers can move the channel override if needed.
                    for name in _backend_fields:
                        pubsub_msg[name] = input[name]

                    pubsub_msg.old_backend_type = old_backend.backend_type
                    pubsub_msg.old_amqp_channel_name = old_backend.amqp_channel_name

                    self.config_dispatcher.publish(pubsub_msg)

                self.response.payload.id = topic.id
                self.response.payload.name = topic.name

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a pub/sub topic.
    """
    input = 'id',

    def handle(self) -> 'None':

        with closing(self.odb.session()) as session:
            try:
                topic = session.query(PubSubTopic).\
                    filter(PubSubTopic.id==self.request.input.id).\
                    one()

                # .. snapshot subscriptions linked to this topic before deletion,
                # .. because the FK cascade on PubSubSubscriptionTopic will remove
                # .. the junction rows when the topic row is deleted ..
                topic_manager = self.server.config_manager.pubsub_topic_manager
                linked_subs = topic_manager.get_subscriptions_by_topic_id(topic.id)

                session.delete(topic)
                session.commit()
            except Exception:
                self.logger.error('Could not delete pub/sub topic, e:`%s`', format_exc())
                session.rollback()

                raise
            else:

                pubsub_msg = Bunch()
                pubsub_msg.cid = self.cid
                pubsub_msg.action = PUBSUB.TOPIC_DELETE.value
                pubsub_msg.topic_name = topic.name

                self.config_dispatcher.publish(pubsub_msg)

                # .. delete subscriptions that have no remaining topics ..
                self._delete_subscriptions_without_topics(session, linked_subs)

    def _delete_subscriptions_without_topics(self, session:'any_', linked_subs:'anylist') -> 'None':
        """ Deletes subscriptions that no longer have any topics after the topic was removed.
        """
        for sub in linked_subs:

            # .. check if this subscription still has topics ..
            remaining_topics = pubsub_subscription_topic_names(session, sub.id)

            # .. if no topics remain, the subscription must be deleted ..
            if not remaining_topics:
                _ = self.invoke('zato.pubsub.subscription.delete', {'id': sub.id})

# ################################################################################################################################
# ################################################################################################################################

class GetMatches(AdminService):
    """ Returns a list of pub/sub topics matching a given pattern.
    """
    input = 'cluster_id', 'pattern'
    output = '-id', '-name', '-description'

    def handle(self):

        input_pattern = self.request.input.pattern
        cluster_id = self.request.input.cluster_id

        # Extract the actual topic pattern (after pub= or sub= if present)
        if input_pattern.startswith('pub=') or input_pattern.startswith('sub='):
            topic_pattern = input_pattern.split('=', 1)[1]
        else:
            topic_pattern = input_pattern

        with closing(self.odb.session()) as session:
            # Get all topics for this cluster
            topics = session.query(PubSubTopic).filter(
                PubSubTopic.cluster_id == cluster_id,
            ).all()

            # Create temporary matcher with the pattern
            matcher = PatternMatcher()
            client_id = 'temp_client'
            permissions = [{
                'pattern': topic_pattern,
                'access_type': 'subscriber'
            }]
            matcher.add_client(client_id, permissions)

            matching_topics = []
            for topic in topics:
                result = matcher.evaluate(client_id, topic.name, 'subscribe')
                if result.is_ok:
                    matching_topics.append({
                        'id': topic.id,
                        'name': topic.name,
                        'description': topic.description or ''
                    })

            self.response.payload = matching_topics

# ################################################################################################################################
# ################################################################################################################################

_Stream_Prefix = 'zato:pubsub:stream:'

# ################################################################################################################################
# ################################################################################################################################

def _get_all_topic_names_from_redis(server:'any_') -> 'list':
    """ Collect all topic names by scanning Redis stream keys.
    """
    all_keys = server.pubsub_redis.redis.keys(f'{_Stream_Prefix}*')

    prefix_len = len(_Stream_Prefix)

    out = []

    for key in all_keys:
        topic_name = key[prefix_len:]
        out.append(topic_name)

    return out

# ################################################################################################################################
# ################################################################################################################################

class GetPublishTimeline(AdminService):
    """ Returns a per-minute publish count timeline aggregated across all topics.
    """

    name = 'zato.pubsub.topic.get-publish-timeline'

    def handle(self) -> 'None':

        # Get the time window from the request ..
        since_minutes = self.request.raw_request['since_minutes']

        # .. collect all topic names from Redis ..
        topic_names = _get_all_topic_names_from_redis(self.server)

        # .. and query the backend for the timeline.
        self.response.payload = self.server.pubsub_redis.get_publish_timeline(topic_names, since_minutes)

# ################################################################################################################################
# ################################################################################################################################

class GetPublisherCount(AdminService):
    """ Returns the number of distinct publishers in the last N minutes.
    """

    name = 'zato.pubsub.topic.get-publisher-count'

    def handle(self) -> 'None':

        # Get the time window from the request ..
        since_minutes = self.request.raw_request['since_minutes']

        # .. collect all topic names from Redis ..
        topic_names = _get_all_topic_names_from_redis(self.server)

        # .. count distinct publishers ..
        publisher_count = self.server.pubsub_redis.count_distinct_publishers(topic_names, since_minutes)

        # .. and return the count.
        self.response.payload = {'publisher_count': publisher_count}

# ################################################################################################################################
# ################################################################################################################################

class OnAMQPMessage(Service):
    """ Bridges messages consumed from an AMQP channel into the channel's topic,
    delivering them directly to the topic's push subscribers.
    """

    name = 'zato.pubsub.topic.on-amqp-message'

    def handle(self) -> 'None':

        # The channel that consumed this message is the key to finding the topic ..
        channel_name = self.channel.name

        # .. the body is delivered as-is, without any envelope ..
        body = self.request.raw_request

        config_manager = self.server.config_manager

        # .. map the channel to its AMQP-backed topic ..
        topic_name = config_manager.get_pubsub_topic_by_amqp_channel(channel_name)

        # .. and hand the message over to all of the topic's push subscribers, with this
        # .. invocation's CID so all deliveries of one broker message share it in the audit log.
        # .. Any delivery failure propagates from this call, which means the AMQP message
        # .. is not acked and the broker will redeliver it.
        config_manager.pubsub_deliver_amqp_message(topic_name, body, self.cid)

# ################################################################################################################################
# ################################################################################################################################

class Publish(AdminService):
    """ Publishes a message to a pub/sub topic.
    """

    name = 'zato.pubsub.topic.publish'

    def handle(self) -> 'None':

        # Get the topic name and message data from the request ..
        topic_name = self.request.raw_request['topic_name']
        data = self.request.raw_request['data']

        # .. publish the message ..
        result = self.publish(topic_name, data)

        # .. serialize the result ..
        response_body = dumps({'msg_id': result.msg_id})

        # .. and return it.
        self.response.payload = {
            'response_body': response_body,
            'response_time': '',
        }

# ################################################################################################################################
# ################################################################################################################################
