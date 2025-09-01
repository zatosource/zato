# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK
from logging import getLogger
from traceback import format_exc

# Kombu
from kombu.connection import Connection as KombuConnection
from kombu.entity import Exchange, Queue

# requests
import requests
from requests.auth import HTTPBasicAuth

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.util import get_broker_config
from zato.common.util.api import new_cid_broker_client, wait_for_predicate

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.common import BrokerConfig
    from zato.common.typing_ import any_, dictlist, strdictnone, strlist, callable_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

class BrokerConnection(KombuConnection):

    def ensure_connection(self, *args, **kwargs):
        kwargs['timeout'] = None
        _ = self._ensure_connection(*args, **kwargs)
        return self

# ################################################################################################################################
# ################################################################################################################################

class AMQP:

    def _wait_for_completion(self, func:'callable_', log_message:'str', *args:'any_', **kwargs:'any_') -> 'None':

        def _predicate_func():
            try:
                func(*args, **kwargs)
                return True
            except Exception as e:
                logger.info(f'{log_message}, will retry: {e}')
                return False

        _ = wait_for_predicate(
            _predicate_func,
            100_000_000,  # Wait forever
            2.0,          # Check every 2 seconds
            jitter=0.2
        )

# ################################################################################################################################

    def get_connection(self, broker_config:'BrokerConfig | None'=None, needs_ensure:'bool'=True) -> 'BrokerConnection':
        """ Returns a new AMQP connection object using broker configuration parameters.
        """
        # Get broker configuration
        broker_config = get_broker_config()

        # Split host and port from address
        host, port = broker_config.address.split(':')
        port = int(port)

        # Create and return a new connection
        conn = BrokerConnection(
            hostname=host,
            port=port,
            userid=broker_config.username,
            password=broker_config.password,
            virtual_host=broker_config.vhost,
            transport=broker_config.protocol,
        )

        # Make sure we are connected
        _ = conn.ensure_connection(timeout=1)

        return conn

# ################################################################################################################################

    def create_bindings(
        self,
        cid: 'str',
        sub_key: 'str',
        exchange_name: 'str',
        queue_name: 'str',
        routing_key: 'str',
        conn: 'BrokerConnection | None'=None,
        queue_arguments: 'strdictnone'=None,
    ) -> 'None':

        # Make sure we have a cid
        cid = cid or new_cid_broker_client()

        # Get broker connection from input or build a new one
        if conn:
            should_close = False
        else:
            conn = self.get_connection()
            should_close = True

        # Customize the queue per our needs ..
        queue_arguments = queue_arguments or {}
        queue_arguments.update({
            'x-queue-type': 'quorum',
            'x-delivery-limit': PubSub.Max_Repeats
        })

        # Create exchange and queue objects
        exchange = Exchange(exchange_name, type='topic', durable=True)
        queue = Queue(name=queue_name, exchange=exchange, routing_key=routing_key, durable=True, queue_arguments=queue_arguments)

        # Bind the queue to the exchange with the topic name as the routing key
        logger.debug(f'[{cid}] [{sub_key}] Configuring bindings for exchange={exchange.name} -> queue={queue_name} (topic={routing_key})')

        _ = queue.maybe_bind(conn)
        _ = queue.declare()
        _ = queue.bind_to(
            exchange=exchange, # type: ignore
            routing_key=routing_key
        )

        # Close the connection if it was opened by us
        if should_close:
            conn.close()

# ################################################################################################################################

    def delete_bindings(
        self,
        cid: 'str',
        sub_key: 'str',
        exchange_name: 'str',
        queue_name: 'str',
        routing_key: 'str',
        conn: 'BrokerConnection | None'=None,
    ) -> 'None':

        # Get broker connection from input or build a new one
        conn = conn or self.get_connection()

        # Create exchange and queue objects
        exchange = Exchange(exchange_name, type='topic', durable=True)

        # Unbind the queue from the exchange with the topic name as the routing key

        logger.debug(f'[{cid}] [{sub_key}] Removing bindings for exchange={exchange.name} -> queue={queue_name} (topic={routing_key})')

        # Get a channel from the connection
        channel = conn.channel()

        # Unbind the queue from the exchange
        _ = channel.queue_unbind(
            queue=queue_name,
            exchange=exchange_name,
            routing_key=routing_key
        )

