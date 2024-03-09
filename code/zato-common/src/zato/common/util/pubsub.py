# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from operator import itemgetter

# Zato
from zato.common.api import PUBSUB
from zato.common.exception import BadRequest
from zato.common.odb.query import pubsub_endpoint_queue_list_by_sub_keys
from zato.common.pubsub import MSG_PREFIX as PUBSUB_MSG_PREFIX
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anydict, anylist, dictlist, dictorlist, intnone, stranydict, strlist
    from zato.server.base.parallel import ParallelServer
    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

_PRIORITY = PUBSUB.PRIORITY

_pri_min = _PRIORITY.MIN
_pri_max = _PRIORITY.MAX
_pri_def = _PRIORITY.DEFAULT

_default_expiration = PUBSUB.DEFAULT.EXPIRATION

# ################################################################################################################################
# ################################################################################################################################

def make_short_msg_copy_from_dict(msg:'stranydict', data_prefix_len:'int', data_prefix_short_len:'int') -> 'stranydict':
    out_msg = {} # type: stranydict
    out_msg['msg_id'] = msg['pub_msg_id']
    out_msg['in_reply_to'] = msg.get('in_reply_to')
    out_msg['data'] = msg['data'][:data_prefix_len]
    out_msg['data_prefix_short'] = out_msg['data'][:data_prefix_short_len]
    out_msg['size'] = msg['size']
    out_msg['pub_pattern_matched'] = msg['pub_pattern_matched']
    out_msg['sub_pattern_matched'] = msg['sub_pattern_matched']
    out_msg['pub_time'] = msg['pub_time']
    out_msg['expiration'] = msg['expiration']
    out_msg['expiration_time'] = msg['expiration_time']
    out_msg['topic_id'] = msg['topic_id']
    out_msg['topic_name'] = msg['topic_name']
    out_msg['cluster_id'] = msg['cluster_id']
    out_msg['published_by_id'] = msg['published_by_id']
    out_msg['delivery_status'] = msg['delivery_status']
    out_msg['server_name'] = msg['server_name']
    out_msg['server_pid'] = msg['server_pid']
    out_msg['has_gd'] = msg['has_gd']
    out_msg['recv_time'] = msg['recv_time']
    out_msg['sub_key'] = msg['sub_key']
    return out_msg

# ################################################################################################################################

def make_short_msg_copy_from_msg(msg:'any_', data_prefix_len:'int', data_prefix_short_len:'int') -> 'stranydict':
    out_msg = {} # type: stranydict
    out_msg['msg_id'] = msg.pub_msg_id
    out_msg['in_reply_to'] = msg.in_reply_to
    out_msg['data'] = msg.data[:data_prefix_len]
    out_msg['data_prefix_short'] = out_msg['data'][:data_prefix_short_len]
    out_msg['size'] = msg.size
    out_msg['pub_pattern_matched'] = msg.pub_pattern_matched
    out_msg['sub_pattern_matched'] = msg.sub_pattern_matched
    out_msg['pub_time'] = msg.pub_time
    out_msg['expiration'] = msg.expiration
    out_msg['expiration_time'] = msg.expiration_time
    out_msg['topic_id'] = msg.topic_id
    out_msg['topic_name'] = msg.topic_name
    out_msg['cluster_id'] = msg.cluster_id
    out_msg['published_by_id'] = msg.published_by_id
    out_msg['delivery_status'] = msg.delivery_status
    out_msg['server_name'] = msg.server_name
    out_msg['server_pid'] = msg.server_pid
    out_msg['has_gd'] = msg.has_gd
    out_msg['recv_time'] = msg.recv_time
    out_msg['sub_key'] = msg.sub_key
    return out_msg

# ################################################################################################################################

