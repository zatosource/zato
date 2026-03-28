# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64decode
from http.client import BAD_REQUEST, OK, UNAUTHORIZED
from logging import getLogger

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.util import validate_topic_name
from zato.common.util.auth import check_basic_auth
from zato.server.service import AsIs, Int, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_min_priority = PubSub.Message.Priority_Min
_max_priority = PubSub.Message.Priority_Max
_default_priority = PubSub.Message.Priority_Default
_default_expiration = PubSub.Message.Default_Expiration
_max_messages_default = 50
_max_len_default = 5_000_000

# ################################################################################################################################
# ################################################################################################################################

def extract_basic_auth_credentials(wsgi_environ:'anydict') -> 'tuple':
    """ Extracts username and password from HTTP Basic Auth header.
    """
    auth_header = wsgi_environ.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Basic '):
        return None, None

    try:
        encoded = auth_header[6:]
        decoded = b64decode(encoded).decode('utf-8')
        username, password = decoded.split(':', 1)
        return username, password
    except Exception:
        return None, None

# ################################################################################################################################
# ################################################################################################################################

class PubSubRESTService(Service):
    """ Base class for pub/sub REST services with common authentication.
    """

    suppress_internal_errors = True

    def before_handle(self) -> 'None':
        pass

    def after_handle(self) -> 'None':
        pass

    def authenticate(self) -> 'tuple':
        """ Extract and validate credentials. Returns (username, error_response) tuple.
        """
        username, password = extract_basic_auth_credentials(self.wsgi_environ)

        if not username:
            return None, ('Authentication required', UNAUTHORIZED)

        if not self._validate_credentials(username, password):
            return None, ('Invalid credentials', UNAUTHORIZED)

        return username, None

    def _validate_credentials(self, username:'str', password:'str') -> 'bool':
        """ Validate username/password against all basic auth security definitions.
        """
        basic_auth_config = self.server.worker_store.request_dispatcher.url_data.basic_auth_config
        auth_header = self.wsgi_environ.get('HTTP_AUTHORIZATION', '')

        for sec_def in basic_auth_config.values():
            config = sec_def.get('config', {})
            expected_username = config.get('username')
            expected_password = config.get('password')
            if expected_username and expected_password:
                result = check_basic_auth(self.cid, auth_header, expected_username, expected_password)
                if result is True:
                    return True
        return False

# ################################################################################################################################
# ################################################################################################################################

class Publish(PubSubRESTService):
    """ Publish a message to a topic.
    """
    name = 'pubsub.rest.publish'

    class SimpleIO:
        input_required = 'topic_name', AsIs('data')
        input_optional = 'priority', 'expiration', AsIs('correl_id'), AsIs('in_reply_to'), AsIs('ext_client_id'), 'pub_time'
        output_optional = AsIs('msg_id'), 'is_ok', 'cid', Int('status'), 'details'
        skip_empty_keys = True

