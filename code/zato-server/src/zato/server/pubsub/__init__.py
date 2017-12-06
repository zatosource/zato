# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from contextlib import closing
from traceback import format_exc

# gevent
from gevent import sleep
from gevent.lock import RLock

# globre
from globre import compile as globre_compile

# Zato
from zato.common import DATA_FORMAT, PUBSUB
from zato.common.broker_message import PUBSUB as BROKER_MSG_PUBSUB
from zato.common.exception import BadRequest
from zato.common.odb.model import WebSocketClientPubSubKeys
from zato.common.odb.query_ps_delivery import confirm_pubsub_msg_delivered as _confirm_pubsub_msg_delivered, \
     get_sql_messages_by_sub_key as _get_sql_messages_by_sub_key
from zato.common.time_util import utcnow_as_ms
from zato.common.util import spawn_greenlet

# ################################################################################################################################

logger = logging.getLogger('zato_pubsub')
logger_zato = logging.getLogger('zato')
logger_overflow = logging.getLogger('zato_pubsub_overflow')

# ################################################################################################################################

_PRIORITY=PUBSUB.PRIORITY
_JSON=DATA_FORMAT.JSON

# ################################################################################################################################

def get_priority(cid, input, _pri_min=_PRIORITY.MIN, _pri_max=_PRIORITY.MAX, _pri_def=_PRIORITY.DEFAULT):
    """ Get and validate message priority.
    """
    priority = input.get('priority')
    if priority:
        if priority < _pri_min or priority > _pri_max:
            raise BadRequest(cid, 'Priority `{}` outside of allowed range {}-{}'.format(priority, _pri_min, _pri_max))
    else:
        priority = _pri_def

    return priority

# ################################################################################################################################

def get_expiration(cid, input, default_expiration=2147483647):
    """ Get and validate message expiration. Returns 2 ** 31 - 1 (around 68 years) if not expiration is set explicitly.
    """
    expiration = input.get('expiration')
    if expiration is not None and expiration < 0:
        raise BadRequest(cid, 'Expiration `{}` must not be negative'.format(expiration))

    return expiration or default_expiration

# ################################################################################################################################

class Endpoint(object):
    """ A publisher/subscriber in pub/sub workflows.
    """
    def __init__(self, config):
        self.config = config
        self.id = config.id
        self.name = config.name
        self.role = config.role
        self.is_active = config.is_active
        self.is_internal = config.is_internal

        self.topic_patterns = config.topic_patterns or ''

        self.pub_topic_patterns = []
        self.sub_topic_patterns = []

        self.pub_topics = {}
        self.sub_topics = {}

        self.set_up_patterns()

# ################################################################################################################################

    def set_up_patterns(self):
        data = {
            'topic': self.topic_patterns,
        }

        # is_pub, is_topic -> target set
        targets = {
            (True, True): self.pub_topic_patterns,
            (False, True): self.sub_topic_patterns,
        }

        for key, config in data.iteritems():
            is_topic = key == 'topic'

            for line in config.splitlines():
                line = line.strip()
                if line.startswith('pub=') or line.startswith('sub='):
                    is_pub = line.startswith('pub=')

                    matcher = line[line.find('=')+1:]
                    matcher = globre_compile(matcher)

                    source = (is_pub, is_topic)
                    target = targets[source]
                    target.append([line, matcher])

                else:
                    logger.warn('Ignoring invalid {} pattern `{}` for `{}` (role:{}) (reason: no pub=/sub= prefix found)'.format(
                        key, line, self.name, self.role))

# ################################################################################################################################

class Topic(object):
    """ An individiual topic ib in pub/sub workflows.
    """
    def __init__(self, config):
        self.config = config
        self.id = config.id
        self.name = config.name
        self.is_active = config.is_active
        self.is_internal = config.is_internal
        self.max_depth_gd = config.max_depth_gd
        self.max_depth_non_gd = config.max_depth_non_gd
        self.has_gd = config.has_gd
        self.gd_depth_check_freq = config.gd_depth_check_freq
        self.gd_depth_check_iter = 0
        self.hook_service_invoker = config.hook_service_invoker

    def incr_gd_depth_check(self):
        """ Increases counter indicating whether topic's depth should be checked for max_depth reached.
        """
        self.gd_depth_check_iter += 1

    def needs_gd_depth_check(self):
        return self.gd_depth_check_iter % self.gd_depth_check_freq == 0

