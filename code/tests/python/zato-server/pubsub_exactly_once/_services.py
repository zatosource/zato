# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
from gevent import spawn

# Zato
from zato.common.db_env.engine import call_database
from zato.common.test.exactly_once import claim_failure, claim_hold, claim_write_hold, hold_write_lock, Output_Topic, \
    record_invocation, wait_while_exists
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

    name = 'test.eo.relay'

    def handle(self) -> 'None':

        key = self.request.payload['key']

        # Each invocation is recorded outside of the transaction of the batch ..
        record_invocation(key)

        # .. a request of the test makes this invocation take the write lock of the SQLite pub/sub file of the process,
        # .. which a thread of the pool holds while every later commit of the process waits for it ..
        if claim_write_hold(key):
            engine = self.server.pubsub_backend.engine
            _ = spawn(call_database, engine, hold_write_lock)

        # .. a hold of the test keeps the invocation between the start of the batch and its commit ..
        if held_path := claim_hold(key):
            wait_while_exists(held_path)

        _ = self.publish(Output_Topic, {'key': key}, correl_id=key)

        # .. and a failure requested by the test fails the invocation after its publication.
        if claim_failure(key):
            raise Exception(f'Failure requested for key `{key}`')

# ################################################################################################################################
# ################################################################################################################################

class Publish(Service):
    """ Publishes a message with the key of the request, under a message ID derived from the request.
    """

    name = 'test.eo.publish'

    def handle(self) -> 'None':

        topic_name = self.request.payload['topic_name']
        key = self.request.payload['key']
        msg_id = self.request.payload['msg_id']

        result = self.publish(topic_name, {'key': key}, correl_id=key, msg_id=msg_id)

        self.response.payload = {'msg_id': result.msg_id}

# ################################################################################################################################
# ################################################################################################################################
