# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import BAD_REQUEST, CONFLICT, UNAUTHORIZED

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.sql.fenced_ack import PubSubAckConflict
from zato.common.pubsub.sql.publication import build_publication
from zato.common.pubsub.sql.writes import PubSubDuplicateMsgID
from zato.server.service import AsIs, Int
from zato.server.service.internal.pubsub.rest import PubSubRESTService
from zato.server.service.internal.pubsub.rest_publication import is_valid_msg_id, Msg_ID_Pattern, parse_publication, \
    PublicationError

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.sql.backend import consumed_list
    from zato.common.pubsub.sql.publication import built_publication_list
    from zato.common.typing_ import any_, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

# How many elements each list of a request may have
_max_elements = 1000

_status_ok           = PubSub.Status.OK
_status_bad_request  = PubSub.Status.Bad_Request
_status_unauthorized = PubSub.Status.Unauthorized
_status_conflict     = PubSub.Status.Conflict

# The lowest delivery attempt, which the first pull of a message hands it out with
_min_delivery_attempt = 1

# ################################################################################################################################
# ################################################################################################################################

class AckInputError(Exception):
    """ Raised for an acknowledgement request whose input is invalid.
    """

# ################################################################################################################################
# ################################################################################################################################

def _is_absent(value:'any_') -> 'bool':
    """ Whether an optional element was not sent, which the input of a service represents as None or an empty string.
    """
    if value is None:
        out = True
    else:
        out = value == ''

    return out

# ################################################################################################################################

def _check_list(value:'any_', name:'str') -> 'None':
    """ Checks that an element is a list of no more than the maximum number of elements.
    """
    if not isinstance(value, list):
        raise AckInputError(f'{name} must be a list')

    element_count = len(value)

    if element_count > _max_elements:
        raise AckInputError(f'{name} may have at most {_max_elements} elements')

# ################################################################################################################################

def _check_msg_ids(msg_ids:'any_') -> 'None':
    """ Checks the message IDs of a plain acknowledgement.
    """
    _check_list(msg_ids, 'msg_ids')

    for msg_id in msg_ids:
        if not is_valid_msg_id(msg_id):
            raise AckInputError(f'Each element of msg_ids must match {Msg_ID_Pattern.pattern}')

# ################################################################################################################################

def _parse_consumed(consumed:'any_') -> 'consumed_list':
    """ Returns the message ID and the delivery attempt of each consumed message.
    """
    _check_list(consumed, 'consumed')

    out:'consumed_list' = []

    for item in consumed:

        if not isinstance(item, dict):
            raise AckInputError('Each element of consumed must be an object')

        if 'msg_id' not in item:
            raise AckInputError("Each element of consumed must have a 'msg_id'")

        if 'delivery_attempt' not in item:
            raise AckInputError("Each element of consumed must have a 'delivery_attempt'")

        msg_id = item['msg_id']
        delivery_attempt = item['delivery_attempt']

        if not is_valid_msg_id(msg_id):
            raise AckInputError(f'Each msg_id of consumed must match {Msg_ID_Pattern.pattern}')

        # A boolean is an integer to Python, though not to a client ..
        if isinstance(delivery_attempt, bool):
            raise AckInputError('Each delivery_attempt of consumed must be an integer')

        if not isinstance(delivery_attempt, int):
            raise AckInputError('Each delivery_attempt of consumed must be an integer')

        # .. and the first pull of a message hands it out with the lowest attempt.
        if delivery_attempt < _min_delivery_attempt:
            raise AckInputError(f'Each delivery_attempt of consumed must be at least {_min_delivery_attempt}')

        consumed_message = (msg_id, delivery_attempt)
        out.append(consumed_message)

    return out

# ################################################################################################################################
# ################################################################################################################################

class AckMessages(PubSubRESTService):
    """ Acknowledges messages that the authenticated user pulled, removing them from its queue, either by their IDs alone
    or with the delivery attempt of each, in which case the publications that the user produced from them
    are committed in the same transaction.
    """
    name = 'pubsub.rest.ack-messages'

    input = AsIs('-msg_ids'), AsIs('-consumed'), AsIs('-publish')
    output = Int('-ack_count'), AsIs('-published'), '-is_ok', '-cid', AsIs('-status'), '-details'

# ################################################################################################################################

    def handle(self) -> 'None':

        # Local aliases
        input = self.request.input

        # Authenticate
        username, error = self.authenticate()
        if error:
            self.set_error(error)
            return

        # Get sub_key for this user
        sub_key = self.server.pubsub_subscriptions.get_sub_key_by_username(username)

        if not sub_key:
            error = ('No subscription found for user', _status_unauthorized, UNAUTHORIZED)
            self.set_error(error)
            return

        has_msg_ids = not _is_absent(input.msg_ids)
        has_consumed = not _is_absent(input.consumed)
        has_publish = not _is_absent(input.publish)

        # The input comes from the caller, so its shape is checked before anything reaches the database ..
        try:

            if has_msg_ids == has_consumed:
                raise AckInputError('Exactly one of msg_ids and consumed is required')

            if has_publish:
                if not has_consumed:
                    raise AckInputError('publish requires consumed')

            # .. a plain acknowledgement removes the messages that are still in the queue ..
            if has_msg_ids:
                _check_msg_ids(input.msg_ids)
                ack_count = self.server.pubsub_backend.ack_pulled(sub_key, input.msg_ids)
                published:'strlist' = []

            # .. whereas one with the attempts commits with the publications or not at all.
            else:
                consumed = _parse_consumed(input.consumed)
                publications = self._build_publications(username, input.publish, has_publish)
                result = self.server.pubsub_backend.ack_pulled_with_publications(sub_key, consumed, publications)
                ack_count = result.removed_count
                published = result.published

        except AckInputError as e:
            error = (str(e), _status_bad_request, BAD_REQUEST)
            self.set_error(error)
            return

        except PublicationError as e:
            self.set_error(e.error)
            return

        except (PubSubAckConflict, PubSubDuplicateMsgID) as e:
            error = (str(e), _status_conflict, CONFLICT)
            self.set_error(error)
            return

        # Build response
        self.response.payload.is_ok     = True
        self.response.payload.cid       = self.cid
        self.response.payload.ack_count = ack_count
        self.response.payload.status    = _status_ok

        if has_consumed:
            self.response.payload.published = published

# ################################################################################################################################

    def _build_publications(self, username:'str', publish:'any_', has_publish:'bool') -> 'built_publication_list':
        """ Validates each publication of a request and builds its message, before anything is written.
        """
        out:'built_publication_list' = []

        if not has_publish:
            return out

        _check_list(publish, 'publish')

        items:'anylist' = publish

        for item in items:

            if not isinstance(item, dict):
                raise AckInputError('Each element of publish must be an object')

            publication = parse_publication(self.server, username, self.cid, item)

            # A topic of the AMQP backend cannot take part in a transaction of the pub/sub database.
            if self.server.config_manager.get_pubsub_topic_backend(publication.topic_name):
                raise AckInputError(f'Topic {publication.topic_name} is not stored in the pub/sub database')

            built = build_publication(
                self.server.pubsub_backend,
                publication.topic_name,
                publication.data,
                priority=publication.priority,
                expiration=publication.expiration,
                correl_id=publication.correl_id,
                in_reply_to=publication.in_reply_to,
                ext_client_id=publication.ext_client_id,
                publisher=username,
                pub_time=publication.pub_time,
                cid=self.cid,
                msg_id=publication.msg_id,
            )

            out.append(built)

        return out

# ################################################################################################################################
# ################################################################################################################################
