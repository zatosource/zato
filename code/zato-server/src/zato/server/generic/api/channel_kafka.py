# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.common.api import HTTP_SOAP, KAFKA
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

_consumer = KAFKA.Consumer
_retry = HTTP_SOAP.Retry
_dlq = HTTP_SOAP.DLQ

# ################################################################################################################################
# ################################################################################################################################

# Defaults for fields the create path did not supply
channel_config_defaults:'anydict' = {
    'topic': '',
    'group_id': '',
    'service': '',
    'sasl_mechanism': '',
    'ssl': False,
    'ssl_ca_file': '',
    'ssl_cert_file': '',
    'ssl_key_file': '',
    KAFKA.Field_SSL_Key_Password: '',
    _retry.Field_Max_Retries: _retry.Default_Max_Retries,
    _retry.Field_Sleep_Time: _retry.Default_Sleep_Time,
    _retry.Field_Backoff_Threshold: _retry.Default_Backoff_Threshold,
    _retry.Field_Backoff_Multiplier: _retry.Default_Backoff_Multiplier,
}
channel_config_defaults.update(_consumer.Defaults)
channel_config_defaults.update(Delivery_Field_Defaults)

# A channel's queue switch is always off
channel_config_defaults[HTTP_SOAP.Queue.Field_Use_Queue] = False

# Config keys that must be integers but may arrive as strings from opaque storage
channel_int_config_keys = _consumer.IntFieldList + (
    _retry.Field_Max_Retries,
    _retry.Field_Sleep_Time,
    _retry.Field_Backoff_Threshold,
    _retry.Field_Backoff_Multiplier,
    _dlq.Field_Retries,
    _dlq.Field_Retry_Interval,
)

# Config keys that must be booleans but may arrive as strings from opaque storage
channel_bool_config_keys = _consumer.BoolFieldList + (
    'ssl',
    _dlq.Field_Use_DLQ,
    _dlq.Field_Keep_Header,
)

# ################################################################################################################################
# ################################################################################################################################

class ChannelKafkaWrapper:
    """ The configuration of a Kafka channel.
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        self.config = config
        self.server = server
        logger.info('Kafka channel `%s` registered', config.name)

    def delete(self) -> 'None':
        pass

    def build_wrapper(self) -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################
