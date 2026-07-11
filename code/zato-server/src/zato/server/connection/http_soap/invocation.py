# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# gevent
from gevent import spawn

# lxml
from lxml import etree

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.soap.message import SOAPMessage, serialize
from zato.common.util.rest_invocation import evaluate_jsonata, evaluate_param_rows, evaluate_request_data, evaluate_xpath, \
    map_response, parse_param_rows
from zato.common.util.xml_.message import XMLMessage

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, dictnone, stranydict
    from zato.server.base.parallel import ParallelServer

    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

_invocation = HTTP_SOAP.Invocation
_callback_type = _invocation.CallbackType

# The result of merging explicit call arguments with a connection's declarative profile
merged_request = 'tuple[str, any_, dictnone, dictnone]'

# ################################################################################################################################
# ################################################################################################################################

def build_jsonata_context(data:'any_') -> 'any_':
    """ Returns the context that JSONata expressions are evaluated against - the request data
    the calling service passed in. Scheduled calls pass nothing so their context is empty.
    """

    # Only structural data can serve as a context - strings and models cannot
    if isinstance(data, (dict, list)):
        out = data
    else:
        out = {}

    return out

# ################################################################################################################################

def merge_declarative_request(
    config,  # type: stranydict
    method,  # type: str
    data,    # type: any_
    params,  # type: dictnone
    headers, # type: dictnone
    context, # type: any_
    ) -> 'merged_request':
    """ Fills in the blanks of an outgoing REST call from the connection's declarative invocation
    profile - explicit arguments always win, the declarative values only cover what the caller
    did not provide. JSONata-mode values are evaluated at call time against the given context,
    which also means a JSONata-mode body reshapes the data the caller passed in.
    """

    # An empty method resolves to the declarative one, which in turn defaults
    # to the connection's own method.
    if not method:
        method = config.get('request_method') or config.get('method') or ''

    # Query string and path parameter rows both merge into params - path placeholders
    # are picked out of the very same dict when the address is formatted ..
    declarative_params:'stranydict' = {}

    for field_name in (_invocation.Field_Request_Query_String, _invocation.Field_Request_Path_Params):
        if rows_json := config.get(field_name):
            rows = parse_param_rows(rows_json)
            declarative_params.update(evaluate_param_rows(rows, context))

    # .. an explicit parameter wins per key ..
    if declarative_params:
        if params is None:
            params = {}
        for key, value in declarative_params.items():
            if key not in params:
                params[key] = value

    # .. header rows merge the same way, an explicit header wins per key ..
    if rows_json := config.get(_invocation.Field_Request_Headers):
        rows = parse_param_rows(rows_json)
        declarative_headers = evaluate_param_rows(rows, context)

        if headers is None:
            headers = {}
        for key, value in declarative_headers.items():
            if key not in headers:
                headers[key] = value

    # .. the body - a JSONata-mode body is a transform of whatever the caller passed in,
    # so it runs on every call, while a text-mode body only fills in an empty one.
    if request_data := config.get(_invocation.Field_Request_Data):
        data_mode = config.get(_invocation.Field_Request_Data_Mode)
        if not data_mode:
            data_mode = _invocation.ValueMode.Text

        if data_mode == _invocation.ValueMode.JSONata:
            data = evaluate_request_data(request_data, data_mode, context)
        elif not data:
            data = request_data

    return method, data, params, headers

# ################################################################################################################################
# ################################################################################################################################

def soap_message_to_dict(message:'XMLMessage') -> 'stranydict':
    """ Converts a dot-accessed SOAP message to a plain dict so JSONata expressions
    and callback deliveries can consume it.
    """
    out:'stranydict' = {}

    for name, value in message._children.items():
        out[name] = _soap_value_to_plain(value)

    return out

# ################################################################################################################################

def _soap_value_to_plain(value:'any_') -> 'any_':
    """ Converts one message value to its plain form - a node with children becomes a dict,
    a leaf node becomes its text, a list converts item by item and scalars stay as they are.
    """
    if isinstance(value, XMLMessage):
        if value._children:
            out = soap_message_to_dict(value)
        else:
            out = value._text
    elif isinstance(value, list):
        out = [_soap_value_to_plain(item) for item in value]
    else:
        out = value

    return out

