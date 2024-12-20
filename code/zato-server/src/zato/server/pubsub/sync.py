# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pylint: disable=unused-import, unused-variable

# stdlib
import logging
from traceback import format_exc

# gevent
from gevent import sleep
from gevent.lock import RLock

# Zato
from zato.common.api import PUBSUB
from zato.common.exception import BadRequest
from zato.common.util.api import spawn_greenlet
from zato.common.util.pubsub import make_short_msg_copy_from_dict
from zato.common.util.time_ import utcnow_as_ms

# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, anyset, anytuple, callable_, dict_, dictlist, intsetdict, strlist, \
        strdictdict, strset, strsetdict
    from zato.server.pubsub import PubSub
    from zato.server.pubsub.model import Endpoint
    any_ = any_
    anyset = anyset
    anytuple = anytuple
    dict_ = dict_
    strset = strset
    Endpoint = Endpoint

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

_default_pri=PUBSUB.PRIORITY.DEFAULT
_pri_min=PUBSUB.PRIORITY.MIN
_pri_max=PUBSUB.PRIORITY.MAX

# ################################################################################################################################

_update_attrs = (
    'data', 'size', 'expiration', 'priority', 'pub_correl_id', 'in_reply_to', 'mime_type', 'expiration', 'expiration_time'
)

# ################################################################################################################################

_default_expiration = PUBSUB.DEFAULT.EXPIRATION
default_sk_server_table_columns = 6, 15, 8, 6, 17, 80

# ################################################################################################################################

def get_priority(
    cid,   # type: str
    input, # type: anydict
    _pri_min=_pri_min,    # type: int
    _pri_max=_pri_max,    # type: int
    _pri_def=_default_pri # type: int
) -> 'int':
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

def get_expiration(
    cid,   # type: str
    input, # type: anydict
    default_expiration=_default_expiration # type: int
) -> 'int':
    """ Get and validate message expiration.
    Returns (2 ** 31 - 1) * 1000 milliseconds (around 70 years) if expiration is not set explicitly.
    """
    expiration = input.get('expiration')
    if expiration is not None and expiration < 0:
        raise BadRequest(cid, 'Expiration `{}` must not be negative'.format(expiration))

    return expiration or default_expiration

# ################################################################################################################################

class InRAMSync:
    """ A backlog of messages kept in RAM for whom there are subscriptions - that is, they are known to have subscribers
    and will be ultimately delivered to them. Stores a list of sub_keys and all messages that a sub_key points to.
    It acts as a multi-key dict and keeps only a single copy of message for each sub_key.
    """

    lock: 'RLock'
    pubsub: 'PubSub'

    msg_id_to_msg:     'strdictdict'
    topic_id_msg_id:   'intsetdict'
    sub_key_to_msg_id: 'strsetdict'
    msg_id_to_sub_key: 'strsetdict'

    def __init__(self, pubsub:'PubSub') -> 'None':

        self.lock = RLock()
        self.pubsub = pubsub

        # Msg ID   -> Message data - What is the actual contents of each message
        self.msg_id_to_msg = {}

        # Topic ID -> Msg ID set --- What messages are available for each topic (no matter sub_key)
        self.topic_id_msg_id = {}

        # Sub key  -> Msg ID set --- What messages are available for a given subcriber
        self.sub_key_to_msg_id = {}

        # Msg ID   -> Sub key set  - What subscribers are interested in a given message
        self.msg_id_to_sub_key = {}

        # Start in background a cleanup task that deletes all expired and removed messages
        _ = spawn_greenlet(self.run_cleanup_task)

# ################################################################################################################################

    def add_messages(
        self,
        cid,        # type: str
        topic_id,   # type: int
        topic_name, # type: str
        max_depth,  # type: int
        sub_keys,   # type: strlist
        messages,   # type: dictlist
        _default_pri=_default_pri # type: int
    ) -> 'None':
        """ Adds all input messages to sub_keys for the topic.
        """
        with self.lock:

            # Local aliases
            msg_ids = [msg['pub_msg_id'] for msg in messages]
            len_messages = len(messages)
            topic_messages = self.topic_id_msg_id.setdefault(topic_id, set())

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

    def update_msg(
        self,
        msg, # type: anydict
        _update_attrs=_update_attrs,                 # type: anytuple
        _warn='No such message in sync backlog `%s`' # type: str
        ) -> 'bool':

        with self.lock:
            _msg = self.msg_id_to_msg.get(msg['msg_id'])
            if not _msg:
                logger.warning(_warn, msg['msg_id'])
                logger_zato.warning(_warn, msg['msg_id'])
                return False # No such message
            else:
                for attr in _update_attrs:
                    _msg[attr] = msg[attr]

                # Ok, found and updated
                return True

