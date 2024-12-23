# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from dataclasses import dataclass
from logging import DEBUG, getLogger
from operator import itemgetter
from traceback import format_exc

# ciso8601 / dateparser
try:
    from ciso8601 import parse_datetime_as_naive
except ImportError:
    from dateparser.parser import parse as parse_datetime_as_naive # type: ignore

# gevent
from gevent import spawn

# typing-extensions
from typing_extensions import TypeAlias

# Zato
from zato.common.api import PUBSUB, ZATO_NONE
from zato.common.exception import Forbidden, NotFound, ServiceUnavailable
from zato.common.json_ import dumps as json_dumps
from zato.common.marshal_.api import Model
from zato.common.odb.query.pubsub.publish import sql_publish_with_retry
from zato.common.odb.query.pubsub.topic import get_gd_depth_topic
from zato.common.pubsub import new_msg_id, PubSubMessage
from zato.common.typing_ import any_, anydict, anydictnone, anylistnone, anynone, boolnone, cast_, dict_field, intnone, \
    list_field, strlistnone, strnone
from zato.common.util.pubsub import get_expiration, get_priority
from zato.common.util.sql import set_instance_opaque_attrs
from zato.common.util.time_ import datetime_from_ms, datetime_to_ms, utcnow_as_ms

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.marshal_.api import MarshalAPI
    from zato.common.typing_ import anylist, callable_, dictlist, strlist, tuple_
    from zato.server.base.parallel import ParallelServer
    from zato.server.pubsub import PubSub, Topic
    from zato.server.pubsub.model import sublist
    from zato.server.service import Service
    dictlist = dictlist
    strlist = strlist
    sublist = sublist
    Service = Service

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')
logger_pubsub = getLogger('zato_pubsub.srv')
logger_audit = getLogger('zato_pubsub_audit')

has_logger_pubsub_debug = logger_pubsub.isEnabledFor(DEBUG)

# ################################################################################################################################
# ################################################################################################################################

PublicationResult:TypeAlias = 'str | strlist | None'

# ################################################################################################################################
# ################################################################################################################################

_initialized = str(PUBSUB.DELIVERY_STATUS.INITIALIZED)

_meta_topic_key = PUBSUB.REDIS.META_TOPIC_LAST_KEY
_meta_endpoint_key = PUBSUB.REDIS.META_ENDPOINT_PUB_KEY
_meta_topic_optional = ('pub_correl_id', 'ext_client_id', 'in_reply_to')
_meta_sort_key = itemgetter('pub_time', 'ext_pub_time')

_log_turning_gd_msg = 'Turning message `%s` into a GD one ({})'
_inserting_gd_msg = 'Inserting GD messages for topic `%s` `%s` published by `%s` (ext:%s) (cid:%s)'

# ################################################################################################################################
# ################################################################################################################################

class _GetMessage:
    _skip = PUBSUB.HOOK_ACTION.SKIP
    _default_pri = PUBSUB.PRIORITY.DEFAULT
    _opaque_only = PUBSUB.DEFAULT.SK_OPAQUE
    _float_str = PUBSUB.FLOAT_STRING_CONVERT
    _zato_mime_type = PUBSUB.MIMEType.Zato

# ################################################################################################################################
# ################################################################################################################################

