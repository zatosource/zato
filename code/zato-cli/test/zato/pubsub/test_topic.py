# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
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

    def _confirm_topic_created(self, out:'anydict', expected_prefix:'str') -> 'None':

        # We expect only for two keys to exist - id and name
        self.assertEqual(len(out), 2)

        topic_id   = out['id']   # type: int
        topic_name = out['name'] # type: str

        self.assertIsInstance(topic_id,   int)
        self.assertIsInstance(topic_name, str)

        self.assertTrue(topic_name.startswith(expected_prefix))
        self.assertTrue(len(topic_name) >= 30)

# ################################################################################################################################

    def test_create_topic_does_not_exist(self) -> 'None':

        # Test data
        expected_prefix = '/auto/topic.2'  # E.g. /auto/topic.2022_01_31T12_28_42_280577

        # Command to invoke ..
        cli_params = ['pubsub', 'create-topic']

        # .. get its response as a dict ..
        out = self.run_zato_cli_json_command(cli_params) # type: anydict

        # .. and confirm that the topic was created.
        self._confirm_topic_created(out, expected_prefix)

# ################################################################################################################################

    def test_create_topic_already_exists(self) -> 'None':

        # Test data
        prefix = 'test.already-exists.'
        topic_name = prefix + datetime.utcnow().isoformat()

        # Command to invoke ..
        cli_params = ['pubsub', 'create-topic', '--name', topic_name]

        # Create the topic once ..
        out = self.run_zato_cli_json_command(cli_params) # type: anydict

        # .. there should be no error yet
        self._confirm_topic_created(out, prefix)

        # .. create it once more ..
        out = self.run_zato_cli_json_command(cli_params) # type: anydict

        # now, we expect for three keys to exist - cid, result, and details
        self.assertEqual(len(out), 3)

        cid     = out['cid']    # type: str
        result  = out['result']  # type: str
        details = out['details'] # type: str

        expected_details_message = f'A pub/sub topic `{topic_name}` already exists in this cluster'

        self.assertTrue(len(cid) >= 20)
        self.assertEqual(result,  'Error')
        self.assertEqual(details, expected_details_message)

# ################################################################################################################################

    def _run_get_topic_test_one_topic(self, command:'str') -> 'None':
        pass

# ################################################################################################################################

    def _run_get_topic_test_multiple_topics(self, command:'str') -> 'None':
        pass

# ################################################################################################################################

    def test_get_topics(self) -> 'None':

        # Pub/sub command to run
        command = 'get-topics'

        # Run all tests
        self._run_get_topic_test_one_topic(command)
        self._run_get_topic_test_one_topic(command)

# ################################################################################################################################

    def test_get_topic(self) -> 'None':

        # Pub/sub command to run
        command = 'get-topic'

        # Run all tests
        self._run_get_topic_test_one_topic(command)
        self._run_get_topic_test_one_topic(command)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
