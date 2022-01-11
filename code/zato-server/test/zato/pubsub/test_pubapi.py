# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main

# Zato
from zato.common import PUBSUB
from zato.common.test.rest_client import RESTClientTestCase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

sec_name   = PUBSUB.DEFAULT.INTERNAL_SECDEF_NAME
username   = 'pubsub'
topic_name = '/zato/demo/sample'

class config:
    path_publish     = f'/zato/pubsub/topic/{topic_name}'
    path_receive     = f'/zato/pubsub/topic/{topic_name}'
    path_subscribe   = f'/zato/pubsub/subscribe/topic/{topic_name}'
    path_unsubscribe = f'/zato/pubsub/subscribe/topic/{topic_name}'

# ################################################################################################################################
# ################################################################################################################################

class PubAPITestCase(RESTClientTestCase):

    needs_current_app     = False
    payload_only_messages = False

# ################################################################################################################################

    def setUp(self) -> None:
        super().setUp()
        self.rest_client.init(username=username, sec_name=sec_name)

# ################################################################################################################################

    def _unsubscribe(self) -> 'anydict':
        response = self.rest_client.delete(config.path_unsubscribe) # type: anydict

        # We always expect an empty dict on reply from unsubscribe
        self.assertDictEqual(response, {})

        # Our caller may want to run its own assertion too
        return response

# ################################################################################################################################

    def test_self_subscribe(self):

        # Before subscribing, make sure we are not currently subscribed
        self._unsubscribe()

# ################################################################################################################################

    def test_self_unsubscribe(self):

        # Unsubscribe once ..
        response = self._unsubscribe()

        # .. we expect an empty dict on reply
        self.assertDictEqual(response, {})

        # .. unsubscribe once more - it is not an error to unsubscribe
        # .. even if we are already unsubscribed.
        response = self._unsubscribe()
        self.assertDictEqual(response, {})

# ################################################################################################################################
# ################################################################################################################################


if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