class PubCtx:
    """ A container for information describing a single publication.
    """
    def __init__(
        self,
        *,
        cid: 'str',
        cluster_id: 'int',
        pubsub: 'PubSub',
        topic: 'Topic',
        endpoint_id: 'int',
        endpoint_name: 'str',
        subscriptions_by_topic: 'sublist',
        msg_id_list: 'anylist',
        gd_msg_list: 'anylist',
        non_gd_msg_list: 'anylist',
        pub_pattern_matched: 'str',
        ext_client_id: 'str',
        is_first_run: 'bool',
        now: 'float',
        is_wsx: 'bool',
        service_invoke_func: 'callable_',
        new_session_func: 'callable_',
    ) -> 'None':

        self.cid = cid
        self.cluster_id = cluster_id
        self.pubsub = pubsub
        self.topic = topic
        self.endpoint_id = endpoint_id
        self.endpoint_name = endpoint_name
        self.subscriptions_by_topic = subscriptions_by_topic
        self.msg_id_list = msg_id_list
        self.gd_msg_list = gd_msg_list
        self.non_gd_msg_list = non_gd_msg_list
        self.pub_pattern_matched = pub_pattern_matched
        self.ext_client_id = ext_client_id
        self.is_first_run = is_first_run
        self.now = now
        self.is_wsx = is_wsx
        self.service_invoke_func = service_invoke_func
        self.new_session_func = new_session_func
        self.current_depth = 0

        # Make sure we have the expected lists on input.
        if not (self.gd_msg_list or self.non_gd_msg_list):
            raise ValueError('At least one of gd_msg_list or non_gd_msg_list must be provided')

        # We can now extract the last message for later use by our callers.
        self.last_msg = self.gd_msg_list[-1] if self.gd_msg_list else self.non_gd_msg_list[-1]

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PubRequest(Model):

    cid: str
    topic_name: str = ''
    pub_pattern_matched: str = ''

    msg_id:      strnone = ''
    correl_id:   strnone = None
    in_reply_to: strnone = None
    has_gd:      boolnone = None

    data:        anynone     = None
    data_list:   anylistnone = None

    priority:   intnone = PUBSUB.PRIORITY.DEFAULT
    expiration: intnone = PUBSUB.DEFAULT.EXPIRATION

    mime_type:  strnone = PUBSUB.DEFAULT.MIME_TYPE

    ext_client_id: strnone = ''
    ext_pub_time:  strnone = None

    security_id:   intnone = None
    security_name: strnone = None

    endpoint_id:   intnone = None
    endpoint_name: strnone = None

    ws_channel_id: intnone = None

    group_id:          strnone = ''
    position_in_group: intnone = PUBSUB.DEFAULT.PositionInGroup

    reply_to_sk:   strlistnone = list_field()
    deliver_to_sk: strlistnone = list_field()

    user_ctx:      anynone    = None
    zato_ctx:      anydictnone = dict_field()

# ################################################################################################################################
# ################################################################################################################################

class Publisher:
    """ Actual implementation of message publishing exposed through other services to the outside world.
    """
    pubsub: 'PubSub'
    server: 'ParallelServer'
    marshal_api: 'MarshalAPI'
    service_invoke_func: 'callable_'
    new_session_func: 'callable_'

    def __init__(
        self,
        *,
        pubsub: 'PubSub',
        server: 'ParallelServer',
        marshal_api: 'MarshalAPI',
        service_invoke_func: 'callable_',
        new_session_func: 'callable_'
    ) -> 'None':
        self.pubsub = pubsub
        self.server = server
        self.marshal_api = marshal_api
        self.service_invoke_func = service_invoke_func
        self.new_session_func = new_session_func

# ################################################################################################################################

    def get_data_prefixes(self, data:'str') -> 'tuple_[str, str]':
        data_prefix = data[:self.pubsub.data_prefix_len]
        data_prefix_short = data[:self.pubsub.data_prefix_short_len]

        return data_prefix, data_prefix_short

