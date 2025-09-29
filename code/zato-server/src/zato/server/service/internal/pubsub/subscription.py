# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from operator import itemgetter
from traceback import format_exc
from urllib.parse import quote

# Bunch
from bunch import Bunch, bunchify

# Zato
from zato.common.broker_message import PUBSUB
from zato.common.api import PubSub
from zato.common.odb.model import Cluster, HTTPSOAP, PubSubSubscription, PubSubSubscriptionTopic, PubSubTopic, SecurityBase
from zato.common.odb.query import pubsub_subscription_list
from zato.common.pubsub.util import evaluate_pattern_match, get_security_definition, set_time_since
from zato.common.util.api import new_sub_key, utcnow
from zato.common.util.sql import elems_with_opaque
from zato.server.service import AsIs, PubSubMessage, Service
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################
# ################################################################################################################################

def _build_topic_objects_list(topic_data_list=None, topics=None, topic_data_by_name=None):
    """ Build topic objects with flags for frontend response.
    """
    topic_objects_list = []

    if topic_data_list:
        # For create - we have topic_data_list directly
        for item in topic_data_list:
            topic_item = {
                'topic_name': item['topic_name'],
                'is_pub_enabled': item['is_pub_enabled'],
                'is_delivery_enabled': item['is_delivery_enabled']
            }
            topic_objects_list.append(topic_item)

    elif topics and topic_data_by_name:
        # For edit - we have topics and need to look up data
        for topic in topics:
            topic_data = topic_data_by_name[topic.name]
            topic_item = {
                'topic_name': topic.name,
                'is_pub_enabled': topic_data['is_pub_enabled'],
                'is_delivery_enabled': topic_data['is_delivery_enabled']
            }
            topic_objects_list.append(topic_item)

    topic_objects_list.sort(key=itemgetter('topic_name'))
    return topic_objects_list

# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.common.typing_ import strdict, strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Action_Subsctibe = 'Subscribe'
    Action_Unsubsctibe = 'Unsubscribe'

# ################################################################################################################################
# ################################################################################################################################

_push_type = PubSub.Push_Type

# ################################################################################################################################
# ################################################################################################################################

