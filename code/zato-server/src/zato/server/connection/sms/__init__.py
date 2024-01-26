# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# ################################################################################################################################

if 0:
    from zato.server.connection.sms.twilio import TwilioAPI

    TwilioAPI = TwilioAPI

# ################################################################################################################################

class SMSAPI:
    def __init__(self, twilio):
        # type: (TwilioAPI)
        self.twilio = twilio

# ################################################################################################################################
