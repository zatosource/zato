# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from traceback import format_exc
from urllib.parse import quote

# Bunch
from bunch import Bunch

# Zato
from zato.common.broker_message import PUBSUB
from zato.common.api import PubSub
from zato.common.odb.model import Cluster, HTTPSOAP, PubSubSubscription, PubSubSubscriptionTopic, PubSubTopic, SecurityBase
from zato.common.odb.query import pubsub_subscription_list
from zato.common.pubsub.util import evaluate_pattern_match
from zato.common.util.api import new_sub_key
from zato.common.util.sql import elems_with_opaque
from zato.server.service import AsIs, PubSubMessage, Service
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.common.typing_ import strdict
# ################################################################################################################################
# ################################################################################################################################

_push_type = PubSub.Push_Type

# ################################################################################################################################
# ################################################################################################################################

def get_topic_link(topic_name:'str') -> 'str':
    topic_link = '<a href="/zato/pubsub/topic/?cluster=1&query={}">{}</a>'.format(quote(topic_name), topic_name)
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
        output_required = 'id', 'sub_key', 'is_active', 'created', AsIs('topic_links'), 'sec_base_id', 'sec_name', 'username', \
            'delivery_type', 'push_type', 'rest_push_endpoint_id', 'push_service_name'
        output_optional = 'rest_push_endpoint_name', AsIs('topic_names'), 'password'
        output_repeated = True

    def get_data(self, session):

        # Check if password should be included in the response
        needs_password = self.request.input.needs_password

        # Query always returns password now, but we only need to use it if requested
        result = self._search(pubsub_subscription_list, session, self.request.input.cluster_id, None, False)

        # Group by subscription ID
        subscriptions_by_id = {}
        topic_names_by_id = {}

        for item in result:

            sub_id = item.id
            topic_name = item.topic_name
            password = item.password

            if sub_id not in subscriptions_by_id:

                item_dict = item._asdict()

                # Include password in response only if requested
                if needs_password:
                    password = self.crypto.decrypt(password)
                    item_dict['password'] = password

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
            sub_dict['topic_names'] = sorted_topic_names

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
    """ Creates a new pub/sub subscription.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_subscription_create_request'
        response_elem = 'zato_pubsub_subscription_create_response'
        input_required = 'cluster_id', AsIs('topic_name_list'), 'sec_base_id', 'delivery_type'
        input_optional = 'is_active', 'push_type', 'rest_push_endpoint_id', 'push_service_name'
        output_required = 'id', 'sub_key', 'is_active', 'created', 'sec_name', 'delivery_type'
        output_optional = AsIs('topic_name_list'), AsIs('topic_link_list')

    def handle(self):

        # Our input
        input = self.request.input

        # A part of what we're returning
        topic_link_list = []
        topic_name_list = sorted(input.topic_name_list)

        with closing(self.odb.session()) as session:
            try:
                # Get cluster and security definition
                cluster = session.query(Cluster).filter_by(id=input.cluster_id).first()
                security_def = session.query(SecurityBase).filter_by(id=input.sec_base_id).first()

                # Generate a new subscription key
                sub_key = new_sub_key(security_def.username)

                # Get topics
                topics = []
                topic_names = []

                for topic_name in topic_name_list:
                    topic = session.query(PubSubTopic).\
                        filter(PubSubTopic.cluster_id==input.cluster_id).\
                        filter(PubSubTopic.name==topic_name).first()

                    if not topic:
                        raise Exception('Pub/sub topic with ID `{}` not found in this cluster'.format(topic_name))

                    topics.append(topic)
                    topic_names.append(topic.name)

                # Create the subscription
                sub = PubSubSubscription()
                sub.sub_key = sub_key # type: ignore
                sub.is_active = input.is_active
                sub.cluster = cluster
                sub.sec_base = security_def
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

                    with session.no_autoflush:
                        pattern_matched = evaluate_pattern_match(session, input.sec_base_id, input.cluster_id, topic.name)
                    sub_topic.pattern_matched = pattern_matched

                    session.add(sub_topic)

                    topic_link = get_topic_link(topic.name)
                    topic_link_list.append(topic_link)

                session.commit()

            except Exception:
                self.logger.error('Could not create pub/sub subscription, e:`%s`', format_exc())
                session.rollback()
                raise
            else:

                # Notify broker about the creation of a new subscription
                pubsub_msg = Bunch()
                pubsub_msg.cid = self.cid
                pubsub_msg.sub_key = sub.sub_key
                pubsub_msg.is_active = input.is_active
                pubsub_msg.sec_name = security_def.name # type: ignore
                pubsub_msg.username = security_def.username
                pubsub_msg.topic_name_list = topic_name_list
                pubsub_msg.action = PUBSUB.SUBSCRIPTION_CREATE.value

                self.broker_client.publish(pubsub_msg)
                self.broker_client.publish(pubsub_msg, routing_key='pubsub')

                self.response.payload.id = sub.id
                self.response.payload.sub_key = sub.sub_key
                self.response.payload.is_active = sub.is_active
                self.response.payload.created = sub.created
                self.response.payload.sec_name = security_def.name # type: ignore
                self.response.payload.delivery_type = sub.delivery_type

                self.response.payload.topic_name_list = topic_name_list
                self.response.payload.topic_link_list = sorted(topic_link_list)

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates a pub/sub subscription.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_subscription_edit_request'
        response_elem = 'zato_pubsub_subscription_edit_response'
        input_required = 'sub_key', 'cluster_id', AsIs('topic_id_list'), 'sec_base_id', 'delivery_type'
        input_optional = 'is_active', 'push_type', 'rest_push_endpoint_id', 'push_service_name'
        output_required = 'id', 'sub_key', 'is_active', 'sec_name', 'delivery_type', AsIs('topic_links')
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

                sub.sec_base_id = input.sec_base_id
                sub.delivery_type = input.delivery_type
                sub.is_active = input.is_active

                sub.push_type = input.push_type
                sub.rest_push_endpoint_id = input.rest_push_endpoint_id
                sub.push_service_name = input.push_service_name

                # Get the security definition
                sec_def = session.query(SecurityBase).\
                    filter(SecurityBase.id==sub.sec_base_id).\
                    one()

                # Delete all current topic associations
                _ = session.query(PubSubSubscriptionTopic).\
                    filter(PubSubSubscriptionTopic.subscription_id==sub.id).\
                    delete()

                # Process topics if any are provided
                topic_id_list = input.get('topic_id_list') or []
                topic_name_list = []
                topics = []

                if topic_id_list:

                    # Create new topic associations
                    for topic_id in topic_id_list:

                        # Make sure the topic exists
                        topic = session.query(PubSubTopic).\
                            filter(PubSubTopic.cluster_id==input.cluster_id).\
                            filter(PubSubTopic.id==topic_id).\
                            first()

                        if topic:
                            topics.append(topic)

                            # Create subscription-topic association
                            sub_topic = PubSubSubscriptionTopic()
                            sub_topic.cluster_id = input.cluster_id
                            sub_topic.subscription_id = sub.id
                            sub_topic.topic_id = topic.id

                            # Use no_autoflush to prevent premature flush during pattern evaluation
                            with session.no_autoflush:
                                pattern_matched = evaluate_pattern_match(session, input.sec_base_id, input.cluster_id, topic.name)
                            sub_topic.pattern_matched = pattern_matched

                            session.add(sub_topic)

                            # Create topic HTML link
                            topic_name = topic.name
                            topic_link = get_topic_link(topic_name)
                            topic_name_list.append(topic_link)

                # Commit all changes
                session.commit()

            except Exception:
                self.logger.error('Could not update pub/sub subscription, e:`%s`', format_exc())
                session.rollback()
                raise
            else:

                # Plain topic names (without HTML)
                plain_topic_names = []

                for topic in topics:
                    plain_topic_names.append(topic.name)

                # Make sure they're always sorted
                plain_topic_names.sort()

                # Notify broker about the update
                pubsub_msg = Bunch()
                pubsub_msg.cid = self.cid
                pubsub_msg.sub_key = input.sub_key
                pubsub_msg.is_active = input.is_active
                pubsub_msg.topic_name_list = plain_topic_names
                pubsub_msg.action = PUBSUB.SUBSCRIPTION_EDIT.value

                self.broker_client.publish(pubsub_msg)
                self.broker_client.publish(pubsub_msg, routing_key='pubsub')

                # Set response payload
                self.response.payload.id = sub.id
                self.response.payload.sub_key = sub.sub_key
                self.response.payload.is_active = sub.is_active
                self.response.payload.sec_name = sec_def.name
                self.response.payload.delivery_type = sub.delivery_type

                # Add topic links
                if topic_name_list:
                    topic_name_list = sorted(topic_name_list)
                    self.response.payload.topic_links = ', '.join(topic_name_list)
                    self.response.payload.topic_link_list = topic_name_list
                else:
                    self.response.payload.topic_links = []
                    self.response.payload.topic_link_list = []

                # Add topic names too
                self.response.payload.topic_name_list = plain_topic_names

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a pub/sub subscription.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_subscription_delete_request'
        response_elem = 'zato_pubsub_subscription_delete_response'
        input_required = 'id',

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                sub = session.query(PubSubSubscription).\
                    filter(PubSubSubscription.id==self.request.input.id).\
                    one()

                security_def = session.query(SecurityBase).\
                    filter(SecurityBase.id==sub.sec_base_id).\
                    one()

                session.delete(sub)
                session.commit()

            except Exception:
                self.logger.error('Could not delete pub/sub subscription, e:`%s`', format_exc())
                session.rollback()
                raise
            else:

                pubsub_msg = Bunch()
                pubsub_msg.cid = self.cid
                pubsub_msg.sub_key = sub.sub_key
                pubsub_msg.username = security_def.username
                pubsub_msg.action = PUBSUB.SUBSCRIPTION_DELETE.value

                self.broker_client.publish(pubsub_msg)
                self.broker_client.publish(pubsub_msg, routing_key='pubsub')

# ################################################################################################################################
# ################################################################################################################################

class HandleDelivery(Service):

    def build_business_message(self, input:'Bunch') -> 'PubSubMessage':

        msg = PubSubMessage()

        msg.msg_id = input.msg_id
        msg.correl_id = input.correl_id

        msg.data = input.data
        msg.size = input.size

        msg.publisher = input.publisher

        msg.pub_time_iso = input.pub_time_iso
        msg.recv_time_iso = input.recv_time_iso

        msg.priority = input.priority
        msg.delivery_count = input.delivery_count

        msg.expiration = input.expiration
        msg.expiration_time_iso = input.expiration_time_iso

        msg.ext_client_id = input.ext_client_id
        msg.in_reply_to = input.in_reply_to

        msg.sub_key = input.sub_key
        msg.topic_name = input.topic_name

        return msg

# ################################################################################################################################

    def build_rest_message(self, input:'Bunch', outconn_config:'strdict') -> 'strdict':

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

        # .. and finally return the message to our caller.
        return out_msg

# ################################################################################################################################

    def handle(self):

        # Local aliases
        input = self.request.raw_request

        # Get the detailed configuration of the subscriber ..
        config = self.server.worker_store.get_pubsub_sub_config(input.sub_key)

        # .. we go here if we're to invoke a specific service
        if config.push_type == _push_type.Service:

            # .. the service we need to invoke ..
            service_name = config['push_service_name']

            # .. turn the incoming message into a business one ..
            msg = self.build_business_message(input)

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
            msg = f'Unrecognized push_type: {repr(input.push_type)} ({input.msg_id} - {input.correl_id})'
            raise Exception(msg)

# ################################################################################################################################
# ################################################################################################################################
