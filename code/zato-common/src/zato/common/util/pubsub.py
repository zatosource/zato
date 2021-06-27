# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from operator import itemgetter

# Zato
from zato.common.odb.query import pubsub_endpoint_queue_list_by_sub_keys

# ################################################################################################################################

if 0:
    from typing import Union as union
    from zato.server.base.parallel import ParallelServer

    ParallelServer = ParallelServer
    union = union

# ################################################################################################################################

def make_short_msg_copy_from_dict(msg, data_prefix_len, data_prefix_short_len):
    out_msg = {}
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

def make_short_msg_copy_from_msg(msg, data_prefix_len, data_prefix_short_len):
    out_msg = {}
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

def get_last_topics(topic_list, as_list=True):
    # type: (list, bool) -> union[dict, list]

    # Response to produce
    out = {}

    for item in topic_list: # type: (dict)

        # Local alias
        topic_id = item['topic_id'] # type: int

        # .. we may have visited this topic already ..
        previous = out.get(topic_id, {}) # type: dict

        # .. if we have ..
        if previous:
            if item['pub_time'] > previous['pub_time']:
                out[topic_id] = item

        # .. otherwise, we can just set the current one ..
        else:
            out[topic_id] = item

    if as_list:
        out = sorted(out.values(), key=itemgetter('pub_time'), reverse=True)
        return out
    else:
        return out

# ################################################################################################################################

def get_last_pub_metadata(server, topic_id_list):
    # type: (ParallelServer, list) -> dict

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
    response = server.rpc.invoke_all('zato.pubsub.topic.get-topic-metadata', {'topic_id_list':topic_id_list})

    # Produce our response
    out = get_last_topics(response.data, as_list=False)

    if is_single_topic:
        return out.get(input_topic_id) or {}
    else:
        return out

# ################################################################################################################################

def get_endpoint_metadata(server, endpoint_id):
    # type: (ParallelServer, int) -> dict

    # All topics from all PIDs
    topic_list = []

    response = server.rpc.invoke_all('zato.pubsub.endpoint.get-endpoint-metadata', {'endpoint_id':endpoint_id})

    for pid_response in response.data: # type: dict
        for pid_topic_list in pid_response.values(): # type: list
            for topic_data in pid_topic_list: # type: dict
                topic_list.append(topic_data)

    return get_last_topics(topic_list, as_list=True)

# ################################################################################################################################

def get_topic_sub_keys_from_sub_keys(session, cluster_id, sub_key_list):
    topic_sub_keys = {}

    for item in pubsub_endpoint_queue_list_by_sub_keys(session, cluster_id, sub_key_list):
        sub_keys = topic_sub_keys.setdefault(item.topic_name, [])
        sub_keys.append(item.sub_key)

    return topic_sub_keys

# ################################################################################################################################
