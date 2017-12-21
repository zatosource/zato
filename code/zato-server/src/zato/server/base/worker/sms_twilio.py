# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# Zato
from zato.server.base.worker.common import WorkerImpl

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class SMSTwilio(WorkerImpl):
    """ SMS Twilio-related functionality for worker objects.
    """

# ################################################################################################################################

    def on_broker_msg_SMS_TWILIO_CREATE(self, msg):
        self.sms_twilio_api.create(msg.name, msg)

# ################################################################################################################################

    def on_broker_msg_SMS_TWILIO_EDIT(self, msg):
        # It might be a rename
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']
        self.sms_twilio_api.edit(del_name, msg)

# ################################################################################################################################

    def on_broker_msg_SMS_TWILIO_DELETE(self, msg):
        self.sms_twilio_api.delete(msg.name)

# ################################################################################################################################