# ################################################################################################################################

    def delete_queue(self, cid:'str', queue_name:'str') -> 'None':
        """ Explicitly deletes a queue from the broker.
        """
        try:
            conn = self.get_connection()
            channel = conn.channel()

            channel.queue_delete(queue=queue_name)

            # Log only if it's not a reply to queue - there are too many of them to do it

            if not queue_name.startswith(PubSub.Prefix.Reply_Queue):
                logger.info(f'[{cid}] Deleted queue: {queue_name}')

        except Exception:

            logger.warning(f'[{cid}] Error deleting queue `{queue_name}` -> {format_exc()}')
            raise

# ################################################################################################################################

    def get_bindings(
        self,
        cid: 'str',
        exchange_name: 'str',
    ) -> 'dictlist':

        # Get binding information

        logger.debug(f'[{cid}] Getting bindings for exchange={exchange_name}')

        # We'll store binding information here
        binding_info = []

        # Get broker configuration
        broker_config = get_broker_config()

        # Extract host and port information
        host, _ = broker_config.address.split(':')

        # Default management API port
        rabbitmq_api_port = 15672

        # The management API URL includes the vhost encoded as %2F for default vhost
        vhost_encoded = broker_config.vhost.replace('/', '%2F')

        # Construct the API URL for this exchange's bindings
        api_url = f'http://{host}:{rabbitmq_api_port}/api/exchanges/{vhost_encoded}/{exchange_name}/bindings/source'

        # Make the request to the RabbitMQ API
        response = requests.get(
            api_url,
            auth=HTTPBasicAuth(broker_config.username, broker_config.password),
            headers={'Content-Type': 'application/json'},
            timeout=20
        )

        if not response.status_code == OK:
            msg = f'[{cid}] Failed to get bindings: API returned: {response.text}'
            raise Exception(msg)

        else:

            # Parse bindings from response
            bindings_data = response.json()

            # Process each binding
            for binding in bindings_data:

                # Only include bindings to queues (not to other exchanges)
                if binding['destination_type'] == 'queue':
                    binding_info.append({
                        'queue': binding['destination'],
                        'routing_key': binding['routing_key'],
                        'exchange': binding['source'],
                        'arguments': binding.get('arguments') or {},
                        'vhost': binding['vhost'],
                    })

        return binding_info

# ################################################################################################################################

    def update_bindings(
        self,
        cid: 'str',
        sub_key: 'str',
        exchange_name: 'str',
        queue_name: 'str',
        new_routing_key_list: 'strlist',
        conn: 'BrokerConnection | None'=None,
    ) -> 'dict':

        # Get broker connection from input or build a new one
        conn = conn or self.get_connection()

        # Extract current routing keys for this queue
        current_routing_keys = []
        queue_bindings = self.get_bindings_by_queue(cid, queue_name, exchange_name)

        for binding in queue_bindings:
            current_routing_keys.append(binding['routing_key'])

        # Convert lists to sets for comparison
        current_keys_set = set(current_routing_keys)
        new_keys_set = set(new_routing_key_list)

        # If sets are identical, do nothing

        if current_keys_set == new_keys_set:
            logger.debug(f'[{cid}] [{sub_key}] Routing keys unchanged for exchange={exchange_name} -> queue={queue_name}')
            return {'added': [], 'removed': []}

        logger.info(f'[{cid}] [{sub_key}] Current routing keys: {current_routing_keys}')
        logger.info(f'[{cid}] [{sub_key}] New routing keys: {new_routing_key_list}')

        # Find routing keys to add (in new list but not in current list)
        added_keys = []
        for routing_key in new_routing_key_list:
            if routing_key not in current_routing_keys:
                logger.info(f'[{cid}] [{sub_key}] Adding binding: {routing_key}')
                self.create_bindings(cid, sub_key, exchange_name, queue_name, routing_key, conn)
                added_keys.append(routing_key)

        # Find routing keys to remove (in current list but not in new list)
        removed_keys = []
        for routing_key in current_routing_keys:
            if routing_key not in new_routing_key_list:
                logger.info(f'[{cid}] [{sub_key}] Removing binding: {routing_key}')
                self.delete_bindings(cid, sub_key, exchange_name, queue_name, routing_key, conn)
                removed_keys.append(routing_key)

        logger.info(f'[{cid}] [{sub_key}] Updated bindings for exchange={exchange_name} -> queue={queue_name} -> {new_routing_key_list}')

        return {'added': added_keys, 'removed': removed_keys}

