# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from logging import getLogger
from traceback import format_exc

# datetutil
from dateparser import parse as dt_parse

# gevent
from gevent import spawn

# Zato
from zato.common import DATA_FORMAT, PUBSUB, ZATO_NONE
from zato.common.exception import Forbidden, NotFound, ServiceUnavailable
from zato.common.odb.query.pubsub.cleanup import delete_enq_delivered, delete_enq_marked_deleted, delete_msg_delivered, \
     delete_msg_expired
from zato.common.odb.query.pubsub.publish import sql_publish_with_retry
from zato.common.odb.query.pubsub.topic import get_gd_depth_topic
from zato.common.pubsub import PubSubMessage
from zato.common.pubsub import new_msg_id
from zato.common.util.time_ import datetime_to_ms, utcnow_as_ms
from zato.server.pubsub import get_expiration, get_priority, PubSub, Topic
from zato.server.service import AsIs, Int, List
from zato.server.service.internal import AdminService

# For pyflakes
PubSub = PubSub
Topic = Topic

# ################################################################################################################################

_JSON = DATA_FORMAT.JSON
_initialized = PUBSUB.DELIVERY_STATUS.INITIALIZED

_meta_topic_key = PUBSUB.REDIS.META_TOPIC_KEY
_meta_endpoint_key = PUBSUB.REDIS.META_ENDPOINT_KEY

# ################################################################################################################################

logger_audit = getLogger('zato_pubsub_audit')

# ################################################################################################################################

class PubCtx(object):
    """ A container for information describing a single publication.
    """
    __slots__ = ('cluster_id', 'pubsub', 'topic', 'endpoint_id', 'subscriptions_by_topic', 'msg_id_list', 'gd_msg_list',
        'non_gd_msg_list', 'pattern_matched', 'ext_client_id', 'is_re_run', 'now', 'current_depth', 'last_msg')

    def __init__(self, cluster_id, pubsub, topic, endpoint_id, subscriptions_by_topic, msg_id_list, gd_msg_list, non_gd_msg_list,
            pattern_matched, ext_client_id, is_re_run, now):
        self.cluster_id = cluster_id
        self.pubsub = pubsub
        self.topic = topic
        self.endpoint_id = endpoint_id
        self.subscriptions_by_topic = subscriptions_by_topic
        self.msg_id_list = msg_id_list
        self.gd_msg_list = gd_msg_list
        self.non_gd_msg_list = non_gd_msg_list
        self.pattern_matched = pattern_matched
        self.ext_client_id = ext_client_id
        self.is_re_run = is_re_run
        self.now = now
        self.current_depth = None
        self.last_msg = self.gd_msg_list[-1] if self.gd_msg_list else self.non_gd_msg_list[-1]

# ################################################################################################################################

class Publish(AdminService):
    """ Actual implementation of message publishing exposed through other services to the outside world.
    """
    class SimpleIO:
        input_required = ('topic_name',)
        input_optional = ('data', List('data_list'), AsIs('msg_id'), 'has_gd', Int('priority'), Int('expiration'), 'mime_type',
            AsIs('correl_id'), 'in_reply_to', AsIs('ext_client_id'), 'ext_pub_time', 'pattern_matched', 'security_id',
            'ws_channel_id', 'service_id', 'data_parsed', 'meta', AsIs('group_id'),
            Int('position_in_group'), 'endpoint_id')
        output_optional = (AsIs('msg_id'), List('msg_id_list'))

# ################################################################################################################################

    def _get_data_prefixes(self, data):
        data_prefix = data[:2048]
        data_prefix_short = data[:64]

        return data_prefix, data_prefix_short