def get_topic_link(topic_name:'str', is_pub_enabled:'bool', is_delivery_enabled:'bool') -> 'str':

    pub_class = 'is-pub-enabled-true' if is_pub_enabled else 'is-pub-enabled-false'
    delivery_class = 'is-delivery-enabled-true' if is_delivery_enabled else 'is-delivery-enabled-false'

    topic_link = '<a href="/zato/pubsub/topic/?cluster=1&query={}" class="{} {}">{}</a>'.format(
        quote(topic_name), pub_class, delivery_class, topic_name)
    return topic_link

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of pub/sub subscriptions available.
    """
    _filter_by = PubSubSubscription.sub_key,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_pubsub_subscription_get_list_request'
        response_elem = 'zato_pubsub_subscription_get_list_response'
        input_required = 'cluster_id'
        input_optional = 'needs_password'
        output_required = 'id', 'sub_key', 'is_delivery_active', 'created', AsIs('topic_link_list'), 'sec_base_id', \
            'sec_name', 'username', 'delivery_type', 'push_type', 'rest_push_endpoint_id', 'push_service_name'
        output_optional = 'rest_push_endpoint_name', AsIs('topic_name_list'), 'password'
        output_repeated = True

    def get_data(self, session):

        # Check if password should be included in the response
        needs_password = self.request.input.needs_password

        # Query always returns password now, but we only need to use it if requested
        result = self._search(pubsub_subscription_list, session, self.request.input.cluster_id, None, False)

        # Group by subscription ID
        subscriptions_by_id = {}
        topics_by_id = {}

        for item in result:

            sub_id = item.id
            topic_name = item.topic_name
            is_pub_enabled = item.is_pub_enabled
            is_delivery_enabled = item.is_delivery_enabled
            password = item.password

            if sub_id not in subscriptions_by_id:

                item_dict = item._asdict()

                # Include password in response only if requested
                if needs_password:
                    password = self.crypto.decrypt(password)
                    item_dict['password'] = password

                subscriptions_by_id[sub_id] = item_dict

                # Initialize topics list for this subscription
                topics_by_id[sub_id] = []

            # Store topic with flags if not already present
            topic_dict = {
                'topic_name': topic_name,
                'is_pub_enabled': is_pub_enabled,
                'is_delivery_enabled': is_delivery_enabled
            }

            # Check if this topic is already in the list
            topic_exists = False
            for existing_topic in topics_by_id[sub_id]:
                if existing_topic['topic_name'] == topic_name:
                    topic_exists = True
                    break

            if not topic_exists:
                topics_by_id[sub_id].append(topic_dict)

        # Process data for each subscription
        data = []
        for sub_id, sub_dict in subscriptions_by_id.items():

            # Sort topics by name
            sorted_topics = sorted(topics_by_id[sub_id], key=lambda x: x['topic_name'])

            # Create topic links from sorted topics
            topic_link_list = [get_topic_link(topic['topic_name'], topic['is_pub_enabled'], topic['is_delivery_enabled']) for topic in sorted_topics]

            # Store both fields
            sub_dict['topic_link_list'] = ', '.join(topic_link_list)
            sub_dict['topic_name_list'] = sorted_topics

            data.append(sub_dict)

        out = elems_with_opaque(data)
        return out

# ################################################################################################################################
# ################################################################################################################################

    def handle(self):
        with closing(self.odb.session()) as session:
            data = self.get_data(session)
            self.response.payload[:] = data

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new pub/sub subscription.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_subscription_create_request'
        response_elem = 'zato_pubsub_subscription_create_response'
        input_required = 'cluster_id', AsIs('topic_name_list'), 'sec_base_id', 'delivery_type'
        input_optional = 'is_delivery_active', 'push_type', 'rest_push_endpoint_id', 'push_service_name', 'sub_key'
        output_required = 'id', 'sub_key', 'is_delivery_active', 'created', 'sec_name', 'delivery_type'
        output_optional = AsIs('topic_name_list'), AsIs('topic_link_list')

    def handle(self):

        # Our input
        input = self.request.input

        # A part of what we're returning
        topic_link_list = []

        topic_data_list = input.topic_name_list
        topic_name_list = sorted([item['topic_name'] for item in topic_data_list])

        # Build topic objects with flags for frontend
        topic_objects_list = _build_topic_objects_list(topic_data_list=topic_data_list)

        with closing(self.odb.session()) as session:
            try:
                # Get cluster and security definition
                cluster = session.query(Cluster).filter_by(id=input.cluster_id).first()
                sec_base = session.query(SecurityBase).filter_by(id=input.sec_base_id).first()

                # Generate a new subscription key
                sub_key = input.sub_key or new_sub_key(sec_base.name)

                # Get topics
                topics = []
                topic_data_by_name = {}

                for item in topic_data_list:
                    topic_name = item['topic_name']
                    topic_data_by_name[topic_name] = item

                for topic_name in topic_name_list:
                    topic = session.query(PubSubTopic).\
                        filter(PubSubTopic.cluster_id==input.cluster_id).\
                        filter(PubSubTopic.name==topic_name).first()

                    if not topic:
                        raise Exception('Pub/sub topic with ID `{}` not found in this cluster'.format(topic_name))
                    else:
                        topics.append(topic)

                # Create the subscription
                sub = PubSubSubscription()
                sub.sub_key = sub_key # type: ignore
                sub.is_delivery_active = input.is_delivery_active
                sub.cluster = cluster
                sub.sec_base = sec_base
                sub.delivery_type = input.delivery_type
                sub.push_type = input.push_type
                sub.push_service_name = input.push_service_name

                # For push subscriptions, set the endpoint
                if input.delivery_type == 'push' and input.get('rest_push_endpoint_id'):
                    endpoint = session.query(HTTPSOAP).\
                        filter(HTTPSOAP.id==input.rest_push_endpoint_id).first()
                    sub.rest_push_endpoint = endpoint

                session.add(sub)
                session.flush()  # Get the ID of the new subscription

                # Create subscription-topic associations
                for topic in topics:

                    sub_topic = PubSubSubscriptionTopic()
                    sub_topic.subscription = sub
                    sub_topic.topic = topic
                    sub_topic.cluster = cluster

                    topic_data = topic_data_by_name[topic.name]
                    sub_topic.is_pub_enabled = topic_data['is_pub_enabled']
                    sub_topic.is_delivery_enabled = topic_data['is_delivery_enabled']

                    with session.no_autoflush:
                        pattern_matched = evaluate_pattern_match(
                            session,
                            sec_base.name,
                            input.sec_base_id,
                            input.cluster_id,
                            topic.name
                        )

                    sub_topic.pattern_matched = pattern_matched

                    session.add(sub_topic)

                    topic_data = topic_data_by_name[topic.name]
                    topic_link = get_topic_link(topic.name, topic_data['is_pub_enabled'], topic_data['is_delivery_enabled'])
                    topic_link_list.append(topic_link)

                session.commit()

            except Exception:
                self.logger.error('Could not create pub/sub subscription, e:`%s`', format_exc())
                session.rollback()
                raise
            else:

                # Notify our process and the pub/sub server about the creation of a new subscription ..
                pubsub_msg = Bunch()
                pubsub_msg.cid = self.cid
                pubsub_msg.sub_key = sub.sub_key
                pubsub_msg.is_delivery_active = sub.is_delivery_active
                pubsub_msg.sec_name = sec_base.name # type: ignore
                pubsub_msg.username = sec_base.username
                pubsub_msg.topic_name_list = topic_name_list
                pubsub_msg.delivery_type = input.delivery_type
                pubsub_msg.action = PUBSUB.SUBSCRIPTION_CREATE.value

                # .. our own process we invoke directly ..
                self.server.worker_store.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(pubsub_msg)

                # .. and the pub/sub server is invoked in background.
                self.broker_client.publish_to_pubsub(pubsub_msg)

                self.response.payload.id = sub.id
                self.response.payload.sub_key = sub.sub_key
                self.response.payload.is_delivery_active = sub.is_delivery_active
                self.response.payload.created = sub.created
                self.response.payload.sec_name = sec_base.name # type: ignore
                self.response.payload.delivery_type = sub.delivery_type

                self.response.payload.topic_name_list = topic_objects_list
                self.response.payload.topic_link_list = sorted(topic_link_list)

                self.logger.info('Subscription(s) created for %s -> %s (%s)', sec_base.name, topic_name_list, sub.sub_key)

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates a pub/sub subscription.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_subscription_edit_request'
        response_elem = 'zato_pubsub_subscription_edit_response'
        input_required = 'sub_key', 'cluster_id', AsIs('topic_name_list'), 'sec_base_id', 'delivery_type'
        input_optional = 'is_delivery_active', 'push_type', 'rest_push_endpoint_id', 'push_service_name'
        output_required = 'id', 'sub_key', 'is_delivery_active', 'sec_name', 'delivery_type'
        output_optional = AsIs('topic_name_list'), AsIs('topic_link_list')

    def handle(self):

        input = self.request.input

        with closing(self.odb.session()) as session:
            try:

                # Check if the subscription exists before calling one()
                subscription_query = session.query(PubSubSubscription).\
                    filter(PubSubSubscription.cluster_id==input.cluster_id).\
                    filter(PubSubSubscription.sub_key==input.sub_key)

                # Now get the actual subscription
                sub = subscription_query.one()

                # Store the old delivery type before updating
                old_delivery_type = sub.delivery_type

                sub.sec_base_id = input.sec_base_id
                sub.delivery_type = input.delivery_type

                for key in self.SimpleIO.input_optional:
                    if key in input:
                        value = input[key]
                        setattr(sub, key, value)

                # Get the security definition
                sec_base = session.query(SecurityBase).\
                    filter(SecurityBase.id==sub.sec_base_id).\
                    one()

                # Delete all current topic associations
                _ = session.query(PubSubSubscriptionTopic).\
                    filter(PubSubSubscriptionTopic.subscription_id==sub.id).\
                    delete()

                # Process topics if any are provided
                topic_data_list = input.get('topic_name_list') or []
                topic_name_list = [item['topic_name'] for item in topic_data_list]

                topic_link_list = []
                topics = []
                topic_data_by_name = {}

                for item in topic_data_list:
                    topic_name = item['topic_name']
                    topic_data_by_name[topic_name] = item

                # If we go here, it means we don't have any other topics for that subscription ..
                if not topic_name_list:
                    self.logger.info('No topics provided for subscription %s, deleting subscription', sub.sub_key)

                    # .. so we can prepare a request to delete that subscription ..
                    delete_request = Bunch()
                    delete_request.id = sub.id
                    delete_request.session = session

                    # .. do delete it ..
                    _ = self.invoke('zato.pubsub.subscription.delete', delete_request)

                    # .. produce the response for our caller ..
                    self.response.payload.id = sub.id
                    self.response.payload.sub_key = sub.sub_key
                    self.response.payload.is_delivery_active = False
                    self.response.payload.sec_name = sec_base.name
                    self.response.payload.delivery_type = sub.delivery_type
                    self.response.payload.topic_name_list = []
                    self.response.payload.topic_link_list = []

                    # .. and return early since the subscription was deleted.
                    return

                # If we are here, it means there is at least one topic for that subscription ..
                if topic_name_list:

                    # Create new topic associations
                    for topic_name in topic_name_list:

                        # Make sure the topic exists
                        topic = session.query(PubSubTopic).\
                            filter(PubSubTopic.cluster_id==input.cluster_id).\
                            filter(PubSubTopic.name==topic_name).\
                            first()

                        if topic:
                            topics.append(topic)

                            # Create subscription-topic association
                            sub_topic = PubSubSubscriptionTopic()
                            sub_topic.cluster_id = input.cluster_id
                            sub_topic.subscription_id = sub.id
                            sub_topic.topic_id = topic.id

                            topic_data = topic_data_by_name[topic.name]
                            sub_topic.is_pub_enabled = topic_data['is_pub_enabled']
                            sub_topic.is_delivery_enabled = topic_data['is_delivery_enabled']

                            # Use no_autoflush to prevent premature flush during pattern evaluation
                            with session.no_autoflush:
                                pattern_matched = evaluate_pattern_match(
                                    session,
                                    sec_base.name,
                                    input.sec_base_id,
                                    input.cluster_id,
                                    topic.name
                                )
                            sub_topic.pattern_matched = pattern_matched

                            session.add(sub_topic)

                            topic_data = topic_data_by_name[topic.name]
                            topic_link = get_topic_link(topic.name, topic_data['is_pub_enabled'], topic_data['is_delivery_enabled'])
                            topic_link_list.append(topic_link)

                # Commit all changes
                session.commit()

            except Exception:
                self.logger.error('Could not update pub/sub subscription, e:`%s`', format_exc())
                session.rollback()
                raise
            else:

                # Build topic objects with flags for frontend
                topic_objects_list = _build_topic_objects_list(topics=topics, topic_data_by_name=topic_data_by_name)

                # Plain topic names (without HTML) for internal use
                topic_name_list = []
                for topic in topics:
                    topic_name_list.append(topic.name)
                topic_name_list.sort()

                # Notify our process and the pub/sub server about the creation of a new subscription ..
                pubsub_msg = Bunch()
                pubsub_msg.cid = self.cid
                pubsub_msg.sub_key = input.sub_key
                pubsub_msg.is_delivery_active = sub.is_delivery_active
                pubsub_msg.sec_name = sec_base.name
                pubsub_msg.username = sec_base.username
                pubsub_msg.topic_name_list = topic_name_list
                pubsub_msg.delivery_type = sub.delivery_type
                pubsub_msg.old_delivery_type = old_delivery_type
                pubsub_msg.rest_push_endpoint_id = input.rest_push_endpoint_id
                pubsub_msg.push_service_name = input.push_service_name
                pubsub_msg.action = PUBSUB.SUBSCRIPTION_EDIT.value

                # .. our own process we invoke directly ..
                self.server.worker_store.on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT(pubsub_msg)

                # .. and the pub/sub server is invoked in background.
                self.broker_client.publish_to_pubsub(pubsub_msg)

                self.response.payload.id = sub.id
                self.response.payload.sub_key = sub.sub_key
                self.response.payload.is_delivery_active = sub.is_delivery_active
                self.response.payload.sec_name = sec_base.name
                self.response.payload.delivery_type = sub.delivery_type

                self.response.payload.topic_name_list = topic_objects_list
                self.response.payload.topic_link_list = sorted(topic_link_list)

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a pub/sub subscription.
    """
    skip_before_handle = True

    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_subscription_delete_request'
        response_elem = 'zato_pubsub_subscription_delete_response'
        input_required = 'id',
        input_optional = AsIs('session'),

    def handle(self):

        has_input_session = bool(self.request.input.session)
        needs_new_session = not has_input_session

        # Use provided session or create new one
        if has_input_session:
            session = self.request.input.session
        else:
            session = self.odb.session()

        try:
            sub = session.query(PubSubSubscription).\
                filter(PubSubSubscription.id==self.request.input.id).\
                one()

            sec_def = session.query(SecurityBase).\
                filter(SecurityBase.id==sub.sec_base_id).\
                one()

            sec_def_name = sec_def.name
            sec_def_username = sec_def.username


            session.delete(sub)
            session.commit()

        except Exception:
            self.logger.error('Could not delete pub/sub subscription, e:`%s`', format_exc())
            session.rollback()
            raise
        finally:
            if needs_new_session:
                session.close()

        # Send broker notification (only for the pub/sub server) ..
        pubsub_msg = Bunch()
        pubsub_msg.cid = self.cid
        pubsub_msg.sub_key = sub.sub_key
        pubsub_msg.username = sec_def_name
        pubsub_msg.sec_name = sec_def_username
        pubsub_msg.action = PUBSUB.SUBSCRIPTION_DELETE.value

        # .. our own consumer task (from the same process) we want to stop synchronously so we call the handler directly ..
        self.server.worker_store.on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE(pubsub_msg)

        # .. and now we can notify the pub/sub server, knowing that the consumer is already stopped.
        # self.broker_client.publish_to_pubsub(pubsub_msg)

