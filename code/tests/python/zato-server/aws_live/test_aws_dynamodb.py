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

class TestAWSDynamoDB:

    def test_dynamodb_roundtrip(self, zato_server:'anydict') -> 'None':
        """ An item stored in DynamoDB through self.aws is read back through the resource API.
        """
        client = AdminClient(zato_server['base_url'], zato_server['invoke_password'])
        result = client.invoke('test.aws.dynamodb-roundtrip', {
            'conn_name': zato_server['conn_name'],
            'table_name': 'test-customers',
            'customer_id': 'customer-2026-001',
            'customer_name': 'Test Customer',
        })

        assert result['customer_id'] == 'customer-2026-001'
        assert result['name'] == 'Test Customer'

# ################################################################################################################################
# ################################################################################################################################