# ################################################################################################################################

def dict_to_soap_message(data:'stranydict') -> 'SOAPMessage':
    """ Builds a SOAPMessage out of a dict - keys may be dot paths (order.customer_id),
    values may be scalars, nested dicts or lists.
    """
    out = SOAPMessage()

    for key, value in data.items():
        _set_message_path(out, key, value)

    return out

# ################################################################################################################################

def _set_message_path(message:'SOAPMessage', path:'str', value:'any_') -> 'None':
    """ Sets one value on a message under a dot path, auto-vivifying the intermediate nodes.
    """
    node = message
    parts = path.split('.')

    # Reading each intermediate name auto-vivifies an empty node along the way
    for part in parts[:-1]:
        node = getattr(node, part)

    last = parts[-1]

    # A dict value builds a whole subtree under the last name ..
    if isinstance(value, dict):
        child = getattr(node, last)
        for child_key, child_value in value.items():
            _set_message_path(child, child_key, child_value)

    # .. a list of dicts becomes repeated message nodes, scalars in a list stay as they are ..
    elif isinstance(value, list):
        items = []
        for item in value:
            if isinstance(item, dict):
                items.append(dict_to_soap_message(item))
            else:
                items.append(item)
        setattr(node, last, items)

    # .. and a scalar is a plain leaf assignment.
    else:
        setattr(node, last, value)

# ################################################################################################################################

def build_soap_jsonata_context(message:'any_') -> 'any_':
    """ Returns the context that a SOAP connection's JSONata expressions are evaluated against -
    the message the calling service passed in. Scheduled calls pass nothing so their context is empty.
    """
    if isinstance(message, XMLMessage):
        out = soap_message_to_dict(message)
    elif isinstance(message, dict):
        out = message
    else:
        out = {}

    return out

# ################################################################################################################################

def merge_declarative_soap_request(
    config,    # type: stranydict
    operation, # type: str
    message,   # type: any_
    context,   # type: any_
    ) -> 'tuple[str, SOAPMessage]':
    """ Fills in the blanks of an outgoing SOAP call from the connection's declarative invocation
    profile - explicit arguments always win. A message the caller did not pass is built either
    by the message map, one JSONata expression producing the whole dict, or from the message rows,
    each setting one dot-path element.
    """

    # An empty operation resolves to the declarative one
    if not operation:
        operation = config.get(_invocation.Field_Request_Operation) or ''

    if message is None:

        # The message map builds the whole message in one expression ..
        if message_map := config.get(_invocation.Field_Request_Message_Map):
            result = evaluate_jsonata(message_map, context)
            message = dict_to_soap_message(result)

        # .. otherwise each message row sets one dot-path element ..
        elif rows_json := config.get(_invocation.Field_Request_Message):
            rows = parse_param_rows(rows_json)
            values = evaluate_param_rows(rows, context)
            message = dict_to_soap_message(values)

        # .. and with neither configured the operation goes out with an empty body.
        else:
            message = SOAPMessage()

    # A dict passed by the caller is accepted for convenience
    elif isinstance(message, dict):
        message = dict_to_soap_message(message)

    return operation, message

# ################################################################################################################################

def evaluate_soap_headers(config:'stranydict', context:'any_') -> 'dictnone':
    """ Returns the custom SOAP header elements to inject into the envelope - a dict of name
    to value with JSONata-mode values evaluated at call time, or None without any rows configured.
    """
    rows_json = config.get(_invocation.Field_Request_SOAP_Headers)

    if not rows_json:
        return None

    rows = parse_param_rows(rows_json)

    out = evaluate_param_rows(rows, context)
    return out

# ################################################################################################################################
# ################################################################################################################################

