# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Live HL7
from live_hl7.recording import Raising_Error_Text, Raising_Service, Recorder, Send_Service

# ################################################################################################################################
# ################################################################################################################################

# The service behind the channel the PACS publishes identity changes to - it records what the PACS said
# and the channel's destinations carry it on to the second department
PACS_Record_Service = 'hospital.pacs.record'
PACS_Record_Label = 'pacs.adt'

# What the rest of the suite takes from the toolkit through this module
Raising_Error_Text = Raising_Error_Text
Raising_Service = Raising_Service
Send_Service = Send_Service

# ################################################################################################################################
# ################################################################################################################################

Recorders = [
    Recorder(PACS_Record_Label, PACS_Record_Service),
]

# ################################################################################################################################
# ################################################################################################################################
