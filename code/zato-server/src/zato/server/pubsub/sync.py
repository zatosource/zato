# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from traceback import format_exc

# gevent
from gevent import sleep
from gevent.lock import RLock

# Python 2/3 compatibility
from future.utils import iteritems, itervalues

# Zato
from zato.common import DATA_FORMAT, PUBSUB, SEARCH
from zato.common.exception import BadRequest
from zato.common.util import spawn_greenlet
from zato.common.util.pubsub import make_short_msg_copy_from_dict
from zato.common.util.time_ import utcnow_as_ms

# ################################################################################################################################

logger = logging.getLogger('zato_pubsub.ps')
logger_zato = logging.getLogger('zato')
logger_overflow = logging.getLogger('zato_pubsub_overflow')

# ################################################################################################################################

hook_type_to_method = {
    PUBSUB.HOOK_TYPE.BEFORE_PUBLISH: 'before_publish',
    PUBSUB.HOOK_TYPE.BEFORE_DELIVERY: 'before_delivery',
    PUBSUB.HOOK_TYPE.ON_OUTGOING_SOAP_INVOKE: 'on_outgoing_soap_invoke',
    PUBSUB.HOOK_TYPE.ON_SUBSCRIBED: 'on_subscribed',
    PUBSUB.HOOK_TYPE.ON_UNSUBSCRIBED: 'on_unsubscribed',
}

# ################################################################################################################################

_service_read_messages_gd = 'zato.pubsub.endpoint.get-endpoint-queue-messages-gd'
_service_read_messages_non_gd = 'zato.pubsub.endpoint.get-endpoint-queue-messages-non-gd'

_service_read_message_gd = 'zato.pubsub.message.get-from-queue-gd'
_service_read_message_non_gd = 'zato.pubsub.message.get-from-queue-non-gd'

_service_delete_message_gd = 'zato.pubsub.message.queue-delete-gd'
_service_delete_message_non_gd = 'zato.pubsub.message.queue-delete-non-gd'

# ################################################################################################################################

_pub_role = (PUBSUB.ROLE.PUBLISHER_SUBSCRIBER.id, PUBSUB.ROLE.PUBLISHER.id)
_sub_role = (PUBSUB.ROLE.PUBLISHER_SUBSCRIBER.id, PUBSUB.ROLE.SUBSCRIBER.id)

# ################################################################################################################################

_update_attrs = ('data', 'size', 'expiration', 'priority', 'pub_correl_id', 'in_reply_to', 'mime_type',
    'expiration', 'expiration_time')

# ################################################################################################################################

_does_not_exist = object()

# ################################################################################################################################

_default_expiration = PUBSUB.DEFAULT.EXPIRATION
default_sk_server_table_columns = 6, 15, 8, 6, 17, 80

# ################################################################################################################################

_PRIORITY=PUBSUB.PRIORITY
_JSON=DATA_FORMAT.JSON
_page_size = SEARCH.ZATO.DEFAULTS.PAGE_SIZE.value

class msg:
    wsx_sub_resumed = 'WSX subscription resumed, sk:`%s`, peer:`%s`'

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

def get_expiration(cid, input, default_expiration=_default_expiration):
    """ Get and validate message expiration.
    Returns (2 ** 31 - 1) * 1000 milliseconds (around 68 years) if expiration is not set explicitly.
    """
    expiration = input.get('expiration')
    if expiration is not None and expiration < 0:
        raise BadRequest(cid, 'Expiration `{}` must not be negative'.format(expiration))

    return expiration or default_expiration

# ################################################################################################################################

class InRAMSync(object):
    """ A backlog of messages kept in RAM for whom there are subscriptions - that is, they are known to have subscribers
    and will be ultimately delivered to them. Stores a list of sub_keys and all messages that a sub_key points to.
    It acts as a multi-key dict and keeps only a single copy of message for each sub_key.
    """
    def __init__(self, pubsub):
        self.pubsub = pubsub        # type: PubSub
        self.sub_key_to_msg_id = {} # Sub key  -> Msg ID set --- What messages are available for a given subcriber
        self.msg_id_to_sub_key = {} # Msg ID   -> Sub key set  - What subscribers are interested in a given message
        self.msg_id_to_msg = {}     # Msg ID   -> Message data - What is the actual contents of each message
        self.topic_msg_id = {}      # Topic ID -> Msg ID set --- What messages are available for each topic (no matter sub_key)
        self.lock = RLock()

        # Start in background a cleanup task that deletes all expired and removed messages
        spawn_greenlet(self.run_cleanup_task)

