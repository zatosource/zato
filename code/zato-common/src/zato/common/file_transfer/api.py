# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class VerifyHow:
    """ The ways a connection checks a stored file.
    """
    Size      = 'size'
    Read_Back = 'read-back'

Verify_How_List    = (VerifyHow.Size, VerifyHow.Read_Back)
Default_Verify_How = VerifyHow.Size

Verify_How_Human = {
    VerifyHow.Size:      'Size',
    VerifyHow.Read_Back: 'Read back',
}

# ################################################################################################################################
# ################################################################################################################################

# The retry settings of a schedule, zero attempts means no limit.
Default_Max_Attempts         = 5
Default_Retry_Backoff        = 60
Retry_Backoff_Max            = 3600
Default_Quarantine_Directory = 'quarantine'

# The daily expectation of a schedule, zero files means no expectation, the days are ISO weekday numbers.
Default_Expected_Files = 0
Default_Expected_By    = ''
Default_Expected_Days  = '1,2,3,4,5'

# ################################################################################################################################
# ################################################################################################################################
