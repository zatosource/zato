# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli import ServerAwareCommand
from zato.common.api import GENERIC
from zato.common.test.config import TestConfig
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from argparse import Namespace
    from zato.common.typing_ import anydict, anylist, strdict
    Namespace = Namespace

# ################################################################################################################################
# ################################################################################################################################

_opaque_attr = GENERIC.ATTR_NAME

class Config:
    DefaultTopicKeys = ('id', 'name', 'current_depth_gd', 'last_pub_time', 'last_pub_msg_id', 'last_endpoint_name',
        'last_pub_server_name', 'last_pub_server_pid', 'last_pub_has_gd')

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
        {'name':'--limit-sub-inactivity',
            'help':'After how many seconds an inactive subscription will be deleted', 'required':False},
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

        limit_retention      = getattr(args, 'limit_retention',      0) or _default.LimitTopicRetention
        limit_sub_inactivity = getattr(args, 'limit_sub_inactivity', 0) or _default.LimitSubInactivity
        limit_message_expiry = getattr(args, 'limit_message_expiry', 0) or _default.LimitMessageExpiry

        limit_retention = int(limit_retention)
        limit_sub_inactivity = int(limit_sub_inactivity)
        limit_message_expiry = int(limit_message_expiry)

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
            'limit_retention': limit_retention,
            'limit_sub_inactivity': limit_sub_inactivity,
            'limit_message_expiry': limit_message_expiry,
        }

        self._invoke_service_and_log_response(service, request)

# ################################################################################################################################
# ################################################################################################################################

class GetTopics(ServerAwareCommand):
    """ Returns one or more topic by their name. Accepts partial names, e.g. "demo" will match "/my/demo/topic".
    """
    opts = [
        {'name':'--name',  'help':'Query to look up topics by', 'required':False},
        {'name':'--keys',  'help':'What JSON keys to return on put. Use "all" to return them all', 'required':False},
        {'name':'--path',  'help':'Path to a Zato server', 'required':False},
    ]

# ################################################################################################################################

    def execute(self, args:'Namespace'):

        # Make sure that keys are always a set object to look up information in
        args_keys = getattr(args, 'keys', '')
        if args_keys:
            if isinstance(args_keys, str):
                args_keys = args_keys.split(',')
                args_keys = [elem.strip() for elem in args_keys]

            has_all = 'all' in args_keys
            needs_default_keys = has_all or (not args_keys)

        else:
            has_all = False
            needs_default_keys = True
            args_keys = Config.DefaultTopicKeys

        args_keys = set(args_keys)

        def hook_func(data:'anydict') -> 'anylist':

            # Response to produce ..
            out = [] # type: anylist

            # .. extract the top-level element ..
            data = data['zato_pubsub_topic_get_list_response']

            # .. go through each response element found ..
            for elem in data: # type: dict
                elem = cast_('anydict', elem)

                # Delete the opaque attributes container
                _ = elem.pop(_opaque_attr, '')

                # Make sure we return only the requested keys. Note that we build a new dictionary
                # because we want to preserve the order of DefaultConfigKeys. Also note that if all keys
                # are requested, for consistency, we still initially populate the dictionary
                # with keys from DefaultTopicKeys and only then do we proceed to the remaining keys.
                out_elem = {}

                # We are possibly return the default keys
                if needs_default_keys:

                    # First, populate the default keys ..
                    for name in Config.DefaultTopicKeys:
                        value = elem.get(name)
                        out_elem[name] = value

                # .. otherwise, we return only the specifically requested keys
                for name, value in sorted(elem.items()):
                    if has_all or (name in args_keys):
                        if name not in out_elem:
                            out_elem[name] = value

                # .. we are finished with pre-processing of this element ..
                out.append(out_elem)

            # .. and return the output to our caller.
            return out

        # Our service to invoke
        service = 'zato.pubsub.topic.get-list'

        # Get a list of topics matching the input query, if any
        request = {
            'paginate': True,
            'needs_details': True,
            'query': getattr(args, 'name', ''),
        }

        # Invoke and log, pre-processing the data first with a hook function
        self._invoke_service_and_log_response(service, request, hook_func=hook_func)

# ################################################################################################################################
# ################################################################################################################################

class DeleteTopics(ServerAwareCommand):
    """ Returns one or more topic by their name. Accepts partial names, e.g. "demo" will match "/my/demo/topic".
    """
    opts = [
        {'name':'--id',       'help':'An exact ID of a topic to delete', 'required':False},
        {'name':'--id-list',  'help':'A list of topic IDs to delete', 'required':False},
        {'name':'--name',     'help':'An exact name of a topic to delete', 'required':False},
        {'name':'--name-list','help':'List of topics to delete', 'required':False},
        {'name':'--pattern',  'help':'All topics with names that contain this pattern', 'required':False},
        {'name':'--path',     'help':'Path to a Zato server', 'required':False},
    ]