# ################################################################################################################################

    def _get_message(self, topic, input, now, pattern_matched, endpoint_id, has_subs, _initialized=_initialized,
        _zato_none=ZATO_NONE, _skip=PUBSUB.HOOK_ACTION.SKIP, _default_pri=PUBSUB.PRIORITY.DEFAULT):

        priority = get_priority(self.cid, input)

        # So as not to send it to SQL if it is a default value anyway = less overhead = better performance
        if priority == _default_pri:
            priority = None

        expiration = get_expiration(self.cid, input)
        expiration_time = now + (expiration / 1000.0)

        pub_msg_id = input.get('msg_id', '').encode('utf8') or new_msg_id()

        has_gd = input.get('has_gd', _zato_none)
        if has_gd != _zato_none:
            if not isinstance(has_gd, bool):
                raise ValueError('Input has_gd is not a bool (found:`{}`)'.format(repr(has_gd)))
        else:
            has_gd = topic.has_gd

        pub_correl_id = input.get('correl_id')
        in_reply_to = input.get('in_reply_to')
        ext_client_id = input.get('ext_client_id')
        mime_type = input.get('mime_type')

        ext_pub_time = input.get('ext_pub_time') or None
        if ext_pub_time:
            ext_pub_time = dt_parse(ext_pub_time)
            ext_pub_time = datetime_to_ms(ext_pub_time)

        pub_correl_id = pub_correl_id.encode('utf8') if pub_correl_id else None
        in_reply_to = in_reply_to.encode('utf8') if in_reply_to else None
        ext_client_id = ext_client_id.encode('utf8') if ext_client_id else None
        mime_type = mime_type.encode('utf8') if mime_type else None

        ps_msg = PubSubMessage()
        ps_msg.topic = topic
        ps_msg.pub_msg_id = pub_msg_id
        ps_msg.pub_correl_id = pub_correl_id
        ps_msg.in_reply_to = in_reply_to
        ps_msg.pub_time = now
        ps_msg.delivery_status = _initialized
        ps_msg.pattern_matched = pattern_matched
        ps_msg.data = input['data']
        ps_msg.mime_type = mime_type
        ps_msg.priority = priority
        ps_msg.expiration = expiration
        ps_msg.expiration_time = expiration_time
        ps_msg.published_by_id = endpoint_id
        ps_msg.topic_id = topic.id
        ps_msg.topic_name = topic.name
        ps_msg.cluster_id = self.server.cluster_id
        ps_msg.has_gd = has_gd
        ps_msg.ext_client_id = ext_client_id
        ps_msg.ext_pub_time = ext_pub_time
        ps_msg.group_id = input.get('group_id') or None
        ps_msg.position_in_group = input.get('position_in_group') or None
        ps_msg.is_in_sub_queue = has_subs

        if ps_msg.data:
            ps_msg.size = len(ps_msg.data.encode('utf8')) # We need to store the size in bytes rather than Unicode codepoints
        else:
            ps_msg.size = 0

        # Invoke hook service here because it may want to update data in which case
        # we need to take it into account below.
        if topic.before_publish_hook_service_invoker:
            response = topic.before_publish_hook_service_invoker(topic, ps_msg)

            # Hook service decided that we should not process this message
            if response['hook_action'] == _skip:
                logger_audit.info('Skipping message pub_msg_id:`%s`, pub_correl_id:`%s`, ext_client_id:`%s`',
                    ps_msg.pub_msg_id, ps_msg.pub_correl_id, ps_msg.ext_client_id)
                return

        # These are needed only for GD messages that are stored in SQL
        if has_gd:
            data_prefix, data_prefix_short = self._get_data_prefixes(ps_msg.data)
            ps_msg.data_prefix = data_prefix
            ps_msg.data_prefix_short = data_prefix_short

        return ps_msg

# ################################################################################################################################

    def _get_messages_from_data(self, topic, data_list, input, now, pattern_matched, endpoint_id, has_subs):

        # List of messages with GD enabled
        gd_msg_list = []

        # List of messages without GD enabled
        non_gd_msg_list = []

        # List of all message IDs - in the same order as messages were given on input
        msg_id_list = []

        if data_list and isinstance(data_list, (list, tuple)):
            for elem in data_list:
                msg = self._get_message(topic, elem, now, pattern_matched, endpoint_id, has_subs)
                if msg:
                    msg_id_list.append(msg.pub_msg_id)
                    msg_as_dict = msg.to_dict()
                    target_list = gd_msg_list if msg.has_gd else non_gd_msg_list
                    target_list.append(msg_as_dict)
        else:
            msg = self._get_message(topic, input, now, pattern_matched, endpoint_id, has_subs)
            if msg:
                msg_id_list.append(msg.pub_msg_id)
                msg_as_dict = msg.to_dict()
                target_list = gd_msg_list if msg.has_gd else non_gd_msg_list
                target_list.append(msg_as_dict)

        return msg_id_list, gd_msg_list, non_gd_msg_list

# ################################################################################################################################

    def _notify_pubsub_tasks(self, topic_id, topic_name, subscriptions, non_gd_msg_list, has_gd_msg_list):
        try:
            self.invoke('zato.pubsub.after-publish', {
                'cid': self.cid,
                'topic_id':topic_id,
                'topic_name':topic_name,
                'subscriptions': subscriptions,
                'non_gd_msg_list': non_gd_msg_list,
                'has_gd_msg_list': has_gd_msg_list,
                'is_bg_call': False, # This is not a background call, i.e. we are being called by a pub/sub client
            })
        except Exception:
            self.logger.warn('Could not notify pub/sub tasks, e:`%s`', format_exc())

