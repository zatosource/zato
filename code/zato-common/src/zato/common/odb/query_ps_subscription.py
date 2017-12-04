# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common import PUBSUB
from zato.common.odb.model import Cluster, PubSubTopic, PubSubEndpoint, PubSubSubscription
from zato.common.odb.query import query_wrapper

# SQLAlchemy
from sqlalchemy import func

# ################################################################################################################################

_subscriber_role = (PUBSUB.ROLE.PUBLISHER_SUBSCRIBER.id, PUBSUB.ROLE.SUBSCRIBER.id)

# ################################################################################################################################

def _pubsub_subscription(session, cluster_id):
    return session.query(
        PubSubSubscription.id,
        PubSubSubscription.id.label('name'), # A unique 'name' attribute is needed by ConfigDict
        PubSubSubscription.active_status,
        PubSubSubscription.server_id,
        #PubSubSubscription.server_pid,
        PubSubSubscription.is_internal,
        PubSubSubscription.creation_time,
        PubSubSubscription.sub_key,
        PubSubSubscription.is_durable,
        PubSubSubscription.has_gd,
        PubSubSubscription.topic_id,
        PubSubSubscription.endpoint_id,
        PubSubSubscription.delivery_method,
        PubSubSubscription.delivery_data_format,
        PubSubSubscription.delivery_batch_size,
        PubSubSubscription.wrap_one_msg_in_list,
        PubSubSubscription.delivery_max_retry,
        PubSubSubscription.ext_client_id,

        PubSubSubscription.out_amqp_id,
        PubSubSubscription.amqp_exchange,
        PubSubSubscription.amqp_routing_key,

        PubSubSubscription.files_directory_list,

        PubSubSubscription.ftp_directory_list,

        PubSubSubscription.sms_twilio_from,
        PubSubSubscription.sms_twilio_to_list,

        PubSubSubscription.smtp_is_html,
        PubSubSubscription.smtp_subject,
        PubSubSubscription.smtp_from,
        PubSubSubscription.smtp_to_list,
        PubSubSubscription.smtp_body,

        PubSubSubscription.out_http_soap_id,
        PubSubSubscription.delivery_endpoint,

        PubSubSubscription.ws_sub_id,
        PubSubSubscription.ws_channel_id,
        PubSubSubscription.cluster_id,

        PubSubTopic.name.label('topic_name'),
        PubSubEndpoint.name.label('endpoint_name'),
        PubSubEndpoint.endpoint_type,
        PubSubEndpoint.service_id,
        ).\
        outerjoin(PubSubTopic, PubSubTopic.id==PubSubSubscription.topic_id).\
        filter(PubSubEndpoint.id==PubSubSubscription.endpoint_id).\
        filter(Cluster.id==PubSubSubscription.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(PubSubSubscription.id)

# ################################################################################################################################

def pubsub_subscription(session, cluster_id, id):
    """ A pub/sub subscription.
    """
    return _pubsub_subscription(session, cluster_id).\
        filter(PubSubSubscription.id==id).\
        one()

# ################################################################################################################################

@query_wrapper
def pubsub_subscription_list(session, cluster_id, needs_columns=False):
    """ All pub/sub subscriptions.
    """
    return _pubsub_subscription(session, cluster_id)

# ################################################################################################################################

def pubsub_subscription_list_by_endpoint_id(session, cluster_id, endpoint_id):
    """ A list of all pub/sub subscriptions for a given endpoint.
    """
    return _pubsub_subscription(session, cluster_id).\
        filter(PubSubSubscription.endpoint_id==endpoint_id).\
        all()

# ################################################################################################################################

@query_wrapper
def pubsub_endpoint_summary_list(session, cluster_id, needs_columns=False):
    return session.query(
        PubSubEndpoint.id,
        PubSubEndpoint.is_active,
        PubSubEndpoint.is_internal,
        PubSubEndpoint.role,
        PubSubEndpoint.name.label('endpoint_name'),
        PubSubEndpoint.endpoint_type,
        PubSubEndpoint.last_seen,
        PubSubEndpoint.last_deliv_time,
        func.count(PubSubSubscription.id).label('subscription_count'),
        ).\
        group_by(PubSubEndpoint.id).\
        outerjoin(PubSubSubscription, PubSubEndpoint.id==PubSubSubscription.endpoint_id).\
        filter(Cluster.id==PubSubEndpoint.cluster_id).\
        filter(Cluster.id==cluster_id).\
        filter(PubSubEndpoint.role.in_(_subscriber_role)).\
        order_by(PubSubEndpoint.id)

# ################################################################################################################################