# ################################################################################################################################

    def execute(self, args:'Namespace'):

        # stdlib
        import sys

        # This will be built based on the option provided by user
        request = {}

        options = ['--id', '--id-list', '--name', '--name-list', '--pattern']
        for name in options:
            arg_attr = name.replace('--', '')
            arg_attr = arg_attr.replace('-', '-s')
            value = getattr(args, arg_attr, None)
            if value:
                request[arg_attr] = value
                break

        if not request:
            options = ', '.join(options)
            self.logger.warn(f'Input missing. One of the following is expected: {options}')
            sys.exit(self.SYS_ERROR.PARAMETER_MISSING)

        # Our service to invoke
        service = 'zato.pubsub.topic.delete-topics'

        # Invoke the service and log the response it produced
        self._invoke_service_and_log_response(service, request)

# ################################################################################################################################
# ################################################################################################################################

class CreateTopics(ServerAwareCommand):
    """ Creates multiple topics based on an input file.
    """
    opts = [
        {'name':'--input', 'help':'Path to a file with the list of topics to be created', 'required':False},
        {'name':'--count', 'help':'How many topics to create', 'required':False},
        {'name':'--prefix', 'help':'Prefix that each of the topics to be created will have', 'required':False},
        {'name':'--path',  'help':'Path to a Zato server', 'required':False},
    ]

# ################################################################################################################################

    def execute(self, args:'Namespace'):

        # Local variables
        count = 1000
        prefix = TestConfig.pubsub_topic_name_perf_auto_create

        # Our service to invoke
        service = 'topics1.create-topics'

        # Read the parameters from the command line or fall back on the defaults
        count = int(getattr(args, 'count') or count)
        prefix = getattr(args, 'prefix') or prefix

        # Find out to how many digits we should fill tha names
        digits = len(str(count))

        # The list to create
        name_list = []

        for idx, _ in enumerate(range(count), 1):
            idx = str(idx).zfill(digits)
            topic_name = f'{prefix}{idx}'
            name_list.append(topic_name)

        request:'strdict' = {
            'name_list': name_list
        }

        # Invoke the service and log the response it produced
        self._invoke_service_and_log_response(service, request)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    from argparse import Namespace
    from os import environ

    args = Namespace()
    args.verbose      = True
    args.store_log    = False
    args.store_config = False
    args.path = environ['ZATO_SERVER_BASE_DIR']

    command = DeleteTopics(args)
    command.run(args)

    """
    args = Namespace()
    args.keys         = 'all'
    args.verbose      = True
    args.store_log    = False
    args.store_config = False
    args.path = environ['ZATO_SERVER_BASE_DIR']

    command = GetTopics(args)
    command.run(args)
    """

    """
    args = Namespace()
    args.verbose      = True
    args.store_log    = False
    args.store_config = False
    args.path = environ['ZATO_SERVER_BASE_DIR']

    command = CreateTopic(args)
    command.run(args)
    """

# ################################################################################################################################
# ################################################################################################################################

'''
# -*- coding: utf-8 -*-

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.api import PUBSUB
from zato.common.exception import BadRequest
from zato.common.odb.model import PubSubTopic
from zato.common.typing_ import dictlist, strlist
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

_ps_default = PUBSUB.DEFAULT

# ################################################################################################################################
# ################################################################################################################################

TopicTable = PubSubTopic.__table__
TopicInsert = TopicTable.insert

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CreateTopicRequest(Model):
    name_list: strlist

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CreateTopicResponse(Model):
    topics_created: dictlist

# ################################################################################################################################
# ################################################################################################################################

class CreateTopics(Service):
    name = 'topics1.create-topics'

    class SimpleIO:
        input = CreateTopicRequest
        output = CreateTopicResponse

    def handle(self):

        # Local variables
        input:'CreateTopicRequest' = self.request.input

        # Log what we are about to do
        self.logger.info('Creating topics -> len=%s', len(input.name_list))

        # .. go through each name we are given on input ..
        for name in input.name_list:

            # .. fill out all the details ..
            request = {
                'name': name,
                'has_gd': True,
                'is_active': True,
                'is_api_sub_allowed': True,
                'cluster_id': 1,
                'task_sync_interval': _ps_default.TASK_SYNC_INTERVAL,
                'task_delivery_interval': _ps_default.TASK_DELIVERY_INTERVAL,
                'depth_check_freq': _ps_default.DEPTH_CHECK_FREQ,
                'max_depth_gd': _ps_default.TOPIC_MAX_DEPTH_GD,
                'max_depth_non_gd': _ps_default.TOPIC_MAX_DEPTH_NON_GD,
                'pub_buffer_size_gd': _ps_default.PUB_BUFFER_SIZE_GD,
            }

            # .. create a topic now ..
            try:
                _ = self.invoke('zato.pubsub.topic.create', request)
            except BadRequest as e:
                # .. ignore topics that already exist ..
                self.logger.info('Ignoring -> %s', e)

        # .. finally, store information in logs that we are done.
        self.logger.info('Topic created')

# ################################################################################################################################
# ################################################################################################################################
'''