# ################################################################################################################################

    def get_pattern_matched(self, endpoint_id, input):
        """ Returns a publication pattern matched that allows the endpoint to publish messages
        or raises an exception if no pattern was matched. Takes into account various IDs possibly given on input,
        depending on what our caller wanted to provide.
        """
        pubsub = self.server.worker_store.pubsub
        security_id = input.security_id or None
        ws_channel_id = input.ws_channel_id or None

        if not endpoint_id:

            if security_id:
                endpoint_id = pubsub.get_endpoint_id_by_sec_id(security_id)
            elif ws_channel_id:
                endpoint_id = pubsub.get_endpoint_id_by_ws_channel_id(ws_channel_id)
            else:
                raise NotImplementedError('To be implemented')

            kwargs = {'security_id':security_id} if security_id else {'ws_channel_id':ws_channel_id}
            pattern_matched = pubsub.is_allowed_pub_topic(input.topic_name, **kwargs)

        else:
            pattern_matched = pubsub.is_allowed_pub_topic_by_endpoint_id(input.topic_name, endpoint_id)

        # Not allowed, raise an exception in that case
        if not pattern_matched:
            raise Forbidden(self.cid)

        # Alright, we are in
        return endpoint_id, pattern_matched

# ################################################################################################################################

    def handle(self):

        input = self.request.input
        pubsub = self.server.worker_store.pubsub # type: PubSub
        endpoint_id = input.endpoint_id

        # Will return publication pattern matched or raise an exception that we don't catch
        endpoint_id, pattern_matched = self.get_pattern_matched(endpoint_id, input)

        try:
            topic = pubsub.get_topic_by_name(input.topic_name) # type: Topic
        except KeyError:
            raise NotFound(self.cid, 'No such topic `{}`'.format(input.topic_name))

        # We always count time in milliseconds since UNIX epoch
        now = utcnow_as_ms()

        # Get all subscribers for that topic from local worker store
        subscriptions_by_topic = pubsub.get_subscriptions_by_topic(topic.name)

        # If input.data is a list, it means that it is a list of messages, each of which has its own
        # metadata. Otherwise, it's a string to publish and other input parameters describe it.
        data_list = input.data_list if input.data_list else None

        # Input messages may contain a mix of GD and non-GD messages, and we need to extract them separately.
        msg_id_list, gd_msg_list, non_gd_msg_list = self._get_messages_from_data(
            topic, data_list, input, now, pattern_matched, endpoint_id, bool(subscriptions_by_topic))

        # Create a wrapper object for all the input data and metadata
        ctx = PubCtx(self.server.cluster_id, pubsub, topic, endpoint_id, subscriptions_by_topic, msg_id_list, gd_msg_list,
            non_gd_msg_list, pattern_matched, input.get('ext_client_id') or 'n/a', False, now)

        # We have all the input data, publish the message(s) now
        self._publish(ctx)

# ################################################################################################################################

    def _cleanup_sql_data(self, session, cluster_id, topic_id, now):
        delete_msg_delivered(session, cluster_id, topic_id)
        delete_msg_expired(session, cluster_id, topic_id, now)
        delete_enq_delivered(session, cluster_id, topic_id)
        delete_enq_marked_deleted(session, cluster_id, topic_id)

