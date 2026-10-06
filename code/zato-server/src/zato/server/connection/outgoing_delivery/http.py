# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How a queued message is handed over to an outgoing REST, SOAP or FHIR connection, and what the delivery page shows of it.

# stdlib
from urllib.parse import urlencode

# Zato
from zato.common.api import CHANNEL, HTTP_SOAP, URL_TYPE
from zato.common.pubsub.outgoing import Body_Mode_JSON, Body_Mode_XML, detect_body_mode, encode_payload, Key_Data, \
    Key_Data_Format, Key_Headers, Key_Method, Key_Operation, Key_Params, Key_Path, Key_Path_Params, Key_Service, \
    Key_Transport, OutgoingInvoker, OutgoingPage
from zato.common.soap.common import SOAP_Action_Header
from zato.common.util.retry import RetryPolicy
from zato.server.connection.http_soap.channel_queue import build_delivery_request_ctx
from zato.server.connection.http_soap.channel_soap import parse_soap_request, resolve_soap_payload

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anytuple, dictlist, stranydict
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

_dlq = HTTP_SOAP.DLQ
_retry = HTTP_SOAP.Retry

# The request facts of the details window
_fact_method       = 'Method'
_fact_operation    = 'Operation'
_fact_path         = 'Path'
_fact_content_type = 'Content type'
_fact_headers      = 'Headers'
_fact_soap_headers = 'SOAP headers'
_fact_query_string = 'Query string'
_fact_path_params  = 'Path parameters'
_fact_data_format  = 'Data format'

# The WSGI keys a channel's queued request carries its content type and its SOAP action under
_wsgi_content_type = 'CONTENT_TYPE'
_soap_action_header_key = 'HTTP_{}'.format(SOAP_Action_Header.upper())

# What a FHIR connection sends, which is always this
_fhir_content_type = 'application/json'

# How many seconds to wait for a pooled FHIR client
_fhir_block_timeout = 30

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

def locate_fhir(server:'ParallelServer', conn_id:'int') -> 'anytuple':
    """ An outgoing HL7 FHIR connection by its id, as its name and its wrapper.
    """
    for item in server.config_manager.outconn_hl7_fhir.values():
        if item['id'] == conn_id:
            out = (item['name'], item.conn)
            return out

    return ()

# ################################################################################################################################

def deliver_to_fhir(server:'ParallelServer', cid:'str', wrapper:'any_', request:'stranydict') -> 'None':
    """ Makes one attempt to hand a request over to an outgoing HL7 FHIR connection through one of its pooled clients.
    """
    with wrapper.client(should_block=True, block_timeout=_fhir_block_timeout) as client:
        client.zato_send_from_queue(cid, request)

# ################################################################################################################################

def get_http_retry_policy(wrapper:'any_') -> 'RetryPolicy':
    """ The retry policy of an outgoing REST, SOAP, FHIR or MLLP connection - all four carry the same fields in their config.
    """
    out = RetryPolicy.from_config(wrapper.config, _retry)
    return out

# ################################################################################################################################

def get_http_dlq_settings(wrapper:'any_') -> 'stranydict':
    """ The DLQ settings of an outgoing REST, SOAP, FHIR or MLLP connection, with defaults filled in.
    """
    out = _dlq_settings_from_config(wrapper.config)
    return out

# ################################################################################################################################

def _dlq_settings_from_config(config:'stranydict') -> 'stranydict':
    """ The DLQ settings one config carries, with defaults filled in for the fields it does not say.
    """
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

def get_fhir_destination(wrapper:'any_', request:'stranydict') -> 'str':
    """ The method and the address a queued FHIR request goes to - the connection's base address with the request's path
    under it, and the message's own query string.
    """
    base_address = wrapper.config['address'].rstrip('/')
    path = request[Key_Path].lstrip('/')
    address = f'{base_address}/{path}'

    if params := request[Key_Params]:
        query_string = urlencode(params)
        address = f'{address}?{query_string}'

    out = f'{request[Key_Method]} {address}'
    return out

# ################################################################################################################################

def get_fhir_details_facts(request:'stranydict') -> 'dictlist':
    """ The request facts the details window lists of a queued FHIR request.
    """
    out = [
        {'label': _fact_method, 'value': request[Key_Method]},
        {'label': _fact_path, 'value': request[Key_Path]},
        {'label': _fact_content_type, 'value': _fhir_content_type},
        {'label': _fact_query_string, 'value': request[Key_Params]},
    ]

    return out

# ################################################################################################################################

def get_fhir_body_mode(request:'stranydict') -> 'str':
    """ A queued FHIR request's body is the JSON of its resource.
    """
    return Body_Mode_JSON

# ################################################################################################################################

# What the delivery page shows of an outgoing FHIR connection's messages - its list page has no invoke dialog
fhir_page = OutgoingPage()
fhir_page.destination = get_fhir_destination
fhir_page.details_facts = get_fhir_details_facts
fhir_page.body_mode = get_fhir_body_mode

# ################################################################################################################################
# ################################################################################################################################

