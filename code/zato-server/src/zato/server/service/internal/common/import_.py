# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from copy import deepcopy
from dataclasses import dataclass
from json import dumps

# SQLAlchemy
from sqlalchemy import insert

# Zato
from zato.common.api import GENERIC, PUBSUB, Sec_Def_Type, Zato_No_Security
from zato.common.odb.model import HTTPBasicAuth, PubSubEndpoint, PubSubSubscription, PubSubTopic, SecurityBase
from zato.common.odb.query.common import get_object_list, get_object_list_by_columns, get_object_list_by_name_list
from zato.common.pubsub import new_sub_key
from zato.common.crypto.api import CryptoManager
from zato.common.typing_ import cast_
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, dictlist, strdict

# ################################################################################################################################
# ################################################################################################################################

HTTPBasicAuthTable:'any_' = HTTPBasicAuth.__table__
SecurityBaseTable:'any_' = SecurityBase.__table__
PubSubEndpointTable:'any_' = PubSubEndpoint.__table__
PubSubSubscriptionTable:'any_' = PubSubSubscription.__table__
PubSubTopicTable:'any_' = PubSubTopic.__table__

HTTPBasicAuthInsert = HTTPBasicAuthTable.insert

# ################################################################################################################################
# ################################################################################################################################

Default = PUBSUB.DEFAULT
Generic_Attr_Name = GENERIC.ATTR_NAME

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ObjectContainer(Model):

    pubsub_topic: 'dictlist | None' = None
    pubsub_endpoint: 'dictlist | None' = None
    pubsub_subscription: 'dictlist | None' = None
    basic_auth: 'dictlist | None' = None

# ################################################################################################################################

    def get_topic_id_by_name(self, name:'str') -> 'any_':
        for item in self.pubsub_topic: # type: ignore
            if item['name'] == name:
                return item['id']
        else:
            raise Exception(f'Topic not found -> {name}')

# ################################################################################################################################

    def get_endpoint_by_name(self, name:'str') -> 'any_':
        for item in self.pubsub_endpoint: # type: ignore
            if item['name'] == name:
                return item
        else:
            raise Exception(f'Endpoint not found -> {name}')

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ItemsInfo(Model):

    to_add: 'dictlist'
    to_update: 'dictlist'

# ################################################################################################################################
# ################################################################################################################################

