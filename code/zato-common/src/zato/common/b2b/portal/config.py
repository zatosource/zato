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
Local_Organization = 'Pinecrest Telecom'

# The environment variable with the path to the logo of the organization, which replaces its name above the navigation
Logo_Env_Variable = 'Zato_B2B_Gateway_Logo'

Logo_Path = os.environ.get(Logo_Env_Variable)

# The address the logo is served under
Logo_URL = '/logo'

# The cookie the browser keeps the width of the navigation pane in, in pixels, after the pane is resized
Navigation_Width_Cookie = 'navigation-width'

# The cookie the browser keeps in whether the navigation pane is collapsed, and the value it has when it is
Navigation_Collapsed_Cookie = 'navigation-collapsed'
Navigation_Collapsed_Value = '1'

Local_Party_ID = '232510151'

Local_Role = 'WholesaleProvider'

Local_Host = 'b2b.pinecrest-telecom.example.com'

Local_AS2_ID = 'PINECREST-B2B'

# ################################################################################################################################
# ################################################################################################################################
