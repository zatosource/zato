# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from datetime import datetime, timedelta
from logging import getLogger

# Python 2/3 compatibility
from zato.common.ext.future.utils import iteritems

# Zato
from zato.common.api import WEB_SOCKET
from zato.common.broker_message import PUBSUB
from zato.common.odb.model import ChannelWebSocket, PubSubSubscription, WebSocketClient, WebSocketClientPubSubKeys
from zato.common.util.pubsub import get_topic_sub_keys_from_sub_keys
from zato.common.util.api import parse_extra_into_dict
from zato.common.util.time_ import datetime_from_ms, utcnow_as_ms
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

logger_pubsub = getLogger('zato_pubsub.srv')

# ################################################################################################################################

SubscriptionTable = PubSubSubscription.__table__
SubscriptionDelete = SubscriptionTable.delete
SubscriptionSelect = SubscriptionTable.select

WSXChannelTable = ChannelWebSocket.__table__

WSXClientTable = WebSocketClient.__table__
WSXClientDelete = WSXClientTable.delete
WSXClientSelect = WSXClientTable.select

# ################################################################################################################################

class _msg:
    initial = 'Cleaning up old WSX connections; now:`%s`, md:`%s`, ma:`%s`'
    found = 'Found %d WSX connection%s to clean up'
    cleaning = 'Cleaning up WSX connection %d/%d; %s'
    cleaned_up = 'Cleaned up WSX connection %d/%d; %s'
    unsubscribing = 'Unsubscribing `%s` (%s) from `%s`'
    deleting = 'Deleting `%s` from ODB'

# ################################################################################################################################

class _CleanupWSX:
    """ A container for WSX connections that are about to be cleaned up, along with their subscriptions.
    """
    __slots__ = 'pub_client_id', 'sk_dict'

    def __init__(self):
        self.pub_client_id = None
        self.sk_dict = None

    def __repr__(self):
        return '<{} at {}, pci:{}, sk_dict:{}>'.format(self.__class__.__name__, hex(id(self)), self.pub_client_id, self.sk_dict)

    def to_dict(self):
        return {
            'pub_client_id': self.pub_client_id,
            'sk_dict': self.sk_dict,
        }

# ################################################################################################################################
# ################################################################################################################################

class CleanupWSXPubSub(AdminService):
    """ Deletes all old WSX clients and their subscriptions.
    """
    name = 'pub.zato.channel.web-socket.cleanup-wsx-pub-sub'

    def _run_max_allowed_query(self, session, query, channel_name, max_allowed):
        return session.execute(
            query.\
            where(SubscriptionTable.c.ws_channel_id==WSXChannelTable.c.id).\
            where(SubscriptionTable.c.cluster_id==self.server.cluster_id).\
            where(WSXChannelTable.c.name==channel_name).\
            where(SubscriptionTable.c.last_interaction_time < max_allowed)
        )

    def handle(self, _msg='Cleaning up WSX pub/sub, channel:`%s`, now:`%s (%s)`, md:`%s`, ma:`%s` (%s)'):

        # We receive a multi-line list of WSX channel name -> max timeout accepted on input
        config = parse_extra_into_dict(self.request.raw_request)

        self.logger.info('Running %s with config %r', self.get_name(), config)

        with closing(self.odb.session()) as session:

            # Delete stale connections for each subscriber
            for channel_name, max_delta in config.items():

                # Input timeout is in minutes but timestamps in ODB are in seconds
                # so we convert the minutes to seconds, as expected by the database.
                max_delta = max_delta * 60

                # We compare everything using seconds
                now = utcnow_as_ms()

                # Laster interaction time for each connection must not be older than that many seconds ago
                max_allowed = now - max_delta

                now_as_iso = datetime_from_ms(now * 1000)
                max_allowed_as_iso = datetime_from_ms(max_allowed * 1000)

                # Get all sub_keys that are about to be deleted - retrieving them from the DELETE
                # statement below is not portable so we do it manually first.
                items = self._run_max_allowed_query(session, SubscriptionSelect(), channel_name, max_allowed)
                sub_key_list = [item.sub_key for item in items]

                if sub_key_list:
                    self.logger.debug(_msg, channel_name, now_as_iso, now, max_delta, max_allowed_as_iso, max_allowed)
                    logger_pubsub.info(_msg, channel_name, now_as_iso, now, max_delta, max_allowed_as_iso, max_allowed)

                # First we need a list of topics to which sub_keys were related - required by broker messages.
                topic_sub_keys = get_topic_sub_keys_from_sub_keys(session, self.server.cluster_id, sub_key_list)

                # Now, delete old connections for that channel from SQL
                self._run_max_allowed_query(session, SubscriptionDelete(), channel_name, max_allowed)

                # Next, notify processes about deleted subscriptions to allow to update in-RAM structures
                if topic_sub_keys:
                    self.broker_client.publish({
                        'topic_sub_keys': topic_sub_keys,
                        'action': PUBSUB.SUBSCRIPTION_DELETE.value,
                    })
                    logger_pubsub.info('Published a request to delete sub_keys: %s', sorted(topic_sub_keys))
                else:
                    logger_pubsub.info('Found no sub_keys required to be deleted (%r)', config)

            # Commit all deletions
            session.commit()

