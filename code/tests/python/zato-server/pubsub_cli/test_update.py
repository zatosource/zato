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

def _run_cli(zato_bin:'str', server_dir:'str', subcommand:'str', *args:'str') -> 'subprocess.CompletedProcess[str]':
    """ Runs a 'zato pubsub <subcommand>' CLI command against the server.
    """
    command = [zato_bin, 'pubsub', subcommand, server_dir] + list(args)

    out = subprocess.run(command, capture_output=True, text=True, check=False, timeout=30)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestUpdate:
    """ Update a message payload via CLI.
    """

    def test_update_message_payload(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient
        from zato.common.test.config_pubsub_cli import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

        sub_key = _get_sub_key(admin, TestConfig.puller_username)

        # .. clear and publish a message ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})
        publish_result = publisher.publish(_topic, '{"original": true}')
        msg_id = publish_result['msg_id']
        time.sleep(_settle_time)

        # .. update via CLI ..
        result = _run_cli(
            TestConfig.zato_bin, TestConfig.server_directory,
            'update',
            '--msg-id', msg_id,
            '--topic-name', _topic,
            '--data', '{"updated": true}',
        )

        assert result.returncode == 0, f'CLI failed: {result.stdout}\n{result.stderr}'
        assert 'Message updated' in result.stdout

        # .. verify the payload was updated by getting the message detail ..
        browse_result = admin.invoke('zato.pubsub.subscription.browse-queue', {
            'sub_key': sub_key,
            'state': 'pending',
        })

        rows = browse_result['rows']
        target_row = None
        for row in rows:
            if row['msg_id'] == msg_id:
                target_row = row
                break

        assert target_row is not None
        redis_stream_id = target_row['redis_stream_id']

        detail = admin.invoke('zato.pubsub.subscription.get-message-detail', {
            'msg_id': msg_id,
            'topic_name': _topic,
            'redis_stream_id': redis_stream_id,
        })

        assert '{"updated": true}' in detail['data']

# ################################################################################################################################
# ################################################################################################################################
