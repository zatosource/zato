# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK

# Zato
from pubsub_exactly_once.harness import new_keys, verify
from pubsub_exactly_once.rest import post_json, publish
from zato.common.test import pubsub_db
from zato.common.test.exactly_once.config import TestConfig
from zato.common.test.exactly_once.control import Input_Topic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# How many input messages each test publishes
_key_count = 50

# How many times a request is sent through the service and over REST
_service_repeats = 2
_rest_repeats    = 3

# The service that publishes under a message ID derived from its request, deployed after the import of the template,
# and the user of the server that invokes it
_publish_service_path = '/zato/api/invoke/test.exactly-once.publish'
_invoke_username      = 'admin.invoke'

# ################################################################################################################################
# ################################################################################################################################

def test_idempotent_publication_through_service(zato_server:'any_') -> 'None':
    """ A service that publishes under a message ID derived from its request, invoked twice per request,
    stores one message per request, and each of them is relayed once.
    """
    prefix, keys = new_keys(_key_count)

    for key in keys:

        payload = {
            'topic_name': Input_Topic,
            'key': key,
            'msg_id': key,
        }

        for _ in range(_service_repeats):
            result = post_json(_publish_service_path, _invoke_username, TestConfig.password, payload)

            assert result.status_code == OK, result
            assert result.body['msg_id'] == key, result

    assert pubsub_db.count_message_rows(keys) == _key_count

    _ = verify(prefix, keys)

# ################################################################################################################################

def test_idempotent_publication_over_rest(zato_server:'any_') -> 'None':
    """ A REST client that publishes under its own message ID, three times per message, receives the same message ID
    in every response, one message is stored per publication, and each of them is relayed once.
    """
    prefix, keys = new_keys(_key_count)

    for key in keys:

        payload = {
            'data': {'key': key},
            'msg_id': key,
        }

        for _ in range(_rest_repeats):
            result = publish(TestConfig.publisher_username, TestConfig.publisher_password, Input_Topic, payload)

            assert result.status_code == OK, result
            assert result.body['msg_id'] == key, result

    assert pubsub_db.count_message_rows(keys) == _key_count

    _ = verify(prefix, keys)

# ################################################################################################################################
# ################################################################################################################################