# ################################################################################################################################

    def add_messages(self, cid, topic_id, topic_name, max_depth, sub_keys, messages, _default_pri=PUBSUB.PRIORITY.DEFAULT):
        """ Adds all input messages to sub_keys for the topic.
        """
        with self.lock:

            # Local aliases
            msg_ids = [msg['pub_msg_id'] for msg in messages]
            len_messages = len(messages)
            topic_messages = self.topic_msg_id.setdefault(topic_id, set())

            # Try to append the messages for each of their subscribers ..
            for sub_key in sub_keys:

                # .. but first, make sure that storing these messages would not overflow the topic's depth,
                # if it could exceed the max depth, store the messages in log files only ..
                if len(topic_messages) + len_messages > max_depth:
                    self.log_messages_to_store(cid, topic_name, max_depth, sub_key, messages)

                    # .. skip this sub_key in such a case ..
                    continue

                # .. otherwise, we make it known that the sub_key is interested in this message ..
                sub_key_msg = self.sub_key_to_msg_id.setdefault(sub_key, set())
                sub_key_msg.update(msg_ids)

            # For each message given on input, store its actual contents ..
            for msg in messages:
                self.msg_id_to_msg[msg['pub_msg_id']] = msg

                # We received timestamps as strings whereas our recipients require floats
                # so we need to do the conversion here.
                msg['pub_time'] = float(msg['pub_time'])
                if msg.get('ext_pub_time'):
                    msg['ext_pub_time'] = float(msg['ext_pub_time'])

                # .. attach server metadata ..
                msg['server_name'] = self.pubsub.server.name
                msg['server_pid'] = self.pubsub.server.pid

                # .. set default priority if none was given ..
                if 'priority' not in msg:
                    msg['priority'] = _default_pri

                # .. add a reverse mapping, from message ID to sub_key ..
                msg_sub_key = self.msg_id_to_sub_key.setdefault(msg['pub_msg_id'], set())
                msg_sub_key.update(sub_keys)

            # .. and add a reference to it to the topic.
            topic_messages.update(msg_ids)

# ################################################################################################################################

    def update_msg(self, msg, _update_attrs=_update_attrs, _warn='No such message in sync backlog `%s`'):
        with self.lock:
            _msg = self.msg_id_to_msg.get(msg['msg_id'])
            if not _msg:
                logger.warn(_warn, msg['msg_id'])
                logger_zato.warn(_warn, msg['msg_id'])
                return False # No such message
            else:
                for attr in _update_attrs:
                    _msg[attr] = msg[attr]

                # Ok, found and updated
                return True

# ################################################################################################################################

    def delete_msg_by_id(self, msg_id):
        """ Deletes a message by its ID.
        """
        return self.delete_messages([msg_id])

# ################################################################################################################################

    def _delete_messages(self, msg_list):
        """ Low-level implementation of self.delete_messages - must be called with self.lock held.
        """
        logger.info('Deleting non-GD messages `%s`', msg_list)

        for msg_id in list(msg_list):

            found_to_sub_key = self.msg_id_to_sub_key.pop(msg_id, None)
            found_to_msg = self.msg_id_to_msg.pop(msg_id, None)

            _has_topic_msg = False # Was the ID found for at least one topic
            _has_sk_msg = False     # Ditto but for sub_keys

            for _topic_msg_set in itervalues(self.topic_msg_id):
                try:
                    _topic_msg_set.remove(msg_id)
                except KeyError:
                    pass # This is fine, msg_id did not belong to this topic
                else:
                    _has_topic_msg = True

            for _sk_msg_set in itervalues(self.sub_key_to_msg_id):
                try:
                    _sk_msg_set.remove(msg_id)
                except KeyError:
                    pass # This is fine, msg_id did not belong to this topic
                else:
                    _has_sk_msg = True

            if not found_to_sub_key:
                logger.warn('Message not found (msg_id_to_sub_key) %s', msg_id)
                logger_zato.warn('Message not found (msg_id_to_sub_key) %s', msg_id)

            if not found_to_msg:
                logger.warn('Message not found (msg_id_to_msg) %s', msg_id)
                logger_zato.warn('Message not found (msg_id_to_msg) %s', msg_id)

            if not _has_topic_msg:
                logger.warn('Message not found (_has_topic_msg) %s', msg_id)
                logger_zato.warn('Message not found (_has_topic_msg) %s', msg_id)

            if not _has_sk_msg:
                logger.warn('Message not found (_has_sk_msg) %s', msg_id)
                logger_zato.warn('Message not found (_has_sk_msg) %s', msg_id)

# ################################################################################################################################

    def delete_messages(self, msg_list):
        """ Deletes all messages from input msg_list.
        """
        with self.lock:
            self._delete_messages(msg_list)

# ################################################################################################################################

    def has_messages_by_sub_key(self, sub_key):
        with self.lock:
            return len(self.sub_key_to_msg_id.get(sub_key, [])) > 0