# ################################################################################################################################

    def delete_msg_by_id(self, msg_id:'str') -> 'None':
        """ Deletes a message by its ID.
        """
        self.delete_messages([msg_id])

# ################################################################################################################################

    def _delete_messages(self, msg_list:'strlist') -> 'None':
        """ Low-level implementation of self.delete_messages - must be called with self.lock held.
        """
        logger.info('Deleting non-GD messages `%s`', msg_list)

        for msg_id in list(msg_list):

            found_to_sub_key = self.msg_id_to_sub_key.pop(msg_id, None)
            found_to_msg = self.msg_id_to_msg.pop(msg_id, None)

            _has_topic_msg = False # Was the ID found for at least one topic
            _has_sk_msg = False     # Ditto but for sub_keys

            for _topic_msg_set in self.topic_id_msg_id.values():
                try:
                    _ = _topic_msg_set.remove(msg_id)
                except KeyError:
                    pass # This is fine, msg_id did not belong to this topic
                else:
                    _has_topic_msg = True

            for _sk_msg_set in self.sub_key_to_msg_id.values():
                try:
                    _ = _sk_msg_set.remove(msg_id)
                except KeyError:
                    pass # This is fine, msg_id did not belong to this topic
                else:
                    _has_sk_msg = True

            if not found_to_sub_key:
                logger.warning('Message not found (msg_id_to_sub_key) %s', msg_id)
                logger_zato.warning('Message not found (msg_id_to_sub_key) %s', msg_id)

            if not found_to_msg:
                logger.warning('Message not found (msg_id_to_msg) %s', msg_id)
                logger_zato.warning('Message not found (msg_id_to_msg) %s', msg_id)

            if not _has_topic_msg:
                logger.warning('Message not found (_has_topic_msg) %s', msg_id)
                logger_zato.warning('Message not found (_has_topic_msg) %s', msg_id)

            if not _has_sk_msg:
                logger.warning('Message not found (_has_sk_msg) %s', msg_id)
                logger_zato.warning('Message not found (_has_sk_msg) %s', msg_id)

# ################################################################################################################################

    def delete_messages(self, msg_list:'strlist') -> 'None':
        """ Deletes all messages from input msg_list.
        """
        with self.lock:
            self._delete_messages(msg_list)

# ################################################################################################################################

    def has_messages_by_sub_key(self, sub_key:'str') -> 'bool':
        with self.lock:
            msg_id_set = self.sub_key_to_msg_id.get(sub_key) or set()
            return len(msg_id_set) > 0

# ################################################################################################################################

    def clear_topic(self, topic_id:'int') -> 'None':
        logger.info('Clearing topic `%s` (id:%s)', self.pubsub.get_topic_by_id(topic_id).name, topic_id)

        with self.lock:

            # Not all servers will have messages for the topic, hence .get
            messages = self.topic_id_msg_id.get(topic_id, set())

            if messages:
                messages = list(messages) # We need a copy so as not to change the input set during iteration later on
                self._delete_messages(messages)
            else:
                logger.info(
                    'Did not find any non-GD messages to delete for topic `%s`',
                    self.pubsub.get_topic_by_id(topic_id))

# ################################################################################################################################

    def get_delete_messages_by_sub_keys(
        self,
        topic_id, # type: int
        sub_keys, # type: strlist
        delete_msg=True, # type: bool
        delete_sub=False # type: bool
    ) -> 'dictlist':
        """ Low-level implementation of retrieve_messages_by_sub_keys which must be called with self.lock held.
        """

        # Forward declaration
        msg_id: 'str'

        # We cannot return expired messages
        now = utcnow_as_ms()

        # We cannot have duplicates on output
        msg_seen = set() # type: strset

        # Response to product
        out = [] # type: dictlist

        # A list of messages that will be optionally deleted before they are returned
        to_delete_msg = set() # type: anyset

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
                        logger.warning('Msg `%s` not found in self.msg_id_to_msg', msg_id)
                        continue
                    if now >= msg['expiration_time']:
                        continue
                    else:
                        out.append(self.msg_id_to_msg[msg_id])

                if delete_msg:
                    to_delete_msg.add(msg_id)

        # Delete all messages marked to be deleted ..
        for msg_id in to_delete_msg:

            # .. first, direct mappings ..
            _ = self.msg_id_to_msg.pop(msg_id, None)

            logger.info('Deleting msg from mapping dict `%s`, before:`%s`', msg_id, self.msg_id_to_msg)

            # .. now, remove the message from topic ..
            self.topic_id_msg_id[topic_id].remove(msg_id)

            logger.info('Deleting msg from mapping topic `%s`, after:`%s`', msg_id, self.topic_id_msg_id)

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

    def retrieve_messages_by_sub_keys(self, topic_id:'int', sub_keys:'strlist') -> 'dictlist':
        """ Retrieves and returns all messages matching input - messages are deleted from RAM.
        """
        with self.lock:
            return self.get_delete_messages_by_sub_keys(topic_id, sub_keys)

