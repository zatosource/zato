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

class TestAWSPing:

    def test_ping(self, zato_server:'anydict') -> 'None':
        """ A ping through the AWS connection returns the caller's account ID.
        """
        client = AdminClient(zato_server['base_url'], zato_server['invoke_password'])
        result = client.invoke('test.aws.ping', {
            'conn_name': zato_server['conn_name'],
        })

        assert result['account']

# ################################################################################################################################
# ################################################################################################################################
