# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import urllib.request
from logging import getLogger
from traceback import format_exc

# gevent
from gevent.subprocess import run as subprocess_run

# orjson
import orjson

# Zato
from zato.common.typing_ import dict_
from zato.common.util.api import as_bool

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import dict_, list_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)
_needs_details = as_bool(os.environ.get('Zato_Needs_Details', False))

# ################################################################################################################################
# ################################################################################################################################

def _get_connections_data(vhost:'str') -> 'dict_':
    """ Get raw connections data from rabbitmqctl.
    """
    result = subprocess_run(
        f"sudo rabbitmqctl list_connections name user client_properties connected_at channels --vhost {vhost} --formatter json",
        shell=True,
        capture_output=True,
        text=True,
        timeout=30
    )

    return {
        'returncode': result.returncode,
        'stdout': result.stdout,
        'stderr': result.stderr
    }

# ################################################################################################################################

def _get_consumers_data(vhost:'str') -> 'dict_':
    """ Get raw consumers data from rabbitmqctl.
    """
    command_args = f"list_consumers queue_name consumer_tag channel_pid --vhost {vhost} --formatter json"

    request_data = {
        'args': command_args
    }

    data = json.dumps(request_data).encode('utf-8')

    req = urllib.request.Request(
        'http://127.0.0.1:25090',
        data=data,
        headers={'Content-Type': 'application/json'}
    )

    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            return response_data
    except Exception:
        return {
            'returncode': -1,
            'stdout': '',
            'stderr': f'Failed to connect to rabbitmqctl server -> {format_exc()}'
        }

# ################################################################################################################################

def _parse_client_properties(client_props_list:'list_') -> 'dict_':
    """ Parse client properties list into dictionary.
    """
    client_properties = {}
    for prop in client_props_list:
        if len(prop) >= 3:
            key = prop[0]
            value = prop[2]
            client_properties[key] = value

    return client_properties

# ################################################################################################################################

def _parse_connections_output(stdout:'str') -> 'list_':
    """ Parse rabbitmqctl connections JSON output into structured data.
    """
    if not stdout.strip():
        return []

    raw_connections = orjson.loads(stdout)
    connections = []

    for conn in raw_connections:
        client_properties = _parse_client_properties(conn['client_properties'])

        connections.append({
            'name': conn['name'],
            'user': conn['user'],
            'client_properties': client_properties,
            'connected_at': conn['connected_at'],
            'channels': conn['channels']
        })

    return connections

# ################################################################################################################################

def _parse_consumers_output(stdout:'str') -> 'dict_':
    """ Parse rabbitmqctl consumers JSON output into queue counts.
    """
    consumers_per_queue = {}

    if not stdout.strip():
        return consumers_per_queue

    raw_consumers = orjson.loads(stdout)

    for consumer in raw_consumers:
        queue = consumer['queue_name']
        if queue not in consumers_per_queue:
            consumers_per_queue[queue] = 0
        consumers_per_queue[queue] += 1

    return consumers_per_queue

# ################################################################################################################################

def _parse_consumers_details(stdout:'str', vhost:'str') -> 'list_':
    """ Parse rabbitmqctl consumers JSON output into detailed consumer objects.
    """
    if not stdout.strip():
        return []

    raw_consumers = orjson.loads(stdout)
    consumers = []

    for consumer in raw_consumers:
        consumers.append({
            'consumer_tag': consumer['consumer_tag']
        })

    return consumers

# ################################################################################################################################

def _analyze_connections(connections:'list_') -> 'dict_':
    """ Analyze connections data to extract statistics.
    """
    connection_types = {}
    user_connections = {}
    client_properties = {}

    for conn in connections:
        # Group by connection type
        conn_type = conn['client_properties'].get('connection_name', 'Unknown')
        connection_types[conn_type] = connection_types.get(conn_type, 0) + 1

        # Group by user
        user = conn['user']
        if user not in user_connections:
            user_connections[user] = []
        user_connections[user].append({
            'client_properties': conn['client_properties'],
            'connected_at': conn['connected_at'],
            'channels': conn['channels']
        })

        # Track unique client properties
        for key, value in conn['client_properties'].items():
            if key not in client_properties:
                client_properties[key] = set()
            if isinstance(value, (str, int, bool, float)):
                client_properties[key].add(value)

    # Convert sets to lists for JSON serialization
    for key in client_properties:
        client_properties[key] = list(client_properties[key])

    return {
        'connection_types': connection_types,
        'user_connections': user_connections,
        'client_properties_unique_values': client_properties
    }