# ################################################################################################################################

    # def _publish(self, pubsub, topic, endpoint_id, subscriptions_by_topic, msg_id_list, gd_msg_list, non_gd_msg_list,
    #     pattern_matched, ext_client_id, is_re_run, now):

    def _publish(self, ctx):
        # Type: PubCtx
        """ Publishes GD and non-GD messages to topics and, if subscribers exist, moves them to their queues / notifies them.
        """
        len_gd_msg_list = len(ctx.gd_msg_list)
        has_gd_msg_list = bool(len_gd_msg_list)

        # Just so it is not overlooked, log information that no subscribers are found for this topic
        if not ctx.subscriptions_by_topic:
            self.logger.warn('No subscribers found for topic `%s` (cid:%s, re-run:%s)', ctx.topic.name, self.cid, ctx.is_re_run)

        # Local aliases
        has_pubsub_audit_log = self.server.has_pubsub_audit_log

        # We don't always have GD messages on input so there is no point in running an SQL transaction otherwise.
        if has_gd_msg_list:

            with closing(self.odb.session()) as session:

                # Increase depth check counter..
                ctx.topic.incr_msg_pub_iter()

                # Increase message cleanup counter ..

                # No matter if we can publish or not, we may possibly cleanup old messages first.
                if ctx.topic.needs_msg_cleanup():
                    self._cleanup_sql_data(session, ctx.cluster_id, ctx.topic.id, ctx.now)

                # .. test first if we should check the depth in this iteration.
                if ctx.topic.needs_depth_check():

                    # Get current depth of this topic ..
                    ctx.current_depth = get_gd_depth_topic(session, ctx.cluster_id, ctx.topic.id)

                    # .. and abort if max depth is already reached.
                    if ctx.current_depth + len_gd_msg_list > ctx.topic.max_depth_gd:
                        self.reject_publication(ctx.topic.name, True)
                    else:

                        # This only updates the local ctx variable
                        ctx.current_depth = ctx.current_depth + len_gd_msg_list

                # This is the call that runs SQL INSERT statements with messages for topics and subscriber queues
                sql_publish_with_retry(session, self.cid, ctx.cluster_id, ctx.topic.id, ctx.subscriptions_by_topic,
                    ctx.gd_msg_list, ctx.now)

                # Run an SQL commit for all queries above ..
                session.commit()

            # .. and set a flag to signal that there are some GD messages available
            ctx.pubsub.set_sync_has_msg(ctx.topic.id, True, True, ctx.now)

        # Either commit succeeded or there were no GD messages on input but in both cases we can now,
        # optionally, store data in pub/sub audit log.
        if has_pubsub_audit_log:

            msg = 'Message published. CID:`%s`, topic:`%s`, from:`%s`, ext_client_id:`%s`, pattern:`%s`, new_depth:`%s`' \
                  ', GD data:`%s`, non-GD data:`%s`'

            logger_audit.info(msg, self.cid, ctx.topic.name, self.pubsub.endpoints[ctx.endpoint_id].name,
                ctx.ext_client_id, ctx.pattern_matched, ctx.current_depth, ctx.gd_msg_list, ctx.non_gd_msg_list)

        # If this is the very first time we are running during this invocation, try to deliver non-GD messages
        if not ctx.is_re_run:

            if ctx.subscriptions_by_topic:

                # Place all the non-GD messages in the in-RAM sync backlog
                if ctx.non_gd_msg_list:
                    ctx.pubsub.store_in_ram(self.cid, ctx.topic.id, ctx.topic.name,
                        [item.sub_key for item in ctx.subscriptions_by_topic], ctx.non_gd_msg_list)

            # .. however, if there are no subscriptions at the moment while there are non-GD messages,
            # we need to re-run again and publish all such messages as GD ones. This is because if there
            # are no subscriptions, we do not know to what delivery server they should go, so it's safest
            # to store them in SQL.
            else:
                if ctx.non_gd_msg_list:

                    # Turn all non-GD messages into GD ones.
                    for msg in ctx.non_gd_msg_list:
                        msg['has_gd'] = True

                        data_prefix, data_prefix_short = self._get_data_prefixes(msg['data'])
                        msg['data_prefix'] = data_prefix
                        msg['data_prefix_short'] = data_prefix_short

                    # Note the reversed order - now non-GD messages are sent as GD ones and the list of non-GD messages is empty.
                    ctx.gd_msg_list = ctx.non_gd_msg_list
                    ctx.non_gd_msg_list[:] = []
                    ctx.is_re_run = True

                    # Re-run with GD and non-GD reversed now
                    self._publish(ctx)

        # Update metadata in background
        spawn(self._update_pub_metadata, ctx)

        # Return either a single msg_id if there was only one message published or a list of message IDs,
        # one for each message published.
        len_msg_list = len_gd_msg_list + len(ctx.non_gd_msg_list)

        if len_msg_list == 1:
            self.response.payload.msg_id = ctx.msg_id_list[0]
        else:
            self.response.payload.msg_id_list = ctx.msg_id_list

# ################################################################################################################################

    def reject_publication(self, topic_name, is_gd):
        """ Raises an exception to indicate that a publication was rejected.
        """
        raise ServiceUnavailable(self.cid,
            'Publication rejected - would exceed {} max depth for `{}`'.format('GD' if is_gd else 'non-GD', topic_name))

# ################################################################################################################################

    def _update_pub_metadata(self, ctx, _optional=('pub_correl_id', 'ext_client_id', 'in_reply_to'), _topic_key=_meta_topic_key,
        _endpoint_key=_meta_endpoint_key):
        """ Updates in background metadata about a topic and publisher after each publication.
        """
        try:
            last_pub_msg_id = ctx.last_msg['pub_msg_id']

            topic_key = _topic_key % (ctx.cluster_id, ctx.topic.id)
            endpoint_key = _endpoint_key % (ctx.cluster_id, ctx.endpoint_id)

            # For endpoint_key, there is a superfluous key here, (already in the key itself), but it will not hurt that much
            data = {
                'pub_time': ctx.now,
                'endpoint_id': ctx.endpoint_id,
                'pub_msg_id': last_pub_msg_id,
                'pattern_matched': ctx.pattern_matched
            }

            for name in _optional:
                value = ctx.last_msg.get(name)
                if value:
                    data[name] = value

            self.kvdb.conn.hmset(topic_key, data)
            self.kvdb.conn.hmset(endpoint_key, data)

        except Exception:
            self.logger.warn('Error while updating pub metadata `%s`', format_exc())

# ################################################################################################################################
