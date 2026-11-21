# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# PyYAML
import yaml

# Zato
from _support import wait_for_no_unconfirmed

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def test_flags(environment:'any_', pickup:'any_', runtime:'any_', names:'any_', client:'any_') -> 'None':
    """ Every flag changed by an enmasse file of a running server is stored and returned by get-list.
    """
    definition = {
        'pubsub_topic': [
            {'name': names.topic_pull, 'is_active': False},
            {'name': names.topic_second, 'is_active': True},
        ],
        'pubsub_subscription': [{
            'security': names.security_pull,
            'delivery_type': 'pull',
            'is_pub_active': False,
            'topic_list': [
                {
                    'name': names.topic_pull,
                    'is_pub_enabled': False,
                    'is_delivery_enabled': False,
                },
                {
                    'name': names.topic_second,
                    'is_pub_enabled': True,
                    'is_delivery_enabled': True,
                },
            ],
        }],
    }

    pickup.apply('flags', yaml.dump(definition))
    wait_for_no_unconfirmed(runtime)

    response = client.invoke('zato.pubsub.subscription.get-list', {})

    found = False

    for item in response:
        if item['sec_name'] != names.security_pull:
            continue

        assert item['is_pub_active'] is False
        found = True

        for topic in item['topic_name_list']:
            if topic['topic_name'] == names.topic_pull.lower():
                assert topic['is_pub_enabled'] is False
                assert topic['is_delivery_enabled'] is False
            if topic['topic_name'] == names.topic_second.lower():
                assert topic['is_pub_enabled'] is True
                assert topic['is_delivery_enabled'] is True

    assert found

# ################################################################################################################################
# ################################################################################################################################
