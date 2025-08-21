# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from http.client import NO_CONTENT, NOT_FOUND, OK
from logging import getLogger
from urllib.parse import quote

# Requests
import requests
from requests.exceptions import RequestException

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.common import BrokerConfig

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Max_Length = OK

# ################################################################################################################################
# ################################################################################################################################

def get_broker_config() -> 'BrokerConfig':

    config = BrokerConfig()

    config.protocol = os.environ['Zato_Broker_Protocol']
    config.address = os.environ['Zato_Broker_Address']
    config.vhost = os.environ['Zato_Broker_Virtual_Host']
    config.username = os.environ['Zato_Broker_Username']
    config.password = os.environ['Zato_Broker_Password']

    return config

# ################################################################################################################################
# ################################################################################################################################

def validate_topic_name(topic_name:'str') -> 'None':
    """ Validate topic name according to pub/sub rules.

    Raises ValueError if validation fails.
    """
    if not topic_name:
        raise ValueError('Topic name cannot be empty')

    if len(topic_name) > ModuleCtx.Max_Length:
        raise ValueError(f'Topic name exceeds maximum length of {ModuleCtx.Max_Length} characters: {len(topic_name)}')

    if '#' in topic_name:
        raise ValueError('Topic name cannot contain "#" character')

    if not _is_ascii_only(topic_name):
        raise ValueError(f'Topic name contains non-ASCII characters: {topic_name}')

# ################################################################################################################################

def validate_pattern(pattern:'str') -> 'None':
    """ Validate pattern according to pub/sub rules.

    Raises ValueError if validation fails.
    """
    if not pattern:
        raise ValueError('Pattern cannot be empty')

    if len(pattern) > ModuleCtx.Max_Length:
        raise ValueError(f'Pattern exceeds maximum length of {ModuleCtx.Max_Length} characters: {len(pattern)}')

    if _contains_reserved_name(pattern):
        raise ValueError(f'Pattern contains reserved name: {pattern}')

    if not _is_ascii_only(pattern):
        raise ValueError(f'Pattern contains non-ASCII characters: {pattern}')

# ################################################################################################################################

def _contains_reserved_name(pattern:'str') -> 'bool':
    """ Check if pattern contains reserved names case-insensitively.
    """
    pattern_lower = pattern.lower()
    return 'zato' in pattern_lower or 'zpsk' in pattern_lower

# ################################################################################################################################

def _is_ascii_only(text:'str') -> 'bool':
    """ Check if text contains only ASCII characters.
    """
    try:
        _ = text.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False

# ################################################################################################################################

def get_permissions_for_sec_base(session, sec_base_id:'int', cluster_id:'int') -> 'list':
    """ Get all active permissions for a security definition.
    Returns a list of permission dictionaries with pattern and access_type.
    """
    from zato.common.odb.model import PubSubPermission

    permissions = session.query(PubSubPermission).filter(
        PubSubPermission.sec_base_id == sec_base_id,
        PubSubPermission.cluster_id == cluster_id,
        PubSubPermission.is_active == True
    ).all()

    result = []
    sub_prefix = 'sub='
    pub_prefix = 'pub='

    for perm in permissions:

        # Split patterns on newlines since service layer joins them
        patterns = [elem.strip() for elem in perm.pattern.splitlines() if elem.strip()]

        for individual_pattern in patterns:
            for prefix in [sub_prefix, pub_prefix]:
                if individual_pattern.startswith(prefix):
                    clean_pattern = individual_pattern[len(prefix):]
                    result.append({
                        'pattern': clean_pattern,
                        'access_type': perm.access_type
                    })
                    break

    return result

# ################################################################################################################################

def evaluate_pattern_match(session, sec_base_name:'str', sec_base_id:'int', cluster_id:'int', topic_name:'str') -> 'str':
    """ Evaluate which pattern matches the given topic name for a security definition.
    Returns the matched pattern or raises an exception if no pattern matches.
    """
    # Zato
    from zato.common.pubsub.matcher import PatternMatcher

    permissions = get_permissions_for_sec_base(session, sec_base_id, cluster_id)

    if not permissions:
        msg = f'No permissions defined for security definition {sec_base_id} ({sec_base_name})'
        raise ValueError(msg)

    # Create temporary matcher
    matcher = PatternMatcher()

    # Add client to matcher
    client_id = f'eval.{sec_base_id}.{topic_name}'
    matcher.add_client(client_id, permissions)

    # Evaluate for subscribe operation (subscriptions are for subscribers)
    result = matcher.evaluate(client_id, topic_name, 'subscribe')

    if result.is_ok and result.matched_pattern:
        return result.matched_pattern
    else:
        msg = f'Topic "{topic_name}" does not match any subscription patterns for security definition {sec_base_id} ({sec_base_name})'
        raise ValueError(msg)

