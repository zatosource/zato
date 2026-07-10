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

class TestAWSS3:

    def test_s3_roundtrip(self, zato_server:'anydict') -> 'None':
        """ An object stored in S3 through self.aws can be read back and its bucket is listed.
        """
        client = AdminClient(zato_server['base_url'], zato_server['invoke_password'])
        result = client.invoke('test.aws.s3-roundtrip', {
            'conn_name': zato_server['conn_name'],
            'bucket': 'test-invoices',
            'key': 'invoice-2026-001.json',
            'data': '{"invoice_id": "2026-001", "amount": 123.45}',
        })

        assert result['data'] == '{"invoice_id": "2026-001", "amount": 123.45}'
        assert 'test-invoices' in result['buckets']

# ################################################################################################################################
# ################################################################################################################################
