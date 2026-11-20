# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.pubsub.sql.errors import PubSubDuplicateMsgID
from zato.common.test.exactly_once.control import claim_hold, count_invocations, record_invocation, record_publication, \
    wait_while_exists
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
    publishes the key to the output topic under the message ID that the message names, if any, and records
    the outcome of the publication, waits while the test holds the key in the invocation that the message names
    and fails if the message says so.
    """

    name = 'test.ha-push-delivery.target'

    def handle(self) -> 'None':

        payload = self.request.payload
        key = payload['key']

        # Each invocation is recorded outside of the transaction of the batch ..
        record_invocation(key)
        invocation_count = count_invocations(key)

        # .. the outgoing call is made ..
        data = {'key': key}
        conn = self.out.rest[_outgoing_name].conn
        _ = conn.post(self.cid, data)

        # .. and published about, with the outcome of the publication recorded ..
        try:
            result = self.publish(_output_topic, data, correl_id=key, msg_id=payload['output_msg_id'])
        except PubSubDuplicateMsgID as e:
            record_publication(key, e.__class__.__name__)
            raise
        else:
            record_publication(key, result.msg_id)

        # .. a hold of the test keeps the invocation that it is meant for in progress ..
        if invocation_count == payload['held_invocation']:
            if held_path := claim_hold(key):
                wait_while_exists(held_path)

        # .. and a message that is to fail raises after its side effects.
        if payload['should_fail']:
            raise Exception(f'Failure requested for key `{key}`')

# ################################################################################################################################
# ################################################################################################################################

class Publish(Service):
    """ Publishes one message to a topic, with the options that the request gives, e.g. its retry settings.
    """

    name = 'test.ha-push-delivery.publish'

    def handle(self) -> 'None':

        request = self.request.raw_request

        topic_name = request['topic_name']
        data = request['data']
        options = request['options']

        result = self.publish(topic_name, data, **options)

        self.response.payload = {'msg_id': result.msg_id}

# ################################################################################################################################
# ################################################################################################################################
