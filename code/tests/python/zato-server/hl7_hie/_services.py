# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Live HL7
from live_hl7.recording import Recorder, Send_Service

# ################################################################################################################################
# ################################################################################################################################

# The service behind the shared record's channel - it records the message and hands it to the record's queue
Record_Service = 'hie.shr.record'

# What the shared record's front door files what reached it under
Record_Label = 'shr'

# What the record's channel calls the destination its message goes on to, and the key the record's REST
# resource expects the message under
SHR_Destination = 'shr'
SHR_JSON_Key = 'hl7'

# The service a facility's own systems reach the exchange through
Send_Service = Send_Service

# ################################################################################################################################
# ################################################################################################################################

# The one recording service of the exchange - the shared record's front door
Recorders = [
    Recorder(Record_Label, Record_Service, SHR_Destination, SHR_JSON_Key),
]

# ################################################################################################################################
# ################################################################################################################################