# ################################################################################################################################

def create_subscription_bindings(broker_client, cid:'str', sub_key:'str', exchange_name:'str', topic_name:'str') -> 'None':
    """ Create AMQP bindings for a subscription.
    """
    logger.debug(f'[{cid}] Creating AMQP bindings: sub_key={sub_key}, exchange={exchange_name}, topic={topic_name}')
    broker_client.create_bindings(cid, sub_key, exchange_name, sub_key, topic_name)

# ################################################################################################################################

def cleanup_broker_impl(
    broker_config: 'BrokerConfig',
    management_port: 'int'
) -> 'dict':
    """ Clean up AMQP bindings and queues implementation.
    """
    prefixes = ['zpsk', PubSub.Prefix.Reply_Queue]

    # Extract host from address (remove port if present)
    host = broker_config.address.split(':')[0] if ':' in broker_config.address else broker_config.address

    # URL encode the vhost
    encoded_vhost = quote(broker_config.vhost, safe='')

    # Build HTTP API base URL
    api_base_url = f'http://{host}:{management_port}/api'
    auth = (broker_config.username, broker_config.password)

    logger.info(f'Connecting to RabbitMQ API at: {api_base_url}')

    result = {'queues_removed': 0, 'bindings_removed': 0, 'errors': []}

    # Find and remove all queues with specified prefixes
    try:
        logger.info(f'Listing queues with prefixes: {prefixes}')
        queues_url = f'{api_base_url}/queues/{encoded_vhost}'
        response = requests.get(queues_url, auth=auth)

        if response.status_code == OK:
            all_queues = response.json()

            # Process each prefix
            for prefix in prefixes:
                matching_queues = [queue for queue in all_queues if queue['name'].startswith(prefix)]
                queue_count = len(matching_queues)
                if queue_count == 1:
                    logger.info(f'Found 1 queue with prefix {prefix}')
                else:
                    logger.info(f'Found {queue_count} queues with prefix {prefix}')

                # Delete each matching queue
                for queue in matching_queues:
                    queue_name = queue['name']
                    logger.info(f'Removing queue: {queue_name}')

                    # Delete the queue - empty all arguments to force deletion
                    queue_url = f'{api_base_url}/queues/{encoded_vhost}/{queue_name}'
                    delete_response = requests.delete(
                        queue_url,
                        auth=auth,
                        params={'if-unused': 'false', 'if-empty': 'false'}
                    )

                    if delete_response.status_code in (OK, NO_CONTENT):
                        logger.info(f'Successfully removed queue: {queue_name}')
                        result['queues_removed'] += 1
                    else:
                        error_msg = f'Failed to remove queue: {delete_response.status_code}, {delete_response.text}'
                        logger.error(error_msg)
                        result['errors'].append(error_msg)
        else:
            error_msg = f'Failed to list queues: {response.status_code}, {response.text}'
            logger.error(error_msg)
            result['errors'].append(error_msg)

    except Exception as e:
        error_msg = f'Error removing queues: {e}'
        logger.error(error_msg)
        result['errors'].append(error_msg)

    # List all bindings from pubsubapi exchange
    try:
        logger.info('Listing bindings from pubsubapi exchange')
        bindings_url = f'{api_base_url}/exchanges/{encoded_vhost}/pubsubapi/bindings/source'
        response = requests.get(bindings_url, auth=auth)

        if response.status_code == OK:
            bindings = response.json()
            binding_count = len(bindings)
            if binding_count == 1:
                logger.info('Found 1 binding for pubsubapi exchange')
            else:
                logger.info(f'Found {binding_count} bindings for pubsubapi exchange')

            # Remove all bindings from pubsubapi exchange
            for binding in bindings:
                queue_name = binding.get('destination')

                # Only process if the destination is a queue
                if binding.get('destination_type') == 'queue':

                    routing_key = binding.get('routing_key', '')
                    logger.info(f'Removing binding: queue={queue_name}, routing_key={routing_key} from exchange=pubsubapi')

                    # Delete the binding
                    unbind_url = f'{api_base_url}/bindings/{encoded_vhost}/e/pubsubapi/q/{queue_name}/{quote(routing_key, safe="")}'
                    delete_response = requests.delete(unbind_url, auth=auth)

                    if delete_response.status_code in (OK, NO_CONTENT):
                        logger.info(f'Successfully removed binding for queue: {queue_name}')
                        result['bindings_removed'] += 1
                    else:
                        error_msg = f'Failed to remove binding: {delete_response.status_code}, {delete_response.text}'
                        logger.error(error_msg)
                        result['errors'].append(error_msg)
        else:
            error_msg = f'Failed to list bindings: {response.status_code}, {response.text}'
            logger.error(error_msg)
            result['errors'].append(error_msg)

    except Exception as e:
        error_msg = f'Error removing bindings: {e}'
        logger.error(error_msg)
        result['errors'].append(error_msg)

    return result