def get_last_topics(topic_list:'dictlist', as_list:'bool'=True) -> 'dictorlist':

    # Response to produce if as_list is not True.
    out = {} # type: anydict

    for item in topic_list:

        for _ignored_topic_key, topic_data in item.items():

            # Local alias
            topic_id = topic_data['topic_id'] # type: int

            # .. we may have visited this topic already ..
            previous = out.get(topic_id, {}) # type: anydict

            # .. if we have ..
            if previous:
                if topic_data['pub_time'] > previous['pub_time']:
                    out[topic_id] = topic_data

            # .. otherwise, we can just set the current one ..
            else:
                out[topic_id] = topic_data

    if as_list:
        out = sorted(out.values(), key=itemgetter('pub_time'), reverse=True) # type: ignore
        return out
    else:
        return out

# ################################################################################################################################

def get_last_pub_metadata(server:'ParallelServer', topic_id_list:'anylist | int') -> 'anydict':

    # Make sure we have a list on input
    if isinstance(topic_id_list, list):
        input_topic_id = None
        is_single_topic = False
    else:
        input_topic_id = int(topic_id_list)
        is_single_topic = True
        topic_id_list = [topic_id_list]

    # Always use integers for topic IDs
    topic_id_list = [int(elem) for elem in topic_id_list]

    # Look up topic metadata in all the servers ..
    response = server.rpc.invoke_all(
        'zato.pubsub.topic.get-topic-metadata', {'topic_id_list':topic_id_list}, skip_response_elem=False)

    # Produce our response
    out = get_last_topics(response.data, as_list=False) # type: any_

    if is_single_topic:
        return out.get(input_topic_id) or {}
    else:
        return out

# ################################################################################################################################

def get_endpoint_metadata(server:'ParallelServer', endpoint_id:'int') -> 'dictorlist':

    # All topics from all PIDs
    topic_list = [] # type: dictlist

    # Information about a single topic
    topic_dict = {}

    response = server.rpc.invoke_all('zato.pubsub.endpoint.get-endpoint-metadata', {'endpoint_id':endpoint_id})

    for pid_response in response.data:
        for pid_topic_list in pid_response.values():
            for topic_data in pid_topic_list:
                topic_id = topic_data['topic_id']
                topic_dict[topic_id] = topic_data
                topic_list.append(topic_dict)

    return get_last_topics(topic_list, as_list=True)

# ################################################################################################################################

def get_topic_sub_keys_from_sub_keys(session:'SASession', cluster_id:'int', sub_key_list:'strlist') -> 'stranydict':

    topic_sub_keys = {} # type: stranydict

    for item in pubsub_endpoint_queue_list_by_sub_keys(session, cluster_id, sub_key_list):
        topic_name = cast_('str', item.topic_name)
        sub_keys = topic_sub_keys.setdefault(topic_name, []) # type: strlist
        sub_keys.append(item.sub_key)

    return topic_sub_keys

# ################################################################################################################################

def get_priority(
    cid,   # type: str
    priority, # type: intnone
    _pri_min=_pri_min, # type: int
    _pri_max=_pri_max, # type: int
    _pri_def=_pri_def  # type: int
) -> 'int':
    """ Get and validate message priority.
    """
    if priority:
        if priority < _pri_min or priority > _pri_max:
            raise BadRequest(cid, 'Priority `{}` outside of allowed range {}-{}'.format(priority, _pri_min, _pri_max))
    else:
        priority = _pri_def

    return priority

# ################################################################################################################################

def get_expiration(
    cid:'str',
    expiration:'intnone',
    topic_limit_message_expiry:'int',
    default_expiration:'int'=_default_expiration
) -> 'int':
    """ Get and validate message expiration.
    """
    expiration = expiration or 0
    if expiration is not None and expiration < 0:
        raise BadRequest(cid, 'Expiration `{}` must not be negative'.format(expiration))

    # If there is no expiration set, try the default one ..
    expiration = expiration or default_expiration

    # .. however, we can never exceed the limit set by the topic object,
    # .. so we need to take that into account as well.
    expiration = min(expiration, topic_limit_message_expiry)

    # We can return the final value now
    return expiration

# ################################################################################################################################

def is_service_subscription(config:'any_') -> 'bool':
    return config.sub_key.startswith(PUBSUB_MSG_PREFIX.SERVICE_SK)

# ################################################################################################################################