class ImportObjects(Service):
    """ Imports multiple pub/sub objects en masse.
    """
    name = 'zato.common.import-objects'

    def handle(self):

        # data = test_data
        data = self.request.raw_request

        # Data that we received on input
        input:'ObjectContainer' = ObjectContainer.from_dict(data)

        has_input:'any_' = input.basic_auth or input.pubsub_topic or input.pubsub_endpoint or input.pubsub_subscription
        if not has_input:
            return

        self.logger.info('*' * 60)

        # Data that already exists
        with closing(self.odb.session()) as session:

            # All security definitions that currently exist
            sec_list = self._get_sec_list(session)

            # If we have security definitions on input,
            # import them first, as they may be needed in subsequent steps.
            if input.basic_auth:

                sec_info = self._handle_basic_auth_input(input.basic_auth, sec_list)

                if sec_info.to_add:
                    self.create_basic_auth(session, sec_info.to_add, input.basic_auth)

                if sec_info.to_update:
                    self.update_objects(session, SecurityBase, sec_info.to_update)

                if sec_info.to_add:
                    self.logger.info('Basic Auth created: %s', len(sec_info.to_add))

                if sec_info.to_update:
                    self.logger.info('Basic Auth updated: %s', len(sec_info.to_update))

                session.commit()

            # Rebuild it now because we may have added some above
            sec_list = self._get_sec_list(session)

            # All pub/sub objects that currently exist
            existing = self._get_existing_data(session, needs_subs=True)

            # Make sure we always have lists of dicts
            input_topics = input.pubsub_topic or []
            existing_topics = existing.pubsub_topic or []

            input_endpoints = input.pubsub_endpoint or []
            existing_endpoints = existing.pubsub_endpoint or []

            topics_info = self._find_items(input_topics, existing_topics)
            endpoints_info = self._find_items(input_endpoints, existing_endpoints)

            self._enrich_topics(topics_info.to_add)
            self._enrich_topics(topics_info.to_update)

            self._enrich_endpoints(endpoints_info.to_add, sec_list)
            self._enrich_endpoints(endpoints_info.to_update, sec_list)

            if topics_info.to_add:
                topics_insert = self.create_objects(PubSubTopicTable, topics_info.to_add)
                _ = session.execute(topics_insert)

            if topics_info.to_update:
                self.update_objects(session, PubSubTopic, topics_info.to_update)

            if endpoints_info.to_add:
                endpoints_insert = self.create_objects(PubSubEndpointTable, endpoints_info.to_add)
                _ = session.execute(endpoints_insert)

            if endpoints_info.to_update:
                self.update_objects(session, PubSubEndpoint, endpoints_info.to_update)

            # Commit topics and endpoints so that we can find them when we handle subscriptions below
            session.commit()

            # Load it again, now that we added topics and endpoints
            existing = self._get_existing_data(session, needs_subs=True)

            input_subscriptions = input.pubsub_subscription or []
            existing_subscriptions = existing.pubsub_subscription or []
            input_subscriptions = self._resolve_input_subscriptions(input_subscriptions, existing)
            subscriptions_info = self._find_subscriptions(input_subscriptions, existing_subscriptions)

            # Now we can enrich subscriptions too
            self._enrich_subscriptions(subscriptions_info.to_add)
            self._enrich_subscriptions(subscriptions_info.to_update)

            if subscriptions_info.to_add:
                subscriptions_insert = self.create_objects(PubSubSubscriptionTable, subscriptions_info.to_add)
                _ = session.execute(subscriptions_insert)

            if subscriptions_info.to_update:
                self.update_objects(session, PubSubSubscription, subscriptions_info.to_update)

            # Commit once more, this time around, it will include subscriptions
            session.commit()

        if topics_info.to_add:
            self.logger.info('Topics created: %s', len(topics_info.to_add))

        if topics_info.to_update:
            self.logger.info('Topics updated: %s', len(topics_info.to_update))

        if endpoints_info.to_add:
            self.logger.info('Endpoints created: %s', len(endpoints_info.to_add))

        if endpoints_info.to_update:
            self.logger.info('Endpoints updated: %s', len(endpoints_info.to_update))

        if subscriptions_info.to_add:
            self.logger.info('Subscriptions created: %s', len(subscriptions_info.to_add))

        if subscriptions_info.to_update:
            self.logger.info('Subscriptions updated: %s', len(subscriptions_info.to_update))

# ################################################################################################################################

    def _get_rest_conn_id_by_name(self, name:'str') -> 'int':

        if conn := self.server.worker_store.get_outconn_rest(name):
            conn_config = conn['config']
            conn_id = conn_config['id']
            return conn_id
        else:
            raise Exception(f'Outgoing REST connection not found -> {name}')

# ################################################################################################################################

    def _get_rest_conn_id_by_item(self, item:'strdict') -> 'int | None':

        if rest_connection := item.get('rest_connection'): # type: ignore
            rest_connection_id = self._get_rest_conn_id_by_name(rest_connection)
            return rest_connection_id

# ################################################################################################################################

    def _resolve_input_subscriptions(self, input_subscriptions:'dictlist', existing:'ObjectContainer') -> 'dictlist':

        out:'dictlist' = []

        for item in deepcopy(input_subscriptions):

            _ = item.pop('name', None)

            endpoint_name = item.pop('endpoint_name')
            endpoint = existing.get_endpoint_by_name(endpoint_name)

            endpoint_id = endpoint['id']
            endpoint_type = endpoint['endpoint_type']

            has_gd = item.get('has_gd', Default.Has_GD)
            wrap_one_msg_in_list = item.get('wrap_one_msg_in_list', Default.Wrap_One_Msg_In_List)
            delivery_err_should_block = item.get('delivery_err_should_block', Default.Delivery_Err_Should_Block)

            # Resolve a potential outgoing REST connection
            out_http_soap_id = self._get_rest_conn_id_by_item(item)

            # A new item needs to be created for each topic this endpoint is subscribed to ..
            for topic_name in item.pop('topic_list_json'):

                # .. turn a topic's name into its ID ..
                topic_id = existing.get_topic_id_by_name(topic_name)

                # .. build basic information about the subscription ..
                new_item:'strdict' = {
                    'topic_id': topic_id,
                    'endpoint_id': endpoint_id,
                    'delivery_method': item['delivery_method'],
                    'creation_time': self.time.utcnow_as_float(),
                    'sub_key': new_sub_key(endpoint_type),
                    'sub_pattern_matched': 'auto-import',
                    'has_gd': has_gd,
                    'wrap_one_msg_in_list': wrap_one_msg_in_list,
                    'delivery_err_should_block': delivery_err_should_block,
                    'out_http_soap_id': out_http_soap_id,
                }

                # .. append the item for later use ..
                out.append(new_item)

        # .. now, we can return everything to our caller.
        return out

