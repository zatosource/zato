# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.common.test.pubsub.publisher import PublisherTestData
from zato.common.typing_ import cast_
from zato.server.pubsub.publisher import PubCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylistnone
    from zato.server.base.parallel import ParallelServer
    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

class PublisherCtxTestCase(TestCase):

    def _get_test_ctx(self, gd_msg_list:'anylistnone', non_gd_msg_list:'anylistnone') -> 'PubCtx':

        ctx = PubCtx(
            cid = PublisherTestData.cid,
            cluster_id = PublisherTestData.cluster_id,
            pubsub = PublisherTestData.pubsub,
            topic = PublisherTestData.topic,
            endpoint_id = PublisherTestData.endpoint_id,
            endpoint_name = PublisherTestData.endpoint_name,
            subscriptions_by_topic = PublisherTestData.subscriptions_by_topic,
            msg_id_list = PublisherTestData.msg_id_list,
            pub_pattern_matched = PublisherTestData.pub_pattern_matched,
            ext_client_id = PublisherTestData.ext_client_id,
            is_first_run = PublisherTestData.is_first_run,
            now = PublisherTestData.now,
            is_wsx = PublisherTestData.is_wsx,
            service_invoke_func = PublisherTestData.service_invoke_func,
            new_session_func = PublisherTestData.new_session_func,

            gd_msg_list = cast_('list', gd_msg_list),
            non_gd_msg_list = cast_('list', non_gd_msg_list),
        )

        return ctx

# ################################################################################################################################

    def test_msg_id_lists_are_none(self):

        # We do not provide any list on input
        gd_msg_list = None
        non_gd_msg_list = None

        with self.assertRaises(ValueError) as cm:
            self._get_test_ctx(gd_msg_list, non_gd_msg_list)

        # Extract the exception ..
        exception = cm.exception

        # .. and run the assertions now.

        self.assertIs(type(exception), ValueError)
        self.assertEqual(str(exception), 'At least one of gd_msg_list or non_gd_msg_list must be provided')

# ################################################################################################################################

    def test_msg_id_gd_msg_list_is_none(self):

        # One of the elements is a list, but an empty one
        gd_msg_list = []
        non_gd_msg_list = None

        with self.assertRaises(ValueError) as cm:
            self._get_test_ctx(gd_msg_list, non_gd_msg_list)

        # Extract the exception ..
        exception = cm.exception

        # .. and run the assertions now.

        self.assertIs(type(exception), ValueError)
        self.assertEqual(str(exception), 'At least one of gd_msg_list or non_gd_msg_list must be provided')

# ################################################################################################################################

    def test_msg_id_non_gd_msg_list_is_none(self):

        # Another of the elements is a list, but an empty one
        gd_msg_list = None
        non_gd_msg_list = []

        with self.assertRaises(ValueError) as cm:
            self._get_test_ctx(gd_msg_list, non_gd_msg_list)

        # Extract the exception ..
        exception = cm.exception

        # .. and run the assertions now.

        self.assertIs(type(exception), ValueError)
        self.assertEqual(str(exception), 'At least one of gd_msg_list or non_gd_msg_list must be provided')

# ################################################################################################################################

    def test_msg_id_both_lists_are_empty(self):

        # Both elements are lists but both are empty
        gd_msg_list = []
        non_gd_msg_list = []

        with self.assertRaises(ValueError) as cm:
            self._get_test_ctx(gd_msg_list, non_gd_msg_list)

        # Extract the exception ..
        exception = cm.exception

        # .. and run the assertions now.

        self.assertIs(type(exception), ValueError)
        self.assertEqual(str(exception), 'At least one of gd_msg_list or non_gd_msg_list must be provided')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    from unittest import main
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
