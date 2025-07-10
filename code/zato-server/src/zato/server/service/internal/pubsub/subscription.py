# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from traceback import format_exc
from urllib.parse import quote

# Zato
from zato.common.broker_message import PUBSUB
from zato.common.odb.model import Cluster, HTTPSOAP, PubSubSubscription, PubSubSubscriptionTopic, PubSubTopic, SecurityBase
from zato.common.odb.query import pubsub_subscription_list
from zato.common.util.api import new_sub_key
from zato.common.util.sql import elems_with_opaque
from zato.server.service import AsIs
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################
# ################################################################################################################################

def get_topic_link(topic_name:'str') -> 'str':
    topic_link = '<a href="/zato/pubsub/topic/?cluster=1&query={}">{}</a>'.format(quote(topic_name), topic_name)
    return topic_link

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of Pub/Sub subscriptions available.
    """
    _filter_by = PubSubSubscription.sub_key,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_pubsub_subscription_get_list_request'
        response_elem = 'zato_pubsub_subscription_get_list_response'
        input_required = 'cluster_id'
        output_required = 'id', 'sub_key', 'is_active', 'created', AsIs('topic_links'), 'sec_name', \
            'delivery_type', 'rest_push_endpoint_id'
        output_optional = 'rest_push_endpoint_name', AsIs('topic_names')

    def get_data(self, session):

        result = self._search(pubsub_subscription_list, session, self.request.input.cluster_id, None, False)

        # Group by subscription ID
        subscriptions_by_id = {}
        topic_names_by_id = {}

        for item in result:
            subscription, topic_name, sec_name, rest_push_endpoint_name = item
            sub_id = subscription.id

            if sub_id not in subscriptions_by_id:

                item_dict = subscription.asdict()
                item_dict['sec_name'] = sec_name
                item_dict['rest_push_endpoint_name'] = rest_push_endpoint_name
                subscriptions_by_id[sub_id] = item_dict

                # Initialize topic names list for this subscription
                topic_names_by_id[sub_id] = []

            # Store plain topic name if not already present
            if topic_name not in topic_names_by_id[sub_id]:
                topic_names_by_id[sub_id].append(topic_name)

        # Process data for each subscription
        data = []
        for sub_id, sub_dict in subscriptions_by_id.items():

            # Sort topic names
            sorted_topic_names = sorted(topic_names_by_id[sub_id])

            # Create topic links
            topic_links = [get_topic_link(name) for name in sorted_topic_names]

            # Store both fields
            sub_dict['topic_links'] = ', '.join(topic_links)
            sub_dict['topic_names'] = ', '.join(sorted_topic_names)

            data.append(sub_dict)

        return elems_with_opaque(data)

# ################################################################################################################################
# ################################################################################################################################

    def handle(self):
        with closing(self.odb.session()) as session:
            data = self.get_data(session)
            self.response.payload[:] = data

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new Pub/Sub subscription.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_subscription_create_request'
        response_elem = 'zato_pubsub_subscription_create_response'
        input_required = 'cluster_id', AsIs('topic_id_list'), 'sec_base_id', 'delivery_type'
        input_optional = 'is_active', 'rest_push_endpoint_id'
        output_required = 'id', 'sub_key', 'is_active', 'created', AsIs('topic_links'), 'sec_name', 'delivery_type'
        output_optional = AsIs('topic_names')

    def handle(self):

        # Our input
        input = self.request.input

        # A part of what we're returning
        topic_name_list = []

        with closing(self.odb.session()) as session:
            try:
                # Get cluster and security definition
                cluster = session.query(Cluster).filter_by(id=input.cluster_id).first()
                security_def = session.query(SecurityBase).filter_by(id=input.sec_base_id).first()

                # Generate a new subscription key
                sub_key = new_sub_key()

                # Get topics
                topic_id_list = input.topic_id_list
                topics = []
                topic_names = []

                for topic_id in topic_id_list:
                    topic = session.query(PubSubTopic).\
                        filter(PubSubTopic.cluster_id==input.cluster_id).\
                        filter(PubSubTopic.id==topic_id).first()

                    if not topic:
                        raise Exception('Pub/Sub topic with ID `{}` not found in this cluster'.format(topic_id))

                    topics.append(topic)
                    topic_names.append(topic.name)

                # Create the subscription
                subscription = PubSubSubscription()
                subscription.sub_key = sub_key # type: ignore
                subscription.is_active = input.is_active
                subscription.cluster = cluster
                subscription.sec_base = security_def
                subscription.delivery_type = input.delivery_type

                # For push subscriptions, set the endpoint
                if input.delivery_type == 'push' and input.get('rest_push_endpoint_id'):
                    endpoint = session.query(HTTPSOAP).\
                        filter(HTTPSOAP.id==input.rest_push_endpoint_id).first()
                    subscription.rest_push_endpoint = endpoint

                session.add(subscription)
                session.flush()  # Get the ID of the new subscription

                # Create subscription-topic associations
                for topic in topics:

                    sub_topic = PubSubSubscriptionTopic()
                    sub_topic.subscription = subscription
                    sub_topic.topic = topic
                    sub_topic.cluster = cluster
                    sub_topic.pattern_matched = topic.name

                    session.add(sub_topic)

                    # Append for later use
                    topic_link = get_topic_link(topic.name)
                    topic_name_list.append(topic_link)

                session.commit()

            except Exception:
                self.logger.error('Could not create Pub/Sub subscription, e:`%s`', format_exc())
                session.rollback()
                raise
            else:
                input.action = PUBSUB.SUBSCRIPTION_CREATE.value
                input.sub_key = sub_key
                self.broker_client.publish(input)

                self.response.payload.id = subscription.id
                self.response.payload.sub_key = subscription.sub_key
                self.response.payload.is_active = subscription.is_active
                self.response.payload.created = subscription.created
                self.response.payload.sec_name = security_def.name # type: ignore
                self.response.payload.delivery_type = subscription.delivery_type

                topic_name_list = sorted(topic_name_list)
                self.response.payload.topic_links = ', '.join(topic_name_list)

                # Add plain topic names (without HTML)
                plain_topic_names = []
                for topic in topics:
                    plain_topic_names.append(topic.name)
                self.response.payload.topic_names = ', '.join(sorted(plain_topic_names))

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates a Pub/Sub subscription.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_subscription_edit_request'
        response_elem = 'zato_pubsub_subscription_edit_response'
        input_required = 'sub_key', 'cluster_id', AsIs('topic_id_list'), 'sec_base_id', 'delivery_type'
        input_optional = 'is_active', 'rest_push_endpoint_id'
        output_required = 'id', 'sub_key', 'is_active', 'sec_name', 'delivery_type', AsIs('topic_links')
        output_optional = AsIs('topic_names')

    def handle(self):
        self.logger.info('DEBUG - Edit.handle - Starting subscription edit, input:`%s`', self.request.input)
        with closing(self.odb.session()) as session:
            try:
                # Get the subscription by sub_key
                self.logger.info('DEBUG - Edit.handle - Looking for subscription with sub_key:`%s` in cluster:`%s`',
                    self.request.input.sub_key, self.request.input.cluster_id)
                subscription = session.query(PubSubSubscription).\
                    filter(PubSubSubscription.cluster_id==self.request.input.cluster_id).\
                    filter(PubSubSubscription.sub_key==self.request.input.sub_key).\
                    one()
                self.logger.info('DEBUG - Edit.handle - Found subscription, id:`%s`', subscription.id)

                self.logger.info('DEBUG - Edit.handle - Updating subscription properties, sec_base_id:`%s`, delivery_type:`%s`, is_active:`%s`, rest_push_endpoint_id:`%s`',
                    self.request.input.sec_base_id, self.request.input.delivery_type,
                    self.request.input.is_active, self.request.input.rest_push_endpoint_id)
                subscription.sec_base_id = self.request.input.sec_base_id
                subscription.delivery_type = self.request.input.delivery_type

                subscription.is_active = self.request.input.is_active
                subscription.rest_push_endpoint_id = self.request.input.rest_push_endpoint_id

                # Get the security definition
                self.logger.info('DEBUG - Edit.handle - Getting security definition for id:`%s`', subscription.sec_base_id)
                security_def = session.query(SecurityBase).\
                    filter(SecurityBase.id==subscription.sec_base_id).\
                    one()
                self.logger.info('DEBUG - Edit.handle - Found security definition, name:`%s`', security_def.name)

                # Delete all current topic associations
                self.logger.info('DEBUG - Edit.handle - Deleting current topic associations for subscription_id:`%s`', subscription.id)
                deleted_count = session.query(PubSubSubscriptionTopic).\
                    filter(PubSubSubscriptionTopic.subscription_id==subscription.id).\
                    delete()
                self.logger.info('DEBUG - Edit.handle - Deleted `%s` topic associations', deleted_count)

                # Process topics if any are provided
                topic_id_list = self.request.input.get('topic_id_list') or []
                self.logger.info('DEBUG - Edit.handle - Processing `%s` topics from topic_id_list:`%s`',
                    len(topic_id_list), topic_id_list)
                topic_name_list = []
                topics = []

                if topic_id_list:
                    # Create new topic associations
                    for topic_id in topic_id_list:
                        # Make sure the topic exists
                        self.logger.info('DEBUG - Edit.handle - Looking for topic id:`%s` in cluster:`%s`',
                            topic_id, self.request.input.cluster_id)
                        topic = session.query(PubSubTopic).\
                            filter(PubSubTopic.cluster_id==self.request.input.cluster_id).\
                            filter(PubSubTopic.id==topic_id).\
                            first()

                        if topic:
                            self.logger.info('DEBUG - Edit.handle - Found topic, id:`%s`, name:`%s`', topic.id, topic.name)
                            topics.append(topic)

                            # Create subscription-topic association
                            self.logger.info('DEBUG - Edit.handle - Creating topic association subscription_id:`%s`, topic_id:`%s`',
                                subscription.id, topic.id)
                            st = PubSubSubscriptionTopic()
                            st.cluster_id = self.request.input.cluster_id
                            st.subscription_id = subscription.id
                            st.topic_id = topic.id
                            session.add(st)

                            # Create topic HTML link
                            topic_name = topic.name
                            topic_link = get_topic_link(topic_name)
                            topic_name_list.append(topic_link)
                        else:
                            self.logger.info('DEBUG - Edit.handle - Topic id:`%s` not found, skipping', topic_id)

                # Commit all changes
                self.logger.info('DEBUG - Edit.handle - Committing all changes to database')
                session.commit()
                self.logger.info('DEBUG - Edit.handle - Changes committed successfully')

            except Exception:
                self.logger.error('Could not update Pub/Sub subscription, e:`%s`', format_exc())
                self.logger.info('DEBUG - Edit.handle - Rolling back transaction due to error')
                session.rollback()
                raise
            else:
                # Notify broker about the update
                self.logger.info('DEBUG - Edit.handle - Notifying broker about subscription update, sub_key:`%s`, action:`%s`',
                    subscription.sub_key, PUBSUB.SUBSCRIPTION_EDIT.value)
                self.request.input.action = PUBSUB.SUBSCRIPTION_EDIT.value
                self.broker_client.publish(self.request.input)

                # Set response payload
                self.logger.info('DEBUG - Edit.handle - Setting response payload')
                self.response.payload.id = subscription.id
                self.response.payload.sub_key = subscription.sub_key
                self.response.payload.is_active = subscription.is_active
                self.response.payload.sec_name = security_def.name
                self.response.payload.delivery_type = subscription.delivery_type

                # Sort and join topic links
                self.logger.info('DEBUG - Edit.handle - Processing topic links, count:`%s`', len(topic_name_list))
                if topic_name_list:
                    topic_name_list = sorted(topic_name_list)
                    self.response.payload.topic_links = ', '.join(topic_name_list)
                    self.logger.info('DEBUG - Edit.handle - Topic links joined: `%s`', self.response.payload.topic_links)
                else:
                    self.response.payload.topic_links = []
                    self.logger.info('DEBUG - Edit.handle - No topic links to process')

                # Add plain topic names (without HTML)
                self.logger.info('DEBUG - Edit.handle - Processing plain topic names, count:`%s`', len(topics))
                if topics:
                    plain_topic_names = []
                    for topic in topics:
                        plain_topic_names.append(topic.name)
                    self.response.payload.topic_names = ', '.join(sorted(plain_topic_names))
                    self.logger.info('DEBUG - Edit.handle - Plain topic names joined: `%s`', self.response.payload.topic_names)
                else:
                    self.response.payload.topic_names = []
                    self.logger.info('DEBUG - Edit.handle - No plain topic names to process')

                self.logger.info('DEBUG - Edit.handle - Subscription edit complete, sub_key:`%s`', subscription.sub_key)

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a Pub/Sub subscription.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_subscription_delete_request'
        response_elem = 'zato_pubsub_subscription_delete_response'
        input_required = 'id',

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                subscription = session.query(PubSubSubscription).\
                    filter(PubSubSubscription.id==self.request.input.id).\
                    one()

                # Find all subscriptions with the same sub_key and sec_base_id (multi-topic subscription group)
                related_subscriptions = session.query(PubSubSubscription).\
                    filter(PubSubSubscription.sub_key==subscription.sub_key).\
                    filter(PubSubSubscription.sec_base_id==subscription.sec_base_id).\
                    all()

                # Delete all related subscriptions
                for related_sub in related_subscriptions:
                    session.delete(related_sub)

                session.commit()

            except Exception:
                self.logger.error('Could not delete Pub/Sub subscription, e:`%s`', format_exc())
                session.rollback()
                raise
            else:
                self.request.input.action = PUBSUB.SUBSCRIPTION_DELETE.value
                self.request.input.sub_key = subscription.sub_key
                self.broker_client.publish(self.request.input)

# ################################################################################################################################
# ################################################################################################################################