# ################################################################################################################################

    def _find_subscriptions(self, incoming:'dictlist', existing:'dictlist') -> 'ItemsInfo':

        # Our response to produce
        out = ItemsInfo()
        out.to_add = []
        out.to_update = []

        for new_item in deepcopy(incoming):

            for existing_item in existing:
                subscription_id, topic_id, endpoint_id = existing_item
                if new_item['topic_id'] == topic_id and new_item['endpoint_id'] == endpoint_id:
                    new_item['id'] = subscription_id
                    _ = new_item.pop('sub_key', None)
                    _ = new_item.pop('creation_time', None)
                    _ = new_item.pop('sub_pattern_matched', None)
                    out.to_update.append(new_item)
                    break
            else:
                new_item['cluster_id'] = self.server.cluster_id
                new_item[Generic_Attr_Name] = None
                out.to_add.append(new_item)

        # .. now, we can return the response to our caller.
        return out

# ################################################################################################################################

    def _handle_basic_auth_input(self, incoming:'dictlist', existing:'dictlist') -> 'ItemsInfo':

        # Our response to produce
        out = ItemsInfo()
        out.to_add = []
        out.to_update = []

        # Go through each item that we potentially need to create and see if there is a match
        for new_item in deepcopy(incoming):
            for existing_item in existing:
                if existing_item['sec_type'] == Sec_Def_Type.BASIC_AUTH:
                    if new_item['name'] == existing_item['name']:
                        new_item['id'] = existing_item['id']
                        new_item['sec_type'] = existing_item['sec_type']
                        new_item['cluster_id'] = self.server.cluster_id
                        _ = new_item.pop('realm', None)
                        out.to_update.append(new_item)
                        break

            # .. if we are here, it means that there was no match, which means that this item truly is new ..
            else:

                # .. passwords are optional on input ..
                if not 'password' in new_item:
                    new_item['password'] = self.name + ' ' + cast_('str', CryptoManager.generate_secret(as_str=True))

                new_item['sec_type'] = Sec_Def_Type.BASIC_AUTH
                new_item['cluster_id'] = self.server.cluster_id
                out.to_add.append(new_item)

        # .. now, we can return the response to our caller.
        return out

# ################################################################################################################################

    def _get_basic_auth_realm_by_sec_name(self, incoming:'dictlist', name:'str') -> 'str':
        for item in incoming:
            if item['name'] == name:
                return item['realm']
        else:
            raise Exception(f'Security definition not found (realm) -> {name}')

# ################################################################################################################################

    def create_basic_auth(self, session:'SASession', values:'dictlist', incoming:'dictlist') -> 'None':

        # We need to create a new list with only these values
        # that the base table can support.
        sec_base_values = []

        for item in values:
            sec_base_item = deepcopy(item)
            _ = sec_base_item.pop('realm', None)
            sec_base_values.append(sec_base_item)

        # First, insert rows in the base table ..
        sec_base_insert = insert(SecurityBase).values(sec_base_values)
        _ = session.execute(sec_base_insert)
        session.commit()

        # .. now, get all of their IDs ..
        name_list:'any_' = [item['name'] for item in values]
        newly_added = get_object_list_by_name_list(session, SecurityBaseTable, name_list)

        to_add_basic_auth = []
        for item in values:
            for newly_added_item in newly_added:
                if item['name'] == newly_added_item['name']:
                    to_add_item = {
                        'id': newly_added_item['id'],
                        'realm': item['realm'],
                    }
                    to_add_basic_auth.append(to_add_item)
                    break

        _ = session.execute(HTTPBasicAuthInsert().values(to_add_basic_auth))
        session.commit()

