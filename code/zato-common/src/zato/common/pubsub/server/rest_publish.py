# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Must come first
from gevent import monkey;
_ = monkey.patch_all()

# stdlib
import os
from datetime import datetime
from logging import getLogger

# werkzeug
from werkzeug.wrappers import Request

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.models import PubMessage, APIResponse, _base_response
from zato.common.pubsub.server.rest_base import BadRequestException, BaseRESTServer, UnauthorizedException
from zato.common.pubsub.util import validate_topic_name
from zato.common.util.api import as_bool

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_needs_details = as_bool(os.environ.get('Zato_Needs_Details', False))

_min_priority = PubSub.Message.Priority_Min
_max_priority = PubSub.Message.Priority_Max
_default_priority = PubSub.Message.Priority_Default

_default_expiration = PubSub.Message.Default_Expiration

# ################################################################################################################################
# ################################################################################################################################

class PubSubRESTServerPublish(BaseRESTServer):
    """ A REST server for pub/sub operations.
    """
    server_type = 'publish'

    def on_publish(self, cid:'str', environ:'anydict', start_response:'any_', topic_name:'str') -> '_base_response':
        """ Publish a message to a topic.
        """
        # Log what we're doing ..
        if _needs_details:
            logger.info(f'[{cid}] Processing publish request')

        # .. make sure the client is allowed to carry out this action ..
        username = self.authenticate(cid, environ)

        if _needs_details:
            logger.info(f'[{cid}] Authenticated user for messages/publish: `{username}`')

        # .. validate topic name ..
        validate_topic_name(topic_name)

        # .. check if user has permission to publish to this topic ..
        permission_result = self.backend.pattern_matcher.evaluate(username, topic_name, 'publish')

        if _needs_details:
            logger.info(f'[{cid}] Permission check for user {username} on topic {topic_name}: is_ok={permission_result.is_ok}, reason={permission_result.reason}')

        if not permission_result.is_ok:
            logger.warning(f'[{cid}] User {username} denied publish access to topic {topic_name}: {permission_result.reason}')
            raise UnauthorizedException(cid, 'Permission denied')

        # .. build our representation of the request ..
        request = Request(environ)
        data = self._parse_json(cid, request)

        # .. make sure we actually did receive anything ..
        if not data:
            raise BadRequestException(cid, 'Input data missing')

        # .. now also check if we've received the business data ..
        msg_data = data.get('data')

        # .. well, we haven't ..
        if msg_data is None:
            raise BadRequestException(cid, "Invalid input: 'data' element missing")

        # .. get all the details from the message now that we know we have it ..
        ext_client_id = data.get('ext_client_id', '')
        priority = data.get('priority', _default_priority)
        expiration = data.get('expiration', _default_expiration)
        correl_id = data.get('correl_id', '') or cid
        in_reply_to=data.get('in_reply_to', '')

        # .. this is optional ..
        pub_time = data.get('pub_time', '')

        # .. make sure it's valid if given on input ..
        if pub_time:
            _ = datetime.fromisoformat(pub_time)

        # .. make sure the priority is valid ..
        if priority < _min_priority or priority > _max_priority:
            priority = _default_priority

        # .. make sure the expiration is valid ..
        expiration = round(expiration)
        if expiration < 1:
            expiration = 1

        # .. build a business message ..
        msg:'PubMessage' = {
            'data': msg_data,
            'priority': priority,
            'expiration': expiration,
            'correl_id': correl_id,
            'ext_client_id': ext_client_id,
            'pub_time': pub_time,
            'in_reply_to': in_reply_to
        }

        # .. let the backend handle it ..
        if _needs_details:
            logger.info(f'[{cid}] Calling backend.publish_impl for user {username} on topic {topic_name}')

        result = self.backend.publish_impl(cid, topic_name, msg, username, ext_client_id)

        if _needs_details:
            logger.info(f'[{cid}] Backend publish_impl result: {result}')

        # .. build our response ..
        response:'APIResponse' = {
            'is_ok': result['is_ok'], # type: ignore
            'cid': cid,
        }

        # .. add status if present ..
        if status := result.get('status'):
            response['status'] = status

        # .. add error details if present ..
        if details := result.get('details'):
            response['details'] = details

        # .. this is optional because the result may indicate an error ..
        if msg_id := result.get('msg_id'):
            response['msg_id'] = msg_id

        # .. and return it to the caller.
        return response

# ################################################################################################################################
# ################################################################################################################################
