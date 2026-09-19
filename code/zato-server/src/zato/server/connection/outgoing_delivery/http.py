# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How a queued message is handed over to an outgoing REST connection.

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.util.http_retry import RetryPolicy

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anytuple, stranydict
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

_dlq = HTTP_SOAP.DLQ

# Defaults of the DLQ fields
_dlq_defaults = {
    _dlq.Field_Use_DLQ: _dlq.Default_Use_DLQ,
    _dlq.Field_Action: _dlq.Default_Action,
    _dlq.Field_Retries: _dlq.Default_Retries,
    _dlq.Field_Retry_Interval: _dlq.Default_Retry_Interval,
    _dlq.Field_Forward_To: _dlq.Default_Forward_To,
    _dlq.Field_Keep_Header: _dlq.Default_Keep_Header,
}

# ################################################################################################################################
# ################################################################################################################################

def locate_rest(server:'ParallelServer', conn_id:'int') -> 'anytuple':
    """ An outgoing REST connection by its id, as its name and its wrapper.
    """
    item = server.config_manager.config_store.out_plain_http.get_by_id(conn_id)

    if not item:
        return ()

    out = (item.config['name'], item.conn)
    return out

# ################################################################################################################################

def deliver_to_rest(server:'ParallelServer', cid:'str', wrapper:'any_', request:'stranydict') -> 'None':
    """ Makes one attempt to hand a request over to an outgoing REST connection.
    """
    _ = wrapper.send_from_queue(cid, request)

# ################################################################################################################################

def get_rest_retry_policy(wrapper:'any_') -> 'RetryPolicy':
    """ The retry policy of an outgoing REST connection.
    """
    out = RetryPolicy.from_config(wrapper.config)
    return out

# ################################################################################################################################

def get_rest_dlq_settings(wrapper:'any_') -> 'stranydict':
    """ The DLQ settings of an outgoing REST connection, with defaults filled in.
    """
    config = wrapper.config
    out = {}

    for field, default in _dlq_defaults.items():
        value = config[field]

        if value is None:
            value = default

        out[field] = value

    return out

# ################################################################################################################################
# ################################################################################################################################

