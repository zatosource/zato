# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.test.exactly_once.control import claim_hold, record_invocation, wait_while_exists
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

# This file is placed in the pickup directory of the server of the tests of push delivery batches.

# ################################################################################################################################
# ################################################################################################################################

# The outgoing connection that the target calls and the topic that it publishes to
_outgoing_name = 'test.ha-push-delivery.out'
_output_topic  = 'ha-push-delivery.output'

# ################################################################################################################################
# ################################################################################################################################

class Target(Service):
    """ The subscriber of the input topic. It calls the outgoing REST connection with the key of the message,
    publishes the key to the output topic, waits while the test holds the key and fails if the message says so.
    """

    name = 'test.ha-push-delivery.target'

    def handle(self) -> 'None':

        payload = self.request.payload
        key = payload['key']

        # Each invocation is recorded outside of the transaction of the batch ..
        record_invocation(key)

        # .. the outgoing call is made and published about ..
        data = {'key': key}
        conn = self.out.rest[_outgoing_name].conn
        _ = conn.post(self.cid, data)

        _ = self.publish(_output_topic, data, correl_id=key)

        # .. a hold of the test keeps the invocation in progress ..
        if held_path := claim_hold(key):
            wait_while_exists(held_path)

        # .. and a message that is to fail raises after its side effects.
        if payload['should_fail']:
            raise Exception(f'Failure requested for key `{key}`')

# ################################################################################################################################
# ################################################################################################################################

class Publish(Service):
    """ Publishes one message to a topic, with the retry settings that the request gives.
    """

    name = 'test.ha-push-delivery.publish'

    def handle(self) -> 'None':

        request = self.request.raw_request

        topic_name = request['topic_name']
        data = request['data']
        retry_settings = request['retry_settings']

        result = self.publish(topic_name, data, **retry_settings)

        self.response.payload = {'msg_id': result.msg_id}

# ################################################################################################################################
# ################################################################################################################################
