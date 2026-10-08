# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An SMS channel - the configuration alone, because its traffic arrives either through the internal webhook
# channel or through the scheduler job that polls its provider. The provider and the credentials come from the
# outgoing connection the channel names and are never stored twice.

# stdlib
from logging import getLogger

# Zato
from zato.common.api import HTTP_SOAP, SMS
from zato.common.util.delivery_config import Delivery_Field_Defaults

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import anydict
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

_retry = HTTP_SOAP.Retry
_dlq = HTTP_SOAP.DLQ
_scheduler = SMS.Scheduler

# ################################################################################################################################
# ################################################################################################################################

# Defaults for fields the create path did not supply
channel_config_defaults:'anydict' = {
    SMS.Field_Outconn_Name: '',
    SMS.Field_Service: '',
    SMS.Field_Receive_Mode: SMS.Receive_Mode.Webhook,
    SMS.Field_Poll_State: '',
    _scheduler.Field_Run_Every: _scheduler.Default_Run_Every,
    _scheduler.Field_Run_Unit: _scheduler.Default_Run_Unit,
    _scheduler.Field_Job_ID: 0,
    _retry.Field_Max_Retries: _retry.Default_Max_Retries,
    _retry.Field_Sleep_Time: _retry.Default_Sleep_Time,
    _retry.Field_Backoff_Threshold: _retry.Default_Backoff_Threshold,
    _retry.Field_Backoff_Multiplier: _retry.Default_Backoff_Multiplier,
}
channel_config_defaults.update(Delivery_Field_Defaults)

# Config keys that must be integers but may arrive as strings from opaque storage
channel_int_config_keys = (
    _scheduler.Field_Run_Every,
    _scheduler.Field_Job_ID,
    _retry.Field_Max_Retries,
    _retry.Field_Sleep_Time,
    _retry.Field_Backoff_Threshold,
    _retry.Field_Backoff_Multiplier,
    _dlq.Field_Retries,
    _dlq.Field_Retry_Interval,
)

# Config keys that must be booleans but may arrive as strings from opaque storage
channel_bool_config_keys = (
    HTTP_SOAP.Queue.Field_Use_Queue,
    _dlq.Field_Use_DLQ,
    _dlq.Field_Keep_Header,
)

# ################################################################################################################################
# ################################################################################################################################

class ChannelSMSWrapper:
    """ The configuration of an SMS channel.
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        self.config = config
        self.server = server
        logger.info('SMS channel `%s` registered (%s)', config.name, config[SMS.Field_Receive_Mode])

    def delete(self) -> 'None':
        pass

    def build_wrapper(self) -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################