# ################################################################################################################################
# ################################################################################################################################

class _BaseModifyTopicList(AdminService):
    """ Base class for Subscribe/Unsubscribe operations.
    """
    action = '<Action-Not-Set>'

    class SimpleIO(AdminSIO):
        input_required = AsIs('topic_name_list')
        input_optional = 'username', 'sec_name', 'is_delivery_active', 'delivery_type', 'push_type', \
            'rest_push_endpoint_id', 'push_service_name', 'sub_key'
        output_optional = AsIs('topic_name_list')
        response_elem = None

# ################################################################################################################################

    def _modify_topic_list(self, existing_topic_names:'strlist', new_topic_names:'strlist') -> 'strlist':
        raise NotImplementedError('Subclasses must implement _modify_topic_list')

# ################################################################################################################################

    def _get_subscriptions_by_sec(self, cluster_id, sec_base_id):
        """ Get subscriptions for a security definition.
        """
        get_list_request = {
            'cluster_id': cluster_id,
            'sec_base_id': sec_base_id
        }

        get_list_response = self.invoke('zato.pubsub.subscription.get-list', get_list_request, skip_response_elem=True)
        return get_list_response

# ################################################################################################################################

    def handle(self):

        input = self.request.input
        cluster_id = 1

        # Get security definition by username
        with closing(self.odb.session()) as session:
            try:
                # .. find security definition by username or sec_name ..
                sec_base, lookup_field, lookup_value = get_security_definition(
                    session,
                    cluster_id,
                    username=getattr(input, 'username', None),
                    sec_name=getattr(input, 'sec_name', None)
                )

                sec_base_id = sec_base.id

                # .. find any existing subscriptions using GetList service  ..
                subscriptions = self._get_subscriptions_by_sec(cluster_id, sec_base_id)

                # .. if we do not have any subscription, what to do next, depends on whether we are creating
                # .. new subscriptions, or if we're unsubscribing the client ..
                if not subscriptions:

                    # .. or, we are to create a new (the very first) subscription ..
                    if self.action == ModuleCtx.Action_Subsctibe:

                        # .. prepare our request ..
                        create_request = Bunch()
                        create_request.sub_key = input.sub_key
                        create_request.cluster_id = cluster_id
                        create_request.topic_name_list = input.topic_name_list
                        create_request.sec_base_id = sec_base_id
                        create_request.delivery_type = input.delivery_type
                        create_request.is_delivery_active = input.is_delivery_active
                        create_request.push_type = input.push_type
                        create_request.rest_push_endpoint_id = input.rest_push_endpoint_id
                        create_request.push_service_name = input.push_service_name

                        # .. invoke the Create service ..
                        _ = self.invoke('zato.pubsub.subscription.create', create_request)

                        # .. and now we can return because we've already done what needed doing for the first subscription ..
                        return

                    elif self.action == ModuleCtx.Action_Unsubsctibe:

                        # .. if weare here, it means that someone called unsubscribe on a client without any subscriptions, ..
                        # .. which is not an error but we don't really have anything to do here so we can just return ..
                        # .. indicate that there are no topics for this client ..
                        self.response.payload.topic_name_list = []

                        # .. and now we can return.
                        return

                # Extract subscriptions for this security definition
                current_sub = None

                for item in subscriptions:
                    item = bunchify(item)
                    if item.sec_base_id == sec_base_id:
                        current_sub = item
                        break
                else:
                    err_msg = f'{self.action}: Could not find subscription for input {lookup_field} `{lookup_value}` -> {subscriptions}'
                    raise Exception(err_msg)

                # Find topics and check permissions
                new_topic_names = []

                for topic_name in input.topic_name_list:

                    # Check if the topic exists
                    topic = session.query(PubSubTopic).\
                        filter(PubSubTopic.cluster_id==cluster_id).\
                        filter(PubSubTopic.name==topic_name).\
                        first()

                    if not topic:
                        raise Exception(f'Topic `{topic_name}` not found')

                    # Check if the security definition has permission to subscribe to or unsubscribe from this topic
                    pattern_matched = evaluate_pattern_match(
                        session,
                        sec_base.name,
                        sec_base_id,
                        cluster_id,
                        topic_name
                    )

                    if not pattern_matched:
                        msg = f'User `{sec_base.username}` does not have permission for action `{self.action}` on topic `{topic_name}`'
                        raise Exception(msg)

                    new_topic_names.append(topic_name)

                # Get current subscription and topic names
                sub_key = current_sub.sub_key
                existing_topic_names = current_sub.topic_name_list

                # Apply subclass-specific modification logic
                all_topic_names = self._modify_topic_list(existing_topic_names, new_topic_names)

                # Sort the final list
                all_topic_names.sort()

                # Update existing subscription with the combined topics
                request = Bunch()
                request.sub_key = sub_key
                request.cluster_id = cluster_id
                request.topic_name_list = all_topic_names
                request.sec_base_id = sec_base_id
                request.delivery_type = current_sub.delivery_type
                request.is_delivery_active = current_sub.is_delivery_active
                request.push_service_name = current_sub.push_service_name
                request.push_type = current_sub.push_type
                request.rest_push_endpoint_id = current_sub.rest_push_endpoint_id

                # Update the subscription
                _ = self.invoke('zato.pubsub.subscription.edit', request)

                # Set response with sorted topic list
                self.response.payload.topic_name_list = all_topic_names

            except Exception:
                session.rollback()
                raise

