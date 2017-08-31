# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# Twilio
from twilio.rest import Client

# Zato
from zato.server.store import BaseAPI, BaseStore

logger = getLogger(__name__)

class TwilioAPI(BaseAPI):
    """ API to obtain Twilio connections through.
    """

class TwilioConnStore(BaseStore):
    """ Stores connections to Twilio.
    """
    def create_impl(self, config, config_no_sensitive):
        logger.warn('To be done %s', config)