# ################################################################################################################################

    def clear_topic(self, topic_id):
        logger.info('Clearing topic `%s` (id:%s)', self.pubsub.get_topic_by_id(topic_id).name, topic_id)

        with self.lock:
            # Not all servers will have messages for the topic, hence .get
            messages = self.topic_msg_id.get(topic_id) or []
            if messages:
                messages = list(messages) # We need a copy so as not to change the input set during iteration later on
            self._delete_messages(messages)

# ################################################################################################################################

    def _get_delete_messages_by_sub_keys(self, topic_id, sub_keys, delete_msg=True, delete_sub=False):
        """ Low-level implementation of retrieve_messages_by_sub_keys which must be called with self.lock held.
        """
        now = utcnow_as_ms() # We cannot return expired messages
        msg_seen = set() # We cannot have duplicates on output
        out = []

        # A list of messages that will be optionally deleted before they are returned
        to_delete_msg = set()

        # First, collect data for all sub_keys ..
        for sub_key in sub_keys:

            for msg_id in self.sub_key_to_msg_id.get(sub_key, []):

                # We already had this message marked for output
                if msg_id in msg_seen:
                    continue
                else:
                    # Mark as already seen
                    msg_seen.add(msg_id)

                    # Filter out expired messages
                    msg = self.msg_id_to_msg.get(msg_id)
                    if not msg:
                        logger.warn('Msg `%s` not found in self.msg_id_to_msg', msg_id)
                        continue
                    if now >= msg['expiration_time']:
                        continue
                    else:
                        out.append(self.msg_id_to_msg[msg_id])

                if delete_msg:
                    to_delete_msg.add(msg_id)

        # Explicitly delete a left-over name from the loop above
        del sub_key

        # Delete all messages marked to be deleted ..
        for msg_id in to_delete_msg:

            # .. first, direct mappings ..
            self.msg_id_to_msg.pop(msg_id, None)

            logger.info('Deleting msg from mapping dict `%s`, before:`%s`', msg_id, self.msg_id_to_msg)

            # .. now, remove the message from topic ..
            self.topic_msg_id[topic_id].remove(msg_id)

            logger.info('Deleting msg from mapping topic `%s`, after:`%s`', msg_id, self.topic_msg_id)

            # .. now, find the message for each sub_key ..
            for sub_key in sub_keys:
                sub_key_to_msg_id = self.sub_key_to_msg_id.get(sub_key)

                # We need this if statement because it is possible that a client is subscribed to a topic
                # but it will not receive a particular message. This is possible if the message is a response
                # to a previous request and the latter used reply_to_sk, in which case only that one sub_key pointed to
                # by reply_to_sk will get the response, which ultimately means that self.sub_key_to_msg_id
                # will not have this response for current sub_key.
                if sub_key_to_msg_id:

                    # .. delete the message itself - but we need to catch ValueError because
                    # to_delete_msg is a list of all messages to be deleted and we do not know
                    # if this particular message belonged to this particular sub_key or not.
                    try:
                        sub_key_to_msg_id.remove(msg_id)
                    except KeyError:
                        pass # OK, message was not found for this sub_key

                    # .. now delete the sub_key either because we are explicitly told to (e.g. during unsubscribe)
                    if delete_sub:# or (not sub_key_to_msg_id):
                        del self.sub_key_to_msg_id[sub_key]

        return out

# ################################################################################################################################

    def retrieve_messages_by_sub_keys(self, topic_id, sub_keys):
        """ Retrieves and returns all messages matching input - messages are deleted from RAM.
        """
        with self.lock:
            return self._get_delete_messages_by_sub_keys(topic_id, sub_keys)

# ################################################################################################################################

    def get_messages_by_topic_id(self, topic_id, needs_short_copy, query=None):
        """ Returns messages for topic by its ID, optionally with pagination and filtering by input query.
        """
        with self.lock:
            msg_id_list = self.topic_msg_id.get(topic_id, [])
            if not msg_id_list:
                return []

            # A list of messages to be returned - we actually need to build a whole list instead of using
            # generators because the underlying container is an unsorted set and we need a sorted result on output.
            msg_list = []

            for msg_id in msg_id_list:
                msg = self.msg_id_to_msg[msg_id]
                if query:
                    if query not in msg['data'][:self.pubsub.data_prefix_len]:
                        continue

                if needs_short_copy:
                    out_msg = make_short_msg_copy_from_dict(msg, self.pubsub.data_prefix_len, self.pubsub.data_prefix_short_len)
                else:
                    out_msg = msg

                msg_list.append(out_msg)

            return msg_list

# ################################################################################################################################

    def get_message_by_id(self, msg_id):
        with self.lock:
            return self.msg_id_to_msg[msg_id]

