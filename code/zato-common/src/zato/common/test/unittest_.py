# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import sleep

# Zato
from zato.common import PUBSUB
from zato.common.test import PubSubConfig
from zato.common.test.rest_client import RESTClient, RESTClientTestCase
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

_default = PUBSUB.DEFAULT

sec_name = _default.DEFAULT_SECDEF_NAME
username = _default.DEFAULT_USERNAME

# ################################################################################################################################
# ################################################################################################################################

class PubSubAPIRestImpl:
    def __init__(self, test:'BasePubSubRestTestCase', rest_client:'RESTClient') -> 'None':
        self.test = test
        self.rest_client = rest_client

# ################################################################################################################################

    def _publish(self, topic_name:'str', data:'any_') -> 'stranydict':
        request = {'data': data, 'has_gd':True}
        response = self.rest_client.post(PubSubConfig.PathPublish + topic_name, request) # type: stranydict
        sleep(6)
        return response

# ################################################################################################################################

    def _receive(self, topic_name:'str', needs_sleep:'bool'=True, expect_ok:'bool'=True) -> 'anylist':

        # Wait a moment to make sure a previously published message is delivered -
        # the server's delivery task runs once in 2 seconds.
        sleep(6)

        return cast_('anylist', self.rest_client.patch(PubSubConfig.PathReceive + topic_name, expect_ok=expect_ok))

# ################################################################################################################################

    def _subscribe(self, topic_name:'str', needs_unsubscribe:'bool'=False) -> 'str':
        if needs_unsubscribe:
            _ = self._unsubscribe(topic_name)
        response = self.rest_client.post(PubSubConfig.PathSubscribe + topic_name)
        sleep(6)
        return response['sub_key']

# ################################################################################################################################

    def _unsubscribe(self, topic_name:'str') -> 'anydict':

        # Delete a potential subscription based on our credentials
        response = self.rest_client.delete(PubSubConfig.PathUnsubscribe + topic_name) # type: anydict

        # Wait a moment to make sure the subscription is deleted
        sleep(6)

        # We always expect an empty dict on reply from unsubscribe
        self.test.assertDictEqual(response, {})

        # Our caller may want to run its own assertion too
        return response

# ################################################################################################################################
# ################################################################################################################################

class BasePubSubRestTestCase(RESTClientTestCase):

    needs_current_app       = False
    payload_only_messages   = False
    should_init_rest_client = True

# ################################################################################################################################

    def setUp(self) -> 'None':
        super().setUp()
        if self.should_init_rest_client:
            self.rest_client.init(username=username, sec_name=sec_name)
            self.api_impl = PubSubAPIRestImpl(self, self.rest_client)

# ################################################################################################################################

    def _publish(self, topic_name:'str', data:'any_') -> 'stranydict':
        return self.api_impl._publish(topic_name, data)

# ################################################################################################################################

    def _receive(self, topic_name:'str', needs_sleep:'bool'=True, expect_ok:'bool'=True) -> 'anylist':
        return self.api_impl._receive(topic_name, needs_sleep, expect_ok)

# ################################################################################################################################

    def _subscribe(self, topic_name:'str', needs_unsubscribe:'bool'=False) -> 'str':
        return self.api_impl._subscribe(topic_name, needs_unsubscribe)

# ################################################################################################################################

    def _unsubscribe(self, topic_name:'str') -> 'anydict':
        return self.api_impl._unsubscribe(topic_name)

# ################################################################################################################################
# ################################################################################################################################