# ################################################################################################################################
# ################################################################################################################################

class Subscribe(_BaseModifyTopicList):
    """ Subscribes security definition to one or more topics.
    """
    action = ModuleCtx.Action_Subsctibe

    def _modify_topic_list(self, existing_topic_names:'strlist', new_topic_names:'strlist') -> 'strlist':

        # Start with existing topics
        all_topic_names = existing_topic_names[:]

        # Add new topics that are not already in the list
        for new_topic_name in new_topic_names:
            if new_topic_name not in all_topic_names:
                all_topic_names.append(new_topic_name)

        return all_topic_names

# ################################################################################################################################
# ################################################################################################################################

class Unsubscribe(_BaseModifyTopicList):
    """ Unsubscribes security definition from one or more topics.
    """
    action = ModuleCtx.Action_Unsubsctibe

    def _modify_topic_list(self, existing_topic_names:'strlist', new_topic_names:'strlist') -> 'strlist':

        # Start with existing topics
        all_topic_names = existing_topic_names[:]

        # Remove topics that are in the new list
        for topic_to_remove in new_topic_names:
            if topic_to_remove in all_topic_names:
                all_topic_names.remove(topic_to_remove)

        return all_topic_names

# ################################################################################################################################
# ################################################################################################################################

class HandleDelivery(Service):

    def build_business_message(self, input:'strdict', sub_key:'str', delivery_count:'int') -> 'PubSubMessage':

        msg = PubSubMessage()

        msg.msg_id = input['msg_id']
        msg.correl_id = input['correl_id']

        msg.data = input['data']
        msg.size = input['size']

        msg.publisher = input['publisher']

        msg.pub_time_iso = input['pub_time_iso']
        msg.recv_time_iso = input['recv_time_iso']

        msg.priority = input['priority']
        msg.delivery_count = delivery_count

        msg.expiration = input['expiration']
        msg.expiration_time_iso = input['expiration_time_iso']

        msg.sub_key = sub_key
        msg.topic_name = input['topic_name']

        # Calculate and set time deltas
        current_time = utcnow()
        set_time_since(input, input['pub_time_iso'], input['recv_time_iso'], current_time)
        msg.time_since_pub = input['time_since_pub']
        msg.time_since_recv = input['time_since_recv']

        # These are optional
        if ext_client_id := input.get('ext_client_id'):
            msg.ext_client_id = ext_client_id

        if in_reply_to := input.get('in_reply_to'):
            msg.in_reply_to = in_reply_to

        return msg

