# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Live HL7
from live_hl7.recording import Raising_Error_Text, Raising_Service, Recorder

# ################################################################################################################################
# ################################################################################################################################

# The channel the LIS dispatches orders to, and the service behind it - the analyzer's side of the middleware,
# it records what the LIS ordered under the channel's name and acknowledges it
Orders_Channel = 'lab.orders'
Orders_Record_Service = 'lab.orders.record'

# What the rest of the suite takes from the toolkit through this module
Raising_Error_Text = Raising_Error_Text
Raising_Service = Raising_Service

# ################################################################################################################################
# ################################################################################################################################

Recorders = [
    Recorder(Orders_Channel, Orders_Record_Service),
]

# ################################################################################################################################
# ################################################################################################################################
