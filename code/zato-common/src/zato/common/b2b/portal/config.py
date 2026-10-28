# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# ################################################################################################################################
# ################################################################################################################################

Package_Dir = os.path.dirname(os.path.abspath(__file__))

Static_Dir = os.path.join(Package_Dir, 'static')

Template_Dir = os.path.join(Package_Dir, 'templates')

# The prefix of every asset URL
Static_URL = '/assets/'

# The name the server announces in the Server header of each response
Server_Name = 'server'

# The organization the portal is operated by, shown above the navigation
Local_Organization = 'Lorem Ipsum'

Local_Party_ID = '232510151'

Local_Role = 'WholesaleProvider'

Local_Host = 'b2b.lorem-ipsum.example.com'

# ################################################################################################################################
# ################################################################################################################################