def _locate_http_channel(server:'ParallelServer', transport:'str', conn_id:'int') -> 'anytuple':
    """ A REST or SOAP channel by its id, as its name and its channel item - the item stands where an outgoing
    connection's wrapper does, the service reads it as self.channel.config.
    """
    url_data = server.config_manager.request_dispatcher.url_data

    for item in url_data.channel_data:
        if item['transport'] == transport:
            if item['id'] == conn_id:
                out = (item['name'], item)
                return out

    return ()

# ################################################################################################################################

def locate_rest_channel(server:'ParallelServer', conn_id:'int') -> 'anytuple':
    """ A REST channel by its id, as its name and its channel item.
    """
    out = _locate_http_channel(server, URL_TYPE.PLAIN_HTTP, conn_id)
    return out

# ################################################################################################################################

def locate_soap_channel(server:'ParallelServer', conn_id:'int') -> 'anytuple':
    """ A SOAP channel by its id, as its name and its channel item.
    """
    out = _locate_http_channel(server, URL_TYPE.SOAP, conn_id)
    return out

# ################################################################################################################################

def deliver_to_http_channel(server:'ParallelServer', cid:'str', channel_item:'any_', request:'stranydict') -> 'None':
    """ Makes one attempt to run the service of a REST or SOAP channel with a request its queue stored - a full invocation,
    with the hooks around handle and the destinations after it, and an exception out of it is the failed attempt.
    """
    request_ctx = build_delivery_request_ctx(channel_item, request)
    raw_request = encode_payload(request)

    # A SOAP channel's service reads the operation element as its payload and the envelope's context as self.request.soap,
    # the same as it would had the request just arrived - the envelope was stored as it came, so it is parsed now.
    if channel_item['transport'] == URL_TYPE.SOAP:

        # A caller that declared no content type is parsed by the body alone, as it was when the request arrived
        content_type = request_ctx.get(_wsgi_content_type)
        if content_type is None:
            content_type = ''

        soap_action_header = request_ctx.get(_soap_action_header_key)

        soap_context = parse_soap_request(cid, raw_request, content_type, channel_item, soap_action_header)
        request_ctx['zato.request.soap'] = soap_context

        resolve_soap_payload(cid, soap_context, request_ctx)
        request_ctx['zato.request.payload'] = soap_context.payload

    # The channel's parameters are built the way the channel builds them for a request that has just arrived
    request_handler = server.config_manager.request_dispatcher.request_handler

    if channel_item['merge_url_params_req']:
        channel_params = request_handler.create_channel_params(
            request[Key_Path_Params], channel_item, request_ctx, raw_request, None)
    else:
        channel_params = {}

    _ = server.invoke(
        request[Key_Service],
        raw_request,
        channel=CHANNEL.HTTP_SOAP,
        data_format=request[Key_Data_Format],
        transport=request[Key_Transport],
        request_ctx=request_ctx,
        channel_params=channel_params,
        url_match=request[Key_Path_Params],
        channel_item=channel_item,
        cid=cid,
        zato_response_headers_container={},
    )

# ################################################################################################################################

def get_channel_retry_policy(channel_item:'any_') -> 'RetryPolicy':
    """ The retry policy of a REST or SOAP channel's queue - the channel item carries the same fields an outgoing
    connection's config does.
    """
    out = RetryPolicy.from_config(channel_item, _retry)
    return out

# ################################################################################################################################

def get_channel_dlq_settings(channel_item:'any_') -> 'stranydict':
    """ The DLQ settings of a REST or SOAP channel's queue, with defaults filled in.
    """
    out = _dlq_settings_from_config(channel_item)
    return out

# ################################################################################################################################

def get_http_channel_destination(channel_item:'any_', request:'stranydict') -> 'str':
    """ Where a channel's queued request goes - the method and the path it arrived at, and the service that runs it.
    """
    out = f'{request[Key_Method]} {request[Key_Path]} -> {request[Key_Service]}'
    return out

# ################################################################################################################################

def get_http_channel_details_facts(request:'stranydict') -> 'dictlist':
    """ The request facts the details window lists of a channel's queued request.
    """
    content_type = get_http_content_type(request)

    out = [
        {'label': _fact_method, 'value': request[Key_Method]},
        {'label': _fact_path, 'value': request[Key_Path]},
        {'label': _fact_path_params, 'value': request[Key_Path_Params]},
        {'label': _fact_query_string, 'value': request[Key_Params]},
        {'label': _fact_content_type, 'value': content_type},
        {'label': _fact_headers, 'value': request[Key_Headers]},
        {'label': _fact_data_format, 'value': request[Key_Data_Format]},
    ]

    return out

# ################################################################################################################################

# What the delivery page shows of a REST channel's queued requests
rest_channel_page = OutgoingPage()
rest_channel_page.destination = get_http_channel_destination
rest_channel_page.details_facts = get_http_channel_details_facts
rest_channel_page.body_mode = get_http_body_mode

# What the delivery page shows of a SOAP channel's queued requests - the body is the envelope as it arrived
soap_channel_page = OutgoingPage()
soap_channel_page.destination = get_http_channel_destination
soap_channel_page.details_facts = get_http_channel_details_facts
soap_channel_page.body_mode = get_soap_body_mode

# ################################################################################################################################
# ################################################################################################################################