# ################################################################################################################################

class Subscription(object):
    def __init__(self, config):
        self.config = config
        self.id = config.id
        self.sub_key = config.sub_key
        self.endpoint_id = config.endpoint_id
        self.topic_name = config.topic_name

# ################################################################################################################################

class HookCtx(object):
    def __init__(self, hook_type, msg, topic):
        self.hook_type = hook_type
        self.msg = msg
        self.topic = topic

# ################################################################################################################################

class SubKeyServer(object):
    """ Holds information about which server has subscribers to an individual sub_key.
    """
    def __init__(self, config):
        self.sub_key = config['sub_key']
        self.cluster_id = config['cluster_id']
        self.server_name = config['server_name']
        self.server_pid = config['server_pid']
        self.endpoint_type = config['endpoint_type']

        # Attributes below are only for WebSockets
        self.channel_name = config.get('channel_name')
        self.pub_client_id = config.get('pub_client_id')

# ################################################################################################################################

class InRAMBacklog(object):
    """ A backlog of messages kept in RAM. Stores a list of sub_keys and all messages that a sub_key points to.
    It acts as a multi-key dict and keeps only a single copy of message for each sub_key.
    """
    def __init__(self):
        self.lock = RLock()
        self.topic_sub_key_to_msg_id = {} # Topic ID -> Sub key -> Msg ID
        self.topic_msg_id_to_msg = {}     # Topic ID -> Msg ID  -> Message data
        self.msg_id_to_expiration = {}    # Msg ID   -> (Topic ID, sub_keys, expiration time in milliseconds)

        # Start in background a cleanup task that removes all expired messages
        spawn_greenlet(self.run_cleanup_task)

# ################################################################################################################################

    def _get_delete_messages_by_sub_keys(self, topic_id, sub_keys, needs_out, delete_sub=False):
        """ Deletes from RAM all messages matching input sub_keys and, optionally, returns them.
        If delete_sub is True, deletes subscription by sub_key from that topic altogether.
        """
        # Optional output
        if needs_out:
            out = {}

        # We always delete messages found, no matter if they are to be returned or not
        to_delete = []

        with self.lock:

            # First, collect data for all sub_keys ..

            for sub_key in sub_keys:
                msg_ids = self.topic_sub_key_to_msg_id.get(topic_id, {}).get(sub_key, [])
                for msg_id in msg_ids:

                    if needs_out:
                        out_sub_key = out.setdefault(sub_key, {})
                        out_sub_key[msg_id] = self.topic_msg_id_to_msg[topic_id][msg_id]

                    # Make note of what needs to be deleted
                    to_delete.append((topic_id, sub_key, msg_id))

            # Now delete all messages, and possibly subscriptions, found above
            for topic_id, sub_key, msg_id in to_delete:

                # We can access and delete them safely because we run under self.lock
                # and we have just collected them above so they must exist
                self.topic_sub_key_to_msg_id[topic_id][sub_key].remove(msg_id)

                # Delete sub_keys if delete_sub is explicitly set (because we are unsubscring),
                # or if there are no messages left for that topic
                if delete_sub or (not self.topic_sub_key_to_msg_id[topic_id][sub_key]):
                    del self.topic_sub_key_to_msg_id[topic_id][sub_key]

                # Also, check if there are any other subscribers for Msg IDs that we are returning.
                # If there are none, delete the message from in-RAM topic dictionaries.
                for topic_sub_key in self.topic_sub_key_to_msg_id[topic_id]:
                    if msg_id in self.topic_sub_key_to_msg_id[topic_id][topic_sub_key]:

                        # Ok, there is at least one reference to that Msg ID
                        break

                # No break caught above = this Msg ID is not needed by any subscriber,
                # again, we are doing it under self.lock so del is fine.
                else:
                    del self.topic_msg_id_to_msg[topic_id][msg_id]
                    del self.msg_id_to_expiration[msg_id]

        if needs_out:
            return out

