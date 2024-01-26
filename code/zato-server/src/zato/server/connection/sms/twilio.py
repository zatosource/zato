# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
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

def send(twilio_messages, config):
    """ Sends a Twilio message 'body' to phone number 'to' from the phone number 'from'. Attached dynamically
    to all Twilio connections so as to make it for Zato users to specify default values in configuration.
    """
    def _send(_zato_body, _zato_to=None, _zato_from=None, **kwargs):
        """ Actually sends the messae.
        """
        return twilio_messages.create(**dict({
            'body': _zato_body,
            'to': _zato_to or config.default_to or kwargs.pop('to', None),
            'from_': _zato_from or config.default_from or kwargs.pop('from_', None),
        }, **kwargs))

    return _send

# ################################################################################################################################

class TwilioConnStore(BaseStore):
    """ Stores connections to Twilio.
    """
    def create_impl(self, config, config_no_sensitive):
        twilio_messages = _TwilioClient(config.account_sid, config.auth_token).messages
        twilio_messages.send = send(twilio_messages, config)

        return twilio_messages

# ################################################################################################################################