# ################################################################################################################################

    def build_message(
        self,
        topic:'Topic',
        request:'PubRequest',
        now:'float',
        pub_pattern_matched:'str',
        endpoint_id:'int',
        subscriptions_by_topic:'sublist',
        has_no_sk_server:'bool'
    ) -> 'PubSubMessage | None':

        priority = get_priority(request.cid, request.priority)

        # So as not to send it to SQL if it is a default value anyway = less overhead = better performance
        if priority == _GetMessage._default_pri:
            priority = None

        expiration = get_expiration(request.cid, request.expiration, topic.limit_message_expiry)
        expiration_time = now + expiration

        pub_msg_id = request.msg_id or new_msg_id()

        # If there is at least one WSX subscriber to this topic which is not connected at the moment,
        # which means it has no delivery server, we uncoditionally turn this message into a GD one ..
        if has_no_sk_server:
            has_gd = True
            logger_pubsub.info(_log_turning_gd_msg.format('no SK server'), pub_msg_id)

        # .. otherwise, use request GD value or the default per topic.
        else:
            has_gd = request.has_gd
            if has_gd not in (None, '', ZATO_NONE):
                if not isinstance(has_gd, bool): # type: ignore
                    raise ValueError('Input has_gd is not a bool (found:`{}`)'.format(repr(has_gd)))
            else:
                has_gd = topic.has_gd

        pub_correl_id = request.correl_id
        in_reply_to = request.in_reply_to
        ext_client_id = request.ext_client_id
        mime_type = request.mime_type

        ext_pub_time = request.ext_pub_time or None
        if ext_pub_time:
            ext_pub_time = parse_datetime_as_naive(ext_pub_time) # type: ignore
            ext_pub_time = datetime_to_ms(ext_pub_time) / 1000.0 # type: ignore

        pub_correl_id = pub_correl_id if pub_correl_id else None
        in_reply_to = in_reply_to if in_reply_to else None
        ext_client_id = ext_client_id if ext_client_id else ''
        mime_type = mime_type if mime_type else PUBSUB.DEFAULT.MIME_TYPE
        reply_to_sk = request.reply_to_sk
        deliver_to_sk = request.deliver_to_sk

        user_ctx = request.user_ctx or None
        zato_ctx = request.zato_ctx or {}

        ps_msg = PubSubMessage()
        ps_msg.topic = topic
        ps_msg.pub_msg_id = pub_msg_id
        ps_msg.pub_correl_id = pub_correl_id
        ps_msg.in_reply_to = in_reply_to

        # Convert to string to prevent pg8000 from rounding up float values.
        # Note that the model says these fields are floats and this is why we ignore the type warnings in this case.
        ps_msg.pub_time = _GetMessage._float_str.format(now)
        ps_msg.ext_pub_time = _GetMessage._float_str.format(ext_pub_time) if ext_pub_time else ext_pub_time

        # If the data published is not a string or object, we need to serialise it to JSON
        # so as to be able to save it in the database - a delivery task will later
        # need to de-serialise it.
        data = request.data
        if not isinstance(data, (str, bytes)):
            data = json_dumps(data)
            zato_ctx['zato_mime_type'] = _GetMessage._zato_mime_type

        zato_ctx = json_dumps(zato_ctx)

        ps_msg.delivery_status = _initialized
        ps_msg.pub_pattern_matched = pub_pattern_matched
        ps_msg.data = data
        ps_msg.mime_type = mime_type
        ps_msg.priority = priority # type: ignore
        ps_msg.expiration = expiration
        ps_msg.expiration_time = expiration_time
        ps_msg.published_by_id = endpoint_id
        ps_msg.topic_id = topic.id
        ps_msg.topic_name = topic.name
        ps_msg.cluster_id = self.server.cluster_id
        ps_msg.has_gd = has_gd
        ps_msg.ext_client_id = ext_client_id
        ps_msg.group_id = request.group_id or None
        ps_msg.position_in_group = request.position_in_group or PUBSUB.DEFAULT.PositionInGroup
        ps_msg.is_in_sub_queue = bool(subscriptions_by_topic)
        ps_msg.reply_to_sk = reply_to_sk # type: ignore
        ps_msg.deliver_to_sk = deliver_to_sk # type: ignore
        ps_msg.user_ctx = user_ctx
        ps_msg.zato_ctx = zato_ctx

        # Opaque attributes - we only need reply to sub_keys to be placed in there
        # but we do not do it unless we known that any such sub key was actually requested.
        if reply_to_sk or deliver_to_sk:
            set_instance_opaque_attrs(ps_msg, request.to_dict(), only=_GetMessage._opaque_only)

        # If there are any subscriptions for the topic this message was published to, we want to establish
        # based on what subscription pattern each subscriber will receive the message.
        for sub in subscriptions_by_topic:
            ps_msg.sub_pattern_matched[sub.sub_key] = sub.sub_pattern_matched

        if ps_msg.data:
            # We need to store the size in bytes rather than Unicode codepoints
            ps_msg.size = len(ps_msg.data if isinstance(ps_msg.data, bytes) else ps_msg.data.encode('utf8'))
        else:
            ps_msg.size = 0

        # Invoke hook service here because it may want to update data in which case
        # we need to take it into account below.
        if topic.before_publish_hook_service_invoker:
            response = topic.before_publish_hook_service_invoker(topic, ps_msg)

            # Hook service decided that we should not process this message
            if response.get('hook_action') == _GetMessage._skip:
                logger_audit.info('Skipping message pub_msg_id:`%s`, pub_correl_id:`%s`, ext_client_id:`%s`',
                    ps_msg.pub_msg_id, ps_msg.pub_correl_id, ps_msg.ext_client_id)
                return None

        # These are needed only for GD messages that are stored in SQL
        if has_gd:
            data_prefix, data_prefix_short = self.get_data_prefixes(cast_('str', ps_msg.data))
            ps_msg.data_prefix = data_prefix
            ps_msg.data_prefix_short = data_prefix_short

        return ps_msg

