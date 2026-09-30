# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# This file is hot-deployed into a test Zato server by conftest.py. It holds the service that publishes
# with retry settings, the target those publications are pushed to, and the services the tests
# steer and observe the target with.

# stdlib
from time import monotonic

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

# A refusal count meaning that the target refuses everything until it is told otherwise.
Refuse_Everything = -1

# Every invocation of the target, in the order they were made - when it was made, whether it was accepted
# and what it carried.
_invocations:'anylist' = []

# How many more invocations the target refuses before it accepts again.
_behaviour:'anydict' = {
    'refuse_left': 0,
}

# ################################################################################################################################
# ################################################################################################################################

class Publish(Service):
    """ Publishes one message the way an application does it, with whatever retry settings the test gives.
    """

    name = 'test.publish-retry.publish'

    def handle(self) -> 'None':

        request = self.request.raw_request

        topic_name = request['topic_name']
        data = request['data']

        # Anything else in the request travels as a keyword argument of the publication - the retry settings
        # and the expiration, when the test gives them.
        kwargs = {}

        for key, value in request.items():
            if key in ('topic_name', 'data'):
                continue
            kwargs[key] = value

        result = self.publish(topic_name, data, **kwargs)

        self.response.payload = {'msg_id': result.msg_id, 'cid': self.cid}

# ################################################################################################################################
# ################################################################################################################################

class Target(Service):
    """ What the publications are pushed to - it records every invocation and refuses as many of them
    as it was told to.
    """

    name = 'test.publish-retry.target'

    def handle(self) -> 'None':

        refuse_left = _behaviour['refuse_left']

        if refuse_left == Refuse_Everything:
            is_accepted = False

        elif refuse_left > 0:
            _behaviour['refuse_left'] = refuse_left - 1
            is_accepted = False

        else:
            is_accepted = True

        data = str(self.request.raw_request)

        _invocations.append({
            'time': monotonic(),
            'is_accepted': is_accepted,
            'data': data,
        })

        if not is_accepted:
            raise Exception('The target refuses this invocation')

# ################################################################################################################################
# ################################################################################################################################

class SetBehaviour(Service):
    """ Tells the target how many of the coming invocations to refuse, forgetting the invocations made so far.
    """

    name = 'test.publish-retry.set-behaviour'

    def handle(self) -> 'None':

        _behaviour['refuse_left'] = self.request.raw_request['refuse_count']
        _invocations.clear()

        self.response.payload = {'refuse_left': _behaviour['refuse_left']}

# ################################################################################################################################
# ################################################################################################################################

class GetReceived(Service):
    """ Every invocation the target has seen since its behaviour was last set.
    """

    name = 'test.publish-retry.get-received'

    def handle(self) -> 'None':
        self.response.payload = {'invocations': list(_invocations)}

# ################################################################################################################################
# ################################################################################################################################

class GetQueue(Service):
    """ How many messages wait in the queues of the push subscribers of one topic.
    """

    name = 'test.publish-retry.get-queue'

    def handle(self) -> 'None':

        topic_name = self.request.raw_request['topic_name']

        pairs = []

        for sub_key, config_list in self.server.config_manager._push_subs.items():
            for config in config_list:
                if config['topic_name'] == topic_name:
                    pairs.append((sub_key, topic_name))

        depths = self.server.pubsub_backend.get_pending_depths(pairs)

        pending = 0

        for depth in depths.values():
            pending += depth

        self.response.payload = {'pending': pending, 'sub_keys': sorted(depths)}

# ################################################################################################################################
# ################################################################################################################################
