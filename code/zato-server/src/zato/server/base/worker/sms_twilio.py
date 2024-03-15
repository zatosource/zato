# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.base.worker.common import WorkerImpl

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.server.base.worker import WorkerStore

# ################################################################################################################################
# ################################################################################################################################

class SMSTwilio(WorkerImpl):
    """ SMS Twilio-related functionality for worker objects.
    """
    def on_broker_msg_SMS_TWILIO_CREATE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':

        msg.auth_token = self.server.decrypt(msg.auth_token)
        self.sms_twilio_api.create(msg.name, msg)

# ################################################################################################################################

    def on_broker_msg_SMS_TWILIO_EDIT(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':

        # It might be a rename
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']
        msg.auth_token = self.server.decrypt(msg.auth_token)
        self.sms_twilio_api.edit(del_name, msg)

# ################################################################################################################################

    def on_broker_msg_SMS_TWILIO_DELETE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.sms_twilio_api.delete(msg.name)

# ################################################################################################################################
