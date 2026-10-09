# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The field lists and the validation of SMS connection and channel definitions, used by the server and by enmasse.

# Zato
from zato.common.api import SMS

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

_scheduler = SMS.Scheduler

# The fields of an outgoing connection beyond its name and active flag
Outgoing_Field_Names = (
    SMS.Field_Provider,
    SMS.Field_Host,
    SMS.Field_Username,
    SMS.Field_Sender,
    SMS.Field_Signature_Secret,
    SMS.Field_Channel_Name,
    SMS.Field_Pool_Size,
    SMS.Field_Timeout,
)

# The fields of an outgoing connection that are integers
Outgoing_Int_Field_Names = (
    SMS.Field_Pool_Size,
    SMS.Field_Timeout,
)

# The fields of a channel beyond its name and active flag
Channel_Field_Names = (
    SMS.Field_Outconn_Name,
    SMS.Field_Service,
    SMS.Field_Receive_Mode,
    _scheduler.Field_Run_Every,
    _scheduler.Field_Run_Unit,
    _scheduler.Field_Job_ID,
    SMS.Field_Poll_State,
)

# The fields of a channel that are integers
Channel_Int_Field_Names = (
    _scheduler.Field_Run_Every,
    _scheduler.Field_Job_ID,
)

# ################################################################################################################################
# ################################################################################################################################

def get_webhook_path(channel_name:'str') -> 'str':
    """ The webhook URL path of one SMS channel.
    """
    out = SMS.Webhook_Path_Prefix + channel_name
    return out

# ################################################################################################################################

def validate_outgoing_definition(data:'stranydict') -> 'None':
    """ Checks the provider-dependent fields of an outgoing SMS connection, raising ValueError on the first fault.
    """
    provider = data.get(SMS.Field_Provider)

    if provider not in SMS.ProviderList:
        raise ValueError(f'SMS provider `{provider}` is not one of `{SMS.ProviderList}`')

    signature_secret = data.get(SMS.Field_Signature_Secret)

    if signature_secret:
        if provider not in SMS.Providers_With_Signature_Secret:
            raise ValueError(f'SMS provider `{provider}` does not use a signature secret')

    host = data.get(SMS.Field_Host)

    if not host:
        if provider in SMS.Providers_Requiring_Host:
            raise ValueError(f'SMS provider `{provider}` requires a host')

# ################################################################################################################################

def validate_channel_definition(data:'stranydict') -> 'None':
    """ Checks the fields of an SMS channel, raising ValueError on the first fault.
    """
    receive_mode = data.get(SMS.Field_Receive_Mode)

    if receive_mode not in SMS.Receive_Mode_List:
        raise ValueError(f'SMS receive mode `{receive_mode}` is not one of `{SMS.Receive_Mode_List}`')

    if not data.get(SMS.Field_Outconn_Name):
        raise ValueError('An SMS channel requires an outgoing connection')

    if not data.get(SMS.Field_Service):
        raise ValueError('An SMS channel requires a service')

# ################################################################################################################################

def apply_outgoing_host_default(data:'stranydict') -> 'None':
    """ Sets the provider's default host on a definition without a host.
    """
    if not data.get(SMS.Field_Host):
        provider = data[SMS.Field_Provider]
        data[SMS.Field_Host] = SMS.Default_Host[provider]

# ################################################################################################################################

def is_polling(data:'any_') -> 'bool':
    """ Whether a channel is in polling mode.
    """
    out = data.get(SMS.Field_Receive_Mode) == SMS.Receive_Mode.Polling
    return out

# ################################################################################################################################
# ################################################################################################################################
