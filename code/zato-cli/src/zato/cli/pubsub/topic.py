# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps

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
        {'name':'--path', 'help':'Path to a Zato server',   'required':False},
    ]

# ################################################################################################################################

    def execute(self, args:'Namespace'):

        # stdlib
        import sys

        # Zato
        from zato.common.api import PUBSUB
        from zato.common.util.file_system import fs_safe_now

        _default = PUBSUB.DEFAULT

        # Topic name will be generated if it is now given on input
        topic_name = getattr(args, 'name', None)
        has_gd = getattr(args, 'gd', True)

        if not topic_name:
            topic_name = '/auto/topic.{}'.format(fs_safe_now())

        service = 'zato.pubsub.topic.create'
        request = {
            'name': topic_name,
            'is_active': True,
            'is_internal': True,
            'has_gd': has_gd,
            'is_api_sub_allowed': True,
            'max_depth_gd': _default.TOPIC_MAX_DEPTH_GD,
            'max_depth_non_gd': _default.TOPIC_MAX_DEPTH_NON_GD,
            'depth_check_freq': _default.DEPTH_CHECK_FREQ,
            'pub_buffer_size_gd': _default.PUB_BUFFER_SIZE_GD,
            'task_sync_interval': _default.TASK_SYNC_INTERVAL,
            'task_delivery_interval': _default.TASK_DELIVERY_INTERVAL,
        }

        response = self.zato_client.invoke(**{
            'name': service,
            'payload': request
        })

        data = dumps(response.data)
        sys.stdout.write(data + '\n')

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
