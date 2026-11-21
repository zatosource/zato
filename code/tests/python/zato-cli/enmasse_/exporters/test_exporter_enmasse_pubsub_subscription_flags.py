# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from types import SimpleNamespace
from unittest import TestCase, main
from unittest.mock import MagicMock

# Zato
from zato.cli.enmasse.exporters.pubsub_subscription import PubSubSubscriptionExporter
from zato.common.api import PubSub

# ################################################################################################################################
# ################################################################################################################################

class TestEnmassePubSubSubscriptionFlagsExporter(TestCase):
    """ The exporter of pub/sub subscriptions writes is_pub_active and the flags of each topic.
    """

    def test_export_includes_flags(self) -> 'None':
        """ Each exported subscription carries is_pub_active and the flags of every topic.
        """
        row = SimpleNamespace(
            id=1,
            delivery_type='pull',
            push_type=None,
            rest_push_endpoint_id=None,
            push_service_name=None,
            is_delivery_active=True,
            is_pub_active=False,
            topic_name='orders',
            is_pub_enabled=False,
            is_delivery_enabled=True,
            sec_name='client.1',
            rest_push_endpoint_name=None,
        )

        session = MagicMock()
        query = session.query.return_value
        query.join.return_value = query
        query.outerjoin.return_value = query
        query.order_by.return_value = query
        query.all.return_value = [row]

        exporter = PubSubSubscriptionExporter(None)
        out = exporter.export(session)

        self.assertEqual(len(out), 1)
        self.assertFalse(out[0]['is_pub_active'])
        self.assertEqual(out[0]['topic_list'][0]['name'], 'orders')
        self.assertFalse(out[0]['topic_list'][0]['is_pub_enabled'])
        self.assertTrue(out[0]['topic_list'][0]['is_delivery_enabled'])
        self.assertEqual(out[0]['delivery_type'], PubSub.Delivery_Type.Pull)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
