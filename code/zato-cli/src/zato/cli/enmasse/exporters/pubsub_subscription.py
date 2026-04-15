# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, list_
    pubsub_subscription_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class PubSubSubscriptionExporter:

    def __init__(self, exporter) -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export(self, items) -> 'pubsub_subscription_def_list':
        """ Exports pub/sub subscription definitions.
        """
        logger.info('Exporting pub/sub subscription definitions')

        exported_subscriptions = []

        for item in items:

            security_name = item.get('security') or item.get('sec_name', '')
            delivery_type = item.get('delivery_type', '')
            topic_list = item.get('topic_list', [])

            if not security_name:
                logger.warning('Subscription missing security name, skipping')
                continue

            if not delivery_type:
                logger.warning('Subscription missing delivery_type for security=%s, skipping', security_name)
                continue

            subscription_data = {
                'security': security_name,
                'delivery_type': delivery_type,
                'topic_list': topic_list,
            }

            if delivery_type == 'push':
                push_rest_endpoint = item.get('push_rest_endpoint', '')
                if push_rest_endpoint:
                    subscription_data['push_rest_endpoint'] = push_rest_endpoint

                push_service = item.get('push_service', '')
                if push_service:
                    subscription_data['push_service'] = push_service

            exported_subscriptions.append(subscription_data)

        logger.info('Successfully prepared pub/sub subscription definitions for export: %s', exported_subscriptions)

        return exported_subscriptions

# ################################################################################################################################
# ################################################################################################################################
