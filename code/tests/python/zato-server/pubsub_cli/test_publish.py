# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import subprocess
import time

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

_topic = 'cli.test.topic.1'
_settle_time = 2.0

# ################################################################################################################################
# ################################################################################################################################

def _get_sub_key(admin_client:'any_', username:'str') -> 'str':
    """ Looks up the sub_key for a given security username via the admin API.
    """
    result = admin_client.invoke('zato.pubsub.subscription.get-list', {'cluster_id': 1})

    if isinstance(result, list):
        items:'anylist' = result
    else:
        items = result['zato_pubsub_subscription_get_list_response']

    for item in items:
        sec_name = item['sec_name']
        if sec_name == username:
            return item['sub_key']

    raise RuntimeError(f'No subscription found for username: {username}')

# ################################################################################################################################
# ################################################################################################################################

def _run_cli(zato_bin:'str', server_dir:'str', subcommand:'str', *args:'str') -> 'subprocess.CompletedProcess[str]':
    """ Runs a 'zato pubsub <subcommand>' CLI command against the server.
    """
    command = [zato_bin, 'pubsub', subcommand, server_dir] + list(args)

    out = subprocess.run(command, capture_output=True, text=True, check=False, timeout=30)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestPublish:
    """ Publish a message via CLI, verify it lands in the queue.
    """

    def test_publish_via_cli(self, zato_server:'any_') -> 'None':

        from _client import AdminClient, PublishClient
        from config import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        sub_key = _get_sub_key(admin, TestConfig.puller_username)

        # .. clear any leftover messages ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. publish via CLI ..
        result = _run_cli(
            TestConfig.zato_bin, TestConfig.server_directory,
            'publish',
            '--topic', _topic,
            '--data', '{"cli_test": "publish"}',
        )

        assert result.returncode == 0, f'CLI failed: {result.stdout}\n{result.stderr}'
        assert 'Message published' in result.stdout

        # .. wait for the message to arrive ..
        time.sleep(_settle_time)

        # .. verify via admin browse ..
        browse_result = admin.invoke('zato.pubsub.subscription.browse-queue', {
            'sub_key': sub_key,
            'state': 'pending',
        })

        assert browse_result['total'] >= 1

    def test_publish_with_priority(self, zato_server:'any_') -> 'None':

        from _client import AdminClient
        from config import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        sub_key = _get_sub_key(admin, TestConfig.puller_username)

        # .. clear ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. publish with priority ..
        result = _run_cli(
            TestConfig.zato_bin, TestConfig.server_directory,
            'publish',
            '--topic', _topic,
            '--data', 'priority-test',
            '--priority', '9',
        )

        assert result.returncode == 0
        assert 'Message published' in result.stdout

# ################################################################################################################################
# ################################################################################################################################