# ################################################################################################################################

    def handle(self) -> 'None':

        # Local aliases
        cid = self.cid
        input = self.request.input

        # Authenticate
        username, error = self.authenticate()
        logger.info('Publish auth result: username=%s, error=%s', username, error)
        if error:
            self.response.payload.is_ok = False
            self.response.payload.cid = cid
            self.response.payload.details, self.response.payload.status = error
            return

        # Get topic name
        topic_name = input.topic_name
        logger.info('Publish request: username=%s, topic=%s', username, topic_name)

        # Validate topic name
        try:
            validate_topic_name(topic_name)
        except Exception as e:
            self.response.payload.is_ok = False
            self.response.payload.cid = cid
            self.response.payload.status = BAD_REQUEST
            self.response.payload.details = str(e)
            return

        # Check permissions
        logger.info('Checking permissions: username=%s, topic=%s, action=publish', username, topic_name)

        matcher = self.server.pubsub_pattern_matcher
        logger.info('Pattern matcher clients: %s', list(matcher._clients.keys()))

        client_perms = matcher._clients.get(username)
        if client_perms:
            logger.info('Client %s pub_patterns: %s', username, [p.pattern for p in client_perms.pub_patterns])
            logger.info('Client %s sub_patterns: %s', username, [p.pattern for p in client_perms.sub_patterns])
        else:
            logger.info('Client %s not found in matcher', username)

        permission_result = matcher.evaluate(username, topic_name, 'publish')
        logger.info('Permission result is_ok=%s, reason=%s', permission_result.is_ok, getattr(permission_result, 'reason', 'N/A'))

        if not permission_result.is_ok:
            self.response.payload.is_ok = False
            self.response.payload.cid = cid
            self.response.payload.status = UNAUTHORIZED
            self.response.payload.details = 'Permission denied'
            return

        # Get message data
        data = input.data

        if data is None:
            self.response.payload.is_ok = False
            self.response.payload.cid = cid
            self.response.payload.status = BAD_REQUEST
            self.response.payload.details = "Invalid input: 'data' element missing"
            return

        # Get optional parameters with safe parsing
        try:
            priority = int(input.priority) if input.priority not in (None, '') else _default_priority
        except (ValueError, TypeError):
            priority = _default_priority

        try:
            expiration = int(input.expiration) if input.expiration not in (None, '') else _default_expiration
        except (ValueError, TypeError):
            expiration = _default_expiration

        correl_id = input.correl_id or cid
        in_reply_to = input.in_reply_to or ''
        ext_client_id = input.ext_client_id or ''

        # Validate priority
        if priority < _min_priority or priority > _max_priority:
            priority = _default_priority

        # Validate expiration
        if expiration < 1:
            expiration = 1

        logger.info('Publish params: topic=%s, priority=%s, expiration=%s, correl_id=%s, publisher=%s',
            topic_name, priority, expiration, correl_id, username)

        # Publish to Redis
        msg_id = self.server.pubsub_redis.publish(
            topic_name,
            data,
            priority=priority,
            expiration=expiration,
            correl_id=correl_id,
            in_reply_to=in_reply_to,
            ext_client_id=ext_client_id,
            publisher=username,
        )

        # Build response
        self.response.payload.is_ok = True
        self.response.payload.cid = cid
        self.response.payload.msg_id = msg_id

# ################################################################################################################################
# ################################################################################################################################

class GetMessages(PubSubRESTService):
    """ Retrieve messages for the authenticated user.
    """
    name = 'pubsub.rest.get-messages'

    class SimpleIO:
        input_optional = Int('max_messages'), Int('max_len')
        output_optional = AsIs('messages'), Int('message_count'), 'is_ok', 'cid', Int('status'), 'details'

# ################################################################################################################################

    def handle(self) -> 'None':

        # Local aliases
        cid = self.cid
        input = self.request.input

        # Authenticate
        username, error = self.authenticate()
        if error:
            self.response.payload.is_ok = False
            self.response.payload.cid = cid
            self.response.payload.details, self.response.payload.status = error
            return

        # Get sub_key for this user
        sub_key = self._get_sub_key_for_user(username)

        if not sub_key:
            self.response.payload.is_ok = True
            self.response.payload.cid = cid
            self.response.payload.messages = []
            self.response.payload.message_count = 0
            return

        # Get optional parameters
        max_messages = input.max_messages if input.max_messages else _max_messages_default
        max_len = input.max_len if input.max_len else _max_len_default

        # Fetch messages from Redis
        messages = self.server.pubsub_redis.fetch_messages(
            sub_key,
            max_messages=max_messages,
            max_len=max_len
        )

        # Build response
        self.response.payload.is_ok = True
        self.response.payload.cid = cid
        self.response.payload.messages = messages
        self.response.payload.message_count = len(messages)

# ################################################################################################################################

    def _get_sub_key_for_user(self, username:'str') -> 'str':
        """ Get the subscription key for a user.
        """
        # Look up in the subscriptions store
        return self.server.pubsub_subscriptions.get_sub_key_by_username(username)

# ################################################################################################################################
# ################################################################################################################################

class Subscribe(PubSubRESTService):
    """ Subscribe to a topic.
    """
    name = 'pubsub.rest.subscribe'

    class SimpleIO:
        input_required = 'topic_name'
        output_optional = 'is_ok', 'cid', Int('status'), 'details', 'sub_key'

