# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# ################################################################################################################################
# ################################################################################################################################

str_str_dict = dict[str, str]
str_int_dict = dict[str, int]
str_object_dict = dict[str, object]

# ################################################################################################################################
# ################################################################################################################################

# All available pub/sub push endpoints in fixed order. Each entry is a topic name
# that maps 1:1 to an outgoing REST connection, a subscriber security definition,
# and an HTTP receiver server.
_all_endpoints = [
    'iam.user.created',
    'iam.user.deleted',
    'iam.role.assigned',
    'iam.password.changed',
    'iam.login.failed',
    'customer.registered',
    'customer.updated',
    'customer.deactivated',
    'order.placed',
    'order.shipped',
]

# How many endpoints to activate for this test run
_endpoint_count = int(os.environ.get('Zato_PubSub_Push_Endpoint_Count', '2'))

# The slice of endpoints that are active
_active_endpoints = _all_endpoints[:_endpoint_count]

# ################################################################################################################################
# ################################################################################################################################

def is_endpoint_active(topic_name:'str') -> 'bool':
    """ Check whether a given topic is in the active set for this test run.
    """
    out = topic_name in _active_endpoints
    return out

# ################################################################################################################################

def get_endpoint_index(topic_name:'str') -> 'int':
    """ Return the index of a topic in the master list.
    """
    out = _all_endpoints.index(topic_name)
    return out

# ################################################################################################################################
# ################################################################################################################################

class PubSubPushTestConfig:
    """ Central configuration for the pub/sub push test suite.
    """

    base_url = ''

    publisher_username  = 'pubsub.test.publisher'
    publisher_password  = ''

    puller_username  = 'pubsub.test.puller'
    puller_password  = ''

    subscriber_password = ''

    # Populated at runtime by conftest - maps topic_name -> tmpdir path
    endpoint_output_dirs:'str_str_dict' = {}

    # Populated at runtime by conftest - maps topic_name -> port
    endpoint_ports:'str_int_dict' = {}

    # Populated at runtime by conftest - maps topic_name -> ReceiverBehavior
    receiver_controls:'str_object_dict' = {}

    # Populated at runtime by conftest - maps topic_name -> ReceiverServer
    receiver_servers:'str_object_dict' = {}

# ################################################################################################################################
# ################################################################################################################################
