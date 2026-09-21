# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How a queued message is handed over to an outgoing REST or SOAP connection, and what the delivery page shows of it.

# stdlib
from urllib.parse import urlencode

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.pubsub.outgoing import Body_Mode_XML, detect_body_mode, Key_Data, Key_Headers, Key_Method, Key_Operation, \
    Key_Params, OutgoingInvoker, OutgoingPage
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
_fact_operation    = 'Operation'
_fact_content_type = 'Content type'
_fact_headers      = 'Headers'
_fact_soap_headers = 'SOAP headers'
_fact_query_string = 'Query string'

_content_type_header = 'Content-Type'

# The field of the SOAP invoke dialog a queued message's operation goes into
_operation_field = 'operation'

# Both kinds of connection are invoked through the one outgoing invoke endpoint, which reads the connection's transport
_invoke_url_prefix = '/zato/http-soap/invoke-outconn/'

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

def get_soap_invoker_options(request:'stranydict') -> 'stranydict':
    """ The invoke dialog's options that are a queued SOAP request's own - its operation, in the dialog's own field.
    """
    out = {
        'fields': [
            {'name': _operation_field, 'label': _fact_operation, 'value': request[Key_Operation]},
        ],
    }

    return out

# ################################################################################################################################

# The Dashboard's invoke dialog of outgoing REST connections
rest_invoker = OutgoingInvoker()
rest_invoker.url_prefix = _invoke_url_prefix
rest_invoker.connection = 'outgoing'
rest_invoker.history_key_prefix = 'zato.invoke-history.outconn.'
rest_invoker.options = get_http_invoker_options

# The Dashboard's invoke dialog of outgoing SOAP connections
soap_invoker = OutgoingInvoker()
soap_invoker.url_prefix = _invoke_url_prefix
soap_invoker.connection = 'outconn-soap'
soap_invoker.history_key_prefix = 'zato.invoke-history.outconn-soap.'
soap_invoker.options = get_soap_invoker_options

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

def _locate_http_soap(config_dict:'any_', conn_id:'int') -> 'anytuple':
    """ An outgoing HTTP/SOAP connection by its id in one of the config store's dicts, as its name and its wrapper.
    """
    item = config_dict.get_by_id(conn_id)

    if not item:
        return ()

    out = (item.config['name'], item.conn)
    return out

# ################################################################################################################################

def locate_rest(server:'ParallelServer', conn_id:'int') -> 'anytuple':
    """ An outgoing REST connection by its id, as its name and its wrapper.
    """
    out = _locate_http_soap(server.config_manager.config_store.out_plain_http, conn_id)
    return out

# ################################################################################################################################

def locate_soap(server:'ParallelServer', conn_id:'int') -> 'anytuple':
    """ An outgoing SOAP connection by its id, as its name and its wrapper.
    """
    out = _locate_http_soap(server.config_manager.config_store.out_soap, conn_id)
    return out

# ################################################################################################################################

def deliver_to_rest(server:'ParallelServer', cid:'str', wrapper:'any_', request:'stranydict') -> 'None':
    """ Makes one attempt to hand a request over to an outgoing REST connection.
    """
    _ = wrapper.send_from_queue(cid, request)

# ################################################################################################################################

def deliver_to_soap(server:'ParallelServer', cid:'str', wrapper:'any_', request:'stranydict') -> 'None':
    """ Makes one attempt to hand an invocation over to an outgoing SOAP connection - a fault raises, as any other failure does.
    """
    _ = wrapper.send_soap_from_queue(cid, request)

# ################################################################################################################################

def get_http_retry_policy(wrapper:'any_') -> 'RetryPolicy':
    """ The retry policy of an outgoing REST or SOAP connection.
    """
    out = RetryPolicy.from_config(wrapper.config)
    return out

# ################################################################################################################################

def get_http_dlq_settings(wrapper:'any_') -> 'stranydict':
    """ The DLQ settings of an outgoing REST or SOAP connection, with defaults filled in.
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

def get_soap_destination(wrapper:'any_', request:'stranydict') -> 'str':
    """ The operation and the address a queued SOAP invocation goes to.
    """
    out = f'{request[Key_Operation]} {wrapper.address}'
    return out

# ################################################################################################################################

def get_soap_details_facts(request:'stranydict') -> 'dictlist':
    """ The request facts the details window lists of a queued SOAP invocation.
    """
    out = [
        {'label': _fact_operation, 'value': request[Key_Operation]},
        {'label': _fact_soap_headers, 'value': request[Key_Headers]},
    ]

    return out

# ################################################################################################################################

def get_soap_body_mode(request:'stranydict') -> 'str':
    """ A queued SOAP invocation's body is the XML of its operation element.
    """
    return Body_Mode_XML

# ################################################################################################################################

# What the delivery page shows of an outgoing SOAP connection's messages
soap_page = OutgoingPage()
soap_page.destination = get_soap_destination
soap_page.details_facts = get_soap_details_facts
soap_page.body_mode = get_soap_body_mode
soap_page.invoker = soap_invoker

# ################################################################################################################################
# ################################################################################################################################