def deliver_to_callback(
    server,        # type: ParallelServer
    cid,           # type: str
    callback_type, # type: str
    callback_name, # type: str
    data,          # type: any_
    ) -> 'None':
    """ Delivers data to a callback - a service, a pub/sub topic or another outgoing REST connection.
    This runs in a spawned greenlet so any error is logged rather than propagated to the caller.
    """
    try:
        # The callback is a service invoked with the data on input ..
        if callback_type == _callback_type.Service:
            _ = server.invoke(callback_name, data)

        # .. or a pub/sub topic the data is published to ..
        elif callback_type == _callback_type.Topic:
            _ = server.pubsub_redis.publish(callback_name, data, cid=cid, correl_id=cid)

        # .. or another outgoing REST connection - its own declarative profile,
        # .. including its own potential callback, applies to this delivery too.
        else:
            wrapper = server.config_manager.config_store.out_plain_http[callback_name].conn
            _ = wrapper.post(cid, data)

    except Exception:
        logger.warning('Could not deliver callback `%s` (%s) -> cid=%s -> %s',
            callback_name, callback_type, cid, format_exc())

# ################################################################################################################################

def maybe_run_callback(
    server, # type: ParallelServer
    config, # type: stranydict
    cid,    # type: str
    data,   # type: any_
    ) -> 'None':
    """ Applies the connection's response map to the given data and delivers the result
    to the configured callback in a spawned greenlet, returning to the caller right away.
    A connection without a callback makes this a no-op.
    """
    callback_type = config.get(_invocation.Field_Callback_Type)
    callback_name = config.get(_invocation.Field_Callback_Name)

    # Nothing to do without a fully configured callback
    if not callback_type:
        return
    if not callback_name:
        return

    # Reshape the response first so the greenlet carries the already-mapped result ..
    if response_map := config.get(_invocation.Field_Response_Map):
        map_mode = config.get(_invocation.Field_Response_Map_Mode)
        if not map_mode:
            map_mode = _invocation.ResponseMapMode.JSONata
        data = map_response(data, response_map, map_mode)

    # .. and deliver it in the background.
    _ = spawn(deliver_to_callback, server, cid, callback_type, callback_name, data)

# ################################################################################################################################

def maybe_run_soap_callback(
    server,   # type: ParallelServer
    config,   # type: stranydict
    cid,      # type: str
    response, # type: any_
    ) -> 'None':
    """ The SOAP counterpart of maybe_run_callback - a JSONata map sees the response as a plain
    dict, an XPath map sees the re-serialized response XML, and without a map the callback
    receives the whole response as a dict. A connection without a callback makes this a no-op.
    """
    callback_type = config.get(_invocation.Field_Callback_Type)
    callback_name = config.get(_invocation.Field_Callback_Name)

    # Nothing to do without a fully configured callback
    if not callback_type:
        return
    if not callback_name:
        return

    if response_map := config.get(_invocation.Field_Response_Map):
        map_mode = config.get(_invocation.Field_Response_Map_Mode)
        if not map_mode:
            map_mode = _invocation.ResponseMapMode.JSONata

        # XPath runs against the response serialized back to XML ..
        if map_mode == _invocation.ResponseMapMode.XPath:
            element = serialize(response, 'response')
            data = evaluate_xpath(response_map, etree.tostring(element))

        # .. JSONata runs against its dict form.
        else:
            data = evaluate_jsonata(response_map, soap_message_to_dict(response))
    else:
        data = soap_message_to_dict(response)

    # Deliver the mapped result in the background
    _ = spawn(deliver_to_callback, server, cid, callback_type, callback_name, data)

# ################################################################################################################################

def maybe_run_fault_callback(
    server, # type: ParallelServer
    config, # type: stranydict
    cid,    # type: str
    fault,  # type: any_
    ) -> 'None':
    """ Delivers a SOAP fault to the configured callback with an is_fault flag - the response map
    does not apply since a fault is not a response. A connection without a callback makes this a no-op.
    """
    callback_type = config.get(_invocation.Field_Callback_Type)
    callback_name = config.get(_invocation.Field_Callback_Name)

    # Nothing to do without a fully configured callback
    if not callback_type:
        return
    if not callback_name:
        return

    # The fault travels as a plain dict so every callback type can consume it
    data = {
        'is_fault': True,
        'code': fault.code,
        'reason': fault.reason,
        'detail': soap_message_to_dict(fault.detail),
    }

    _ = spawn(deliver_to_callback, server, cid, callback_type, callback_name, data)

# ################################################################################################################################
# ################################################################################################################################
