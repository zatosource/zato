# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import datetime
from http.client import NO_CONTENT, NOT_FOUND, OK
from logging import getLogger
from urllib.parse import quote

# Requests
import requests
from requests.exceptions import RequestException

# Zato
from zato.common.pubsub.util_cli import close_queue_consumers, get_queue_consumers

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.common import BrokerConfig
from zato.common.util.api import as_bool, utcnow, wait_for_predicate

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)
_needs_details = as_bool(os.environ.get('Zato_Needs_Details', False))

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Max_Length = PubSub.Topic.Name_Max_Len

# ################################################################################################################################
# ################################################################################################################################

def get_broker_config() -> 'BrokerConfig':

    config = BrokerConfig()

    config.protocol = os.environ.get('Zato_Broker_Protocol') or 'amqp'
    config.address = os.environ.get('Zato_Broker_Address') or '127.0.0.1:5672'
    config.vhost = os.environ.get('Zato_Broker_Virtual_Host') or '/'
    config.username = os.environ['Zato_Broker_Username']
    config.password = os.environ['Zato_Broker_Internal_Password']
    config.management_port = int(os.environ.get('Zato_Broker_Management_Port') or 15672)

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
    if _needs_details:
        logger.info(f'[{cid}] Creating AMQP bindings: sub_key={sub_key}, exchange={exchange_name}, topic={topic_name}')
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

    def __init__(self, cid:'str', broker_config:'BrokerConfig'):
        self.broker_config = broker_config
        self.cid = cid
        self.host = broker_config.address.split(':')[0] if ':' in broker_config.address else broker_config.address
        self.management_port = 15672
        self.auth = (broker_config.username, broker_config.password)
        self.ignore_prefixes = ['zato-reply']
        self.request_timeout = 1

# ################################################################################################################################

    def _close_consumers(self, queue_name: 'str') -> 'None':
        """ Close all consumers for a given queue by closing their connections.
        """
        close_queue_consumers(self.cid, self.broker_config.vhost, queue_name)

# ################################################################################################################################

    def close_consumers(self, queue_name: 'str') -> 'None':
        """ Close all consumers for a given queue by closing their channels with retry logic.
        """

        # No need to do anything if we know this queue should be ignored
        for prefix in self.ignore_prefixes:
            if queue_name.startswith(prefix):
                if _needs_details:
                    logger.info(f'[{self.cid}] Ignoring queue with prefix `{prefix}`: `{queue_name}`')
                return
            else:
                if _needs_details:
                    logger.info(f'[{self.cid}] Prefix did not match `{prefix}`: `{queue_name}`')

        # Local variables
        first_response_time = None
        max_wait_time = 10

        def _predicate_close_consumers() -> 'bool':
            """ Predicate function that returns True if _close_consumers succeeds without exception.
            """
            nonlocal first_response_time

            if _needs_details:
                logger.info(f'[{self.cid}] Predicate called for queue: `{queue_name}`')

            try:
                consumers = get_queue_consumers(self.cid, self.broker_config.vhost, queue_name)
                if _needs_details:
                    logger.info(f'[{self.cid}] Got consumers: {len(consumers)} for queue: `{queue_name}`')

                if first_response_time is None:

                    first_response_time = utcnow()

                    if _needs_details:
                        logger.info(f'[{self.cid}] Set first_response_time for queue: `{queue_name}`')

                if consumers:

                    if _needs_details:
                        logger.info(f'[{self.cid}] Calling _close_consumers for queue: `{queue_name}`')

                    self._close_consumers(queue_name)

                    if _needs_details:
                        logger.info(f'[{self.cid}] Called _close_consumers, returning True for queue: `{queue_name}`')

                    return True
                else:

                    current_time = utcnow()
                    time_diff = current_time - first_response_time
                    elapsed_seconds = time_diff.total_seconds()

                    if _needs_details:
                        logger.info(f'[{self.cid}] No consumers, elapsed: {elapsed_seconds}s for queue: `{queue_name}`')

                    if elapsed_seconds > max_wait_time:
                        msg = f'[{self.cid}] No consumers after {max_wait_time} seconds, stopping retry for: `{queue_name}`'
                        if _needs_details:
                            logger.info(msg)
                        return True

                    if _needs_details:
                        logger.info(f'[{self.cid}] Returning False, will retry for queue: `{queue_name}`')

                    return False

            except Exception as e:
                logger.info(f'[{self.cid}] Exception caught: queue: `{queue_name}` -> {e}')
                return False

        _ = wait_for_predicate(
            _predicate_close_consumers,
            100_000_000,
            2.0,
            jitter=0.2
        )

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

def set_time_since(message:'dict', pub_time_iso:'str', recv_time_iso:'str', current_time:'datetime') -> 'None':
    """ Calculate and set time_since_pub and time_since_recv on the message.
    """
    pub_timestamp = datetime.fromisoformat(pub_time_iso)
    time_since_pub = str(current_time - pub_timestamp)

    recv_timestamp = datetime.fromisoformat(recv_time_iso)
    time_since_recv = str(current_time - recv_timestamp)

    message['time_since_pub'] = time_since_pub
    message['time_since_recv'] = time_since_recv

# ################################################################################################################################
# ################################################################################################################################
