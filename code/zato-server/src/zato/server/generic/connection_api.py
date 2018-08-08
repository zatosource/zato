# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# Twilio
from twilio.rest import Client as _TwilioClient

# Zato
from zato.server.store import BaseAPI, BaseStore

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class TwilioAPI(BaseAPI):
    """ API to obtain Twilio connections through.
    """

# ################################################################################################################################

class TwilioConnStore(BaseStore):
    """ Stores connections to Twilio.
    """
    def create_impl(self, config, config_no_sensitive):
        twilio_messages = _TwilioClient(config.account_sid, config.auth_token).messages
        twilio_messages.send = send(twilio_messages, config)

        return twilio_messages

# ################################################################################################################################
