# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from datetime import datetime, timedelta
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common import DATA_FORMAT, WEB_SOCKET
from zato.common.broker_message import CHANNEL
from zato.common.odb.model import ChannelWebSocket, PubSubSubscription, PubSubTopic, Service as ServiceModel, WebSocketClient
from zato.common.odb.query import channel_web_socket_list, channel_web_socket, service, web_socket_client, \
     web_socket_client_by_pub_id, web_socket_client_list, web_socket_sub_key_data_list
from zato.common.util import is_port_taken, parse_extra_into_dict
from zato.common.util.sql import elems_with_opaque
from zato.common.util.time_ import datetime_from_ms, utcnow_as_ms
from zato.server.service import AsIs, DateTime, Int, Service
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################

elem = 'channel_web_socket'
model = ChannelWebSocket
label = 'a WebSocket channel'
broker_message = CHANNEL
broker_message_prefix = 'WEB_SOCKET_'
list_func = channel_web_socket_list
skip_input_params = ['service_id']
create_edit_input_required_extra = ['service_name']
output_optional_extra = ['service_name', 'sec_type']

# ################################################################################################################################

SubscriptionTable = PubSubSubscription.__table__
SubscriptionDelete = SubscriptionTable.delete

WSXChannelTable = ChannelWebSocket.__table__

WSXClientTable = WebSocketClient.__table__
WSXClientDelete = WSXClientTable.delete

# ################################################################################################################################

logger_pubsub = getLogger('zato_pubsub.srv')

# ################################################################################################################################

def broker_message_hook(self, input, instance, attrs, service_type):
    input.source_server = self.server.get_full_name()
    input.config_cid = 'channel.web_socket.{}.{}.{}'.format(service_type, input.source_server, self.cid)

    if service_type == 'create_edit':

        with closing(self.odb.session()) as session:
            full_data = channel_web_socket(session, input.cluster_id, instance.id)

        input.sec_type = full_data.sec_type
        input.sec_name = full_data.sec_name
        input.vault_conn_default_auth_method = full_data.vault_conn_default_auth_method

# ################################################################################################################################

def instance_hook(self, input, instance, attrs):

    if attrs.is_create_edit:
        instance.hook_service = self.server.fs_server_config.get('wsx', {}).get('hook_service', '')
        instance.is_out = False
        instance.service = attrs._meta_session.query(ServiceModel).\
            filter(ServiceModel.name==input.service_name).\
            filter(ServiceModel.cluster_id==input.cluster_id).\
            one()

# ################################################################################################################################

def response_hook(self, input, _ignored_instance, attrs, service_type):
    if service_type == 'get_list' and self.name == 'zato.channel.web-socket.get-list':
        with closing(self.odb.session()) as session:
            for item in self.response.payload:
                item.service_name = service(session, self.server.cluster_id, item.service_id).name

# ################################################################################################################################

class GetList(AdminService):
    _filter_by = ChannelWebSocket.name,
    __metaclass__ = GetListMeta

# ################################################################################################################################

class Create(AdminService):
    __metaclass__ = CreateEditMeta

# ################################################################################################################################

class Edit(AdminService):
    __metaclass__ = CreateEditMeta

# ################################################################################################################################

class Delete(AdminService):
    __metaclass__ = DeleteMeta

# ################################################################################################################################

class Start(Service):
    """ Starts a WebSocket channel.
    """
    class SimpleIO(object):
        input_required = tuple(Edit.SimpleIO.input_required) + ('id', 'config_cid')
        input_optional = tuple(Edit.SimpleIO.input_optional) + (
            Int('bind_port'), 'service_name', 'sec_name', 'sec_type', 'vault_conn_default_auth_method')
        request_elem = 'zato_channel_web_socket_start_request'
        response_elem = 'zato_channel_web_socket_start_response'

    def handle(self):
        input = self.request.input
        if input.bind_port and is_port_taken(input.bind_port):
            self.logger.warn('Cannot bind WebSocket channel `%s` to TCP port %s (already taken)', input.name, input.bind_port)
        else:
            self.server.worker_store.web_socket_channel_create(self.request.input)

# ################################################################################################################################

