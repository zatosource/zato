# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.importer import get_generic_connection_type

# ################################################################################################################################
# ################################################################################################################################

class TestGenericConnectionType(TestCase):
    """ Tests reading the connection type of zato_generic_connection items - the canonical type key
    and the type_ spelling both route an item to the same per-type importer.
    """

    def test_type_key(self):
        item = {'name': 'enmasse.jira.1', 'type': 'cloud-jira'}

        out = get_generic_connection_type(item)

        self.assertEqual(out, 'cloud-jira')

        # The value now lives under type_, which is what the per-type importers and the database column use.
        self.assertNotIn('type', item)
        self.assertEqual(item['type_'], 'cloud-jira')

# ################################################################################################################################

    def test_type_underscore_key(self):
        item = {'name': 'enmasse.jira.1', 'type_': 'cloud-jira'}

        out = get_generic_connection_type(item)

        self.assertEqual(out, 'cloud-jira')
        self.assertEqual(item['type_'], 'cloud-jira')

# ################################################################################################################################

    def test_both_spellings_route_the_same_way(self):

        item_with_type = {'name': 'enmasse.teams.1', 'type': 'chat-microsoft-teams'}
        item_with_type_underscore = {'name': 'enmasse.teams.2', 'type_': 'chat-microsoft-teams'}

        # This mirrors the routing loops in sync_from_yaml - items of one type are collected
        # into the list handled by that type's importer, whichever spelling each item carries.
        teams_list = []

        for item in [item_with_type, item_with_type_underscore]:
            item_type = get_generic_connection_type(item)
            if item_type == 'chat-microsoft-teams':
                teams_list.append(item)

        self.assertEqual(len(teams_list), 2)

# ################################################################################################################################

    def test_repeated_reads(self):

        # The routing loops in sync_from_yaml read each item once per connection type,
        # so the same item is read many times over.
        item = {'name': 'enmasse.slack.1', 'type': 'chat-slack'}

        first = get_generic_connection_type(item)
        second = get_generic_connection_type(item)

        self.assertEqual(first, 'chat-slack')
        self.assertEqual(second, 'chat-slack')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
