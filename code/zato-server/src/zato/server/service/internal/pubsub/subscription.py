# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from operator import itemgetter
from urllib.parse import quote

# Bunch
from bunch import Bunch, bunchify

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.matcher import PatternMatcher
from zato.common.pubsub.util import set_time_since
from zato.common.util.api import new_sub_key, utcnow
from zato.server.service import AsIs, PubSubMessage, Service
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

def _build_topic_objects_list(topic_data_list=None, topics=None, topic_data_by_name=None):
    """ Build topic objects with flags for frontend response.
    """
    topic_objects_list = []

    if topic_data_list:
        for item in topic_data_list:
            if isinstance(item, str):
                topic_item = {
                    'topic_name': item,
                    'is_pub_enabled': True,
                    'is_delivery_enabled': True
                }
            elif isinstance(item, dict):
                topic_item = {
                    'topic_name': item['topic_name'],
                    'is_pub_enabled': item.get('is_pub_enabled', True),
                    'is_delivery_enabled': item.get('is_delivery_enabled', True)
                }
            elif hasattr(item, 'topic_name'):
                topic_item = {
                    'topic_name': item.topic_name,
                    'is_pub_enabled': getattr(item, 'is_pub_enabled', True),
                    'is_delivery_enabled': getattr(item, 'is_delivery_enabled', True)
                }
            else:
                topic_item = {
                    'topic_name': str(item),
                    'is_pub_enabled': True,
                    'is_delivery_enabled': True
                }
            topic_objects_list.append(topic_item)

    elif topics and topic_data_by_name:
        for topic in topics:
            topic_name = topic['topic_name'] if isinstance(topic, dict) else topic.get('name', str(topic))
            topic_data = topic_data_by_name[topic_name]
            topic_item = {
                'topic_name': topic_name,
                'is_pub_enabled': topic_data['is_pub_enabled'],
                'is_delivery_enabled': topic_data['is_delivery_enabled']
            }
            topic_objects_list.append(topic_item)

    topic_objects_list.sort(key=itemgetter('topic_name'))
    return topic_objects_list

# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.common.typing_ import strdict, strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Action_Subsctibe = 'Subscribe'
    Action_Unsubsctibe = 'Unsubscribe'

# ################################################################################################################################
# ################################################################################################################################

_push_type = PubSub.Push_Type

# ################################################################################################################################
# ################################################################################################################################

def get_topic_link(topic_name:'str', is_pub_enabled:'bool', is_delivery_enabled:'bool') -> 'str':

    pub_class = 'is-pub-enabled-true' if is_pub_enabled else 'is-pub-enabled-false'
    delivery_class = 'is-delivery-enabled-true' if is_delivery_enabled else 'is-delivery-enabled-false'

    topic_link = '<a href="/zato/pubsub/topic/?cluster=1&query={}" class="{} {}">{}</a>'.format(
        quote(topic_name), pub_class, delivery_class, topic_name)
    return topic_link

# ################################################################################################################################
# ################################################################################################################################

def _get_sec_by_id(server, sec_base_id):
    """ Look up security definition from its ID via the config store.
    """
    for item in server.config_store.get_list('security'):
        if item.get('id') == sec_base_id:
            return item
    raise Exception('Security definition with id `{}` not found'.format(sec_base_id))

# ################################################################################################################################

def _find_security(server, username=None, sec_name=None):
    """ Look up security definition by username or sec_name via the config store.
    """
    for item in server.config_store.get_list('security'):
        if username and item.get('username') == username:
            return item
        if sec_name and item.get('name') == sec_name:
            return item
    lookup = 'username={}'.format(username) if username else 'sec_name={}'.format(sec_name)
    raise Exception('Security definition not found: {}'.format(lookup))

# ################################################################################################################################

def _topic_exists(server, topic_name):
    """ Check whether a topic exists in the config store.
    """
    for item in server.config_store.get_list('pubsub_topic'):
        if item.get('name') == topic_name:
            return True
    return False

# ################################################################################################################################

