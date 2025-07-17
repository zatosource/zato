# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.common.pubsub.backend.common import Backend

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.broker.client import BrokerClient
    from zato.common.pubsub.server import PubSubRESTServer
    from zato.common.typing_ import strdict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class RESTBackend(Backend):
    """ The consumer backend for the pub/sub REST server.
    """

    def __init__(self, rest_server:'PubSubRESTServer', broker_client:'BrokerClient') -> 'None':

        self.rest_server = rest_server
        super().__init__(broker_client)

# ################################################################################################################################

    def on_broker_msg_SECURITY_BASIC_AUTH_CREATE(self, msg:'strdict') -> 'None':

        # Local aliases
        cid = msg['cid']
        sec_name = msg['sec_name']
        password = msg['password']

        # Create the user now
        self.rest_server.create_user(cid, sec_name, password)

# ################################################################################################################################

    def on_broker_msg_SECURITY_BASIC_AUTH_EDIT(self, msg:'strdict') -> 'None':

        # Local aliases
        cid = msg['cid']

        has_sec_name_changed = msg['has_sec_name_changed']
        has_username_changed = msg['has_username_changed']

        old_sec_name = msg['old_sec_name']
        new_sec_name = msg['new_sec_name']

        old_username = msg['old_username']
        new_username = msg['new_username']

        # We go here if the username is different ..
        if has_username_changed:

            # .. log what we're doing ..
            logger.info(f'[{cid}] Updating username from `{old_username}` to `{new_username}`')

            # .. and actually do it ..
            self.rest_server.change_username(cid, old_username, new_username)

        # .. we go here if the name of the security definition is different ..
        if has_sec_name_changed:

            # .. log what we're doing ..
            logger.info(f'[{cid}] Updating sec_name from {old_sec_name} to {new_sec_name}')

            # .. and actually do it ..
            for topic_name, subs_by_sec_name in self.subs_by_topic.items():

                if old_sec_name in subs_by_sec_name:

                    # .. get the subscription object ..
                    subscription = subs_by_sec_name.pop(old_sec_name)

                    # .. update the sec_name within the subscription object ..
                    subscription.sec_name = new_sec_name

                    # .. store under the new sec_name ..
                    subs_by_sec_name[new_sec_name] = subscription

                    # .. and confirm we're done.
                    log_msg = f'[{cid}] Updated subscription for topic `{topic_name}` from `{old_sec_name}` to `{new_sec_name}`'
                    logger.info(log_msg)

# ################################################################################################################################
# ################################################################################################################################
