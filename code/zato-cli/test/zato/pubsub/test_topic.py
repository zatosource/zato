# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main

# Zato
from zato.common.test import CommandLineTestCase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

class PubSubTopicTestCase(CommandLineTestCase):

    def test_create_topic(self) -> 'None':

        # Command to invoke ..
        cli_params = ['pubsub', 'create-topic']

        # .. and its response as a dict
        out = self.run_zato_cli_json_command(cli_params) # type: anydict

        # We expect only for two keys to exist - id and name
        self.assertEqual(len(out), 2)

        topic_id   = out['id']   # type: int
        topic_name = out['name'] # type: str

        self.assertIsInstance(topic_id,   int)
        self.assertIsInstance(topic_name, str)

        self.assertTrue(topic_name.startswith('/auto/topic.2')) # E.g. /auto/topic.2022_01_31T12_28_42_280577
        self.assertTrue(len(topic_name) >= 30)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