def _check_permission(server, sec_name, topic_name):
    """ Check whether a security definition has permission for a topic using config store permissions.
    Returns True if allowed, False otherwise.
    """
    for perm in server.config_store.get_list('pubsub_permission'):
        perm_sec = perm.get('security') or perm.get('name')
        if perm_sec != sec_name:
            continue

        pattern_lines = (perm.get('pattern') or '').splitlines()
        access_type = perm.get('access_type', 'subscriber')
        permissions_list = [{'pattern': p.strip(), 'access_type': access_type} for p in pattern_lines if p.strip()]

        if permissions_list:
            matcher = PatternMatcher()
            matcher.add_client(sec_name, permissions_list)
            result = matcher.evaluate(sec_name, topic_name, 'subscribe')
            if result.is_ok:
                return True

    return False

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of pub/sub subscriptions available.
    """
    input = 'cluster_id', '-needs_password'
    output = 'id', 'sub_key', 'is_delivery_active', 'is_pub_active', 'created', AsIs('topic_link_list'), 'sec_base_id', \
        'sec_name', 'username', 'delivery_type', 'push_type', 'rest_push_endpoint_id', 'push_service_name', \
        '-rest_push_endpoint_name', AsIs('-topic_name_list'), '-password'
    output_repeated = True

    def handle(self):
        items = self.server.config_store.get_list('pubsub_subscription')

        sec_by_name = {}
        for sec in self.server.config_store.get_list('security'):
            sec_by_name[sec.get('name')] = sec

        out = []
        for item in items:

            sec_name = item.get('sec_name') or item.get('security') or ''
            sec_def = sec_by_name.get(sec_name, {})

            topic_list = item.get('topic_list') or item.get('topic_name_list') or []
            topic_link_list = []
            for t in topic_list:
                topic_name = t if isinstance(t, str) else t.get('topic_name', '')
                topic_link_list.append(get_topic_link(topic_name, True, True))

            enriched = dict(item)
            enriched.setdefault('sub_key', item.get('sub_key', ''))
            enriched.setdefault('is_delivery_active', item.get('is_delivery_active', True))
            enriched.setdefault('is_pub_active', item.get('is_pub_active', True))
            enriched.setdefault('created', item.get('created', ''))
            enriched.setdefault('sec_base_id', sec_def.get('id', 0))
            enriched.setdefault('sec_name', sec_name)
            enriched.setdefault('username', sec_def.get('username', ''))
            enriched.setdefault('push_type', item.get('push_type', ''))
            enriched.setdefault('rest_push_endpoint_id', item.get('rest_push_endpoint_id') or item.get('push_rest_endpoint') or '')
            enriched['topic_link_list'] = topic_link_list
            enriched['topic_name_list'] = [t if isinstance(t, str) else t.get('topic_name', '') for t in topic_list]

            out.append(enriched)

        self.response.payload = self._paginate_list(out)

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new pub/sub subscription.
    """
    input = 'cluster_id', AsIs('topic_name_list'), 'sec_base_id', 'delivery_type', \
        '-is_delivery_active', '-is_pub_active', '-push_type', '-rest_push_endpoint_id', '-push_service_name', '-sub_key'
    output = 'id', 'sub_key', 'is_delivery_active', 'is_pub_active', 'created', 'sec_name', 'delivery_type', \
        AsIs('-topic_name_list'), AsIs('-topic_link_list')

    def handle(self):

        input = self.request.input

        topic_data_list = input.topic_name_list
        topic_objects_list = _build_topic_objects_list(topic_data_list=topic_data_list)

        sec_def = _get_sec_by_id(self.server, input.sec_base_id)
        sec_name = sec_def['name']
        username = sec_def.get('username', '')

        sub_key = input.sub_key or new_sub_key(sec_name)
        created = str(utcnow())

        topic_link_list = []
        for topic_obj in topic_objects_list:
            topic_link = get_topic_link(topic_obj['topic_name'], topic_obj['is_pub_enabled'], topic_obj['is_delivery_enabled'])
            topic_link_list.append(topic_link)

        config_key = '{}:{}'.format(sec_name, input.delivery_type)

        data = {
            'sub_key': sub_key,
            'is_delivery_active': input.is_delivery_active,
            'is_pub_active': input.is_pub_active,
            'created': created,
            'sec_base_id': input.sec_base_id,
            'sec_name': sec_name,
            'username': username,
            'security': sec_name,
            'delivery_type': input.delivery_type,
            'push_type': input.get('push_type') or '',
            'rest_push_endpoint_id': input.get('rest_push_endpoint_id'),
            'push_service_name': input.get('push_service_name') or '',
            'topic_name_list': topic_objects_list,
            'topic_link_list': ', '.join(sorted(topic_link_list)),
        }

        self.server.config_store.set('pubsub_subscription', config_key, data)

        self.response.payload.id = config_key
        self.response.payload.sub_key = sub_key
        self.response.payload.is_delivery_active = input.is_delivery_active
        self.response.payload.is_pub_active = input.is_pub_active
        self.response.payload.created = created
        self.response.payload.sec_name = sec_name
        self.response.payload.delivery_type = input.delivery_type

        self.response.payload.topic_name_list = topic_objects_list
        self.response.payload.topic_link_list = sorted(topic_link_list)

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates a pub/sub subscription.
    """
    input = 'sub_key', 'cluster_id', AsIs('topic_name_list'), 'sec_base_id', 'delivery_type', \
        '-is_delivery_active', '-is_pub_active', '-push_type', '-rest_push_endpoint_id', '-push_service_name'
    output = 'id', 'sub_key', 'is_delivery_active', 'is_pub_active', 'sec_name', 'delivery_type', \
        AsIs('-topic_name_list'), AsIs('-topic_link_list')

    def handle(self):

        input = self.request.input

        topic_data_list = input.get('topic_name_list') or []

        # If no topics are provided, delete the subscription
        if not topic_data_list:
            self.logger.info('No topics provided for subscription %s, deleting subscription', input.sub_key)

            for item in self.server.config_store.get_list('pubsub_subscription'):
                if item.get('sub_key') == input.sub_key:
                    sec_name = item.get('security') or item.get('sec_name')
                    config_key = '{}:{}'.format(sec_name, item.get('delivery_type', ''))
                    self.server.config_store.delete('pubsub_subscription', config_key)
                    break

            sec_def = _get_sec_by_id(self.server, input.sec_base_id)

            self.response.payload.id = input.sub_key
            self.response.payload.sub_key = input.sub_key
            self.response.payload.is_pub_active = input.get('is_pub_active', True)
            self.response.payload.is_delivery_active = input.get('is_delivery_active', True)
            self.response.payload.sec_name = sec_def['name']
            self.response.payload.delivery_type = input.delivery_type
            self.response.payload.topic_name_list = []
            self.response.payload.topic_link_list = []
            return

        topic_objects_list = _build_topic_objects_list(topic_data_list=topic_data_list)

        sec_def = _get_sec_by_id(self.server, input.sec_base_id)
        sec_name = sec_def['name']
        username = sec_def.get('username', '')

        topic_link_list = []
        for topic_obj in topic_objects_list:
            topic_link = get_topic_link(topic_obj['topic_name'], topic_obj['is_pub_enabled'], topic_obj['is_delivery_enabled'])
            topic_link_list.append(topic_link)

        config_key = '{}:{}'.format(sec_name, input.delivery_type)

        # Find the existing entry to preserve created/sub_key
        existing = None
        for item in self.server.config_store.get_list('pubsub_subscription'):
            if item.get('sub_key') == input.sub_key:
                existing = item
                break

        data = {
            'sub_key': input.sub_key,
            'is_delivery_active': input.get('is_delivery_active', True),
            'is_pub_active': input.get('is_pub_active', True),
            'created': existing.get('created', str(utcnow())) if existing else str(utcnow()),
            'sec_base_id': input.sec_base_id,
            'sec_name': sec_name,
            'username': username,
            'security': sec_name,
            'delivery_type': input.delivery_type,
            'push_type': input.get('push_type') or '',
            'rest_push_endpoint_id': input.get('rest_push_endpoint_id'),
            'push_service_name': input.get('push_service_name') or '',
            'topic_name_list': topic_objects_list,
            'topic_link_list': ', '.join(sorted(topic_link_list)),
        }

        self.server.config_store.set('pubsub_subscription', config_key, data)

        self.response.payload.id = config_key
        self.response.payload.sub_key = input.sub_key
        self.response.payload.is_pub_active = data['is_pub_active']
        self.response.payload.is_delivery_active = data['is_delivery_active']
        self.response.payload.sec_name = sec_name
        self.response.payload.delivery_type = input.delivery_type

        self.response.payload.topic_name_list = topic_objects_list
        self.response.payload.topic_link_list = sorted(topic_link_list)

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a pub/sub subscription.
    """
    skip_before_handle = True

    input = '-id', '-sub_key', '-should_call_pubsub_consumer_backend', AsIs('-session')

    def handle(self):

        input_id = self.request.input.get('id')
        sub_key = self.request.input.get('sub_key')

        for item in self.server.config_store.get_list('pubsub_subscription'):
            match_by_id = input_id and (item.get('id') == input_id)
            match_by_key = sub_key and (item.get('sub_key') == sub_key)

            if match_by_id or match_by_key:
                sec_name = item.get('security') or item.get('sec_name')
                delivery_type = item.get('delivery_type', '')
                config_key = '{}:{}'.format(sec_name, delivery_type)
                self.server.config_store.delete('pubsub_subscription', config_key)
                return

        raise Exception('Pub/sub subscription not found (id:`{}`, sub_key:`{}`)'.format(input_id, sub_key))

