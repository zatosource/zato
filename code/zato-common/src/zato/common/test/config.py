# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# ################################################################################################################################
# ################################################################################################################################

class TestConfig:

    default_stdout = b'(None)\n'

    current_app = 'CRM'
    super_user_name = 'zato.unit-test.admin1'
    super_user_password = 'hQ9nl93UDqGus'
    super_user_totp_key = 'KMCLCWN4YPMD2WO3'

    username_prefix = 'test.{}+{}'
    random_prefix = 'rand.{}+{}'

    server_location = os.path.expanduser('~/env/sso.test/server1')
    server_address  = 'http://localhost:17010{}'

# ################################################################################################################################
# ################################################################################################################################
