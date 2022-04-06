# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from unittest import TestCase

# Zato
from zato.common.test.pubsub.publisher import PublisherTestData
from zato.common.typing_ import cast_
from zato.server.pubsub.publisher import Publisher, PubRequest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.server.base.parallel import ParallelServer
    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

class PublisherMessageTestCase(TestCase):

    def get_default_request(
        self,
        *,
        cid,        # type: str
        msg_id,     # type: str
        topic_name, # type: str
        pub_pattern_matched # type: str
    ) -> 'PubRequest':

        data = {
            'msg_id': msg_id,
            'topic_name': topic_name,
            'pub_pattern_matched': pub_pattern_matched,
        }

        # Correlation ID (cid) is provided via extra parameters so as to use the same mechanism that the publish service uses.
        out = PubRequest._zato_from_dict(data, extra={'cid':cid})
        return out

# ################################################################################################################################

    def test_get_data_prefixes(self) -> 'None':

        # Make a deep copy so as not to interfere with other tests.
        test_data = deepcopy(PublisherTestData)

        # Make them shorted for the purposes of our test
        test_data.pubsub.data_prefix_len = 7
        test_data.pubsub.data_prefix_short_len = 3

        publisher = Publisher(
            pubsub = test_data.pubsub,
            server = cast_('ParallelServer', test_data.server),
            marshal_api = test_data.server.marshal_api,
            service_invoke_func = test_data.service_invoke_func,
            new_session_func = test_data.new_session_func,
        )

        data = '1234567890'
        data_prefix, data_prefix_short = publisher.get_data_prefixes(data)

        self.assertEqual(data_prefix, '1234567')
        self.assertEqual(data_prefix_short, '123')

# ################################################################################################################################

    def test_build_message_default(self) -> 'None':

        cid = 'abc'
        msg_id = 'my.msg.123'
        topic_name = '/my-topic'
        pub_pattern_matched = '/*'

        request = self.get_default_request(
            cid = cid,
            msg_id = msg_id,
            topic_name = topic_name,
            pub_pattern_matched = pub_pattern_matched
        )

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    from unittest import main
    main()

# ################################################################################################################################
# ################################################################################################################################