# ################################################################################################################################

def get_queue_consumers(cid:'str', vhost:'str', queue_name:'str') -> 'list_':
    """ Get detailed consumer information for a specific queue.
    """
    consumers_data = None

    if _needs_details:
        logger.info(f'[{cid}] Getting consumers for queue {queue_name}')

    try:
        consumers_data = _get_consumers_data(vhost)

        if consumers_data['returncode'] != 0:
            msg = f'Failed to get consumers: {consumers_data["stderr"]}'
            raise Exception(msg)

        all_consumers = _parse_consumers_details(consumers_data['stdout'], vhost)

        # Filter for specific queue
        if not consumers_data['stdout'].strip():
            return []

        raw_consumers = orjson.loads(consumers_data['stdout'])
        queue_consumers = []

        for idx, consumer in enumerate(raw_consumers):
            if consumer['queue_name'] == queue_name:
                queue_consumers.append(all_consumers[idx])

        return queue_consumers

    except Exception:
        logger.error(f'[{cid}] Error getting queue consumers -> {consumers_data} -> {format_exc()}')
        raise

# ################################################################################################################################

def list_connections(cid:'str', vhost:'str', queue_name:'str'='') -> 'dict_':
    """ List RabbitMQ connections.
    """
    if _needs_details:
        logger.info(f'[{cid}] Listing RabbitMQ connections')

    try:
        # Get connections data
        connections_data = _get_connections_data(vhost)

        if connections_data['returncode'] != 0:
            logger.warning(f'Failed to list connections: {connections_data["stderr"]}')
            return {
                'status': 'error',
                'error': connections_data['stderr'],
                'status_code': connections_data['returncode']
            }

        # Parse connections
        connections = _parse_connections_output(connections_data['stdout'])
        total_count = len(connections)
        connection_word = 'connection' if total_count == 1 else 'connections'
        logger.info(f'[{cid}] Found {total_count} RabbitMQ {connection_word}')

        # Analyze connections
        analysis = _analyze_connections(connections)

        # Get consumers data
        consumers_data = _get_consumers_data(vhost)
        consumers_per_queue = {}
        if consumers_data['returncode'] == 0:
            consumers_per_queue = _parse_consumers_output(consumers_data['stdout'])

            # If queue_name specified, filter for that queue only
            if queue_name:
                filtered_consumers = {}
                for k, v in consumers_per_queue.items():
                    if k == queue_name:
                        filtered_consumers[k] = v

                consumers_per_queue = filtered_consumers

        return {
            'status': 'success',
            'total_connections': total_count,
            'connection_types': analysis['connection_types'],
            'user_connections': analysis['user_connections'],
            'client_properties_unique_values': analysis['client_properties_unique_values'],
            'consumers_per_queue': consumers_per_queue,
            'backend_sub_keys': []
        }

    except Exception as e:
        logger.error(f'[{cid}] Error listing connections: {e}')
        return {
            'status': 'error',
            'error': str(e),
            'status_code': -1
        }

# ################################################################################################################################

def close_queue_consumers(cid:'str', vhost:'str', queue_name:'str') -> 'None':
    """ Close all consumers for a given queue by closing their connections.
    """
    # Get consumers for the queue
    consumers = get_queue_consumers(cid, vhost, queue_name)

    if not consumers:
        if _needs_details:
            logger.info(f'[{cid}] No consumers to close for queue: `{queue_name}`')
        return

    # Get all connections
    connections_data = _get_connections_data(vhost)
    if connections_data['returncode'] != 0:
        logger.warning(f'[{cid}] Failed to get connections: {connections_data["stderr"]}')
        raise Exception(connections_data['stderr'])

    connections = _parse_connections_output(connections_data['stdout'])

    # Close each connection that has consumers for this queue
    for connection in connections:
        connection_name = connection['name']

        try:
            result = subprocess_run(
                f'sudo rabbitmqctl close_connection "{connection_name}" "Closing consumers for queue {queue_name}"',
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                logger.info(f'[{cid}] Closed connection: `{connection_name}` (`{queue_name}`)')
            else:
                msg = f'[{cid}] Failed to close connection `{connection_name}` for queue {queue_name}: {result.stderr}'
                logger.warning(msg)
                raise Exception(msg)

        except Exception as e:
            msg = f'[{cid}] Error closing connection `{connection_name}` for queue {queue_name}: {e}'
            logger.warning(msg)
            raise Exception(msg)

# ################################################################################################################################
# ################################################################################################################################
