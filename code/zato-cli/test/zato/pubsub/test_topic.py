# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from unittest import main

# gevent
from gevent import sleep

# Zato
from zato.cli.pubsub.topic import Config as CLITopicConfig
from zato.common.api import PUBSUB
from zato.common.test import CommandLineTestCase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_default = PUBSUB.DEFAULT

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

    def _run_get_topic_no_such_topic(self, command:'str') -> 'None':

        # There will be no such topic
        topic_name = '/no/such/topic/' + datetime.utcnow().isoformat()

        # Command to invoke ..
        get_cli_params = ['pubsub', command, '--name', topic_name]

        # Get the result - there should be none
        out = self.run_zato_cli_json_command(get_cli_params) # type: any_
        self.assertListEqual(out, [])

# ################################################################################################################################

    def _run_get_topic_test_one_topic(self, command:'str') -> 'None':

        # Test data
        prefix = '/test/'
        topic_name = prefix + datetime.utcnow().isoformat()

        # Command to invoke ..
        create_cli_params = ['pubsub', 'create-topic', '--name', topic_name]

        # Create one topic  ..
        create_out = self.run_zato_cli_json_command(create_cli_params) # type: anydict

        # Command to get the topic back with ..
        get_cli_params = ['pubsub', command, '--name', topic_name]

        # Now, we expect to get that one topic back
        out_get = self.run_zato_cli_json_command(get_cli_params) # type: any_

        # There must be one topic on output
        self.assertTrue(len(out_get), 1)

        # Extract it now ..
        out = out_get[0] # type: anydict

        # .. and run our assertions.

        self.assertEqual(out['id'],   create_out['id'])
        self.assertEqual(out['name'], create_out['name'])
        self.assertEqual(out['name'], topic_name)

        # This is a new topic and we do not expect any sort of publication-related information associated with it.
        self.assertEqual(out['current_depth_gd'], 0)
        self.assertIsNone(out['last_pub_time'])
        self.assertIsNone(out['last_pub_msg_id'])
        self.assertIsNone(out['last_endpoint_name'])
        self.assertIsNone(out['last_pub_server_name'])
        self.assertIsNone(out['last_pub_server_pid'])
        self.assertIsNone(out['last_pub_has_gd'])

# ################################################################################################################################

    def _run_get_topic_test_multiple_topics(self, command:'str') -> 'None':

        # Note that the prefix itself is unique to ensure that it will not repeat
        prefix = '/test/' + datetime.utcnow().isoformat() + '/'

        # Sleep for a moment to make sure that prefix and the rest are different
        sleep(0.05)

        # Both
        topic_name0 = prefix + datetime.utcnow().isoformat()

        # Again, ensure the names are different
        sleep(0.05)

        topic_name1 = prefix + datetime.utcnow().isoformat()

        # Create both topics now
        create_cli_params0 = ['pubsub', 'create-topic', '--name', topic_name0]
        create_cli_params1 = ['pubsub', 'create-topic', '--name', topic_name1]

        create_out0 = self.run_zato_cli_json_command(create_cli_params0) # type: anydict
        create_out1 = self.run_zato_cli_json_command(create_cli_params1) # type: anydict

        # Command to get the two topics with - note that it uses the prefix to ensure that both are returned ..
        get_cli_params = ['pubsub', command, '--name', prefix]

        # Now, we expect to get that one topic back
        out_get = self.run_zato_cli_json_command(get_cli_params) # type: any_

        # Both topics must be on output
        self.assertTrue(len(out_get), 2)

        # Extract them now ..
        out0 = out_get[0] # type: anydict
        out1 = out_get[1] # type: anydict

        # .. and run our assertions ..

        self.assertEqual(out0['id'],   create_out0['id'])
        self.assertEqual(out0['name'], create_out0['name'])
        self.assertEqual(out0['name'], topic_name0)

        self.assertEqual(out1['id'],   create_out1['id'])
        self.assertEqual(out1['name'], create_out1['name'])
        self.assertEqual(out1['name'], topic_name1)

        # .. these are new topics and we do not expect any sort of publication-related information associated with it.

        self.assertEqual(out0['current_depth_gd'], 0)
        self.assertIsNone(out0['last_pub_time'])
        self.assertIsNone(out0['last_pub_msg_id'])
        self.assertIsNone(out0['last_endpoint_name'])
        self.assertIsNone(out0['last_pub_server_name'])
        self.assertIsNone(out0['last_pub_server_pid'])
        self.assertIsNone(out0['last_pub_has_gd'])

        self.assertEqual(out1['current_depth_gd'], 0)
        self.assertIsNone(out1['last_pub_time'])
        self.assertIsNone(out1['last_pub_msg_id'])
        self.assertIsNone(out1['last_endpoint_name'])
        self.assertIsNone(out1['last_pub_server_name'])
        self.assertIsNone(out1['last_pub_server_pid'])
        self.assertIsNone(out1['last_pub_has_gd'])

# ################################################################################################################################

    def _run_get_topic_default_keys(self, command:'str') -> 'None':

        # Test data
        prefix = '/test/'
        topic_name = prefix + datetime.utcnow().isoformat()

        # Command to invoke ..
        create_cli_params = ['pubsub', 'create-topic', '--name', topic_name]

        # Create one topic  ..
        _ = self.run_zato_cli_json_command(create_cli_params) # type: anydict

        # Command to get the topic back with ..
        get_cli_params = ['pubsub', command, '--name', topic_name]

        # Now, we expect to get that one topic back
        out_get = self.run_zato_cli_json_command(get_cli_params) # type: any_

        # There must be one topic on output
        self.assertTrue(len(out_get), 1)

        # Extract it now ..
        out = out_get[0] # type: anydict

        # .. and confirm that all the default keys, and only the default ones, are returned.
        default_keys = CLITopicConfig.DefaultTopicKeys

        len_out = len(out)
        len_default_keys = len(default_keys)

        self.assertEqual(len_out, len_default_keys)

        for key in default_keys:
            self.assertIn(key, out)