# ################################################################################################################################

    def retrieve_messages_by_sub_keys(self, topic_id, sub_keys):
        return self._get_delete_messages_by_sub_keys(topic_id, sub_keys, True)

# ################################################################################################################################

    def unsubscribe(self, topic_id, sub_keys):
        self._get_delete_messages_by_sub_keys(topic_id, sub_keys, False, True)

# ################################################################################################################################

    def run_cleanup_task(self, _utcnow=utcnow_as_ms, _sleep=sleep):
        """ A background task waking up periodically to remove all expired and retrieved messages from backlog.
        """
        while True:
            try:
                with self.lock:

                    # We keep them separate so as not to modify any dictionaries during iteration.
                    to_process = []

                    # Calling it once will suffice.
                    now = _utcnow()

                    # Check expiration for all messages currently held.
                    for msg_id, (topic_id, sub_keys, expiration) in self.msg_id_to_expiration.items():
                        if expiration <= now:
                            to_process.append((topic_id, sub_keys, msg_id))

                    # If we found anything, remove them from per-topic backlogs and from the dict of expiration times.
                    for topic_id, sub_keys, msg_id in to_process:

                        # These are direct mappings.
                        self.msg_id_to_expiration.pop(msg_id)
                        self.topic_msg_id_to_msg.get(topic_id, {}).pop(msg_id)

                        # But here, we need to remove msg_id for each sub_key found in sub_keys.
                        sub_keys_for_topic_id = self.topic_sub_key_to_msg_id.get(topic_id, {})
                        if sub_keys_for_topic_id:
                            for sub_key in sub_keys:
                                msg_ids_for_sub_key = sub_keys_for_topic_id.get(sub_key, {})
                                msg_ids_for_sub_key.pop(msg_id)

                                # Delete sub_key from its parent topic if that was the last message for this sub_key
                                # so as not to keep references to unneeded sub_keys without a reason.
                                if not msg_ids_for_sub_key:
                                    del sub_keys_for_topic_id[sub_key]

                    # Log what was done
                    number = len(to_process)
                    suffix = 's' if(number==0 or number > 1) else ''
                    logger.info('In-RAM. Deleted %s pub/sub message%s' % (number, suffix))

                # Sleep for a moment before looping again, but do it outside the main loop
                # so that other parts of code can acquire the lock for their purposes.
                _sleep(5)

            except Exception, e:
                logger_zato.warn('Could not remove messages from in-RAM backlog, e:`%s`', format_exc(e))
                _sleep(5)

# ################################################################################################################################

    def log_messages_to_store(self, cid, topic_name, max_depth, sub_key, messages):

        # Used by both loggers
        msg = 'Reached max in-RAM depth of %r for topic `%r` (cid:%r). Extra messages will be stored in logs.'
        args = (max_depth, topic_name, cid)

        # Log in pub/sub log and the main one as well, just to make sure it will be easily found
        logger.warn(msg, *args)
        logger_zato.warn(msg, *args)

        # Store messages in logger - by default will go to disk
        logger_overflow.info('CID:%s, topic:`%s`, sub_key:%s, messages:%s', cid, topic_name, sub_key, messages)

# ################################################################################################################################

    def add_messages(self, cid, topic_id, topic_name, max_depth, sub_keys, messages):
        with self.lock:

            # We need to keep data for each topic separately because they have their separate max depth values.
            topic_sub_key_dict = self.topic_sub_key_to_msg_id.setdefault(topic_id, {})
            topic_msg_dict = self.topic_msg_id_to_msg.setdefault(topic_id, {})

            # First, build a list of sub_keys in that topic that have not yet reached max_depth,
            # and for those that have, log messages through logger.
            may_continue = []

            for sub_key in sub_keys:
                sub_key_messages = topic_sub_key_dict.setdefault(sub_key, [])

                if len(sub_key_messages) + len(messages) > max_depth:
                    self.log_messages_to_store(cid, topic_name, max_depth, sub_key, messages)
                else:
                    may_continue.append(sub_key)

            # Continue only if there is at least one sub_key that has not reached max_depth yet
            if may_continue:

                # Messages is a list and we now turn it into a dictionary keyed by msg ID.
                msg_dict = {}

                for item in messages:
                    msg_id = item['pub_msg_id']
                    msg_dict[msg_id] = item

                    # For each message, make its expiration known to background cleanup task
                    self.msg_id_to_expiration[msg_id] = (topic_id, may_continue, item['expiration_time'])

                # Get this list once and refer to it multiple times below
                msg_ids = msg_dict.keys()

                # Add new messages to RAM
                topic_msg_dict.update(msg_dict)

                # Add references to the new messages for each sub_key
                for sub_key in may_continue:
                    sub_key_messages = topic_sub_key_dict.setdefault(sub_key, [])
                    sub_key_messages.extend(msg_ids)