# ################################################################################################################################

    def delete_topic(
        self,
        cid: 'str',
        topic_name: 'str',
        exchange_name: 'str' = 'pubsubapi',
        conn: 'BrokerConnection | None' = None,
    ) -> 'None':
        """ Deletes a topic by removing all bindings with the matching routing key.
        """

        # Get broker connection from input or build a new one
        conn = conn or self.get_connection()

        # Find all bindings with routing key matching this topic
        topic_bindings = self.get_bindings_by_routing_key(cid, exchange_name, topic_name)

        # If no bindings found, just return silently
        if not topic_bindings:
            return


        logger.info(f'[{cid}] Removing topic bindings -> {topic_name} -> {topic_bindings}')

        # Delete each binding
        for binding in topic_bindings:

            # Queue name and sub_key are the same thing
            sub_key = binding['queue']
            self.delete_bindings(cid, sub_key, exchange_name, sub_key, topic_name, conn)

        logger.info(f'[{cid}] Topic {topic_name} successfully removed from exchange {exchange_name}')

# ################################################################################################################################

    def get_bindings_by_queue(self, cid:'str', queue_name:'str', exchange_name:'str') -> 'dictlist':
        """ Returns all bindings that point to the specified queue.
        """
        # Get all bindings for this exchange
        bindings = self.get_bindings(cid, exchange_name)

        # Filter bindings by queue name
        out = []

        for binding in bindings:
            if binding['queue'] == queue_name:
                out.append(binding)

        return out

# ################################################################################################################################

    def queue_has_bindings(self, cid:'str', queue_name:'str', exchange_name:'str') -> 'bool':
        """ Returns True if the queue has any bindings, False otherwise.
        """
        bindings = self.get_bindings_by_queue(cid, queue_name, exchange_name)
        return bool(bindings)

# ################################################################################################################################

    def get_bindings_by_routing_key(self, cid:'str', exchange_name:'str', routing_key:'str') -> 'dictlist':
        """ Returns all bindings that match the specified routing key.
        """
        # Get all bindings for this exchange
        bindings = self.get_bindings(cid, exchange_name)

        # Filter bindings by routing key
        out = []

        for binding in bindings:
            if binding['routing_key'] == routing_key:
                out.append(binding)

        return out

# ################################################################################################################################

    def _rename_topic(
        self,
        cid: 'str',
        old_topic_name: 'str',
        new_topic_name: 'str',
        exchange_name: 'str',
        conn: 'BrokerConnection | None' = None,
    ) -> 'None':
        """ Renames a topic by removing all old bindings and creating new ones with the new name.
        """

        # Get broker connection from input or build a new one
        conn = conn or self.get_connection()

        # Find all bindings with routing key matching the old topic
        topic_bindings = self.get_bindings_by_routing_key(cid, exchange_name, old_topic_name)

        # If no bindings found, just return silently

        if not topic_bindings:
            logger.info(f'[{cid}] Nothing to rename, no bindings found for `{old_topic_name}` in `{exchange_name}`')
            return

        count = len(topic_bindings)
        binding_text = 'binding' if count == 1 else 'bindings'
        logger.info(f'[{cid}] Renaming topic {old_topic_name} to {new_topic_name}, found {count} {binding_text}')

        # Store binding information before deleting
        queue_names = []
        for binding in topic_bindings:
            queue_names.append(binding['queue'])

        # Delete all old bindings first
        for binding in topic_bindings:
            queue_name = binding['queue']
            self.delete_bindings(
                cid,
                queue_name,  # sub_key is the same as queue_name
                exchange_name,
                queue_name,
                old_topic_name,
                conn
            )

        # Create new bindings
        for queue_name in queue_names:
            self.create_bindings(
                cid,
                queue_name,  # sub_key is the same as queue_name
                exchange_name,
                queue_name,
                new_topic_name,
                conn
            )

        logger.info(f'[{cid}] Successfully renamed topic `{old_topic_name}` to `{new_topic_name}`')

# ################################################################################################################################

    def rename_topic(self, *args, **kwargs) -> 'None':
        self._wait_for_completion(self._rename_topic, 'Topic rename failed', *args, **kwargs)

# ################################################################################################################################

    def _create_internal_queue(self, queue_name:'str') -> 'None':
        self.create_bindings('', 'n/a', 'components', queue_name, queue_name)

# ################################################################################################################################

    def create_internal_queue(self, *args, **kwargs) -> 'None':
        self._wait_for_completion(self._create_internal_queue, 'Queue creation failed', *args, **kwargs)

# ################################################################################################################################
# ################################################################################################################################
