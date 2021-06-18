# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.test import rand_int, rand_string
from zato.server.connection.connector.subprocess_.impl.events.database import EventsDatabase

# ################################################################################################################################
# ################################################################################################################################

class EventsDatabaseTestCase(TestCase):

# ################################################################################################################################

    def test_init(self):

        logger = None
        fs_data_path = None
        sync_threshold = rand_int()
        sync_interval  = rand_int()

        events_db = EventsDatabase(logger, fs_data_path, sync_threshold, sync_interval)

        self.assertEqual(events_db.sync_threshold, sync_threshold)
        self.assertEqual(events_db.sync_interval, sync_interval)

# ################################################################################################################################

    def test_push(self):

        data = {
            'key1': rand_string()
        }

        logger = None
        fs_data_path = None
        sync_threshold = rand_int()
        sync_interval  = rand_int()

        events_db = EventsDatabase(logger, fs_data_path, sync_threshold, sync_interval)
        events_db.push(data)

        self.assertEqual(len(events_db.in_ram_store), 1)

        given_data = events_db.in_ram_store[0] # type: dict

        self.assertDictEqual(data, given_data)

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
