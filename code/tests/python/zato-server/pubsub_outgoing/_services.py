# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import HTTP_SOAP, PubSub
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

# What an outgoing REST connection is known as to the services that create, edit and delete these.
_connection = 'outgoing'
_transport = 'plain_http'

# The fields of the declarative invocation profile, which is where the HTTP method a connection sends with
# lives. They are stored in the connection's opaque attributes, so an edit that leaves them out clears them.
_profile_fields = HTTP_SOAP.Invocation.FieldList + HTTP_SOAP.HealthCheck.FieldList + HTTP_SOAP.Retry.FieldList

# ################################################################################################################################
# ################################################################################################################################

class PublishToOutgoingConnection(Service):
    """ Publishes one message to an outgoing connection, the way an application does it.
    """

    name = 'test.outgoing.publish'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        data = self.request.raw_request['data']

        result = self.out.rest[conn_name].publish(data)

        self.response.payload = {'msg_id': result.msg_id}

# ################################################################################################################################
# ################################################################################################################################

class PublishThroughFacade(Service):
    """ Publishes one message to an outgoing connection named through the REST facade, which is
    the other way of naming the same connection.
    """

    name = 'test.outgoing.publish-through-facade'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        data = self.request.raw_request['data']

        result = self.rest[conn_name].publish(data)

        self.response.payload = {'msg_id': result.msg_id}

# ################################################################################################################################
# ################################################################################################################################

class _OutgoingConnectionService(Service):
    """ What the services that change an outgoing REST connection have in common, which is reading
    the configuration that connection has right now, the way the Dashboard reads it into its form.
    """

    def get_config(self, conn_name:'str') -> 'stranydict':

        item = self.server.config_manager.config_store.out_plain_http[conn_name]

        out = item['config']
        return out

# ################################################################################################################################
# ################################################################################################################################

class RenameOutgoingConnection(_OutgoingConnectionService):
    """ Renames an outgoing REST connection the way the Dashboard does, which is by sending
    the connection's current configuration back under a new name.
    """

    name = 'test.outgoing.rename-connection'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        new_name = self.request.raw_request['new_name']

        config = self.get_config(conn_name)

        request = {
            'id': config['id'],
            'name': new_name,
            'connection': _connection,
            'transport': _transport,
            'host': config['host'],
            'url_path': config['url_path'],
            'method': config['method'],
            'data_format': config['data_format'],
            'timeout': config['timeout'],
            'ping_method': config['ping_method'],
            'pool_size': config['pool_size'],
            'is_active': config['is_active'],
            'security_id': config['security_id'],
        }

        # The profile is what the connection sends with, so it goes back untouched
        for field_name in _profile_fields:
            if field_name in config:
                request[field_name] = config[field_name]

        _ = self.invoke('zato.http-soap.edit', request)

        self.response.payload = {'id': config['id']}

# ################################################################################################################################
# ################################################################################################################################

class DeleteOutgoingConnection(_OutgoingConnectionService):
    """ Deletes an outgoing REST connection, which is what its queue is expected not to outlive.
    """

    name = 'test.outgoing.delete-connection'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        config = self.get_config(conn_name)

        conn_id = config['id']

        _ = self.invoke('zato.http-soap.delete', {'id': conn_id, 'connection': _connection})

        self.response.payload = {'id': conn_id}

# ################################################################################################################################
# ################################################################################################################################

class GetOutgoingQueues(Service):
    """ Answers with every queue that stands in front of an outgoing connection, which is how a test
    sees whether a connection has one of them or two.
    """

    name = 'test.outgoing.get-queues'

    def handle(self) -> 'None':

        backend = self.server.pubsub_backend
        sub_key_list = backend.get_sub_keys_by_prefix(PubSub.Outgoing.Sub_Key_Prefix)

        queues:'anylist' = []

        for sub_key in sub_key_list:
            topic_name_list = backend.get_subscribed_topics(sub_key)
            queues.append({'sub_key': sub_key, 'topic_name_list': topic_name_list})

        self.response.payload = {'queues': queues}

# ################################################################################################################################
# ################################################################################################################################