# ################################################################################################################################

    def get_messages_by_topic_id(
        self,
        topic_id,         # type: int
        needs_short_copy, # type: bool
        query=''          # type: str
    ) -> 'anylist':
        """ Returns messages for topic by its ID, optionally with pagination and filtering by input query.
        """

        # Forward declaration
        msg_id: 'str'

        with self.lock:
            msg_id_list = self.topic_id_msg_id.get(topic_id, [])
            if not msg_id_list:
                return []

            # A list of messages to be returned - we actually need to build a whole list instead of using
            # generators because the underlying container is an unsorted set and we need a sorted result on output.
            msg_list = [] # type: dictlist

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

    def get_message_by_id(self, msg_id:'str') -> 'anydict':
        with self.lock:
            return self.msg_id_to_msg[msg_id]

# ################################################################################################################################

    def unsubscribe(
        self,
        topic_id,   # type: int
        topic_name, # type: str
        sub_keys,   # type: strlist
        pattern='Removing subscription info for `%s` from topic `%s`' # type: str
    ) -> 'None':
        """ Unsubscribes all the sub_keys from the input topic.
        """

        # Forward declarations
        msg_id:  'str'
        sub_key: 'str'

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
                        topic_msg = self.topic_id_msg_id[topic_id]
                        topic_msg.remove(msg_id)

        logger.info(pattern, sub_keys, topic_name)
        logger_zato.info(pattern, sub_keys, topic_name)

# ################################################################################################################################

    def run_cleanup_task(self, _utcnow:'callable_'=utcnow_as_ms, _sleep:'callable_'=sleep) -> 'None':
        """ A background task waking up periodically to remove all expired and retrieved messages from backlog.
        """

        # Forward declarations
        msg_id:   'str'
        sub_key:  'str'
        topic_id: 'int'

        while True:
            try:
                with self.lock:

                    # Local alias
                    publishers = {} # type: dict_[int, Endpoint]

                    # We keep them separate so as not to modify any objects during iteration.
                    expired_msg = [] # type: anylist

                    # Calling it once will suffice.
                    now = _utcnow()

                    for _, msg in self.msg_id_to_msg.items():

                        if now >= msg['expiration_time']:

                            # It's possible that there will be many expired messages all sent by the same publisher
                            # so there is no need to query self.pubsub for each message.
                            if msg['published_by_id'] not in publishers:
                                publishers[msg['published_by_id']] = self.pubsub.get_endpoint_by_id(msg['published_by_id'])

                            # We can be sure that it is always found
                            publisher = publishers[msg['published_by_id']] # type: Endpoint

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
                        self.topic_id_msg_id[topic_id].remove(msg_id)

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
                logger.warning(log_msg, e)
                logger_zato.warning(log_msg, e)
                _sleep(0.1)

# ################################################################################################################################

    def log_messages_to_store(
        self,
        cid,        # type: str
        topic_name, # type: str
        max_depth,  # type: int
        sub_key,    # type: str
        messages    # type: any_
    ) -> 'None':
        # Used by both loggers
        msg = 'Reached max in-RAM delivery depth of %r for topic `%r` (cid:%r). Extra messages will be stored in logs.'
        args = (max_depth, topic_name, cid)

        # Log in pub/sub log and the main one as well, just to make sure it will be easily found
        logger.warning(msg, *args)
        logger_zato.warning(msg, *args)

        # Store messages in logger - by default will go to disk
        logger_overflow.info('CID:%s, topic:`%s`, sub_key:%s, messages:%s', cid, topic_name, sub_key, messages)

# ################################################################################################################################

    def get_topic_depth(self, topic_id:'int') -> 'int':
        """ Returns depth of a given in-RAM queue for the topic.
        """
        with self.lock:
            return len(self.topic_id_msg_id.get(topic_id, set()))

# ################################################################################################################################
# ################################################################################################################################