# ################################################################################################################################

class ConsumerManager:
    """ Manages consumers for AMQP queues via RabbitMQ Management API.
    """

    def __init__(self, broker_config:'BrokerConfig', cid:'str'=''):
        self.broker_config = broker_config
        self.cid = cid
        self.host = broker_config.address.split(':')[0] if ':' in broker_config.address else broker_config.address
        self.management_port = 15672
        self.auth = (broker_config.username, broker_config.password)

    def get_consumers(self, queue_name: 'str') -> 'list':
        """ Get the list of consumers for a given queue.
        """
        # URL encode the vhost and queue name
        encoded_vhost = quote(self.broker_config.vhost, safe='')
        encoded_queue_name = quote(queue_name, safe='')

        # Build HTTP API URL for queue consumers
        api_url = f'http://{self.host}:{self.management_port}/api/queues/{encoded_vhost}/{encoded_queue_name}'

        try:
            response = requests.get(api_url, auth=self.auth)

            if response.status_code == OK:
                queue_info = response.json()
                consumers = queue_info['consumer_details']
                consumer_count = len(consumers)
                consumer_word = 'consumer' if consumer_count == 1 else 'consumers'
                logger.info(f'[{self.cid}] Found {consumer_count} {consumer_word} for queue: {queue_name}')
                return consumers
            elif response.status_code == NOT_FOUND:
                logger.info(f'[{self.cid}] No consumers found for queue: {queue_name}')
                return []
            else:
                error_msg = f'[{self.cid}] Failed to get consumers for queue {queue_name}: {response.status_code}, {response.text}'
                logger.error(error_msg)
                raise Exception(error_msg)

        except RequestException as e:
            error_msg = f'[{self.cid}] Error getting consumers for queue {queue_name}: {e}'
            logger.error(error_msg)
            raise Exception(error_msg)

# ################################################################################################################################

    def close_consumers(self, queue_name: 'str') -> 'None':
        """ Close all consumers for a given queue by closing their channels.
        """
        consumers = self.get_consumers(queue_name)

        if not consumers:
            logger.info(f'[{self.cid}] No consumers found for queue: {queue_name}')
            return

        for consumer in consumers:
            channel_details = consumer['channel_details']
            connection_name = channel_details['connection_name']
            consumer_tag = consumer['consumer_tag']

            # URL encode the connection name
            encoded_connection_name = quote(connection_name, safe='')

            # Build API URL to close the connection (which closes all its channels)
            api_url = f'http://{self.host}:{self.management_port}/api/connections/{encoded_connection_name}'

            try:
                response = requests.delete(api_url, auth=self.auth)

                if response.status_code in (OK, NO_CONTENT):
                    logger.info(f'[{self.cid}] Closed consumer: {consumer_tag} ({queue_name})')
                else:
                    error_msg = f'[{self.cid}] Failed to close channel {connection_name} for consumer {consumer_tag} ' + \
                           f'queue {queue_name}: {response.status_code}, {repr(response.text)}'
                    logger.error(error_msg)
                    raise Exception(error_msg)

            except RequestException as e:
                error_msg = f'[{self.cid}] HTTP error closing channel {connection_name} for consumer {consumer_tag} ({queue_name}): {e}'
                logger.error(error_msg)
                raise Exception(error_msg)

# ################################################################################################################################

def get_security_definition(session, cluster_id, username=None, sec_name=None):
    """ Get security definition by username or sec_name.

    Returns tuple of (sec_def, lookup_field, lookup_value).
    Raises Exception if not found or if neither username nor sec_name provided.
    """
    # Zato
    from zato.common.odb.model import SecurityBase

    if username:
        sec_def = session.query(SecurityBase).\
            filter(SecurityBase.cluster_id==cluster_id).\
            filter(SecurityBase.username==username).\
            first()
        lookup_field = 'username'
        lookup_value = username
    elif sec_name:
        sec_def = session.query(SecurityBase).\
            filter(SecurityBase.cluster_id==cluster_id).\
            filter(SecurityBase.name==sec_name).\
            first()
        lookup_field = 'sec_name'
        lookup_value = sec_name
    else:
        raise Exception('Either username or sec_name must be provided')

    if not sec_def:
        raise Exception(f'Security definition not found for {lookup_field} `{lookup_value}`')

    return sec_def, lookup_field, lookup_value

# ################################################################################################################################
# ################################################################################################################################
