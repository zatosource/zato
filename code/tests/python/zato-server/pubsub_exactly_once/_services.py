# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.test.exactly_once.control import claim_failure, claim_hold, Output_Topic, record_invocation, wait_while_exists
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

# This file is hot-deployed into a test Zato server by conftest.py.

# ################################################################################################################################
# ################################################################################################################################

class Relay(Service):
    """ Publishes one message to the output topic per message of the input topic, with the key of the input
    in the correlation ID, under the control files of the test.
    """

    name = 'test.exactly-once.relay'

    def handle(self) -> 'None':

        key = self.request.payload['key']

        # Each invocation is recorded outside of the transaction of the batch ..
        record_invocation(key)

        # .. a hold of the test keeps the invocation between the start of the batch and its commit ..
        if held_path := claim_hold(key):
            wait_while_exists(held_path)

        data = {'key': key}
        _ = self.publish(Output_Topic, data, correl_id=key)

        # .. and a failure requested by the test fails the invocation after its publication.
        if claim_failure(key):
            raise Exception(f'Failure requested for key `{key}`')

# ################################################################################################################################
# ################################################################################################################################

class Publish(Service):
    """ Publishes a message with the key of the request, under a message ID derived from the request.
    """

    name = 'test.exactly-once.publish'

    def handle(self) -> 'None':

        topic_name = self.request.payload['topic_name']
        key = self.request.payload['key']
        msg_id = self.request.payload['msg_id']

        data = {'key': key}
        result = self.publish(topic_name, data, correl_id=key, msg_id=msg_id)

        self.response.payload = {'msg_id': result.msg_id}

# ################################################################################################################################
# ################################################################################################################################