# ################################################################################################################################

class PubSub(object):
    def __init__(self, cluster_id, server, broker_client=None):
        self.cluster_id = cluster_id
        self.server = server
        self.broker_client = broker_client
        self.lock = RLock()

        self.subscriptions_by_topic = {}       # Topic name     -> Subscription object
        self.subscriptions_by_sub_key = {}     # Sub key        -> Subscription object
        self.sub_key_servers = {}              # Sub key        -> Server/PID handling it

        self.endpoints = {}                    # Endpoint ID    -> Endpoint object
        self.topics = {}                       # Topic ID       -> Topic object

        self.sec_id_to_endpoint_id = {}        # Sec def ID     -> Endpoint ID
        self.ws_channel_id_to_endpoint_id = {} # WS chan def ID -> Endpoint ID
        self.service_id_to_endpoint_id = {}    # Service ID     -> Endpoint ID
        self.topic_name_to_id = {}             # Topic name     -> Topic ID

        self.pubsub_tool_by_sub_key = {}       # Sub key        -> PubSubTool object
        self.pubsub_tools = []                 # A list of PubSubTool objects, each containing delivery tasks

        self.in_ram_backlog = InRAMBacklog()

        # Getter methods for each endpoint type that return actual endpoints,
        # e.g. REST outgoing connections. Values are set by worker store.
        self.endpoint_getter = dict.fromkeys(PUBSUB.ENDPOINT_TYPE)

# ################################################################################################################################

    def get_subscriptions_by_topic(self, topic_name):
        with self.lock:
            return self.subscriptions_by_topic.get(topic_name, [])

# ################################################################################################################################

    def get_subscriptions_by_sub_key(self, sub_key):
        with self.lock:
            return self.subscriptions_by_sub_key.get(sub_key, [])

# ################################################################################################################################

    def has_sub_key(self, sub_key):
        with self.lock:
            return sub_key in self.subscriptions_by_sub_key

# ################################################################################################################################

    def get_endpoint_id_by_sec_id(self, sec_id):
        with self.lock:
            return self.sec_id_to_endpoint_id[sec_id]

# ################################################################################################################################

    def get_endpoint_id_by_ws_channel_id(self, ws_channel_id):
        with self.lock:
            return self.ws_channel_id_to_endpoint_id[ws_channel_id]

# ################################################################################################################################

    def get_endpoint_id_by_service_id(self, service_id):
        with self.lock:
            return self.service_id_to_endpoint_id[service_id]

# ################################################################################################################################

    def _get_topic_id_by_name(self, topic_name):
        return self.topic_name_to_id[topic_name]

# ################################################################################################################################

    def get_topic_id_by_name(self, topic_name):
        with self.lock:
            return self._get_topic_id_by_name(topic_name)

# ################################################################################################################################

    def get_topic_by_name(self, topic_name):
        with self.lock:
            return self.topics[self._get_topic_id_by_name(topic_name)]

# ################################################################################################################################

    def _create_endpoint(self, config):
        self.endpoints[config.id] = Endpoint(config)

        if config['security_id']:
            self.sec_id_to_endpoint_id[config['security_id']] = config.id

        if config['ws_channel_id']:
            self.ws_channel_id_to_endpoint_id[config['ws_channel_id']] = config.id

        if config['service_id']:
            self.service_id_to_endpoint_id[config['service_id']] = config.id

