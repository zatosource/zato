# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################


template_simple_03 = """
security:

  - name: 'Test.Enmasse.Simple-03.Sec.01.{test_suffix}'
    username: 'Demo Security Definition.Sec.01.{test_suffix}'
    type: basic_auth
    realm: 'Demo Security Definition'

outgoing_rest:

  - name: 'Test.Enmasse.Simple-03.Demo REST Connection.{test_suffix}'
    host: https://example.com
    url_path: /
    security_name: 'Test.Enmasse.Simple-03.Sec.01.{test_suffix}'

"""

# ################################################################################################################################
# ################################################################################################################################
