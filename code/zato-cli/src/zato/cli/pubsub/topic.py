# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli import ServerAwareCommand

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from argparse import Namespace

# ################################################################################################################################
# ################################################################################################################################

class CreateTopic(ServerAwareCommand):
    """ Creates a new publish/subscribe topic.
    """
    opts = [
        {'name':'--name', 'help':'Name of the topic to create', 'required':False},
        {'name':'--gd',   'help':'Should the topic use Guaranteed Delivery', 'required':False},
        {'name':'--is-internal', 'help':'Is it a topic internal to the platform', 'required':False},
        {'name':'--is-api-sub-allowed', 'help':'Can applications subscribe to the topic via a public API', 'required':False},
        {'name':'--limit-retention', 'help':'Limit retention time in topic to that many seconds', 'required':False},
        {'name':'--limit-message-expiry', 'help':'Limit max. message expiration time to that many seconds', 'required':False},
        {'name':'--path', 'help':'Path to a Zato server', 'required':False},
    ]

# ################################################################################################################################

    def execute(self, args:'Namespace'):

        # Zato
        from zato.common.api import PUBSUB
        from zato.common.util.file_system import fs_safe_now

        _default = PUBSUB.DEFAULT

        # Topic name will be generated if it is now given on input
        topic_name  = getattr(args, 'name', None)

        has_gd             = getattr(args, 'gd',   False)
        is_internal        = getattr(args, 'is_internal', None)
        is_api_sub_allowed = getattr(args, 'is_api_sub_allowed', True)

        limit_expiry    = getattr(args, 'limit_expiry', 0)    or _default.LimitMessageExpiry
        limit_retention = getattr(args, 'limit_retention', 0) or _default.LimitTopicRetention

        limit_expiry    = int(limit_expiry)
        limit_retention = int(limit_retention)

        if not topic_name:
            topic_name = '/auto/topic.{}'.format(fs_safe_now())

        service = 'zato.pubsub.topic.create'
        request = {
            'name': topic_name,
            'is_active': True,
            'is_internal': is_internal,
            'has_gd': has_gd,
            'is_api_sub_allowed': is_api_sub_allowed,
            'max_depth_gd': _default.TOPIC_MAX_DEPTH_GD,
            'max_depth_non_gd': _default.TOPIC_MAX_DEPTH_NON_GD,
            'depth_check_freq': _default.DEPTH_CHECK_FREQ,
            'pub_buffer_size_gd': _default.PUB_BUFFER_SIZE_GD,
            'task_sync_interval': _default.TASK_SYNC_INTERVAL,
            'task_delivery_interval': _default.TASK_DELIVERY_INTERVAL,
            'limit_expiry': limit_expiry,
            'limit_retention': limit_retention,
        }

        self._invoke_service_and_log_response(service, request)

# ################################################################################################################################
# ################################################################################################################################

class GetTopic(ServerAwareCommand):
    """ Returns a topic by its name or a part of its exact name.
    """
    opts = [
        {'name':'--name', 'help':'Name of the topic to return', 'required':False},
        {'name':'--path', 'help':'Path to a Zato server', 'required':False},
    ]

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    from os import environ

    # Bunch
    from bunch import Bunch

    args = Bunch()
    args.verbose      = True
    args.store_log    = False
    args.store_config = False
    args.path = environ['ZATO_SERVER_BASE_DIR']

    command = CreateTopic(args)
    command.run(args)

# ################################################################################################################################
# ################################################################################################################################