# ################################################################################################################################

    def get_messages_from_data(
        self,
        *,
        cid:'str',
        topic:'Topic',
        data_list:'any_',
        request:'PubRequest',
        now:'float',
        pub_pattern_matched:'str',
        endpoint_id:'int',
        subscriptions_by_topic:'sublist',
        has_no_sk_server:'bool'
    ) -> 'tuple_[anylist, ...]':

        # List of messages with GD enabled
        gd_msg_list = [] # type: anylist

        # List of messages without GD enabled
        non_gd_msg_list = [] # type: anylist

        # List of all message IDs - in the same order as messages were given on request
        msg_id_list = [] # type: anylist

        if data_list and isinstance(data_list, (list, tuple)):
            # Cast it to a list so that its type is known to type checkers
            data_list = cast_('anylist', data_list)
            for elem in data_list:
                elem = self.marshal_api.from_dict(cast_('Service', None), elem, PubRequest, extra={'cid':cid})
                msg = self.build_message(topic, elem, now, pub_pattern_matched, endpoint_id, subscriptions_by_topic,
                    has_no_sk_server)
                if msg:
                    msg_id_list.append(msg.pub_msg_id)
                    msg_as_dict = msg.to_dict()
                    target_list = gd_msg_list if msg.has_gd else non_gd_msg_list
                    target_list.append(msg_as_dict)
        else:
            msg = self.build_message(topic, request, now, pub_pattern_matched, endpoint_id, subscriptions_by_topic,
                has_no_sk_server)

            if msg:
                msg_id_list.append(msg.pub_msg_id)
                msg_as_dict = msg.to_dict()
                target_list = gd_msg_list if msg.has_gd else non_gd_msg_list
                target_list.append(msg_as_dict)

        return msg_id_list, gd_msg_list, non_gd_msg_list

# ################################################################################################################################

    def _get_endpoint_id_by_security_name(self, security_name:'str') -> 'intnone':
        security = self.server.worker_store.basic_auth_get(security_name)
        security_config = security['config']
        security_id = security_config['id']
        endpoint_id = self.pubsub.get_endpoint_id_by_sec_id(security_id)
        return endpoint_id

# ################################################################################################################################

    def get_pub_pattern_matched(self, endpoint_id:'intnone', request:'PubRequest') -> 'tuple_[int, str]':
        """ Returns a publication pattern matched that allows the endpoint to publish messages
        or raises an exception if no pattern was matched. Takes into account various IDs possibly given on request,
        depending on what our caller wanted to provide.
        """
        security_id = request.security_id
        security_name = request.security_name

        ws_channel_id = request.ws_channel_id
        endpoint_name = request.endpoint_name

        #
        # Note that if we have security name on input, it will take precedence over input security ID.
        #
        if security_name:
            endpoint_id = self._get_endpoint_id_by_security_name(security_name)

        #
        # Again, the name of the endpoint takes precedence over its ID
        #
        if endpoint_name:
            endpoint = self.pubsub.get_endpoint_by_name(endpoint_name)
            endpoint_id = endpoint.id

        if not endpoint_id:

            if security_id:
                endpoint_id = self.pubsub.get_endpoint_id_by_sec_id(security_id)

            elif ws_channel_id:
                endpoint_id_by_wsx_id = self.pubsub.get_endpoint_id_by_ws_channel_id(ws_channel_id)
                if endpoint_id_by_wsx_id:
                    endpoint_id = endpoint_id_by_wsx_id
                else:
                    raise Exception('Could not find endpoint by WSX channel ID -> `%s`', ws_channel_id)
            else:
                raise Exception('Either security_id or ws_channel_id is required if there is no endpoint_id')

            kwargs = {'security_id':security_id} if security_id else {'ws_channel_id':ws_channel_id}
            pub_pattern_matched = self.pubsub.is_allowed_pub_topic(request.topic_name, **kwargs)

        else:
            pub_pattern_matched = self.pubsub.is_allowed_pub_topic_by_endpoint_id(request.topic_name, endpoint_id)

        # Not allowed, raise an exception in that case
        if not pub_pattern_matched:
            logger.warning('No pub pattern matched topic `%s` and endpoint `%s` (#2)',
                request.topic_name, self.pubsub.get_endpoint_by_id(endpoint_id).name)
            raise Forbidden(request.cid)

        # Alright, we are in
        pub_pattern_matched = cast_('str', pub_pattern_matched)
        return endpoint_id, pub_pattern_matched

