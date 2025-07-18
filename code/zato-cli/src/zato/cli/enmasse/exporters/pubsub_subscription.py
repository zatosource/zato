# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.odb.query import pubsub_subscription_list

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, strlist
    SASession = SASession
    EnmasseYAMLExporter = EnmasseYAMLExporter
    anydict = anydict
    strlist = strlist
    pubsub_subscription_def_list = strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class PubSubSubscriptionExporter:

    def __init__(self, exporter: 'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export(self, session: 'SASession', cluster_id: 'int') -> 'pubsub_subscription_def_list':
        """ Exports pub/sub subscription definitions from the database.
        """
        logger.info('Exporting pub/sub subscription definitions')
        exported_subscriptions = []

        query_result = pubsub_subscription_list(session, cluster_id, needs_columns=False)
        search_results = query_result[0]
        items = search_results.result

        # Group subscriptions by subscription ID to collect all topics
        subscription_groups = {}

        for item in items:
            # Each item contains subscription data and related information
            subscription_id = item.id
            security_name = item.sec_name
            delivery_type = item.delivery_type
            push_type = item.push_type
            rest_push_endpoint_name = item.rest_push_endpoint_name
            push_service_name = item.push_service_name
            topic_name = item.topic_name

            # Only export subscriptions for enmasse security definitions
            if not security_name.startswith('enmasse'):
                continue

            # Validate required fields exist
            if not security_name:
                raise ValueError(f'Subscription missing security name: subscription_id={subscription_id}')

            if not delivery_type:
                raise ValueError(f'Subscription missing delivery_type: subscription_id={subscription_id} security={security_name}')

            if not topic_name:
                raise ValueError(f'Subscription missing topic_name: subscription_id={subscription_id} security={security_name}')

            # Initialize subscription group if not exists
            if subscription_id not in subscription_groups:
                subscription_data = {
                    'security': security_name,
                    'delivery_type': delivery_type,
                    'topic_list': []
                }

                # Add push-specific fields
                if delivery_type == 'push':
                    if push_type == 'rest':
                        if not rest_push_endpoint_name:
                            raise ValueError(f'Push subscription missing rest_push_endpoint_name: subscription_id={subscription_id} security={security_name}')
                        subscription_data['push_rest_endpoint'] = rest_push_endpoint_name
                    elif push_type == 'service':
                        if not push_service_name:
                            raise ValueError(f'Push subscription missing push_service_name: subscription_id={subscription_id} security={security_name}')
                        subscription_data['push_service'] = push_service_name
                    else:
                        raise ValueError(f'Push subscription has unknown push_type {push_type}: subscription_id={subscription_id} security={security_name}')

                subscription_groups[subscription_id] = subscription_data

            # Add topic to the subscription's topic list
            subscription_data = subscription_groups[subscription_id]
            if topic_name not in subscription_data['topic_list']:
                subscription_data['topic_list'].append(topic_name)

        # Convert grouped subscriptions to export format
        for subscription_data in subscription_groups.values():
            exported_subscriptions.append(subscription_data)

        logger.info('Successfully prepared %d pub/sub subscription definitions for export', len(exported_subscriptions))
        return exported_subscriptions

# ################################################################################################################################
# ################################################################################################################################
