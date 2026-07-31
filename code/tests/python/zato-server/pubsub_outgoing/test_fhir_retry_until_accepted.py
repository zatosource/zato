# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
import unittest
from json import loads

# Zato
from zato.common.test.config_pubsub_outgoing import TestConfig

# local
from _helpers import get_client, publish_fhir

# ################################################################################################################################
# ################################################################################################################################

# How many times the FHIR server refuses the document before it stores it.
_refusal_count = 2

# How long to keep watching after the document arrived, to see whether it arrives again.
_quiet_period_seconds = 15

# ################################################################################################################################
# ################################################################################################################################

class FHIRRetryUntilAcceptedTestCase(unittest.TestCase):
    """ A document the FHIR server refuses is offered again until it is stored, and only once after that.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.client = get_client()

# ################################################################################################################################

    def test_a_refused_document_is_delivered_in_the_end(self) -> 'None':

        receiver = TestConfig.fhir_receiver
        receiver.refuse_next(_refusal_count)

        document = {
            'resourceType': 'Patient',
            'name': [{'family': 'Kowalska', 'given': ['Maria']}],
        }

        _ = publish_fhir(self.client, TestConfig.fhir_connection, document)

        requests = receiver.wait_for_requests(1)

        # The document arrived after the server stopped refusing it, which it could only do
        # because the client raised on each refusal and left the document in its queue ..
        self.assertEqual(len(requests), 1, requests)

        self.assertEqual(loads(requests[0].body), document)

        # .. it was refused as many times as the server was told to refuse it ..
        self.assertEqual(receiver.rejection_count, _refusal_count, receiver.rejection_count)

        # .. and having been stored, it is not offered again.
        time.sleep(_quiet_period_seconds)

        self.assertEqual(len(receiver.requests), 1, receiver.requests)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
