# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.test.client import AdminClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

class TestAWSSQS:

    def test_sqs_roundtrip(self, zato_server:'anydict') -> 'None':
        """ A message sent to an SQS queue through self.aws is received back intact.
        """
        client = AdminClient(zato_server['base_url'], zato_server['invoke_password'])
        result = client.invoke('test.aws.sqs-roundtrip', {
            'conn_name': zato_server['conn_name'],
            'queue_name': 'test-orders',
            'message_body': '{"order_id": 123, "status": "confirmed"}',
        })

        assert result['message_body'] == '{"order_id": 123, "status": "confirmed"}'

# ################################################################################################################################
# ################################################################################################################################
