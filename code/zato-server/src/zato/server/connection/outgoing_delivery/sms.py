# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The delivery handlers, the delivery pages and the invoke dialog of outgoing SMS connections and SMS channels.

# Zato
from zato.common.pubsub.outgoing import Body_Mode_JSON, Body_Mode_Text, Key_Headers, Key_Service, OutgoingInvoker, OutgoingPage
from zato.server.connection.sms.channel import Header_ID, Header_Kind, Header_Provider, Header_Status, invoke_sms_service
from zato.server.generic.api.outconn_sms import Key_Sender, Key_To

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anytuple, dictlist, stranydict
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

# The prefix of the Destination column
_destination_prefix = 'SMS'

# The request facts of the details window
_fact_to = 'To'
_fact_from = 'From'
_fact_service = 'Service'
_fact_provider = 'Provider'
_fact_kind = 'Kind'
_fact_id = 'Message ID'
_fact_status = 'Status'

# The value of a fact the message does not have
_not_set = '(none)'

# Where the invoke dialog of an outgoing SMS connection posts to
_invoke_url_prefix = '/zato/outgoing/sms/invoke/'

# The names of the invoke dialog's fields
Invoke_Field_From = 'from_'
Invoke_Field_To = 'to'

# ################################################################################################################################
# ################################################################################################################################

def locate_sms(server:'ParallelServer', conn_id:'int') -> 'anytuple':
    """ An outgoing SMS connection by its id, as its name and its wrapper.
    """
    for item in server.config_manager.outconn_sms.values():
        if item['id'] == conn_id:
            out = (item['name'], item.conn)
            return out

    return ()

# ################################################################################################################################

def deliver_to_sms(server:'ParallelServer', cid:'str', wrapper:'any_', request:'stranydict') -> 'None':
    """ Makes one attempt to hand a message over to an outgoing SMS connection.
    """
    _ = wrapper.send_from_queue(cid, request)

# ################################################################################################################################

def get_sms_destination(wrapper:'any_', request:'stranydict') -> 'str':
    """ Where a queued message goes - the recipient's number.
    """
    out = f'{_destination_prefix} {request[Key_To]}'
    return out

# ################################################################################################################################

def _value_or_none(value:'any_') -> 'str':
    if value is None or value == '':
        out = _not_set
    else:
        out = str(value)

    return out

# ################################################################################################################################

def get_sms_details_facts(request:'stranydict') -> 'dictlist':
    """ The request facts the details window lists of a queued SMS message.
    """
    out = [
        {'label': _fact_to, 'value': _value_or_none(request[Key_To])},
        {'label': _fact_from, 'value': _value_or_none(request[Key_Sender])},
    ]

    return out

# ################################################################################################################################

def get_sms_body_mode(request:'stranydict') -> 'str':
    """ The mode a queued SMS message's body is shown in - the text of the message.
    """
    return Body_Mode_Text

# ################################################################################################################################

def get_sms_invoker_options(request:'stranydict') -> 'stranydict':
    """ The invoke dialog's fields that are a queued message's own - its sender and its recipient.
    """
    out = {
        'fields': [
            {'name': Invoke_Field_From, 'label': _fact_from, 'value': request[Key_Sender]},
            {'name': Invoke_Field_To, 'label': _fact_to, 'value': request[Key_To]},
        ],
    }

    return out

# ################################################################################################################################

# The Dashboard's invoke dialog of outgoing SMS connections
sms_invoker = OutgoingInvoker()
sms_invoker.url_prefix = _invoke_url_prefix
sms_invoker.connection = 'outconn-sms'
sms_invoker.history_key_prefix = 'zato.invoke-history.outconn-sms.'
sms_invoker.options = get_sms_invoker_options

# The delivery page of an outgoing SMS connection
sms_page = OutgoingPage()
sms_page.destination = get_sms_destination
sms_page.details_facts = get_sms_details_facts
sms_page.body_mode = get_sms_body_mode
sms_page.invoker = sms_invoker

# ################################################################################################################################
# ################################################################################################################################

def locate_sms_channel(server:'ParallelServer', conn_id:'int') -> 'anytuple':
    """ An SMS channel by its id, as its name and its wrapper.
    """
    for item in server.config_manager.channel_sms.values():
        if item['id'] == conn_id:
            out = (item['name'], item.conn)
            return out

    return ()

# ################################################################################################################################

def deliver_to_sms_channel(server:'ParallelServer', cid:'str', wrapper:'any_', request:'stranydict') -> 'None':
    """ Makes one attempt to invoke the service a channel's event goes to.
    """
    _ = invoke_sms_service(server, cid, request)

# ################################################################################################################################

def get_sms_channel_destination(wrapper:'any_', request:'stranydict') -> 'str':
    """ Where a channel's event goes - its service.
    """
    out = request[Key_Service]
    return out

# ################################################################################################################################

def get_sms_channel_details_facts(request:'stranydict') -> 'dictlist':
    """ The request facts the details window lists of a channel's event.
    """
    headers = request[Key_Headers]

    out = [
        {'label': _fact_service, 'value': request[Key_Service]},
        {'label': _fact_provider, 'value': headers[Header_Provider]},
        {'label': _fact_kind, 'value': headers[Header_Kind]},
        {'label': _fact_id, 'value': headers[Header_ID]},
        {'label': _fact_status, 'value': _value_or_none(headers[Header_Status])},
    ]

    return out

# ################################################################################################################################

def get_sms_channel_body_mode(request:'stranydict') -> 'str':
    """ The mode a channel's event is shown in - the event is always JSON.
    """
    return Body_Mode_JSON

# ################################################################################################################################

# The delivery page of an SMS channel
sms_channel_page = OutgoingPage()
sms_channel_page.destination = get_sms_channel_destination
sms_channel_page.details_facts = get_sms_channel_details_facts
sms_channel_page.body_mode = get_sms_channel_body_mode

# ################################################################################################################################
# ################################################################################################################################