# ################################################################################################################################

    def run_from_dict(self, cid:'str', data:'anydict') -> 'PublicationResult':
        request = self.marshal_api.from_dict(cast_('Service', None), data, PubRequest, extra={'cid':cid}) # type: PubRequest
        return self.run(request)

# ################################################################################################################################

    def run(self, request:'PubRequest') -> 'PublicationResult':

        endpoint_id = request.endpoint_id

        # Will return publication pattern matched or raise an exception that we don't catch
        endpoint_id, pub_pattern_matched = self.get_pub_pattern_matched(endpoint_id, request)

        try:
            topic = self.pubsub.get_topic_by_name(request.topic_name) # type: Topic
        except KeyError:
            raise NotFound(request.cid, 'No such topic `{}`'.format(request.topic_name))

        # Reject the message is topic is not active
        if not topic.is_active:
            raise ServiceUnavailable(request.cid, 'Topic is inactive `{}`'.format(request.topic_name))

        # We always count time in milliseconds since UNIX epoch
        now = utcnow_as_ms()

        # Get all subscribers for that topic from local worker store
        all_subscriptions_by_topic = self.pubsub.get_subscriptions_by_topic(topic.name)
        len_all_sub = len(all_subscriptions_by_topic)

        # If we are to deliver the message(s) to only selected subscribers only,
        # filter out any unwated ones first.
        if request.deliver_to_sk:

            has_all = False
            subscriptions_by_topic = []

            # Get any matching subscriptions out of the whole set
            for sub in all_subscriptions_by_topic:
                if sub.sub_key in request.deliver_to_sk:
                    subscriptions_by_topic.append(sub)

        else:
            # We deliver this message to all of the topic's subscribers
            has_all = True
            subscriptions_by_topic = all_subscriptions_by_topic

        # This is only for logging purposes
        _subs_found = []

        # Assume that there are no missing servers for WSX clients by default
        has_no_sk_server = False

        for sub in subscriptions_by_topic:

            # Prepare data for logging
            _subs_found.append({sub.sub_key: sub.sub_pattern_matched})

            # Is there at least one WSX subscriber to this topic that is currently not connected?
            # If so, later on we will need to turn all the messages into GD ones.
            sk_server = self.pubsub.get_sub_key_server(sub.sub_key)
            if not sk_server:
                if has_logger_pubsub_debug:
                    logger_pubsub.debug('No sk_server for sub_key `%s` among `%s`', sub.sub_key,
                        sorted(self.pubsub.sub_key_servers.keys()))

                # We have found at least one subscriber that has no server
                # (E.g. this is a WSX that is not currently connected).
                has_no_sk_server = True

        if has_logger_pubsub_debug:
            logger_pubsub.debug('Subscriptions for topic `%s` `%s` (a:%d, %d/%d, cid:%s)',
                topic.name, _subs_found, has_all, len(subscriptions_by_topic), len_all_sub, request.cid)

        # If request.data is a list, it means that it is a list of messages, each of which has its own
        # metadata. Otherwise, it's a string to publish and other request parameters describe it.
        data_list = request.data_list if request.data_list else None

        # Input messages may contain a mix of GD and non-GD messages, and we need to extract them separately.
        msg_id_list, gd_msg_list, non_gd_msg_list = self.get_messages_from_data(
            cid = request.cid,
            topic = topic,
            data_list = data_list,
            request = request,
            now = now,
            pub_pattern_matched = pub_pattern_matched,
            endpoint_id = endpoint_id,
            subscriptions_by_topic = subscriptions_by_topic,
            has_no_sk_server = has_no_sk_server
        )

        # Create a wrapper object for all the request data and metadata
        is_wsx = bool(request.ws_channel_id)
        ctx = PubCtx(
            cid = request.cid,
            cluster_id = self.server.cluster_id,
            pubsub = self.pubsub,
            topic = topic,
            endpoint_id = endpoint_id,
            endpoint_name = self.pubsub.get_endpoint_by_id(endpoint_id).name,
            subscriptions_by_topic = subscriptions_by_topic,
            msg_id_list = msg_id_list,
            gd_msg_list = gd_msg_list,
            non_gd_msg_list = non_gd_msg_list,
            pub_pattern_matched = pub_pattern_matched,
            ext_client_id = request.ext_client_id or '',
            is_first_run = True,
            now = now,
            is_wsx = is_wsx,
            service_invoke_func = self.service_invoke_func,
            new_session_func = self.new_session_func,
        )

        # We have all the request data, publish the message(s) now
        return self._publish(ctx)