# ################################################################################################################################

    def unsubscribe(self, topic_id, topic_name, sub_keys, pattern='Removing subscription info for `%s` from topic `%s`'):
        """ Unsubscribes all the sub_keys from the input topic.
        """
        # Always acquire a lock for this kind of operation
        with self.lock:

            # For each sub_key ..
            for sub_key in sub_keys:

                # .. get all messages waiting for this subscriber, assuming there are any at all ..
                msg_ids = self.sub_key_to_msg_id.pop(sub_key, [])

                # .. for each message found we need to check if it is needed by any other subscriber,
                # and if it's not, then we delete all the reference to this message. Otherwise, we leave it
                # as is, because there is at least one other subscriber waiting for it.
                for msg_id in msg_ids:

                    # Get all subscribers interested in this message ..
                    current_subs = self.msg_id_to_sub_key[msg_id]
                    current_subs.remove(sub_key)

                    # .. if the list is empty, it means that there no some subscribers left for that message,
                    # in which case we may deleted references to this message from other look-up structures.
                    if not current_subs:
                        del self.msg_id_to_msg[msg_id]
                        topic_msg = self.topic_msg_id[topic_id]
                        topic_msg.remove(msg_id)

        logger.info(pattern, sub_keys, topic_name)
        logger_zato.info(pattern, sub_keys, topic_name)

# ################################################################################################################################

    def run_cleanup_task(self, _utcnow=utcnow_as_ms, _sleep=sleep):
        """ A background task waking up periodically to remove all expired and retrieved messages from backlog.
        """
        while True:
            try:
                with self.lock:

                    # Local alias
                    publishers = {}

                    # We keep them separate so as not to modify any objects during iteration.
                    expired_msg = []

                    # Calling it once will suffice.
                    now = _utcnow()

                    for msg_id, msg in iteritems(self.msg_id_to_msg):

                        if now >= msg['expiration_time']:

                            # It's possible that there will be many expired messages all sent by the same publisher
                            # so there is no need to query self.pubsub for each message.
                            if msg['published_by_id'] not in publishers:
                                publishers[msg['published_by_id']] = self.pubsub.get_endpoint_by_id(msg['published_by_id'])

                            # We can be sure that it is always found
                            publisher = publishers[msg['published_by_id']]

                            # Log the message to make sure the expiration event is always logged ..
                            logger_zato.info('Found an expired msg:`%s`, topic:`%s`, publisher:`%s`, pub_time:`%s`, exp:`%s`',
                                msg['pub_msg_id'], msg['topic_name'], publisher.name, msg['pub_time'], msg['expiration'])

                            # .. and append it to the list of messages to be deleted.
                            expired_msg.append((msg['pub_msg_id'], msg['topic_id']))

                    # For logging what was done
                    len_expired = len(expired_msg)

                    # Iterate over all the expired messages found and delete them from in-RAM structures
                    for msg_id, topic_id in expired_msg:

                        # Get all sub_keys waiting for these messages and delete the message from each one,
                        # but note that there may be possibly no subscribers at all if the message was published
                        # to a topic without any subscribers.
                        for sub_key in self.msg_id_to_sub_key.pop(msg_id):
                            self.sub_key_to_msg_id[sub_key].remove(msg_id)

                        # Remove all references to the message from topic
                        self.topic_msg_id[topic_id].remove(msg_id)

                        # And finally, remove the message's contents
                        del self.msg_id_to_msg[msg_id]

                suffix = 's' if (len_expired==0 or len_expired > 1) else ''
                len_messages = len(self.msg_id_to_msg)
                if len_expired or len_messages:
                    logger.info('In-RAM. Deleted %s pub/sub message%s. Left:%s' % (len_expired, suffix, self.msg_id_to_msg))

                # Sleep for a moment before checking again but don't do it with self.lock held.
                _sleep(2)

            except Exception:
                e = format_exc()
                log_msg = 'Could not remove messages from in-RAM backlog, e:`%s`'
                logger.warn(log_msg, e)
                logger_zato.warn(log_msg, e)
                _sleep(0.1)

# ################################################################################################################################

    def log_messages_to_store(self, cid, topic_name, max_depth, sub_key, messages):
        # Used by both loggers
        msg = 'Reached max in-RAM delivery depth of %r for topic `%r` (cid:%r). Extra messages will be stored in logs.'
        args = (max_depth, topic_name, cid)

        # Log in pub/sub log and the main one as well, just to make sure it will be easily found
        logger.warn(msg, *args)
        logger_zato.warn(msg, *args)

        # Store messages in logger - by default will go to disk
        logger_overflow.info('CID:%s, topic:`%s`, sub_key:%s, messages:%s', cid, topic_name, sub_key, messages)

# ################################################################################################################################

    def get_topic_depth(self, topic_id, _default=set()):
        """ Returns depth of a given in-RAM queue for the topic.
        """
        with self.lock:
            return len(self.topic_msg_id.get(topic_id, _default))

# ################################################################################################################################
# ################################################################################################################################
