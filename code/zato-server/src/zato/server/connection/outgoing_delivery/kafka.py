# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The delivery handlers and the delivery pages of outgoing Kafka connections and Kafka channels.

# Zato
from zato.common.api import KAFKA
from zato.common.pubsub.outgoing import detect_body_mode, Key_Data, Key_Headers, Key_Is_Base64, Key_Key, Key_Partition, \
    Key_Service, OutgoingPage
from zato.server.queue_bridge.recv import invoke_channel_request

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anytuple, dictlist, stranydict
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

_header = KAFKA.Header

# The prefix of the Destination column
_destination_prefix = 'Kafka'

# The request facts of the details window
_fact_key       = 'Key'
_fact_partition = 'Partition'
_fact_headers   = 'Headers'
_fact_service   = 'Service'
_fact_topic     = 'Topic'
_fact_offset    = 'Offset'
_fact_encoding  = 'Encoding'

# The encoding of a payload that is not text
_encoding_base64 = 'base64'

# The value of a fact the message does not have
_not_set = '(none)'

# ################################################################################################################################
# ################################################################################################################################

def locate_kafka(server:'ParallelServer', conn_id:'int') -> 'anytuple':
    """ An outgoing Kafka connection by its id, as its name and its wrapper.
    """
    for item in server.config_manager.outconn_kafka.values():
        if item['id'] == conn_id:
            out = (item['name'], item.conn)
            return out

    return ()

# ################################################################################################################################

def deliver_to_kafka(server:'ParallelServer', cid:'str', wrapper:'any_', request:'stranydict') -> 'None':
    """ Makes one attempt to hand a message over to an outgoing Kafka connection.
    """
    _ = wrapper.send_from_queue(cid, request)

# ################################################################################################################################

def get_kafka_destination(wrapper:'any_', request:'stranydict') -> 'str':
    """ Where a queued message goes - the connection's topic.
    """
    out = f'{_destination_prefix} {wrapper.config.topic}'
    return out

# ################################################################################################################################

def _value_or_none(value:'any_') -> 'str':
    if value is None or value == '':
        out = _not_set
    else:
        out = str(value)

    return out

# ################################################################################################################################

def get_kafka_details_facts(request:'stranydict') -> 'dictlist':
    """ The request facts the details window lists of a queued Kafka message.
    """
    out = [
        {'label': _fact_key, 'value': _value_or_none(request[Key_Key])},
        {'label': _fact_partition, 'value': _value_or_none(request[Key_Partition])},
        {'label': _fact_headers, 'value': request[Key_Headers]},
    ]

    return out

# ################################################################################################################################

def get_kafka_body_mode(request:'stranydict') -> 'str':
    """ The mode a queued Kafka message's body is shown in.
    """
    out = detect_body_mode(request[Key_Data])
    return out

# ################################################################################################################################

# The delivery page of an outgoing Kafka connection
kafka_page = OutgoingPage()
kafka_page.destination = get_kafka_destination
kafka_page.details_facts = get_kafka_details_facts
kafka_page.body_mode = get_kafka_body_mode

# ################################################################################################################################
# ################################################################################################################################

def locate_kafka_channel(server:'ParallelServer', conn_id:'int') -> 'anytuple':
    """ A Kafka channel by its id, as its name and its wrapper.
    """
    for item in server.config_manager.channel_kafka.values():
        if item['id'] == conn_id:
            out = (item['name'], item.conn)
            return out

    return ()

# ################################################################################################################################

def deliver_to_kafka_channel(server:'ParallelServer', cid:'str', wrapper:'any_', request:'stranydict') -> 'None':
    """ Makes one attempt to invoke the service a channel's message was routed to.
    """
    _ = invoke_channel_request(server, cid, request)

# ################################################################################################################################

def get_kafka_channel_destination(wrapper:'any_', request:'stranydict') -> 'str':
    """ Where a channel's message goes - the service it was routed to.
    """
    out = request[Key_Service]
    return out

# ################################################################################################################################

def get_kafka_channel_details_facts(request:'stranydict') -> 'dictlist':
    """ The request facts the details window lists of a channel's message.
    """
    headers = request[Key_Headers]

    # A message without a key has no such header.
    if _header.Key in headers:
        key = headers[_header.Key]
    else:
        key = _not_set

    out = [
        {'label': _fact_service, 'value': request[Key_Service]},
        {'label': _fact_topic, 'value': headers[_header.Topic]},
        {'label': _fact_partition, 'value': headers[_header.Partition]},
        {'label': _fact_offset, 'value': headers[_header.Offset]},
        {'label': _fact_key, 'value': key},
        {'label': _fact_headers, 'value': headers},
    ]

    if request[Key_Is_Base64]:
        out.append({'label': _fact_encoding, 'value': _encoding_base64})

    return out

# ################################################################################################################################

# The delivery page of a Kafka channel
kafka_channel_page = OutgoingPage()
kafka_channel_page.destination = get_kafka_channel_destination
kafka_channel_page.details_facts = get_kafka_channel_details_facts
kafka_channel_page.body_mode = get_kafka_body_mode

# ################################################################################################################################
# ################################################################################################################################