# ################################################################################################################################

    def _run_get_topic_all_keys(self, command:'str') -> 'None':

        # Test data
        prefix = '/test/'
        topic_name = prefix + datetime.utcnow().isoformat()

        # Command to invoke ..
        create_cli_params = ['pubsub', 'create-topic', '--name', topic_name]

        # Create one topic  ..
        create_out = self.run_zato_cli_json_command(create_cli_params) # type: anydict

        # Command to get the topic back with - note that we request for all the keys to be returned ..
        get_cli_params = ['pubsub', command, '--name', topic_name, '--keys', 'all']

        # Now, we expect to get that one topic back
        out_get = self.run_zato_cli_json_command(get_cli_params) # type: any_

        # There must be one topic on output
        self.assertTrue(len(out_get), 1)

        # Extract it now ..
        out = out_get[0] # type: anydict

        # .. make sure that the default keys are still returned if all of them are requested ..
        default_keys = CLITopicConfig.DefaultTopicKeys

        len_out = len(out)
        self.assertEqual(len_out, 25)

        # .. each default key is expected to be returned ..
        for key in default_keys:
            self.assertIn(key, out)

        # This, we can compare based on the response from create-topic
        self.assertEqual(out['id'],   create_out['id'])
        self.assertEqual(out['name'], create_out['name'])
        self.assertEqual(out['name'], topic_name)

        # These are default keys
        self.assertEqual(out['current_depth_gd'], 0)
        self.assertIsNone(out['last_pub_time'])
        self.assertIsNone(out['last_pub_msg_id'])
        self.assertIsNone(out['last_endpoint_name'])
        self.assertIsNone(out['last_pub_server_name'])
        self.assertIsNone(out['last_pub_server_pid'])
        self.assertIsNone(out['last_pub_has_gd'])

        # And this is the rest of the keys

        self.assertEqual(out['max_depth_gd'], _default.TOPIC_MAX_DEPTH_GD)
        self.assertEqual(out['limit_retention'], _default.LimitTopicRetention)
        self.assertEqual(out['depth_check_freq'], _default.DEPTH_CHECK_FREQ)
        self.assertEqual(out['max_depth_non_gd'], _default.TOPIC_MAX_DEPTH_NON_GD)
        self.assertEqual(out['task_sync_interval'], _default.TASK_SYNC_INTERVAL)
        self.assertEqual(out['task_delivery_interval'], _default.TASK_DELIVERY_INTERVAL)

        self.assertEqual(out['pub_buffer_size_gd'], 0)
        self.assertEqual(out['limit_sub_inactivity'], _default.LimitSubInactivity)
        self.assertEqual(out['limit_message_expiry'], _default.LimitMessageExpiry)

        self.assertTrue(out['is_active'])

        self.assertFalse(out['has_gd'])
        self.assertFalse(out['is_api_sub_allowed'])
        self.assertFalse(out['is_internal'])

        self.assertIsNone(out['hook_service_id'])
        self.assertIsNone(out['hook_service_name'])
        self.assertIsNone(out['on_no_subs_pub'])

# ################################################################################################################################

    def _run_get_topic_only_selected_keys(self, command:'str') -> 'None':

        # Test data
        prefix = '/test/'
        topic_name = prefix + datetime.utcnow().isoformat()

        # Command to invoke ..
        create_cli_params = ['pubsub', 'create-topic', '--name', topic_name]

        # Create one topic  ..
        create_out = self.run_zato_cli_json_command(create_cli_params) # type: anydict

        # Command to get the topic back with - note that we request for all the keys to be returned ..
        get_cli_params = ['pubsub', command, '--name', topic_name, '--keys', 'id, is_active, is_internal']

        # Now, we expect to get that one topic back
        out_get = self.run_zato_cli_json_command(get_cli_params) # type: any_

        # There must be one topic on output
        self.assertTrue(len(out_get), 1)

        # Extract it now ..
        out = out_get[0] # type: anydict

        # We expect to find only three keys here
        len_out = len(out)
        self.assertEqual(len_out, 3)

        # Run our assertions name
        self.assertEqual(out['id'], create_out['id'])
        self.assertTrue(out['is_active'])
        self.assertFalse(out['is_internal'])

# ################################################################################################################################

    def test_get_topics(self) -> 'None':

        # Pub/sub command to run
        command = 'get-topics'

        # Run all tests
        self._run_get_topic_no_such_topic(command)
        self._run_get_topic_test_one_topic(command)
        self._run_get_topic_test_multiple_topics(command)
        self._run_get_topic_default_keys(command)
        self._run_get_topic_all_keys(command)
        self._run_get_topic_only_selected_keys(command)

# ################################################################################################################################

    def test_get_topic(self) -> 'None':

        # Pub/sub command to run
        command = 'get-topic'

        # Run all tests
        self._run_get_topic_no_such_topic(command)
        self._run_get_topic_test_one_topic(command)
        self._run_get_topic_test_multiple_topics(command)
        self._run_get_topic_default_keys(command)
        self._run_get_topic_all_keys(command)
        self._run_get_topic_only_selected_keys(command)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