class GetConnectionList(AdminService):
    """ Returns a list of WSX connections for a particular channel.
    """
    _filter_by = WebSocketClient.ext_client_id,

    class SimpleIO(GetListAdminSIO):
        input_required = 'id', 'cluster_id'
        output_required = ('local_address', 'peer_address', 'peer_fqdn', AsIs('pub_client_id'), AsIs('ext_client_id'),
            DateTime('connection_time'), 'server_name', 'server_proc_pid')
        output_optional = 'ext_client_name', 'sub_count', 'peer_forwarded_for', 'peer_forwarded_for_fqdn'
        output_repeated = True

    def get_data(self, session):
        result = self._search(web_socket_client_list, session, self.request.input.cluster_id, self.request.input.id, False)
        return elems_with_opaque(result)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################

class _BaseCommand(AdminService):
    server_service = None

    class SimpleIO(AdminSIO):
        input_required = 'cluster_id', 'id', AsIs('pub_client_id')
        input_optional = 'request_data', Int('timeout')
        output_optional = 'response_data'
        response_elem = None

# ################################################################################################################################

    def _get_wsx_client(self, session):
        client = web_socket_client(session, self.request.input.cluster_id, self.request.input.id,
            self.request.input.pub_client_id)
        if not client:
            raise Exception('No such WebSocket connection `{}`'.format(self.request.input.toDict()))
        else:
            return client

# ################################################################################################################################

class _BaseAPICommand(_BaseCommand):

    def handle(self):
        with closing(self.odb.session()) as session:
            client = self._get_wsx_client(session)
            server_name = client.server_name
            server_proc_pid = client.server_proc_pid

        server_response = self.servers[server_name].invoke(
            self.server_service, self.request.input, pid=server_proc_pid, data_format=DATA_FORMAT.JSON)

        if server_response:
            response_data = server_response.get('response_data') or {}
            self.response.payload.response_data = response_data
        else:
            self.logger.warn('No server response from %s:%s received to command `%s` (sr:%s)',
                server_name, server_proc_pid, self.request.input, server_response)

# ################################################################################################################################

class _BaseServerCommand(_BaseCommand):
    func_name = None

    def _get_server_response(self, func, pub_client_id):
        raise NotImplementedError('Must be implemented in subclasses')

    def handle(self):
        pub_client_id = self.request.input.pub_client_id

        try:
            with closing(self.odb.session()) as session:
                client = web_socket_client_by_pub_id(session, pub_client_id)
                wsx_channel_name = client.channel_name

            connector = self.server.worker_store.web_socket_api.connectors[wsx_channel_name]
            func = getattr(connector, self.func_name)
            response_data = self._get_server_response(func, pub_client_id)

        except Exception:
            self.response.payload.response_data = format_exc()
        else:
            self.response.payload.response_data = response_data

# ################################################################################################################################

class DisconnectConnection(_BaseAPICommand):
    """ Deletes an existing WSX connection.
    """
    server_service = 'zato.channel.web-socket.disconnect-connection-server'

# ################################################################################################################################

class DisconnectConnectionServer(_BaseServerCommand):
    """ Low-level implementation of WSX connection deletion - must be invoked on the server where the connection exists.
    """
    func_name = 'disconnect_client'

    def _get_server_response(self, func, pub_client_id):
        func(self.cid, pub_client_id)

# ################################################################################################################################

class InvokeWSX(_BaseAPICommand):
    """ Invokes an existing WSX connection.
    """
    server_service = 'zato.channel.web-socket.server-invoke-wsx'

# ################################################################################################################################

class ServerInvokeWSX(_BaseServerCommand):
    """ Low-level implementation of WSX connection inovcations - must be invoked on the server where the connection exists.
    """
    func_name = 'invoke'

    def _get_server_response(self, func, pub_client_id):
        return func(self.cid, pub_client_id, self.request.input.request_data, self.request.input.timeout)

# ################################################################################################################################