# ################################################################################################################################

    def build_rest_message(self, input:'strdict', outconn_config:'strdict') -> 'strdict':

        # .. our message to produce ..
        out_msg = {}

        # .. now, go through everything we received ..
        for input_key, input_value in input.items():

            # .. special case the publisher because we don't want to reveal the username as is ..
            if input_key == 'publisher':

                # .. go through all the Basic Auth definitions ..
                for sec_config in self.server.worker_store.worker_config.basic_auth.values():

                    # .. dive deeper ..
                    sec_config = sec_config['config']

                    # .. OK, we have our match ..
                    if sec_config['username'] == input_value:
                        publisher = sec_config['name']
                        break

                # .. no match, e.g. it was deleted before we could handle the message ..
                else:
                    publisher = 'notset'

                # .. assign the publisher we found ..
                out_msg['publisher'] = publisher

            # .. assign all the other parameters ..
            else:
                out_msg[input_key] = input_value

        # .. calculate and set time deltas ..
        current_time = utcnow()
        set_time_since(out_msg, input['pub_time_iso'], input['recv_time_iso'], current_time)

        # .. and finally return the message to our caller.
        return out_msg

# ################################################################################################################################

    def handle(self):

        # Local aliases
        input:'strdict' = self.request.raw_request

        # Extract the metadata - and delete it from input because we don't want to deliver it
        meta = input.pop('_zato_meta')

        # Get the individual variables
        sub_key = meta['sub_key']
        delivery_count = meta['delivery_count']

        # Get the detailed configuration of the subscriber ..
        config = self.server.worker_store.get_pubsub_sub_config(sub_key)

        # .. we go here if we're to invoke a specific service
        if config.push_type == _push_type.Service:

            # .. the service we need to invoke ..
            service_name = config['push_service_name']

            # .. turn the incoming message into a business one ..
            msg = self.build_business_message(input, sub_key, delivery_count)

            # .. now, we can invoke our push service
            _ = self.invoke(service_name, msg)

        # .. and we go here if we're invoking a REST endpoint.
        elif config.push_type == _push_type.REST:

            # .. the REST connection we'll be invoking ..
            conn_name = config['rest_push_endpoint_name']

            # .. get the actual connection ..
            conn = self.out.rest[conn_name].conn

            # .. build the message to send ..
            out_msg = self.build_rest_message(input, config)

            # .. and OK, we can now invoke the connection
            _ = conn.post(self.cid, out_msg)

        # .. if we're here, it's an unrecognized push type and we cannot handle this message.
        else:
            msg = f'Unrecognized push_type: {repr(input.get("push_type"))} ({input.get("msg_id")} - {input.get("correl_id")})'
            raise Exception(msg)

# ################################################################################################################################
# ################################################################################################################################