# ################################################################################################################################

    def handle(self) -> 'None':

        # Local aliases
        cid = self.cid
        input = self.request.input

        # Authenticate
        username, error = self.authenticate()
        if error:
            self.response.payload.is_ok = False
            self.response.payload.cid = cid
            self.response.payload.details, self.response.payload.status = error
            return

        # Get topic name
        topic_name = input.topic_name

        # Validate topic name
        try:
            validate_topic_name(topic_name)
        except Exception as e:
            self.response.payload.is_ok = False
            self.response.payload.cid = cid
            self.response.payload.status = BAD_REQUEST
            self.response.payload.details = str(e)
            return

        # Check permissions
        permission_result = self.server.pubsub_pattern_matcher.evaluate(username, topic_name, 'subscribe')

        if not permission_result.is_ok:
            self.response.payload.is_ok = False
            self.response.payload.cid = cid
            self.response.payload.status = UNAUTHORIZED
            self.response.payload.details = 'Permission denied'
            return

        # Get or create sub_key for this user
        sub_key = self.server.pubsub_subscriptions.get_or_create_sub_key(username)

        # Subscribe in Redis
        self.server.pubsub_redis.subscribe(sub_key, topic_name)

        # Persist subscription in ODB
        self._persist_subscription(username, topic_name, sub_key)

        # Build response
        self.response.payload.is_ok = True
        self.response.payload.cid = cid
        self.response.payload.sub_key = sub_key

# ################################################################################################################################

    def _persist_subscription(self, username:'str', topic_name:'str', sub_key:'str') -> 'None':
        """ Persist subscription to ODB.
        """
        sec_name = self._get_sec_name(username)
        logger.info('_persist_subscription: username=%s, topic_name=%s, sub_key=%s, sec_name=%s',
            username, topic_name, sub_key, sec_name)

        request = {
            'sub_key': sub_key,
            'topic_name_list': [topic_name],
            'sec_name': sec_name,
            'is_delivery_active': True,
            'is_pub_active': True,
            'delivery_type': PubSub.Delivery_Type.Pull,
        }
        logger.info('_persist_subscription: invoking zato.pubsub.subscription.subscribe with request=%s', request)
        _ = self.invoke('zato.pubsub.subscription.subscribe', request)
        logger.info('_persist_subscription: invoke completed')

# ################################################################################################################################

    def _get_sec_name(self, username:'str') -> 'str':
        """ Get security definition name for username.
        """
        return self.server.pubsub_subscriptions.get_sec_name_by_username(username)

# ################################################################################################################################
# ################################################################################################################################

class Unsubscribe(PubSubRESTService):
    """ Unsubscribe from a topic.
    """
    name = 'pubsub.rest.unsubscribe'

    class SimpleIO:
        input_required = 'topic_name'
        output_optional = 'is_ok', 'cid', Int('status'), 'details'

# ################################################################################################################################

    def handle(self) -> 'None':

        # Local aliases
        cid = self.cid
        input = self.request.input

        # Authenticate
        username, error = self.authenticate()
        if error:
            self.response.payload.is_ok = False
            self.response.payload.cid = cid
            self.response.payload.details, self.response.payload.status = error
            return

        # Get topic name
        topic_name = input.topic_name

        # Validate topic name
        try:
            validate_topic_name(topic_name)
        except Exception as e:
            self.response.payload.is_ok = False
            self.response.payload.cid = cid
            self.response.payload.status = BAD_REQUEST
            self.response.payload.details = str(e)
            return

        # Get sub_key for this user
        sub_key = self.server.pubsub_subscriptions.get_sub_key_by_username(username)

        if not sub_key:
            # User has no subscriptions, return success (idempotent)
            self.response.payload.is_ok = True
            self.response.payload.cid = cid
            return

        # Unsubscribe in Redis
        self.server.pubsub_redis.unsubscribe(sub_key, topic_name)

        # Clear sub_key so a new one is generated on next subscribe
        self.server.pubsub_subscriptions.clear_sub_key(username)

        # Remove subscription from ODB
        self._remove_subscription(username, topic_name)

        # Build response
        self.response.payload.is_ok = True
        self.response.payload.cid = cid

# ################################################################################################################################

    def _remove_subscription(self, username:'str', topic_name:'str') -> 'None':
        """ Remove subscription from ODB.
        """
        sec_name = self._get_sec_name(username)
        logger.info('_remove_subscription: username=%s, topic_name=%s, sec_name=%s', username, topic_name, sec_name)

        request = {
            'sec_name': sec_name,
            'username': username,
            'topic_name_list': [topic_name],
        }
        logger.info('_remove_subscription: invoking zato.pubsub.subscription.unsubscribe with request=%s', request)
        _ = self.invoke('zato.pubsub.subscription.unsubscribe', request)
        logger.info('_remove_subscription: invoke completed')

# ################################################################################################################################

    def _get_sec_name(self, username:'str') -> 'str':
        """ Get security definition name for username.
        """
        return self.server.pubsub_subscriptions.get_sec_name_by_username(username)

# ################################################################################################################################
# ################################################################################################################################