# ################################################################################################################################

    def _enrich_endpoints(self, endpoints:'dictlist', sec_list:'dictlist') -> 'None':

        for item in endpoints:

            service = item.pop('service', None)
            service_name = item.pop('service_name', None)
            service_name = service or service_name

            _ = item.pop('ws_channel_name', None)
            _ = item.pop('sec_def', None)

            if service_name:
                service_id = self.server.service_store.get_service_id_by_name(service_name)
                item['service_id'] = service_id

            if sec_name := item.pop('sec_name', None):
                for sec_item in sec_list:
                    if sec_name == sec_item['name']:
                        security_id = sec_item['id']
                        item['security_id'] = security_id
                        break
                else:
                    if sec_name != Zato_No_Security:
                        raise Exception(f'Security definition not found -> {sec_name}')

# ################################################################################################################################

    def _enrich_topics(self, topics:'dictlist') -> 'None':

        for item in topics:

            if not Generic_Attr_Name in item:
                item[Generic_Attr_Name] = {}

            opaque1 = item[Generic_Attr_Name]
            opaque1['on_no_subs_pub'] = item.pop('on_no_subs_pub', None)
            opaque1['hook_service_name'] = item.pop('hook_service_name', None)

            item[Generic_Attr_Name] = dumps(opaque1)

# ################################################################################################################################

    def _enrich_subscriptions(self, subscriptions:'dictlist') -> 'None':

        for item in subscriptions:
            item['server_id'] = 1 # We always use the same server

# ################################################################################################################################

    def create_objects(self, table:'any_', values:'dictlist') -> 'any_':
        result = insert(table).values(values)
        return result

# ################################################################################################################################

    def update_objects(self, session:'SASession', table:'any_', values:'dictlist') -> 'any_':
        session.bulk_update_mappings(table, values)

# ################################################################################################################################

    def _find_items(self, incoming:'dictlist', existing:'dictlist') -> 'ItemsInfo':

        # Our response to produce
        out = ItemsInfo()
        out.to_add = []
        out.to_update = []

        # Go through each item that we potentially need to create and see if there is a match
        for new_item in incoming:

            # Turn WSX channel names into their IDs
            if ws_channel_name := new_item.get('ws_channel_name'):
                ws_channel_id:'int' = self.server.worker_store.get_web_socket_channel_id_by_name(ws_channel_name)
                new_item['ws_channel_id'] = ws_channel_id

            for existing_item in existing:
                if new_item['name'] == existing_item['name']:
                    new_item['id'] = existing_item['id']
                    new_item['cluster_id'] = self.server.cluster_id
                    out.to_update.append(new_item)
                    break

            # .. if we are here, it means that there was no match, which means that this item truly is new ..
            else:
                new_item['cluster_id'] = self.server.cluster_id
                out.to_add.append(new_item)

        # .. now, we can return the response to our caller.
        return out

# ################################################################################################################################

    def _get_sec_list(self, session:'SASession') -> 'dictlist':

        columns = [SecurityBaseTable.c.id, SecurityBaseTable.c.name, SecurityBaseTable.c.sec_type]
        out = get_object_list_by_columns(session, columns)
        return out

# ################################################################################################################################

    def _get_existing_topics(self, session:'SASession') -> 'dictlist':

        out = get_object_list(session, PubSubTopicTable)
        return out

# ################################################################################################################################

    def _get_existing_endpoints(self, session:'SASession') -> 'dictlist':

        columns = [
            PubSubEndpointTable.c.id,
            PubSubEndpointTable.c.name,
            PubSubEndpointTable.c.endpoint_type,
        ]

        out = get_object_list_by_columns(session, columns)
        return out

# ################################################################################################################################

    def _get_existing_subscriptions(self, session:'SASession') -> 'dictlist':

        columns = [
            PubSubSubscriptionTable.c.id,
            PubSubSubscriptionTable.c.topic_id,
            PubSubSubscriptionTable.c.endpoint_id,
        ]
        out = get_object_list_by_columns(session, columns)
        return out

# ################################################################################################################################

    def _get_existing_data(self, session:'SASession', *, needs_subs:'bool') -> 'ObjectContainer':

        # Our response to produce
        out = ObjectContainer()
        out.pubsub_topic = []
        out.pubsub_endpoint = []
        out.pubsub_subscription = []

        existing_topics = self._get_existing_topics(session)
        existing_endpoints = self._get_existing_endpoints(session)

        out.pubsub_topic.extend(existing_topics)
        out.pubsub_endpoint.extend(existing_endpoints)

        if needs_subs:
            existing_subscriptions = self._get_existing_subscriptions(session)
            out.pubsub_subscription.extend(existing_subscriptions)

        return out

# ################################################################################################################################
# ################################################################################################################################