# ################################################################################################################################
# ################################################################################################################################

class _BaseModifyTopicList(AdminService):
    """ Base class for Subscribe/Unsubscribe operations.
    """
    action = '<Action-Not-Set>'

    input = AsIs('topic_name_list'), '-username', '-sec_name', '-is_delivery_active', '-delivery_type', '-push_type', \
        '-rest_push_endpoint_id', '-push_service_name', '-sub_key'
    output = AsIs('-topic_name_list'),

# ################################################################################################################################

    def _modify_topic_list(self, existing_topic_names:'strlist', new_topic_names:'strlist') -> 'strlist':
        raise NotImplementedError('Subclasses must implement _modify_topic_list')

# ################################################################################################################################

    def _get_subscriptions_by_sec(self, cluster_id, sec_base_id):
        """ Get subscriptions for a security definition.
        """
        get_list_request = {
            'cluster_id': cluster_id,
            'sec_base_id': sec_base_id
        }

        get_list_response = self.invoke('zato.pubsub.subscription.get-list', get_list_request)

        if isinstance(get_list_response, dict):
            return get_list_response.get('data', [])
        return get_list_response

# ################################################################################################################################

    def handle(self):

        input = self.request.input
        cluster_id = 1

        # Find security definition by username or sec_name via the config store
        sec_def = _find_security(
            self.server,
            username=getattr(input, 'username', None),
            sec_name=getattr(input, 'sec_name', None)
        )

        sec_base_id = sec_def['id']
        sec_name = sec_def['name']
        sec_username = sec_def.get('username', '')

        lookup_field = 'username' if getattr(input, 'username', None) else 'sec_name'
        lookup_value = getattr(input, 'username', None) or getattr(input, 'sec_name', None)

        # Find any existing subscriptions using GetList service
        subscriptions = self._get_subscriptions_by_sec(cluster_id, sec_base_id)

        # Check if there's a subscription for THIS security definition
        has_subscription_for_this_sec = False
        if subscriptions:
            for item in subscriptions:
                item_sec_base_id = item.get('sec_base_id') if isinstance(item, dict) else getattr(item, 'sec_base_id', None)
                if item_sec_base_id == sec_base_id:
                    has_subscription_for_this_sec = True
                    break

        if not has_subscription_for_this_sec:

            if self.action == ModuleCtx.Action_Subsctibe:

                create_request = Bunch()
                create_request.sub_key = input.sub_key
                create_request.cluster_id = cluster_id
                create_request.topic_name_list = input.topic_name_list
                create_request.sec_base_id = sec_base_id
                create_request.delivery_type = input.delivery_type
                create_request.is_delivery_active = input.is_delivery_active
                create_request.push_type = input.push_type
                create_request.rest_push_endpoint_id = input.rest_push_endpoint_id
                create_request.push_service_name = input.push_service_name

                _ = self.invoke('zato.pubsub.subscription.create', create_request)
                return

            elif self.action == ModuleCtx.Action_Unsubsctibe:
                self.response.payload.topic_name_list = []
                return

        # Extract subscriptions for this security definition
        current_sub = None

        for item in subscriptions:
            item = bunchify(item)
            if item.sec_base_id == sec_base_id:
                current_sub = item
                break
        else:
            err_msg = '{}: Could not find subscription for input {} `{}` -> {}'.format(
                self.action, lookup_field, lookup_value, subscriptions)
            raise Exception(err_msg)

        # Find topics and check permissions
        new_topic_names = []

        for topic_name in input.topic_name_list:

            if not _topic_exists(self.server, topic_name):
                raise Exception('Topic `{}` not found'.format(topic_name))

            if not _check_permission(self.server, sec_name, topic_name):
                msg = 'User `{}` does not have permission for action `{}` on topic `{}`'.format(
                    sec_username, self.action, topic_name)
                raise Exception(msg)

            new_topic_names.append(topic_name)

        # Get current subscription and topic names
        sub_key = current_sub.sub_key
        existing_topic_names = current_sub.topic_name_list

        # Apply subclass-specific modification logic
        all_topic_names = self._modify_topic_list(existing_topic_names, new_topic_names)

        # Sort the final list by topic name
        all_topic_names.sort(key=itemgetter('topic_name'))

        # Update existing subscription with the combined topics
        request = Bunch()
        request.sub_key = sub_key
        request.cluster_id = cluster_id
        request.topic_name_list = all_topic_names
        request.sec_base_id = sec_base_id
        request.delivery_type = current_sub.delivery_type
        request.is_delivery_active = current_sub.is_delivery_active
        request.push_service_name = current_sub.push_service_name
        request.push_type = current_sub.push_type
        request.rest_push_endpoint_id = current_sub.rest_push_endpoint_id

        _ = self.invoke('zato.pubsub.subscription.edit', request)

        self.response.payload.topic_name_list = all_topic_names