class GetSubKeyDataList(AdminService):
    """ Returns a list of pub/sub sub_key data for a particular WSX connection.
    """
    _filter_by = PubSubTopic.name,

    class SimpleIO(GetListAdminSIO):
        input_required = 'cluster_id', AsIs('pub_client_id')
        output_required = ('sub_id', 'sub_key', DateTime('creation_time'), 'topic_id', 'topic_name', 'sub_pattern_matched',
            AsIs('ext_client_id'), 'endpoint_id', 'endpoint_name')
        output_repeated = True

    def get_data(self, session):
        return self._search(web_socket_sub_key_data_list,
            session, self.request.input.cluster_id, self.request.input.pub_client_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            data = self.get_data(session)
            for item in data:
                item.creation_time = datetime_from_ms(item.creation_time * 1000)
            self.response.payload[:] = data

# ################################################################################################################################

class CleanupWSXPubSub(AdminService):
    """ Deletes all old WSX clients and their subscriptions.
    """
    name = 'pub.zato.channel.web-socket.cleanup-wsx-pub-sub'

    def handle(self, _msg='Cleaning up WSX pub/sub, channel:`%s`, now:`%s (%s)`, md:`%s`, ma:`%s` (%s)'):

        # We receive a multi-line list of WSX channel name -> max timeout accepted on input
        config = parse_extra_into_dict(self.request.raw_request)

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

                self.logger.info(_msg, channel_name, now_as_iso, now, max_delta, max_allowed_as_iso, max_allowed)
                logger_pubsub.info(_msg, channel_name, now_as_iso, now, max_delta, max_allowed_as_iso, max_allowed)

                # Delete old connections for that channel
                session.execute(
                    SubscriptionDelete().\
                    where(SubscriptionTable.c.ws_channel_id==WSXChannelTable.c.id).\
                    where(WSXChannelTable.c.name==channel_name).\
                    where(SubscriptionTable.c.last_interaction_time < max_allowed)
                )

            # Commit all deletions
            session.commit()

# ################################################################################################################################

class CleanupWSX(AdminService):
    """ Deletes WSX clients that exceeded their ping timeouts. Executed when a server starts. Also invoked through the scheduler.
    """
    name = 'pub.zato.channel.web-socket.cleanup-wsx'

    def handle(self, _msg='Cleaning up old WSX connections now:`%s`, md:`%s`, ma:`%s`'):
        with closing(self.odb.session()) as session:

            # Stale connections are ones that are is older than 2 * interval in which each WebSocket's last_seen time is updated.
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

            self.logger.info(_msg, now_as_iso, max_delta, max_allowed)
            logger_pubsub.info(_msg, now_as_iso, max_delta, max_allowed)

            # Delete old WSX connections now ..
            session.execute(
                WSXClientDelete().\
                where(WSXClientTable.c.last_seen < max_allowed)
            )

            # .. and commit changes.
            session.commit()

'''
# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
#import os
from contextlib import closing
from datetime import datetime, timedelta
#from glob import glob
from logging import getLogger

# Zato
#from zato.common import CONFIG_FILE
from zato.common import WEB_SOCKET
from zato.common.odb.model import ChannelWebSocket, PubSubSubscription, WebSocketClient, WebSocketClientPubSubKeys
from zato.common.util.time_ import datetime_from_ms
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

logger_pubsub = getLogger('zato_pubsub.srv')

# ################################################################################################################################

SubscriptionTable = PubSubSubscription.__table__
SubscriptionDelete = SubscriptionTable.delete

WSXChannelTable = ChannelWebSocket.__table__

WSXClientTable = WebSocketClient.__table__
WSXClientDelete = WSXClientTable.delete
WSXClientSelect = WSXClientTable.select

# ################################################################################################################################

class _msg:
    initial = 'Cleaning up old WSX connections; now:`%s`, md:`%s`, ma:`%s`'
    not_found = 'Did not find any WSX connections to clean up'
    found = 'Found %d WSX connection%s to clean up'
    cleaning = 'Cleaning up WSX connection %d/%d; %s'
    cleaned_up = 'Cleaned up WSX connection %d/%d; %s'

# ################################################################################################################################

class _CleanupWSX(object):
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

class CleanupWSX(AdminService):
    """ Deletes WSX clients that exceeded their ping timeouts. Executed when a server starts. Also invoked through the scheduler.
    """
    name = 'cleanup-wsx'

    class SimpleIO(AdminSIO):
        """ This empty definition is needed in case the service should be invoked through REST.
        """

# ################################################################################################################################

    def _issue_log_msg(self, msg, *args):
        self.logger.info(msg, *args)
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
        max_delta = 1#max_delta * 60 # = * 1 hour

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

        # Maps all sub_keys found, if any, to their underlying topics
        sub_key_to_topic = {}

        with closing(self.odb.session()) as session:

            # Find the old connections now
            result = self._find_old_wsx_connections(session, max_allowed)

        # Nothing to do, log the message and we can return
        if not result:
            self._issue_log_msg(_msg.not_found)
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

        for idx, (pub_client_id, wsx) in enumerate(wsx_clients.iteritems(), 1):

            # All subscription keys for that WSX, we are adding it here
            # for logging purposes only, so that in a moment we are able to say
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

            # Log information that this particular connection is done with
            # (note that for clarity, this part does not reiterate the subscription's details)
            self._issue_log_msg(_msg.cleaned_up, idx, len_found, wsx.pub_client_id)
'''

# ################################################################################################################################
