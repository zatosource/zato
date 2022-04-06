# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.common.test.pubsub.publisher import PublisherTestData
from zato.common.typing_ import cast_
from zato.server.pubsub.publisher import Publisher

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.server.base.parallel import ParallelServer
    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

class PublisherMessageTestCase(TestCase):

    def test_get_data_prefixes(self) -> 'None':

        # Make them shorted for the purposes of our test
        PublisherTestData.pubsub.data_prefix_len = 7
        PublisherTestData.pubsub.data_prefix_short_len = 3

        publisher = Publisher(
            pubsub = PublisherTestData.pubsub,
            server = cast_('ParallelServer', PublisherTestData.server),
            marshal_api = PublisherTestData.server.marshal_api,
            service_invoke_func = PublisherTestData.service_invoke_func,
            new_session_func = PublisherTestData.new_session_func,
        )

        data = '1234567890'
        data_prefix, data_prefix_short = publisher.get_data_prefixes(data)

        self.assertEqual(data_prefix, '1234567')
        self.assertEqual(data_prefix_short, '123')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    from unittest import main
    main()

# ################################################################################################################################
# ################################################################################################################################