# ################################################################################################################################
# ################################################################################################################################

class Subscribe(_BaseModifyTopicList):
    """ Subscribes security definition to one or more topics.
    """
    action = ModuleCtx.Action_Subsctibe

    def _modify_topic_list(self, existing_topic_names:'strlist', new_topic_names:'strlist') -> 'strlist':

        # Start with existing topics
        all_topic_names = existing_topic_names[:]

        # Extract topic names from existing items (may be Bunch or dict)
        existing_names = set()
        for item in existing_topic_names:
            if hasattr(item, 'topic_name'):
                existing_names.add(item.topic_name)
            elif isinstance(item, dict):
                existing_names.add(item.get('topic_name', item))
            else:
                existing_names.add(item)

        # Add new topics that are not already in the list
        for new_topic_name in new_topic_names:
            topic_name = new_topic_name.topic_name if hasattr(new_topic_name, 'topic_name') else new_topic_name
            if topic_name not in existing_names:
                new_entry = Bunch(topic_name=topic_name, is_delivery_enabled=True, is_pub_enabled=True)
                all_topic_names.append(new_entry)

        return all_topic_names

# ################################################################################################################################
# ################################################################################################################################

class Unsubscribe(_BaseModifyTopicList):
    """ Unsubscribes security definition from one or more topics.
    """
    action = ModuleCtx.Action_Unsubsctibe

    def _modify_topic_list(self, existing_topic_names:'strlist', new_topic_names:'strlist') -> 'strlist':

        # Extract topic names to remove (may be Bunch, dict, or string)
        names_to_remove = set()
        for item in new_topic_names:
            if hasattr(item, 'topic_name'):
                names_to_remove.add(item.topic_name)
            elif isinstance(item, dict):
                names_to_remove.add(item.get('topic_name', item))
            else:
                names_to_remove.add(item)

        # Filter out topics to remove
        all_topic_names = []
        for item in existing_topic_names:
            if hasattr(item, 'topic_name'):
                topic_name = item.topic_name
            elif isinstance(item, dict):
                topic_name = item.get('topic_name', item)
            else:
                topic_name = item

            if topic_name not in names_to_remove:
                all_topic_names.append(item)

        return all_topic_names

