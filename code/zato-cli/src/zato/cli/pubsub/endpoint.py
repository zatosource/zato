# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli import ServerAwareCommand
from zato.common.api import CommonObject, PUBSUB
from zato.common.util.api import fs_safe_now

from zato.cli.common import CreateCommon

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from argparse import Namespace
    Namespace = Namespace

# ################################################################################################################################
# ################################################################################################################################

class CreateEndpoint(ServerAwareCommand):
    """ Creates a new pub/sub endpoint.
    """
    opts = [
        {'name':'--name', 'help':'Name of the endpoint to create', 'required':False,},
        {'name':'--role', 'help':'Role the endpoint should have', 'required':False},
        {'name':'--is-active', 'help':'Should the endpoint be active upon creation', 'required':False},
        {'name':'--topic-patterns', 'help':'A comma-separated list of topic patterns allowed', 'required':False},
        {'name':'--wsx-id', 'help':'An ID of a WebSocket channel if the endpoint is associated with one', 'required':False},
        {'name':'--path', 'help':'Path to a Zato server', 'required':True},
    ]

    def execute(self, args:'Namespace'):

        name = getattr(args, 'name', None)
        role = getattr(args, 'role', None)
        wsx_id = getattr(args, 'wsx_id', None)

        is_active = getattr(args, 'is_active', True)
        if is_active is None:
            is_active = True

        topic_patterns = getattr(args, 'topic_patterns', '')

        # If we do not have any patterns, it means that we want to assign the endpoint to all the topics possible.
        if not topic_patterns:
            topic_patterns = 'pub=/*,sub=/*'

        topic_patterns = topic_patterns.split(',')
        topic_patterns = [elem.strip() for elem in topic_patterns]
        topic_patterns = '\n'.join(topic_patterns)

        # Generate a name if one is not given
        name = name or 'auto.pubsub.endpoint.' + fs_safe_now()

        # By default, endpoints can both publish and subscribe
        role = role or PUBSUB.ROLE.PUBLISHER_SUBSCRIBER.id

        # API service to invoke
        service = 'zato.pubsub.endpoint.create'

        # API request to send
        request = {
            'name': name,
            'role': role,
            'is_active': is_active,
            'topic_patterns': topic_patterns,
            'is_internal': False,
        }

        if wsx_id:
            request['ws_channel_id'] = wsx_id
            request['endpoint_type'] = PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id

        self._invoke_service_and_log_response(service, request)

# ################################################################################################################################
# ################################################################################################################################

class DeleteEndpoint(ServerAwareCommand):
    """ Deletes a pub/sub endpoint.
    """
    opts = [
        {'name':'--id', 'help':'ID of the endpoint to delete', 'required':True},
        {'name':'--path', 'help':'Path to a Zato server', 'required':True},
    ]

    def execute(self, args:'Namespace'):

        id = getattr(args, 'id', None)

        # API service to invoke
        service = 'zato.pubsub.endpoint.delete'

        # API request to send
        request = {
            'id': id,
        }

        self._invoke_service_and_log_response(service, request)

# ################################################################################################################################
# ################################################################################################################################

class CreateEndpoints(CreateCommon):
    """ Creates multiple endpoints.
    """
    object_type = CommonObject.PubSub_Topic

    def execute(self, args:'Namespace') -> 'None':
        request = super().execute(args)

        print()
        print(111, request)
        print(222, args)
        print()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    from argparse import Namespace
    from os import environ

    create_args = Namespace()
    create_args.verbose      = True
    create_args.store_log    = False
    create_args.store_config = False
    create_args.wsx_id = 194
    create_args.path = environ['ZATO_SERVER_BASE_DIR']

    create_command = CreateEndpoint(create_args)
    create_command.run(create_args)

    delete_args = Namespace()
    delete_args.verbose      = True
    delete_args.store_log    = False
    delete_args.store_config = False
    delete_args.id = 555
    delete_args.path = environ['ZATO_SERVER_BASE_DIR']

    delete_command = DeleteEndpoint(delete_args)
    delete_command.run(delete_args)

# ################################################################################################################################
# ################################################################################################################################