# ################################################################################################################################

    def create_endpoint(self, config):
        with self.lock:
            self._create_endpoint(config)

# ################################################################################################################################

    def _delete_endpoint(self, endpoint_id):
        del self.endpoints[endpoint_id]

        sec_id = None
        ws_chan_id = None
        service_id = None

        for key, value in self.sec_id_to_endpoint_id.iteritems():
            if value == endpoint_id:
                sec_id = key
                break

        for key, value in self.ws_channel_id_to_endpoint_id.iteritems():
            if value == endpoint_id:
                ws_chan_id = key
                break

        for key, value in self.service_id_to_endpoint_id.iteritems():
            if value == endpoint_id:
                service_id = key
                break

        if sec_id:
            del self.sec_id_to_endpoint_id[sec_id]

        if ws_chan_id:
            del self.ws_channel_id_to_endpoint_id[ws_chan_id]

        if service_id:
            del self.service_id_to_endpoint_id[service_id]

# ################################################################################################################################

    def delete_endpoint(self, endpoint_id):
        with self.lock:
            self._delete_endpoint(endpoint_id)

# ################################################################################################################################

    def edit_endpoint(self, config):
        with self.lock:
            self._delete_endpoint(config.id)
            self._create_endpoint(config)

# ################################################################################################################################

    def create_subscription(self, config):
        with self.lock:
            sub = Subscription(config)

            existing_by_topic = self.subscriptions_by_topic.setdefault(config.topic_name, [])
            existing_by_topic.append(sub)

            existing_by_sub_key = self.subscriptions_by_sub_key[config.sub_key] = sub

            # We don't start dedicated tasks for WebSockets - they are all dynamic without a fixed server.
            # But for other endpoint types, we create and start a delivery task here.
            if config.endpoint_type != PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id:

                # We have a matching server..
                if config.cluster_id == self.cluster_id and config.server_id == self.server.id:

                    # .. but make sure only the first worker of this server will start delivery tasks, not all of them.
                    if self.server.is_first_worker:

                        # Store in shared RAM information that our process handles this key
                        self.server.server_startup_ipc.set_pubsub_pid(self.server.pid)

                        config.server_pid = self.server.pid
                        config.server_name = self.server.name
                        self.set_sub_key_server(config)

                        # Starts the delivery task and notifies other servers that we are the one
                        # to handle deliveries for this particular sub_key.
                        self.server.invoke('zato.pubsub.delivery.create-delivery-task', config)

                    # We are not the first worker of this server and the first one must have already stored
                    # in RAM the mapping of sub_key -> server_pid, so we can safely read it here to add
                    # a subscription server.
                    else:
                        config.server_pid = self.server.server_startup_ipc.get_pubsub_pid()
                        config.server_name = self.server.name
                        self.set_sub_key_server(config)

# ################################################################################################################################

    def get_hook_service_invoker(self, service_name, hook_type):
        """ Returns a function that will invoke pub/sub hooks.
        """
        def _invoke_hook_service(topic, msg):
            """ A function to invoke pub/sub hook services.
            """
            ctx = HookCtx(hook_type, topic, msg)
            return self.server.invoke(service_name, ctx)

        return _invoke_hook_service

# ################################################################################################################################

    def _create_topic(self, config):
        if config.hook_service_id:
            config.hook_service_invoker = self.get_hook_service_invoker(config.hook_service_name, PUBSUB.HOOK_TYPE.PUB)
        else:
            config.hook_service_invoker = None

        self.topics[config.id] = Topic(config)
        self.topic_name_to_id[config.name] = config.id

# ################################################################################################################################

    def create_topic(self, config):
        with self.lock:
            self._create_topic(config)

# ################################################################################################################################

    def _delete_topic(self, topic_id, topic_name):
        del self.topic_name_to_id[topic_name]
        self.subscriptions_by_topic.pop(topic_name, None) # May have no subscriptions hence .pop instead of del
        del self.topics[topic_id]

# ################################################################################################################################

    def delete_topic(self, topic_id):
        with self.lock:
            topic_name = self.topics[topic_id].name
            self._delete_topic(topic_id, topic_name)