# ################################################################################################################################
# ################################################################################################################################

class HandleDelivery(Service):

    def build_business_message(self, input:'strdict', sub_key:'str', delivery_count:'int') -> 'PubSubMessage':

        msg = PubSubMessage()

        msg.msg_id = input['msg_id']
        msg.correl_id = input['correl_id']

        msg.data = input['data']
        msg.size = input['size']

        msg.publisher = input['publisher']

        msg.pub_time_iso = input['pub_time_iso']
        msg.recv_time_iso = input['recv_time_iso']

        msg.priority = input['priority']
        msg.delivery_count = delivery_count

        msg.expiration = input['expiration']
        msg.expiration_time_iso = input['expiration_time_iso']

        msg.sub_key = sub_key
        msg.topic_name = input['topic_name']

        # Calculate and set time deltas
        current_time = utcnow()
        set_time_since(input, input['pub_time_iso'], input['recv_time_iso'], current_time)
        msg.time_since_pub = input['time_since_pub']
        msg.time_since_recv = input['time_since_recv']

        # These are optional
        if ext_client_id := input.get('ext_client_id'):
            msg.ext_client_id = ext_client_id

        if in_reply_to := input.get('in_reply_to'):
            msg.in_reply_to = in_reply_to

        return msg

# ################################################################################################################################

    def build_rest_message(self, input:'strdict', outconn_config:'strdict') -> 'strdict':

        out_msg = {}

        for input_key, input_value in input.items():

            if input_key == 'publisher':

                for sec_config in self.server.worker_store.worker_config.basic_auth.values():

                    sec_config = sec_config['config']

                    if sec_config['username'] == input_value:
                        publisher = sec_config['name']
                        break

                else:
                    publisher = 'notset'

                out_msg['publisher'] = publisher

            else:
                out_msg[input_key] = input_value

        current_time = utcnow()
        set_time_since(out_msg, input['pub_time_iso'], input['recv_time_iso'], current_time)

        return out_msg

# ################################################################################################################################

    def handle(self):

        # Local aliases
        input:'strdict' = self.request.raw_request

        # Extract the metadata - and delete it from input because we don't want to deliver it
        meta = input.pop('_zato_meta')

        # Get the individual variables
        sub_key = meta['sub_key']
        delivery_count = meta['delivery_count']

        # Get the detailed configuration of the subscriber
        config = self.server.worker_store.get_pubsub_sub_config(sub_key)

        if config.push_type == _push_type.Service:

            service_name = config['push_service_name']
            msg = self.build_business_message(input, sub_key, delivery_count)
            _ = self.invoke(service_name, msg)

        elif config.push_type == _push_type.REST:

            conn_name = config['rest_push_endpoint_name']
            conn = self.out.rest[conn_name].conn
            out_msg = self.build_rest_message(input, config)
            _ = conn.post(self.cid, out_msg)

        else:
            msg = 'Unrecognized push_type: {} ({} - {})'.format(repr(input.get('push_type')), input.get('msg_id'), input.get('correl_id'))
            raise Exception(msg)

# ################################################################################################################################
# ################################################################################################################################