# ################################################################################################################################

    def _build_response(self, len_gd_msg_list:'int', ctx:'PubCtx') -> 'PublicationResult':
        """ Return either a single msg_id if there was only one message published or a list of message IDs,
        one for each message published.
        """
        len_msg_list = len_gd_msg_list + len(ctx.non_gd_msg_list)

        if len_msg_list == 1:
            out = ctx.msg_id_list[0]
        else:
            out = ctx.msg_id_list

        return out

# ################################################################################################################################

    def _publish(self, ctx:'PubCtx') -> 'PublicationResult':
        """ Publishes GD and non-GD messages to topics and, if subscribers exist, moves them to their queues / notifies them.
        """
        len_gd_msg_list = len(ctx.gd_msg_list)
        has_gd_msg_list = bool(len_gd_msg_list)

        # Just so it is not overlooked, log information that no subscribers are found for this topic
        if not ctx.subscriptions_by_topic:

            log_msg = 'No matching subscribers found for topic `%s` (cid:%s, first:%d)'
            log_msg_args = ctx.topic.name, ctx.cid, ctx.is_first_run

            # There are no subscribers and depending on configuration we are to drop messages
            # for whom no one is waiting or continue and place them in the topic directly.
            if ctx.topic.config.get('on_no_subs_pub') == PUBSUB.ON_NO_SUBS_PUB.DROP.id:
                log_msg_drop = 'Dropping messages. ' + log_msg
                logger_pubsub.info(log_msg_drop, *log_msg_args)
                return None
            else:
                logger_pubsub.info(log_msg, *log_msg_args)

        # Local aliases
        has_pubsub_audit_log = self.server.has_pubsub_audit_log

        # Increase message counters for this pub/sub server and endpoint
        ctx.pubsub.incr_pubsub_msg_counter(ctx.endpoint_id)

        # Increase message counter for this topic
        ctx.topic.incr_topic_msg_counter(has_gd_msg_list, bool(ctx.non_gd_msg_list))

        # We don't always have GD messages on request so there is no point in running an SQL transaction otherwise.
        if has_gd_msg_list:

            with closing(ctx.new_session_func()) as session:

                # Test first if we should check the depth in this iteration.
                if ctx.topic.needs_depth_check():

                    # Get current depth of this topic ..
                    ctx.current_depth = get_gd_depth_topic(session, ctx.cluster_id, ctx.topic.id)

                    # .. and abort if max depth is already reached ..
                    if ctx.current_depth + len_gd_msg_list > ctx.topic.max_depth_gd:

                        # .. note thath is call raises an exception.
                        self.reject_publication(ctx.cid, ctx.topic.name, True)

                    else:

                        # This only updates the local ctx variable
                        ctx.current_depth = ctx.current_depth + len_gd_msg_list

                pub_msg_list = [elem['pub_msg_id'] for elem in ctx.gd_msg_list]

                if has_logger_pubsub_debug:
                    logger_pubsub.debug(_inserting_gd_msg, ctx.topic.name, pub_msg_list, ctx.endpoint_name,
                        ctx.ext_client_id, ctx.cid)

                # This is the call that runs SQL INSERT statements with messages for topics and subscriber queues
                _ = sql_publish_with_retry(

                    now = ctx.now,
                    cid = ctx.cid,
                    topic_id = ctx.topic.id,
                    topic_name = ctx.topic.name,
                    cluster_id = ctx.cluster_id,
                    pub_counter = self.server.get_pub_counter(),

                    session = session,
                    new_session_func = ctx.new_session_func,
                    before_queue_insert_func = None,

                    gd_msg_list = ctx.gd_msg_list,
                    subscriptions_by_topic = ctx.subscriptions_by_topic,
                    should_collect_ctx = False
                )

                # Run an SQL commit for all queries above ..
                session.commit()

                # .. increase the publication counter now that we have committed the messages ..
                self.server.incr_pub_counter()

            # .. and set a flag to signal that there are some GD messages available
            ctx.pubsub.set_sync_has_msg(
                topic_id = ctx.topic.id,
                is_gd = True,
                value = True,
                source = 'Publish.publish',
                gd_pub_time_max = ctx.now
            )

        # Either commit succeeded or there were no GD messages on request but in both cases we can now,
        # optionally, store data in pub/sub audit log.
        if has_pubsub_audit_log:

            log_msg = 'Message published. CID:`%s`, topic:`%s`, from:`%s`, ext_client_id:`%s`, pattern:`%s`, new_depth:`%s`' + \
                  ', GD data:`%s`, non-GD data:`%s`'

            logger_audit.info(log_msg, ctx.cid, ctx.topic.name, self.pubsub.endpoints[ctx.endpoint_id].name, # type: ignore
                ctx.ext_client_id, ctx.pub_pattern_matched, ctx.current_depth, ctx.gd_msg_list, ctx.non_gd_msg_list)

        # If this is the very first time we are running during this invocation, try to deliver non-GD messages
        if ctx.is_first_run:

            if ctx.subscriptions_by_topic:

                # Place all the non-GD messages in the in-RAM sync backlog
                if ctx.non_gd_msg_list:
                    ctx.pubsub.store_in_ram(ctx.cid, ctx.topic.id, ctx.topic.name,
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

                        logger_pubsub.info(_log_turning_gd_msg.format('no subscribers'), msg['pub_msg_id'])

                        data_prefix, data_prefix_short = self.get_data_prefixes(msg['data'])
                        msg['data_prefix'] = data_prefix
                        msg['data_prefix_short'] = data_prefix_short

                    # Note the reversed order - now non-GD messages are sent as GD ones and the list of non-GD messages is empty.
                    ctx.gd_msg_list = ctx.non_gd_msg_list[:]
                    ctx.non_gd_msg_list[:] = []
                    ctx.is_first_run = False

                    # Re-run with GD and non-GD reversed now
                    return self._publish(ctx)

        # Update topic and endpoint metadata in background if configured to - we have a series of if's to confirm
        # if it's needed because it is not a given that each publication will require the update and we also
        # want to ensure that if there are two thigns to be updated at a time, it is only one greenlet spawned
        # which will in turn use a single Redis pipeline to cut down on the number of Redis calls needed.
        if ctx.pubsub.has_meta_topic or ctx.pubsub.has_meta_endpoint:

            if ctx.pubsub.has_meta_topic and ctx.topic.needs_meta_update():
                has_topic = True
            else:
                has_topic = False

            if ctx.pubsub.has_meta_endpoint and ctx.pubsub.needs_endpoint_meta_update(ctx.endpoint_id):
                has_endpoint = True
            else:
                has_endpoint = False

            if has_topic or has_endpoint:
                _ = spawn(self.update_pub_metadata, ctx, has_topic, has_endpoint,
                    ctx.pubsub.endpoint_meta_data_len, ctx.pubsub.endpoint_meta_max_history)

        # Build and return a response for our caller.
        out = self._build_response(len_gd_msg_list, ctx)
        return out

# ################################################################################################################################

    def reject_publication(self, cid:'str', topic_name:'str', is_gd:'bool') -> 'None':
        """ Raises an exception to indicate that a publication was rejected.
        """
        raise ServiceUnavailable(cid,
            'Publication rejected - would exceed {} max depth for `{}`'.format('GD' if is_gd else 'non-GD', topic_name))

# ################################################################################################################################

    def update_pub_metadata(
        self,
        ctx:'PubCtx',
        has_topic:'bool',
        has_endpoint:'bool',
        endpoint_data_len:'int',
        endpoint_max_history:'int'
    ) -> 'None':
        """ Updates in background metadata about a topic and/or publisher.
        """
        try:

            # For later use
            dt_now = datetime_from_ms(ctx.now * 1000)

            # This is optional
            ext_pub_time = ctx.last_msg.get('ext_pub_time')
            if ext_pub_time:
                if isinstance(ext_pub_time, str):
                    ext_pub_time = float(ext_pub_time)
                ext_pub_time = datetime_from_ms(ext_pub_time * 1000)

            # Prepare a document to update the topic's metadata with
            if has_topic:
                topic_key = _meta_topic_key % (ctx.cluster_id, ctx.topic.id)
                topic_data = {
                    'pub_time': dt_now,
                    'topic_id': ctx.topic.id,
                    'endpoint_id': ctx.endpoint_id,
                    'endpoint_name': ctx.endpoint_name,
                    'pub_msg_id': ctx.last_msg['pub_msg_id'],
                    'pub_pattern_matched': ctx.pub_pattern_matched,
                    'has_gd': ctx.last_msg['has_gd'],
                    'server_name': self.server.name,
                    'server_pid': self.server.pid,
                }

                for name in _meta_topic_optional:
                    value = ctx.last_msg.get(name)
                    if value:
                        topic_data[name] = value

                # Store data in RAM
                self.server.pub_sub_metadata.set(topic_key, topic_data)

            # Prepare a request to udpate the endpoint's metadata with
            if has_endpoint:
                endpoint_key = _meta_endpoint_key % (ctx.cluster_id, ctx.endpoint_id)

                idx_found = None
                endpoint_topic_list = self.server.pub_sub_metadata.get(endpoint_key) or []
                endpoint_topic_list = cast_('dictlist', endpoint_topic_list)

                # If we already have something stored in RAM, find information about this topic and remove it
                # to make room for the newest entry.
                if endpoint_topic_list:
                    for idx, elem in enumerate(endpoint_topic_list):
                        if elem['topic_id'] == ctx.topic.id:
                            idx_found = idx
                            break
                    if idx_found is not None:
                        _ = endpoint_topic_list.pop(idx_found)

                # Newest information about this endpoint's publication to this topic
                endpoint_data = {
                    'pub_time': dt_now,
                    'pub_msg_id': ctx.last_msg['pub_msg_id'],
                    'pub_correl_id': ctx.last_msg.get('pub_correl_id'),
                    'in_reply_to': ctx.last_msg.get('in_reply_to'),
                    'ext_client_id': ctx.last_msg.get('ext_client_id'),
                    'ext_pub_time': ext_pub_time,
                    'pub_pattern_matched': ctx.pub_pattern_matched,
                    'topic_id': ctx.topic.id,
                    'topic_name': ctx.topic.name,
                    'has_gd': ctx.last_msg['has_gd'],
                }

                # Storing actual data along with other information is optional
                data = ctx.last_msg['data'][:endpoint_data_len] if endpoint_data_len else None
                endpoint_data['data'] = data

                # Append the newest entry and sort all results by publication time
                endpoint_topic_list.append(endpoint_data)
                endpoint_topic_list.sort(key=_meta_sort_key, reverse=True)

                # Store only as many entries as configured to
                endpoint_topic_list = endpoint_topic_list[:endpoint_max_history]

                # Same as for topics, store data in RAM
                self.server.pub_sub_metadata.set(endpoint_key, endpoint_topic_list)

                # WSX connections update their SQL pub/sub metadata on their own because
                # each possibly handles multiple sub_keys. Other types of connections
                # update their SQL pub/sub metadata here.
                if not ctx.is_wsx:
                    request = {
                        'sub_key': [sub.sub_key for sub in ctx.subscriptions_by_topic],
                        'last_interaction_time': ctx.now,
                        'last_interaction_type': 'publish',
                        'last_interaction_details': 'publish',
                    }
                    ctx.service_invoke_func('zato.pubsub.subscription.update-interaction-metadata', request)

        except Exception:
            logger.warning('Error while updating pub metadata `%s`', format_exc())

# ################################################################################################################################