# ################################################################################################################################

    def edit_topic(self, del_name, config):
        with self.lock:
            subscriptions_by_topic = self.subscriptions_by_topic.pop(del_name, [])
            self._delete_topic(config.id, del_name)
            self._create_topic(config)
            self.subscriptions_by_topic[config.name] = subscriptions_by_topic

# ################################################################################################################################

    def _is_allowed(self, target, name, security_id, ws_channel_id, endpoint_id=None):

        if not endpoint_id:

            if not(security_id or ws_channel_id):
                raise ValueError(
                    'Either security_id or ws_channel_id must be given on input instead of `{}` `{}`'.format(
                    security_id, ws_channel_id))

            if security_id:
                source, id = self.sec_id_to_endpoint_id, security_id
            else:
                source, id = self.ws_channel_id_to_endpoint_id, ws_channel_id

            endpoint_id = source[id]

        endpoint = self.endpoints[endpoint_id]

        for orig, matcher in getattr(endpoint, target):
            if matcher.match(name):
                return orig

# ################################################################################################################################

    def is_allowed_pub_topic(self, name, security_id=None, ws_channel_id=None):
        return self._is_allowed('pub_topic_patterns', name, security_id, ws_channel_id)

# ################################################################################################################################

    def is_allowed_pub_topic_by_endpoint_id(self, name, endpoint_id):
        return self._is_allowed('pub_topic_patterns', name, None, None, endpoint_id)

# ################################################################################################################################

    def is_allowed_sub_topic(self, name, security_id=None, ws_channel_id=None):
        return self._is_allowed('sub_topic_patterns', name, security_id, ws_channel_id)

# ################################################################################################################################

    def is_allowed_sub_topic_by_endpoint_id(self, name, endpoint_id):
        return self._is_allowed('sub_topic_patterns', name, None, None, endpoint_id)

# ################################################################################################################################

    def add_ws_client_pubsub_keys(self, session, sql_ws_client_id, sub_key, channel_name, pub_client_id):
        """ Adds to SQL information that a given WSX client handles messages for sub_key.
        This information is transient - it will be dropped each time a WSX client disconnects
        """
        # Update state in SQL
        ws_sub_key = WebSocketClientPubSubKeys()
        ws_sub_key.client_id = sql_ws_client_id
        ws_sub_key.sub_key = sub_key
        ws_sub_key.cluster_id = self.cluster_id
        session.add(ws_sub_key)

        # Update in-RAM state of workers
        self.broker_client.publish({
            'action': BROKER_MSG_PUBSUB.SUB_KEY_SERVER_SET.value,
            'cluster_id': self.cluster_id,
            'server_name': self.server.name,
            'server_pid': self.server.pid,
            'sub_key': sub_key,
            'channel_name': channel_name,
            'pub_client_id': pub_client_id,
            'endpoint_type': PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id
        })

# ################################################################################################################################

    def set_sub_key_server(self, config):
        self.sub_key_servers[config['sub_key']] = SubKeyServer(config)

# ################################################################################################################################

    def remove_ws_sub_key_server(self, config):
        """ Called after a WSX client disconnects - provides a list of sub_keys that it handled
        which we must remove from our config because without this client they are no longer usable (until the client reconnects).
        """
        for sub_key in config.sub_key_list:
            self.sub_key_servers.pop(sub_key, None)
            for server_info in self.sub_key_servers.values():
                if server_info.sub_key == sub_key:
                    del self.sub_key_servers[sub_key]
                    break

# ################################################################################################################################

    def get_task_servers_by_sub_keys(self, sub_keys):
        """ Returns a dictionary keyed by (server_name, server_pid, pub_client_id, channel_name) tuples
        and values being sub_keys that a WSX client pointed to by each key has subscribed to.
        """
        found = {}
        not_found = []

        for sub_key in sub_keys:
            info = self.sub_key_servers.get(sub_key)
            if info:
                _key = (info.server_name, info.server_pid, info.pub_client_id, info.channel_name, info.endpoint_type)
                _info = found.setdefault(_key, [])
                _info.append(sub_key)
            else:
                not_found.append(sub_key)

        return found, not_found

