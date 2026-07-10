# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import AS4
from zato.common.json_internal import loads
from zato.server.connection.as4 import build_routed_message
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class Deliver(Service):
    """ The built-in subscriber of the outbound AS4 topic - it performs the actual HTTP delivery
    of each published message, raising an exception on failure so that pub/sub redelivers it.
    """
    name = 'zato.outgoing.as4.deliver'

    def handle(self) -> 'None':

        # The message is what the publishing facade built - it arrives as the JSON string
        # that the pub/sub backend stored at publication time.
        msg = loads(self.request.raw_request)

        # Everything needed to replay the original call is inside the message.
        connection = self.out.as4[msg['connection']]
        wrapper = connection.conn

        # A participant id means the publisher wanted dynamic discovery ..
        if msg['participant_id']:
            _ = wrapper.send_to(
                self.cid,
                msg['participant_id'],
                msg['document_type'],
                msg['data'],
                msg['from_participant'],
                msg['conversation_id'],
            )

        # .. no participant id means a direct send to the configured endpoint.
        else:
            _ = wrapper.send(self.cid, msg['data'], msg['mime_type'], msg['conversation_id'])

# ################################################################################################################################
# ################################################################################################################################

class Pull(Service):
    """ A scheduler-driven pull job - each run sends one pull request over the configured
    outgoing AS4 connection and routes whatever was pulled the way an AS4 channel would,
    to a service or to a pub/sub topic. The scheduler job's extra data configures it,
    one job per connection and MPC, e.g.:

    connection=ICS2 Production
    mpc=urn:fdc:ec.europa.eu:2019:mpc
    service=my.service
    topic=my.topic

    Only connection is required - without a service the payloads go to the topic
    and without a topic they go to the default inbound one.
    """
    name = 'zato.outgoing.as4.pull'

    def handle(self) -> 'None':

        # The scheduler parses the job's extra data into a dictionary before invoking us.
        msg = self.request.raw_request

        connection_name = msg['connection']
        mpc = msg.get('mpc')

        # Where pulled payloads go - a service takes precedence over a topic.
        service_name = msg.get('service')
        topic_name = msg.get('topic')
        if not topic_name:
            topic_name = AS4.Default.Inbound_Topic

        # Send the pull request - an empty partition channel comes back as no message,
        # which is a regular, successful outcome.
        connection = self.out.as4[connection_name]
        wrapper = connection.conn
        result = wrapper.pull(self.cid, mpc)

        if not result.has_message:
            self.logger.info('AS4 pull over `%s` - nothing to pull; mpc:%s', connection_name, mpc)
            return

        # Route each pulled payload the same way an AS4 channel routes inbound ones.
        profile = wrapper.config['as4_profile']

        for payload in result.payloads:

            message = build_routed_message(profile, result.user_message, payload)

            if service_name:
                _ = self.invoke(service_name, message)
            else:
                _ = self.server.pubsub_redis.publish(topic_name, message, cid=self.cid, correl_id=self.cid)

        self.logger.info('AS4 pull over `%s` - message `%s` pulled, %d payload(s) routed',
            connection_name, result.user_message.message_id, len(result.payloads))

# ################################################################################################################################
# ################################################################################################################################
