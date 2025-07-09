# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import uuid
from contextlib import closing
from traceback import format_exc
from urllib.parse import quote

# Zato
from zato.common.api import PubSub
from zato.common.broker_message import PUBSUB
from zato.common.odb.model import PubSubSubscription, PubSubTopic, SecurityBase
from zato.common.odb.query import pubsub_subscription_list
from zato.common.util.sql import elems_with_opaque
from zato.server.service import AsIs
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of Pub/Sub subscriptions available.
    """
    _filter_by = PubSubSubscription.sub_key,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_pubsub_subscription_get_list_request'
        response_elem = 'zato_pubsub_subscription_get_list_response'
        input_required = 'cluster_id',
        output_required = 'id', 'sub_key', 'is_active', 'created', 'pattern_matched', AsIs('topic_name'), 'sec_name', 'delivery_type'

    def get_data(self, session):
        result = self._search(pubsub_subscription_list, session, self.request.input.cluster_id, None, False)

        # Group subscriptions by security definition
        grouped_data = {}

        for subscription, topic_name, sec_name, rest_push_endpoint_name in result:
            sec_key = '{}_{}_{}_{}'.format(subscription.sec_base_id, subscription.sub_key, subscription.delivery_type, subscription.is_active)

            if sec_key not in grouped_data:
                item_dict = subscription.asdict()
                item_dict['sec_name'] = sec_name
                item_dict['rest_push_endpoint_name'] = rest_push_endpoint_name or ''
                item_dict['topic_names'] = []
                item_dict['topic_ids'] = []
                grouped_data[sec_key] = item_dict

            grouped_data[sec_key]['topic_names'].append(topic_name)
            grouped_data[sec_key]['topic_ids'].append(subscription.topic_id)

        # Convert grouped data to list and format topic names as links
        data = []
        for item_dict in grouped_data.values():
            # Create links for each topic name
            topic_links = []
            for topic_name in item_dict['topic_names']:
                topic_link = '<a href="/zato/pubsub/topic/?cluster=1&query={}">{}</a>'.format(
                    quote(topic_name), topic_name)
                topic_links.append(topic_link)

            item_dict['topic_name'] = ', '.join(topic_links)
            del item_dict['topic_names']
            del item_dict['topic_ids']
            data.append(item_dict)

        return elems_with_opaque(data)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

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
        output_required = 'id', 'sub_key', 'is_active', 'created', 'topic_name', 'sec_name', 'delivery_type'

    def handle(self):
        self.logger.info('[DEBUG] Create.handle: Starting subscription creation')
        self.logger.info('[DEBUG] Create.handle: Request input type=%s', type(self.request.input))
        self.logger.info('[DEBUG] Create.handle: Request input.__dict__=%s', getattr(self.request.input, '__dict__', 'no __dict__'))

        # Log specific input fields
        for attr in ['topic_id_list', 'sec_base_id', 'delivery_type', 'is_active', 'rest_push_endpoint_id']:
            if hasattr(self.request.input, attr):
                value = getattr(self.request.input, attr)
                self.logger.info('[DEBUG] Create.handle: Input %s type=%s, value=%s', attr, type(value), value)

        with closing(self.odb.session()) as session:
            try:
                # Handle multiple topic IDs
                topic_ids = self.request.input.topic_id_list
                self.logger.info('[DEBUG] Create.handle: topic_ids before processing type=%s, value=%s', type(topic_ids), topic_ids)

                if isinstance(topic_ids, str):
                    topic_ids = [topic_ids]
                elif not isinstance(topic_ids, list):
                    topic_ids = [topic_ids]

                self.logger.info('[DEBUG] Create.handle: topic_ids after processing type=%s, value=%s', type(topic_ids), topic_ids)

                created_subscriptions = []
                # Generate single sub_key for all subscriptions in this operation
                sub_key = 'zpsk.rest.' + uuid.uuid4().hex[:6]

                for topic_id in topic_ids:
                    # Check if subscription already exists for this topic
                    existing_one = session.query(PubSubSubscription).\
                        filter(PubSubSubscription.cluster_id==self.request.input.cluster_id).\
                        filter(PubSubSubscription.topic_id==topic_id).\
                        filter(PubSubSubscription.sec_base_id==self.request.input.sec_base_id).\
                        first()

                    # Skip if it already exists
                    if existing_one:
                        continue

                    item = PubSubSubscription()
                    item.cluster_id = self.request.input.cluster_id
                    item.topic_id = topic_id
                    item.sec_base_id = self.request.input.sec_base_id
                    item.sub_key = sub_key # type: ignore
                    item.is_active = self.request.input.get('is_active', True)
                    item.delivery_type = self.request.input.delivery_type
                    item.rest_push_endpoint_id = self.request.input.get('rest_push_endpoint_id') if self.request.input.delivery_type == PubSub.Delivery_Type.Push else None
                    # Ensure pattern_matched is set to default value immediately before save
                    item.pattern_matched = '*' # type: ignore

                    session.add(item)
                    created_subscriptions.append(item)

                session.commit()

                # Return info for the created subscriptions - get all topic names
                if created_subscriptions:
                    first_item = created_subscriptions[0]

                    # Get all topic names for this subscription group
                    topic_names = []
                    for subscription in created_subscriptions:
                        topic = session.query(PubSubTopic).filter(PubSubTopic.id == subscription.topic_id).first()
                        if topic:
                            topic_names.append(topic.name)

                    # Create links for each topic name
                    topic_links = []
                    for topic_name in topic_names:
                        topic_link = '<a href="/zato/pubsub/topic/?cluster=1&query={}">{}</a>'.format(
                            quote(topic_name), topic_name)
                        topic_links.append(topic_link)

                    # Get security name
                    from zato.common.odb.model import SecurityBase
                    security = session.query(SecurityBase).filter(SecurityBase.id == first_item.sec_base_id).first()

                    self.response.payload.id = first_item.id
                    self.response.payload.sub_key = first_item.sub_key
                    self.response.payload.is_active = first_item.is_active
                    self.response.payload.created = first_item.created.isoformat()
                    self.response.payload.topic_name = ', '.join(topic_links)
                    self.response.payload.sec_name = security.name if security else ''
                    self.response.payload.delivery_type = first_item.delivery_type
                else:
                    self.logger.info('[DEBUG] Create.handle: No new subscriptions created - some may already exist')
                    # Find an existing subscription to return in response
                    first_topic_id = topic_ids[0] if topic_ids else None
                    if first_topic_id:
                        existing_item = session.query(PubSubSubscription).\
                            filter(PubSubSubscription.cluster_id==self.request.input.cluster_id).\
                            filter(PubSubSubscription.topic_id==first_topic_id).\
                            filter(PubSubSubscription.sec_base_id==self.request.input.sec_base_id).\
                            first()

                        if existing_item:
                            # Get topic and security names for the response
                            topic = session.query(PubSubTopic).filter(PubSubTopic.id == existing_item.topic_id).first()
                            from zato.common.odb.model import SecurityBase
                            security = session.query(SecurityBase).filter(SecurityBase.id == existing_item.sec_base_id).first()

                            self.response.payload.id = existing_item.id
                            self.response.payload.sub_key = existing_item.sub_key
                            self.response.payload.is_active = existing_item.is_active
                            self.response.payload.created = existing_item.created.isoformat()
                            self.response.payload.topic_name = topic.name if topic else ''
                            self.response.payload.sec_name = security.name if security else ''

            except Exception:
                self.logger.error('Could not create Pub/Sub subscription, e:`%s`', format_exc())
                session.rollback()
                raise

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
        output_required = 'id', 'sub_key', AsIs('topic_name_list'), 'topic_name', 'sec_name', 'delivery_type', 'is_active'

    def handle(self):
        self.logger.info('[DEBUG] Edit.handle: Starting subscription edit')
        self.logger.info('[DEBUG] Edit.handle: Request input type=%s', type(self.request.input))
        self.logger.info('[DEBUG] Edit.handle: Request input.__dict__=%s', getattr(self.request.input, '__dict__', 'no __dict__'))

        # Log specific input fields
        for attr in ['sub_key', 'topic_id_list', 'sec_base_id', 'delivery_type', 'is_active', 'rest_push_endpoint_id']:
            if hasattr(self.request.input, attr):
                value = getattr(self.request.input, attr)
                self.logger.info('[DEBUG] Edit.handle: Input %s type=%s, value=%s', attr, type(value), value)

        with closing(self.odb.session()) as session:
            try:
                # Handle topic_id_list - process all topics for edit
                topic_id_list = self.request.input.topic_id_list
                self.logger.info('[DEBUG] Edit.handle: topic_id_list before processing type=%s, value=%s', type(topic_id_list), topic_id_list)

                # Normalize topic_id_list to always be a list
                if not isinstance(topic_id_list, list):
                    topic_id_list = [topic_id_list]

                if not topic_id_list:
                    raise Exception('No topic selected')

                # Convert string IDs to integers
                topic_id_list = [int(topic_id) for topic_id in topic_id_list]
                self.logger.info('[DEBUG] Edit.handle: normalized topic_id_list=%s', topic_id_list)

                # The input sub_key is actually the subscription ID, find the real sub_key
                subscription_id = self.request.input.sub_key
                self.logger.info('[DEBUG] Edit.handle: using subscription_id=%s', subscription_id)

                # Find one existing subscription to get the actual sub_key
                sub = session.query(PubSubSubscription).\
                    filter(PubSubSubscription.cluster_id==self.request.input.cluster_id).\
                    filter(PubSubSubscription.id==subscription_id).\
                    first()

                if not sub:
                    raise Exception(f'Subscription with ID {subscription_id} not found')

                sub_key = sub.sub_key
                self.logger.info('[DEBUG] Edit.handle: found sub_key=%s for id=%s', sub_key, subscription_id)

                # Delete ALL existing subscriptions with the same sub_key
                existing_subscriptions = session.query(PubSubSubscription).\
                    filter(PubSubSubscription.cluster_id==self.request.input.cluster_id).\
                    filter(PubSubSubscription.sub_key==sub_key).\
                    all()

                for existing_sub in existing_subscriptions:
                    session.delete(existing_sub)
                    self.logger.info('[DEBUG] Edit.handle: deleted existing subscription id=%s topic_id=%s sub_key=%s', existing_sub.id, existing_sub.topic_id, existing_sub.sub_key)

                # Flush deletes to database before creating new subscriptions
                session.flush()
                self.logger.info('[DEBUG] Edit.handle: flushed deletions to database')

                # Create new subscriptions for each topic with the same sub_key
                created_subscriptions = []
                for topic_id in topic_id_list:
                    new_subscription = PubSubSubscription()
                    new_subscription.cluster_id = self.request.input.cluster_id
                    new_subscription.topic_id = topic_id # type: ignore
                    new_subscription.sec_base_id = self.request.input.sec_base_id
                    new_subscription.delivery_type = self.request.input.delivery_type
                    new_subscription.rest_push_endpoint_id = self.request.input.get('rest_push_endpoint_id') if self.request.input.delivery_type == PubSub.Delivery_Type.Push else None
                    new_subscription.pattern_matched = '*' # type: ignore
                    new_subscription.is_active = self.request.input.get('is_active', True)
                    new_subscription.sub_key = sub_key

                    session.add(new_subscription)
                    created_subscriptions.append(new_subscription)
                    self.logger.info('[DEBUG] Edit.handle: created new subscription topic_id=%s sub_key=%s', topic_id, sub_key)

                session.commit()

                # Get topic names for the created subscriptions
                topic_names = []
                for sub in created_subscriptions:
                    topic = session.query(PubSubTopic).filter(PubSubTopic.id == sub.topic_id).one()
                    topic_names.append(topic.name)

                self.logger.info('[DEBUG] Edit.handle: created subscriptions for topics=%s', topic_names)

                # Return subscription info with topic names for frontend display
                self.response.payload.id = subscription_id  # Frontend needs this to update table row
                self.response.payload.sub_key = sub_key
                self.response.payload.topic_name_list = topic_names
                # Convert to comma-separated string for table display
                self.response.payload.topic_name = ', '.join(topic_names)

                # Add other fields needed for table display
                # Get security name from sec_base_id
                sec_base = session.query(SecurityBase).filter(SecurityBase.id == self.request.input.sec_base_id).one_or_none()
                self.response.payload.sec_name = sec_base.name if sec_base else ''
                self.response.payload.delivery_type = self.request.input.delivery_type
                self.response.payload.is_active = self.request.input.is_active

            except Exception:
                self.logger.error('Could not update Pub/Sub subscription, e:`%s`', format_exc())
                session.rollback()
                raise

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

                session.delete(subscription)
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