# ################################################################################################################################

    def get_sql_messages_by_sub_key(self, sub_key, last_sql_run, session=None):
        """ Returns from SQL all messages queued up for a given sub_key.
        """
        if not session:
            session = self.server.odb.session()
            needs_close = True
        else:
            needs_close = False

        try:
            return _get_sql_messages_by_sub_key(session, self.server.cluster_id, sub_key, last_sql_run, utcnow_as_ms())
        finally:
            if needs_close:
                session.close()

# ################################################################################################################################

    def confirm_pubsub_msg_delivered(self, sub_key, pub_msg_id):
        """ Sets in SQL delivery status of a given message to True.
        """
        with closing(self.server.odb.session()) as session:
            _confirm_pubsub_msg_delivered(session, self.server.cluster_id, sub_key, pub_msg_id, utcnow_as_ms())
            session.commit()

# ################################################################################################################################

    def store_in_ram(self, cid, topic_id, topic_name, sub_keys, non_gd_msg_list, from_notif_error):
        """ Stores in RAM up to input non-GD messages for each sub_key. A backlog queue for each sub_key
        cannot be longer than topic's max_depth_non_gd and overlown messages are not kept in RAM.
        They are not lost altogether though, because, if enabled by topic's use_overflow_log, all such messages
        go to disk (or to another location that logger_overflown is configured to use).
        """
        self.in_ram_backlog.add_messages(cid, topic_id, topic_name, self.topics[topic_id].max_depth_non_gd,
            sub_keys, non_gd_msg_list)

# ################################################################################################################################

    def unsubscribe(self, topic_sub_keys):
        """ Removes subscriptions for all input sub_keys. topic_sub_keys is a dictionary keyed by topic_name,
        and each value is a list of sub_keys, possibly one-element long.
        """
        for topic_name, sub_keys in topic_sub_keys.items():

            # We receive topic_names on input but in-RAM backlog requires topic IDs.
            topic_id = self.topic_name_to_id[topic_name]

            # Delete subscriptions, and any related messages, from RAM
            self.in_ram_backlog.unsubscribe(topic_id, sub_keys)

            # Delete subscription metadata from local pubsub
            subscriptions_by_topic = self.subscriptions_by_topic[topic_name]

            for sub in subscriptions_by_topic:
                if sub.sub_key in sub_keys:
                    subscriptions_by_topic.remove(sub)

            # Find and stop all delivery tasks if we are the server that handles them
            for sub_key in sub_keys:
                sub_key_server = self.sub_key_servers.get(sub_key)
                if sub_key_server:

                    _cluster_id = sub_key_server.cluster_id
                    _server_name = sub_key_server.server_name
                    _server_pid = sub_key_server.server_pid

                    cluster_id = self.server.cluster_id
                    server_name = self.server.name
                    server_pid = self.server.pid

                    # If we are the server that handles this particular sub_key ..
                    if _cluster_id == cluster_id and _server_name == server_name and _server_pid == server_pid:

                        # .. then find the pubsub_tool that actually does it ..
                        for pubsub_tool in self.pubsub_tools:
                            if pubsub_tool.handles_sub_key(sub_key):

                                # .. stop the delivery task ..
                                pubsub_tool.remove_sub_key(sub_key)

                                # .. and remove the mapping of sub_key -> pubsub_tool.
                                del self.pubsub_tool_by_sub_key[sub_key]

                                # No need to iterate further, there can be only one task for each sub_key
                                break

# ################################################################################################################################

    def register_pubsub_tool(self, pubsub_tool):
        """ Registers a new pubsub_tool for this server, i.e. a new delivery task container.
        """
        self.pubsub_tools.append(pubsub_tool)

# ################################################################################################################################

    def set_pubsub_tool_for_sub_key(self, sub_key, pubsub_tool):
        """ Adds a mapping between a sub_key and pubsub_tool handling its messages.
        """
        self.pubsub_tool_by_sub_key[sub_key] = pubsub_tool

# ################################################################################################################################

    def get_endpoint_by_sub_key(self, sub_key):
        """ Returns an endpoint by subscription's sub_key - the object returned is an actual recipient,
        e.g. an outgoing REST connection.
        """

# ################################################################################################################################
