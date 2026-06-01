# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import subprocess
import time

if 0:
    from zato.common.typing_ import any_, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

_topic = 'cli.test.topic.1'
_settle_time = 0.5

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

def _publish_messages(publish_client:'any_', count:'int') -> 'strlist':
    """ Publishes `count` messages and returns their msg_ids.
    """
    msg_ids:'strlist' = []

    for idx in range(count):
        result = publish_client.publish(_topic, f'browse-test-payload-{idx}')
        msg_id = result['msg_id']
        msg_ids.append(msg_id)

    return msg_ids

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

class TestBrowse:
    """ Browse messages via CLI.
    """

    def test_browse_shows_messages(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient
        from zato.common.test.config_pubsub_cli import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

        sub_key = _get_sub_key(admin, TestConfig.puller_username)

        # .. clear and publish fresh messages ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})
        _ = _publish_messages(publisher, 3)
        time.sleep(_settle_time)

        # .. browse via CLI ..
        result = _run_cli(
            TestConfig.zato_bin, TestConfig.server_directory,
            'browse',
            '--sub-key', sub_key,
            '--state', 'pending',
        )

        assert result.returncode == 0, f'CLI failed: {result.stdout}\n{result.stderr}'
        assert 'total' in result.stdout
        assert 'msg_id' in result.stdout

    def test_browse_with_pagination(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient
        from zato.common.test.config_pubsub_cli import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

        sub_key = _get_sub_key(admin, TestConfig.puller_username)

        # .. clear and publish 5 messages ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})
        _ = _publish_messages(publisher, 5)
        time.sleep(_settle_time)

        # .. browse page 1 with page-size 2 ..
        result = _run_cli(
            TestConfig.zato_bin, TestConfig.server_directory,
            'browse',
            '--sub-key', sub_key,
            '--state', 'pending',
            '--page', '1',
            '--page-size', '2',
        )

        assert result.returncode == 0
        assert 'total' in result.stdout

    def test_browse_empty_queue(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient
        from zato.common.test.config_pubsub_cli import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        sub_key = _get_sub_key(admin, TestConfig.puller_username)

        # .. clear ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. browse should show 0 ..
        result = _run_cli(
            TestConfig.zato_bin, TestConfig.server_directory,
            'browse',
            '--sub-key', sub_key,
            '--state', 'pending',
        )

        assert result.returncode == 0

# ################################################################################################################################
# ################################################################################################################################
