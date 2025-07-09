# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import uuid
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common.api import PubSub
from zato.common.broker_message import PUBSUB
from zato.common.odb.model import PubSubSubscription, PubSubTopic
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
        output_required = 'id', 'sub_key', 'is_active', 'created', 'pattern_matched', 'topic_name', 'sec_name', 'delivery_type'

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
                grouped_data[sec_key] = item_dict

            grouped_data[sec_key]['topic_names'].append(topic_name)

        # Convert grouped data to list and format topic names
        data = []
        for item_dict in grouped_data.values():
            item_dict['topic_name'] = ', '.join(item_dict['topic_names'])
            del item_dict['topic_names']
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
        output_required = 'id', 'sub_key', 'is_active', 'created', 'topic_name', 'sec_name'

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

                    if existing_one:
                        continue  # Skip if already exists

                    item = PubSubSubscription()
                    item.cluster_id = self.request.input.cluster_id
                    item.topic_id = topic_id
                    item.sec_base_id = self.request.input.sec_base_id
                    item.sub_key = sub_key
                    item.is_active = self.request.input.get('is_active', True)
                    item.delivery_type = self.request.input.delivery_type
                    item.rest_push_endpoint_id = self.request.input.get('rest_push_endpoint_id') if self.request.input.delivery_type == PubSub.Delivery_Type.Push else None
                    # Ensure pattern_matched is set to default value immediately before save
                    item.pattern_matched = '*'

                    session.add(item)
                    created_subscriptions.append(item)

                session.commit()

                # Return info for the first created subscription
                if created_subscriptions:
                    first_item = created_subscriptions[0]

                    # Get topic and security names for the response
                    topic = session.query(PubSubTopic).filter(PubSubTopic.id == first_item.topic_id).first()
                    from zato.common.odb.model import SecurityBase
                    security = session.query(SecurityBase).filter(SecurityBase.id == first_item.sec_base_id).first()

                    self.response.payload.id = first_item.id
                    self.response.payload.sub_key = first_item.sub_key
                    self.response.payload.is_active = first_item.is_active
                    self.response.payload.created = first_item.created.isoformat()
                    self.response.payload.topic_name = topic.name if topic else ''
                    self.response.payload.sec_name = security.name if security else ''
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
        input_required = 'id', 'cluster_id', AsIs('topic_id_list'), 'sec_base_id', 'delivery_type'
        input_optional = 'is_active', 'rest_push_endpoint_id'
        output_required = 'id', 'sub_key'

    def handle(self):
        self.logger.info('[DEBUG] Edit.handle: Starting subscription edit')
        self.logger.info('[DEBUG] Edit.handle: Request input type=%s', type(self.request.input))
        self.logger.info('[DEBUG] Edit.handle: Request input.__dict__=%s', getattr(self.request.input, '__dict__', 'no __dict__'))

        # Log specific input fields
        for attr in ['id', 'topic_id_list', 'sec_base_id', 'delivery_type', 'is_active', 'rest_push_endpoint_id']:
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

                # Get the original subscription to preserve sub_key
                original_item = session.query(PubSubSubscription).filter(PubSubSubscription.id==self.request.input.id).one()
                original_sub_key = original_item.sub_key
                self.logger.info('[DEBUG] Edit.handle: original sub_key=%s', original_sub_key)

                # Delete all existing subscriptions with this sub_key
                existing_subscriptions = session.query(PubSubSubscription).\
                    filter(PubSubSubscription.cluster_id==self.request.input.cluster_id).\
                    filter(PubSubSubscription.sub_key==original_sub_key).\
                    all()

                for existing_sub in existing_subscriptions:
                    session.delete(existing_sub)
                    self.logger.info('[DEBUG] Edit.handle: deleted existing subscription id=%s topic_id=%s', existing_sub.id, existing_sub.topic_id)

                # Create new subscriptions for each topic with the same sub_key, skipping existing ones
                created_subscriptions = []
                for topic_id in topic_id_list:
                    # Check if subscription already exists for this topic and security definition
                    existing_one = session.query(PubSubSubscription).\
                        filter(PubSubSubscription.cluster_id==self.request.input.cluster_id).\
                        filter(PubSubSubscription.topic_id==topic_id).\
                        filter(PubSubSubscription.sec_base_id==self.request.input.sec_base_id).\
                        first()

                    if existing_one:
                        self.logger.info('[DEBUG] Edit.handle: skipping topic_id=%s, subscription already exists', topic_id)
                        continue

                    new_subscription = PubSubSubscription()
                    new_subscription.cluster_id = self.request.input.cluster_id
                    new_subscription.topic_id = topic_id
                    new_subscription.sec_base_id = self.request.input.sec_base_id
                    new_subscription.delivery_type = self.request.input.delivery_type
                    new_subscription.rest_push_endpoint_id = self.request.input.get('rest_push_endpoint_id') if self.request.input.delivery_type == PubSub.Delivery_Type.Push else None
                    new_subscription.pattern_matched = '*'
                    new_subscription.is_active = self.request.input.get('is_active', True)
                    new_subscription.sub_key = original_sub_key  # Keep the same sub_key

                    session.add(new_subscription)
                    created_subscriptions.append(new_subscription)
                    self.logger.info('[DEBUG] Edit.handle: created new subscription topic_id=%s sub_key=%s', topic_id, original_sub_key)

                session.commit()

                # Return the first created subscription's info (they all have the same sub_key)
                self.response.payload.id = created_subscriptions[0].id
                self.response.payload.sub_key = original_sub_key

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
