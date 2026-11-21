# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.importers.pubsub_subscription import PubSubSubscriptionImporter

# ################################################################################################################################
# ################################################################################################################################

class TestEnmassePubSubSubscriptionFlagsImporter(TestCase):
    """ The importer of pub/sub subscriptions reads is_pub_active and the flags of each topic.
    """

    def setUp(self) -> 'None':
        self.importer = PubSubSubscriptionImporter(None)

    def test_topic_name_string_defaults_to_enabled(self) -> 'None':
        """ A topic_list entry that is a name string enables publishing and delivery.
        """
        out = self.importer._normalize_topic_item('orders')

        self.assertEqual(out['name'], 'orders')
        self.assertTrue(out['is_pub_enabled'])
        self.assertTrue(out['is_delivery_enabled'])

    def test_topic_dict_carries_flags(self) -> 'None':
        """ A topic_list entry that is a dict carries is_pub_enabled and is_delivery_enabled.
        """
        out = self.importer._normalize_topic_item({
            'name': 'orders',
            'is_pub_enabled': False,
            'is_delivery_enabled': False,
        })

        self.assertEqual(out['name'], 'orders')
        self.assertFalse(out['is_pub_enabled'])
        self.assertFalse(out['is_delivery_enabled'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
