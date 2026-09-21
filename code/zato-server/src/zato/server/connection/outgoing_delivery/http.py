# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How a queued message is handed over to an outgoing REST connection, and what the delivery page shows of it.

# stdlib
from urllib.parse import urlencode

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.pubsub.outgoing import detect_body_mode, Key_Data, Key_Headers, Key_Method, Key_Params, OutgoingInvoker, \
    OutgoingPage
from zato.common.util.http_retry import RetryPolicy

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anytuple, dictlist, stranydict
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

_dlq = HTTP_SOAP.DLQ

# The request facts of the details window
_fact_method       = 'Method'
_fact_content_type = 'Content type'
_fact_headers      = 'Headers'
_fact_query_string = 'Query string'

_content_type_header = 'Content-Type'

# ################################################################################################################################
# ################################################################################################################################

def get_http_invoker_options(request:'stranydict') -> 'stranydict':
    """ The invoke dialog's options that are a queued HTTP request's own - its method and its query string.
    """
    out = {
        'method': request[Key_Method],
        'query_params': urlencode(request[Key_Params]),
    }

    return out

# ################################################################################################################################

# The Dashboard's invoke dialog of outgoing REST connections
rest_invoker = OutgoingInvoker()
rest_invoker.url_prefix = '/zato/http-soap/invoke-outconn/'
rest_invoker.connection = 'outgoing'
rest_invoker.history_key_prefix = 'zato.invoke-history.outconn.'
rest_invoker.options = get_http_invoker_options

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

def get_http_content_type(request:'stranydict') -> 'str':
    """ The content type a queued HTTP request names in its headers, or an empty string if it names none.
    """
    header_name = _content_type_header.lower()

    for name, value in request[Key_Headers].items():
        if name.lower() == header_name:
            out = value
            break
    else:
        out = ''

    return out

# ################################################################################################################################

def get_http_destination(wrapper:'any_', request:'stranydict') -> 'str':
    """ The method and the address a queued HTTP request goes to, the message's own query string included.
    """
    address = wrapper.address

    if params := request[Key_Params]:
        query_string = urlencode(params)
        address = f'{address}?{query_string}'

    out = f'{request[Key_Method]} {address}'
    return out

# ################################################################################################################################

def get_http_details_facts(request:'stranydict') -> 'dictlist':
    """ The request facts the details window lists of a queued HTTP request.
    """
    content_type = get_http_content_type(request)

    out = [
        {'label': _fact_method, 'value': request[Key_Method]},
        {'label': _fact_content_type, 'value': content_type},
        {'label': _fact_headers, 'value': request[Key_Headers]},
        {'label': _fact_query_string, 'value': request[Key_Params]},
    ]

    return out

# ################################################################################################################################

def get_http_body_mode(request:'stranydict') -> 'str':
    """ The mode a queued HTTP request's body is shown in.
    """
    out = detect_body_mode(request[Key_Data])
    return out

# ################################################################################################################################

# What the delivery page shows of an outgoing REST connection's messages
rest_page = OutgoingPage()
rest_page.destination = get_http_destination
rest_page.details_facts = get_http_details_facts
rest_page.body_mode = get_http_body_mode
rest_page.invoker = rest_invoker

# ################################################################################################################################
# ################################################################################################################################

