# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class HL7Config:
    """ The services of the MLLP tests of a server with several workers and the directory in which the channel service
    records its invocations.
    """

    # The directory under the temporary directory of the host that holds one directory for each control ID,
    # in which every invocation of the channel service creates one file named after the slot that ran it
    Record_Directory = 'zato-multi-cpu-hl7'

    Record_Service = 'test.multi-cpu.hl7-record'
    Send_Service = 'test.multi-cpu.mllp-send'
    Exists_Service = 'test.multi-cpu.mllp-exists'

    # The outcomes of a send that the send service reports
    Outcome_Sent = 'sent'
    Outcome_Failed = 'failed'
    Outcome_Stopped = 'stopped'

# ################################################################################################################################
# ################################################################################################################################