# ################################################################################################################################
# ################################################################################################################################

class CleanupWSX(AdminService):
    """ Deletes WSX clients that exceeded their ping timeouts. Executed when a server starts. Also invoked through the scheduler.
    """
    name = 'pub.zato.channel.web-socket.cleanup-wsx'

# ################################################################################################################################

    def _issue_log_msg(self, msg, *args):
        self.logger.debug(msg, *args)
        logger_pubsub.info(msg, *args)

# ################################################################################################################################

    def _get_max_allowed(self):

        # Stale connections are ones that are older than 2 * interval in which each WebSocket's last_seen time is updated.
        # This is generous enough, because WSX send background pings once in 30 seconds. After 5 pings missed their
        # connections are closed. Then, the default interval is 60 minutes, so 2 * 60 = 2 hours. This means
        # that when a connection is broken but we somehow do not delete its relevant entry in SQL (e.g. because our
        # process was abruptly shut down), after these 2 hours the row will be considered ready to be deleted from
        # the database. Note that this service is invoked from the scheduler, by default, once in 30 minutes.

        # This is in minutes ..
        max_delta = WEB_SOCKET.DEFAULT.INTERACT_UPDATE_INTERVAL * 2

        # .. but timedelta expects seconds.
        max_delta = max_delta * 60 # = * 1 hour

        now = datetime.utcnow()
        max_allowed = now - timedelta(seconds=max_delta)
        now_as_iso = now.isoformat()

        self._issue_log_msg(_msg.initial, now_as_iso, max_delta, max_allowed)

        return max_allowed

# ################################################################################################################################

    def _find_old_wsx_connections(self, session, max_allowed):

        # Note that we always pull all the data possible to sort it out in Python code
        return session.query(
            WebSocketClient.id,
            WebSocketClient.pub_client_id,
            WebSocketClient.last_seen,
            WebSocketClientPubSubKeys.sub_key
            ).\
            filter(WebSocketClient.last_seen < max_allowed).\
            filter(WebSocketClient.id == WebSocketClientPubSubKeys.client_id).\
            all()

# ################################################################################################################################

    def handle(self):

        # How far back are we to reach out to find old connections
        max_allowed = self._get_max_allowed()

        with closing(self.odb.session()) as session:

            # Find the old connections now
            result = self._find_old_wsx_connections(session, max_allowed)

        # Nothing to do, we can return
        if not result:
            return

        # At least one old connection was found

        wsx_clients = {} # Maps pub_client_id -> _CleanupWSX object
        wsx_sub_key = {} # Maps pub_client_id -> a list of its sub_keys

        for item in result:
            wsx = wsx_clients.setdefault(item.pub_client_id, _CleanupWSX())
            wsx.pub_client_id = item.pub_client_id

            sk_list = wsx_sub_key.setdefault(item.pub_client_id, [])
            sk_list.append(item.sub_key)

        len_found = len(wsx_clients)

        suffix = '' if len_found == 1 else 's'
        self._issue_log_msg(_msg.found, len_found, suffix)

        for idx, (pub_client_id, wsx) in enumerate(iteritems(wsx_clients), 1):

            # All subscription keys for that WSX, we are adding it here
            # so that below, for logging purposes, we are able to say
            # what subscriptions are being actually deleted.
            wsx.sk_dict = {}.fromkeys(wsx_sub_key[pub_client_id])

            # For each subscription of that WSX, add its details to the sk_dict
            for sub_key in wsx.sk_dict:
                sub = self.pubsub.get_subscription_by_sub_key(sub_key)
                if sub:
                    wsx.sk_dict[sub_key] = {
                        'creation_time': datetime_from_ms(sub.creation_time),
                        'topic_id': sub.topic_id,
                        'topic_name': sub.topic_name,
                        'ext_client_id': sub.ext_client_id,
                        'endpoint_type': sub.config['endpoint_type'],
                        'sub_pattern_matched': sub.sub_pattern_matched,
                    }

            # Log what we are about to do
            self._issue_log_msg(_msg.cleaning, idx, len_found, wsx.to_dict())

            # Unsubscribe the WebSocket first
            for sub_key, info in wsx.sk_dict.items():

                # Object 'info' may be None if we are called while the WSX connection
                # is still alive but did not respond to pings, in which case it cannot be cleaned up.
                if info:
                    self._issue_log_msg(_msg.unsubscribing, sub_key, info['ext_client_id'], info['topic_name'])
                    self.invoke('zato.pubsub.pubapi.unsubscribe',{
                        'sub_key': sub_key,
                        'topic_name': info['topic_name'],
                    })

            # Delete the WebSocket's state in SQL now
            self._issue_log_msg(_msg.deleting, wsx.pub_client_id)

            with closing(self.odb.session()) as session:
                session.execute(
                    WSXClientDelete().\
                    where(WSXClientTable.c.pub_client_id==wsx.pub_client_id)
                )
                session.commit()

            # Log information that this particular connection is done with
            # (note that for clarity, this part does not reiterate the subscription's details)
            self._issue_log_msg(_msg.cleaned_up, idx, len_found, wsx.pub_client_id)

# ################################################################################################################################
# ################################################################################################################################
