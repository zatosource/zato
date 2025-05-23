# -*- coding: utf-8 -*-
"""
Extracts REST channel, service, and security info from the ODB using direct SQLAlchemy queries.
"""
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from zato.common.odb.model import HTTPBasicAuth, APIKeySecurity, HTTPSOAP, GenericObject

# Logger for this module
logger = logging.getLogger(__name__)

_SQLITE_PATH = os.path.expanduser('~/env/qs-1/zato.db')
_ENGINE = create_engine(f'sqlite:///{_SQLITE_PATH}')
Session = sessionmaker(bind=_ENGINE)
CLUSTER_ID = 1

# --- Bulk data fetch ---
def fetch_all():
    session = Session()
    try:
        # Test connection and print tables for debug
        logger.info(f'SQLite path: {_SQLITE_PATH}')
        logger.info(f'File exists: {os.path.exists(_SQLITE_PATH)}')

        # Try with minimal filters first
        all_http = session.query(HTTPSOAP).all()
        logger.info(f'Found {len(all_http)} total HTTP/SOAP objects')

        # Show details about all HTTP/SOAP objects
        for i, channel in enumerate(all_http):
            logger.debug(f'Channel {i}: name={channel.name}, transport={channel.transport}, connection={channel.connection}, is_active={channel.is_active}, path={channel.url_path}, service={channel.service}')

        # Get all channels, regardless of status/transport
        channels = session.query(HTTPSOAP).filter(
            HTTPSOAP.cluster_id == CLUSTER_ID,
            HTTPSOAP.connection == 'channel',  # Only incoming channels
        ).all()
        logger.info(f'All incoming channels with cluster_id={CLUSTER_ID}: {len(channels)}')

        # Include everything (be more permissive)
        logger.info('Using all available channels for OpenAPI generation')

        # All HTTP Basic Auth definitions
        basic_auth_defs = session.query(HTTPBasicAuth).filter(HTTPBasicAuth.cluster_id == CLUSTER_ID).all()

        # All API Key definitions
        api_key_defs = session.query(APIKeySecurity).filter(APIKeySecurity.cluster_id == CLUSTER_ID).all()

        # All groups
        groups = session.query(GenericObject).filter(
            GenericObject.type_ == 'group',
            GenericObject.cluster_id == CLUSTER_ID
        ).all()

        # All group members (as GenericObject, type_='group-member')
        group_members = session.query(GenericObject).filter(
            GenericObject.type_ == 'group-member',
            GenericObject.cluster_id == CLUSTER_ID
        ).all()

        return {
            'channels': channels,
            'basic_auth_defs': basic_auth_defs,
            'api_key_defs': api_key_defs,
            'groups': groups,
            'group_members': group_members,
        }
    finally:
        session.close()

# --- Data assembly ---
def build_scan_results():
    data = fetch_all()
    # Build security lookup tables
    basic_auth_by_id = {x.id: x for x in data['basic_auth_defs']}
    api_key_by_id = {x.id: x for x in data['api_key_defs']}
    # Group membership: group_id -> [member_id]
    group_members = {}
    for gm in data['group_members']:
        parent_id = gm.parent_object_id
        if parent_id not in group_members:
            group_members[parent_id] = []
        group_members[parent_id].append(gm.object_id)
    # Group lookup
    group_by_id = {g.id: g for g in data['groups']}
    # Assemble services (one per channel)
    services = []
    for channel in data['channels']:
        # Debug info for this channel
        logger.debug(f'Processing channel: {channel.name}, security_id: {channel.security_id}')

        # Security resolution
        security = []

        # HTTPSOAP has security_id but not sec_type directly
        # We'll determine the type from the available defs
        if channel.security_id:
            # Try basic auth first
            sec = basic_auth_by_id.get(channel.security_id)
            if sec:
                security.append({'type': 'basic_auth', 'name': sec.name})
                logger.debug(f'  - Found Basic Auth: {sec.name}')

            # Then try API key
            sec = api_key_by_id.get(channel.security_id)
            if sec:
                security.append({'type': 'apikey', 'name': sec.name})
                logger.debug(f'  - Found API Key: {sec.name}')

            # Finally try security group
            group = group_by_id.get(channel.security_id)
            if group:
                logger.debug(f'  - Found Security Group: {group.name}')
                member_ids = group_members.get(group.id, [])
                for mid in member_ids:
                    if mid in basic_auth_by_id:
                        security.append({'type': 'basic_auth', 'name': basic_auth_by_id[mid].name})
                        logger.debug(f'    - Group member: Basic Auth {basic_auth_by_id[mid].name}')
                    elif mid in api_key_by_id:
                        security.append({'type': 'apikey', 'name': api_key_by_id[mid].name})
                        logger.debug(f'    - Group member: API Key {api_key_by_id[mid].name}')
        # Extract service name or use channel name as fallback
        service_name = None
        if hasattr(channel.service, 'name'):
            service_name = channel.service.name
        elif isinstance(channel.service, str):
            service_name = channel.service
        else:
            service_name = channel.name

        logger.debug(f'  - Service name: {service_name}')

        # Compose service entry
        services.append({
            'name': service_name,
            'url_path': channel.url_path,
            'http_method': channel.method.lower() if channel.method else 'post',
            'security': security,
            'channel_name': channel.name,
        })
    # No models for now
    return {'services': services, 'models': {}}
