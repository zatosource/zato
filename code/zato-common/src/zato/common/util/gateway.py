# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, strdict, strnone
    any_ = any_
    anylist = anylist
    strdict = strdict
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

mcp_gateway_name = 'zato.gateway.mcp'
mcp_gateway_url_path = '/mcp/demo'
mcp_service_name = 'zato.server.service.internal.gateway.mcp.MCPEndpoint'

# Each gateway has a security group of its own, named after the gateway with this prefix.
mcp_group_name_prefix = 'mcp.'

# ################################################################################################################################
# ################################################################################################################################

def get_mcp_group_name(gateway_name:'str') -> 'str':
    """ Returns the name of the security group that belongs to the gateway of the given name.
    """
    out = mcp_group_name_prefix + gateway_name
    return out

# ################################################################################################################################
# ################################################################################################################################

def get_mcp_gateway_channel(session:'any_', channel_name:'str') -> 'any_':
    """ Returns the HTTP channel of the gateway of the given name, i.e. the channel of that name
    that invokes the MCP endpoint service, or None if there is no such channel.
    """
    from zato.common.api import CONNECTION
    from zato.common.odb.model import HTTPSOAP, Service

    out = session.query(HTTPSOAP).\
        join(Service, HTTPSOAP.service_id == Service.id).\
        filter(HTTPSOAP.name == channel_name).\
        filter(HTTPSOAP.connection == CONNECTION.CHANNEL).\
        filter(Service.name == mcp_service_name).\
        first()

    return out

# ################################################################################################################################

def _get_other_channel(session:'any_', channel_name:'str', gateway_channel:'any_') -> 'any_':
    """ Returns a channel of the given name other than the gateway's own channel, or None.
    """
    from zato.common.api import CONNECTION
    from zato.common.odb.model import HTTPSOAP

    query = session.query(HTTPSOAP).\
        filter(HTTPSOAP.name == channel_name).\
        filter(HTTPSOAP.connection == CONNECTION.CHANNEL)

    if gateway_channel:
        query = query.filter(HTTPSOAP.id != gateway_channel.id)

    out = query.first()
    return out

# ################################################################################################################################

def _get_group(session:'any_', group_name:'str') -> 'any_':
    """ Returns the security group of the given name, or None.
    """
    from zato.common.api import Groups
    from zato.common.odb.model import GenericObject

    out = session.query(GenericObject).filter(
        GenericObject.name == group_name,
        GenericObject.type_ == Groups.Type.Group_Parent,
    ).first()

    return out

# ################################################################################################################################
# ################################################################################################################################

def ensure_mcp_gateway_exists(session:'any_') -> 'bool':
    """ Creates both the HTTP channel and the generic connection for MCP if they do not exist.
    The HTTP channel routes POST /mcp to the MCPEndpoint service.
    The generic connection registers the gateway-mcp type in the config manager.
    Both must share the same name so MCPEndpoint can look up its handler.
    Returns True if created, False if already existed.
    """
    from zato.common.api import CONNECTION, DATA_FORMAT, GENERIC, URL_TYPE
    from zato.common.odb.model import GenericConn, HTTPSOAP, Service

    existing_http = session.query(HTTPSOAP).filter(
        HTTPSOAP.name == mcp_gateway_name,
        HTTPSOAP.connection == CONNECTION.CHANNEL,
    ).first()

    existing_generic = session.query(GenericConn).filter(
        GenericConn.name == mcp_gateway_name,
        GenericConn.type_ == GENERIC.CONNECTION.TYPE.GATEWAY_MCP,
    ).first()

    if existing_http and existing_generic:
        return False

    # Create the HTTP channel if missing ..
    if not existing_http:

        service = session.query(Service).filter(
            Service.name == mcp_service_name,
        ).first()

        if not service:
            service = Service(None, mcp_service_name, True, mcp_service_name, True)
            session.add(service)
            session.flush()

        channel = HTTPSOAP(
            None, mcp_gateway_name, True, True, CONNECTION.CHANNEL,
            URL_TYPE.PLAIN_HTTP, None, mcp_gateway_url_path, None, '', None, DATA_FORMAT.JSON,
            service=service)
        session.add(channel)

    # .. create the generic connection if missing.
    if not existing_generic:

        generic_conn:'any_' = GenericConn()
        generic_conn.name = mcp_gateway_name
        generic_conn.type_ = GENERIC.CONNECTION.TYPE.GATEWAY_MCP
        generic_conn.is_active = True
        generic_conn.is_internal = True
        generic_conn.is_channel = True
        generic_conn.is_outconn = False
        generic_conn.opaque1 = '{"services": ["demo.echo", "test.raise"], "url_path": "/mcp/demo"}'

        session.add(generic_conn)

    return True

# ################################################################################################################################
# ################################################################################################################################

def ensure_mcp_oauth_metadata_channel_exists(session:'any_') -> 'bool':
    """ Creates the one channel serving the OAuth protected resource metadata of every MCP gateway,
    if it does not exist. Returns True if created, False if it already existed.
    """
    from zato.common.api import CONNECTION, DATA_FORMAT, URL_TYPE
    from zato.common.odb.model import HTTPSOAP, Service
    from zato.common.util.mcp_oauth import Metadata_Channel_Name, Metadata_Channel_Url_Path, Metadata_Service_Name

    existing = session.query(HTTPSOAP).filter(
        HTTPSOAP.name == Metadata_Channel_Name,
        HTTPSOAP.connection == CONNECTION.CHANNEL,
    ).first()

    if existing:
        return False

    service = session.query(Service).filter(
        Service.name == Metadata_Service_Name,
    ).first()

    if not service:
        service = Service(None, Metadata_Service_Name, True, Metadata_Service_Name, True)
        session.add(service)
        session.flush()

    channel = HTTPSOAP(
        None, Metadata_Channel_Name, True, True, CONNECTION.CHANNEL,
        URL_TYPE.PLAIN_HTTP, None, Metadata_Channel_Url_Path, None, '', None, DATA_FORMAT.JSON,
        service=service)
    session.add(channel)

    return True

# ################################################################################################################################
# ################################################################################################################################

def ensure_mcp_rest_channel(
    session:'any_',
    channel_name:'str',
    url_path:'str',
    is_active:'bool'=True,
    security_groups:'anylist | None'=None,
    old_name:'strnone'=None,
    ) -> 'None':
    """ Creates or updates the REST channel that makes an MCP gateway reachable over HTTP.
    Called from both the server-side hook (on_mcp_gateway_create_edit) and the enmasse importer.
    Does NOT commit - the caller is responsible for committing the session.
    """
    from zato.common.api import CONNECTION, DATA_FORMAT, URL_TYPE
    from zato.common.odb.model import HTTPSOAP, Service
    from zato.common.util.channel import find_channel_collision, get_channel_collision_items, validate_channel_url_path
    from zato.common.util.sql import set_instance_opaque_attrs

    security_groups = security_groups or []

    # If this is a rename, delete the old REST channel first ..
    if old_name and old_name != channel_name:
        old_http = get_mcp_gateway_channel(session, old_name)
        if old_http:
            session.delete(old_http)

    # .. check if the REST channel already exists ..
    existing_http = get_mcp_gateway_channel(session, channel_name)

    # .. a channel of that name that is not the gateway's is never taken over ..
    if other_channel := _get_other_channel(session, channel_name, existing_http):
        raise ValueError(f'Channel `{other_channel.name}` already exists')

    # .. the path is checked the way zato.http-soap.create checks it, and since the gateway
    # .. answers every HTTP method at its path, no other channel may share that path ..
    validate_channel_url_path(url_path)

    if existing_http:
        skip_id = existing_http.id
    else:
        skip_id = None

    existing_items = get_channel_collision_items(session)
    colliding_name = find_channel_collision(url_path, None, '', existing_items, skip_id, claims_whole_path=True)

    if colliding_name:
        raise ValueError(f'MCP gateway `{channel_name}` has the URL path of channel `{colliding_name}`: `{url_path}`')

    # .. if it exists, update it ..
    if existing_http:
        existing_http.url_path = url_path
        existing_http.is_active = is_active
        set_instance_opaque_attrs(existing_http, {'security_groups': security_groups})

    # .. otherwise, create a new one.
    else:

        mcp_service = session.query(Service).filter(
            Service.name == mcp_service_name,
        ).first()

        if not mcp_service:
            mcp_service = Service(None, mcp_service_name, True, mcp_service_name, True)
            session.add(mcp_service)
            session.flush()

        http_channel = HTTPSOAP(
            None, channel_name, is_active, True, CONNECTION.CHANNEL,
            URL_TYPE.PLAIN_HTTP, None, url_path, None, '', None, DATA_FORMAT.JSON,
            service=mcp_service, security=None)
        set_instance_opaque_attrs(http_channel, {'security_groups': security_groups})
        session.add(http_channel)

    # The next gateway of the same import compares its path against this channel too
    session.flush()

# ################################################################################################################################
# ################################################################################################################################

def _resolve_security_group_names_to_ids(session:'any_', group_names:'anylist') -> 'anylist':
    """ Converts a list of security group names to their database IDs.
    Needed because GenericConn stores group names but HTTPSOAP needs group IDs
    for the server's security_groups_ctx_builder to work.
    """
    from zato.common.api import Groups
    from zato.common.odb.model import GenericObject

    if not group_names:
        return []

    out = []

    for name in group_names:

        # .. skip entries that are already numeric IDs ..
        if isinstance(name, int):
            out.append(name)
            continue

        group = session.query(GenericObject).filter(
            GenericObject.name == name,
            GenericObject.type_ == Groups.Type.Group_Parent,
        ).first()

        if group:
            out.append(group.id)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_oauth_capable_bearer_names(session:'any_', group_id_list:'anylist') -> 'anylist':
    """ Returns the names of the bearer token definitions among the members of the given groups
    that carry both an issuer and an audience, which is what verifying a JWT needs.
    """
    from zato.common.api import Groups, SEC_DEF_TYPE
    from zato.common.odb.model import GenericObject, OAuth
    from zato.common.util.sql import parse_instance_opaque_attr

    out = []

    # The member types that bearer definitions are stored under
    bearer_types = (SEC_DEF_TYPE.OAUTH, 'bearer_token')

    for group_id in group_id_list:

        members = session.query(GenericObject).filter(
            GenericObject.parent_object_id == group_id,
            GenericObject.type_ == Groups.Type.Group_Member,
        ).all()

        for member in members:

            # A member's name is its type, the definition's id and the group's id joined with dashes
            sec_type, security_id, _ignored = member.name.split('-')

            if sec_type not in bearer_types:
                continue

            sec_def = session.query(OAuth).filter(OAuth.id == int(security_id)).first()

            if not sec_def:
                continue

            # An inactive definition verifies no tokens
            if not sec_def.is_active:
                continue

            opaque = parse_instance_opaque_attr(sec_def)

            if opaque.get('is_static_token'):
                continue

            has_issuer = bool(opaque.get('issuer') or opaque.get('auth_server_url'))
            has_audience = bool(opaque.get('audience'))

            if has_issuer and has_audience:
                out.append(sec_def.name)

    return out

# ################################################################################################################################
# ################################################################################################################################

def validate_oauth_security(session:'any_', data:'strdict', group_id_list:'anylist') -> 'None':
    """ A gateway with OAuth on needs at least one bearer token definition with an issuer
    and an audience among its security definitions - raises ValueError naming what is missing otherwise.
    """
    if not data.get('oauth'):
        return

    gateway_name = data['name']

    if not group_id_list:
        raise ValueError(f'MCP gateway `{gateway_name}` has OAuth on but no security definitions - ' + \
            'add a bearer token definition with an issuer and an audience')

    names = _get_oauth_capable_bearer_names(session, group_id_list)

    if not names:
        raise ValueError(f'MCP gateway `{gateway_name}` has OAuth on but none of its security definitions ' + \
            'is an active bearer token definition with both an issuer and an audience')

# ################################################################################################################################
# ################################################################################################################################

def find_stranded_oauth_gateway(session:'any_', group_id_list:'anylist', skip_gateway_name:'strnone'=None) -> 'strnone':
    """ Takes a session holding a change that is flushed but not committed and returns the name
    of the first MCP gateway with OAuth on, among those using any of the given groups, that the change
    leaves with no bearer token definition able to verify its tokens, or None if there is no such gateway.
    """
    from zato.common.api import GENERIC
    from zato.common.odb.model import GenericConn
    from zato.common.util.sql import parse_instance_opaque_attr

    gateway_list = session.query(GenericConn).\
        filter(GenericConn.type_ == GENERIC.CONNECTION.TYPE.GATEWAY_MCP).\
        all()

    for gateway in gateway_list:

        if gateway.name == skip_gateway_name:
            continue

        opaque = parse_instance_opaque_attr(gateway)

        # A gateway saved before OAuth existed has it off
        if not opaque.get('oauth'):
            continue

        # A gateway saved before security groups existed uses none
        gateway_groups = opaque.get('security_groups')
        if gateway_groups is None:
            continue

        gateway_group_ids = _resolve_security_group_names_to_ids(session, gateway_groups)

        is_affected = False

        for group_id in group_id_list:
            if group_id in gateway_group_ids:
                is_affected = True
                break

        if not is_affected:
            continue

        try:
            validate_oauth_security(session, {'name': gateway.name, 'oauth': True}, gateway_group_ids)
        except ValueError:
            return gateway.name

    return None

# ################################################################################################################################
# ################################################################################################################################

def _validate_size(data:'strdict', name:'str') -> 'None':
    """ Raises ValueError unless the size of the given name, if present, is a whole number of tokens that is not negative.
    """
    if name not in data:
        return

    value = data[name]

    # The opaque storage keeps 0 and 1 as booleans
    if isinstance(value, bool):
        value = int(value)

    if isinstance(value, str):
        try:
            value = int(value)
        except ValueError:
            raise ValueError(f'The value of `{name}` must be a whole number, not `{value}`')

    if not isinstance(value, int):
        raise ValueError(f'The value of `{name}` must be a whole number, not `{value}`')

    if value < 0:
        raise ValueError(f'The value of `{name}` cannot be negative, it is `{value}`')

# ################################################################################################################################

def validate_size_caps(data:'strdict') -> 'None':
    """ Raises ValueError naming the first size cap of a gateway that the response shaping could not apply.
    """
    from math import isfinite

    from zato.common.util.truncate.tokens import Size_Cap_Mode_Block, Size_Cap_Mode_Truncate

    _validate_size(data, 'max_response_size')
    _validate_size(data, 'min_size_threshold')

    if 'characters_per_token' in data:

        ratio = data['characters_per_token']

        # The opaque storage keeps 0 and 1 as booleans
        if isinstance(ratio, bool):
            ratio = int(ratio)

        if isinstance(ratio, str):
            try:
                ratio = float(ratio)
            except ValueError:
                raise ValueError(f'The value of `characters_per_token` must be a number, not `{ratio}`')

        if not isinstance(ratio, (int, float)):
            raise ValueError(f'The value of `characters_per_token` must be a number, not `{ratio}`')

        if not isfinite(ratio):
            raise ValueError(f'The value of `characters_per_token` must be a finite number, not `{ratio}`')

        if ratio <= 0:
            raise ValueError(f'The value of `characters_per_token` must be greater than zero, it is `{ratio}`')

    if 'size_cap_mode' in data:

        mode = data['size_cap_mode']

        if mode not in (Size_Cap_Mode_Truncate, Size_Cap_Mode_Block):
            raise ValueError(f'The value of `size_cap_mode` must be `{Size_Cap_Mode_Truncate}` or ' + \
                f'`{Size_Cap_Mode_Block}`, not `{mode}`')

# ################################################################################################################################
# ################################################################################################################################

def on_mcp_gateway_create_edit(service:'any_', data:'any_', model:'any_', old_name:'strnone') -> 'None':
    """ Hook called by zato.generic.connection create/edit for the gateway-mcp type.
    Creates or updates the HTTPSOAP channel by invoking the standard http-soap services,
    which handle ODB persistence, uniqueness checks, and broker notification.
    """
    import logging
    from contextlib import closing

    from zato.common.api import CONNECTION, DATA_FORMAT, Groups, URL_TYPE
    from zato.common.exception import BadRequest

    logger = logging.getLogger(__name__)

    gateway_name = data['name']
    url_path = data['url_path']

    # What the gateway is stored with, which is also what its channel follows
    is_active = bool(model.is_active)

    # On create, there is no earlier name
    is_rename = bool(old_name) and old_name != gateway_name

    # The id of the gateway's own group when it is to follow a rename
    group_id_to_rename = None

    with closing(service.server.odb.session()) as session:

        security_groups = data.get('security_groups', [])
        security_groups = _resolve_security_group_names_to_ids(session, security_groups)

        try:

            # The response shaping must be able to apply the size caps to every tool call ..
            validate_size_caps(data)

            # .. and a gateway with OAuth on is saved only with a bearer definition that can verify tokens.
            validate_oauth_security(session, data, security_groups)

        except ValueError as e:
            raise BadRequest(service.cid, str(e))

        # The gateway's channel is found under the name the gateway had before this save ..
        if is_rename:
            lookup_name = old_name
        else:
            lookup_name = gateway_name

        existing = get_mcp_gateway_channel(session, lookup_name)

        # .. a new name may not be one that another channel already has ..
        if other_channel := _get_other_channel(session, gateway_name, existing):
            raise BadRequest(service.cid, f'Channel `{other_channel.name}` already exists')

        # .. and the gateway's group follows a rename, unless a group already has the new name.
        if is_rename:

            new_group_name = get_mcp_group_name(gateway_name)

            if _get_group(session, new_group_name):
                raise BadRequest(service.cid, f'Security group `{new_group_name}` already exists')

            if old_group := _get_group(session, get_mcp_group_name(old_name)):
                group_id_to_rename = old_group.id

    # Build the payload common to both create and edit ..
    payload = {
        'name': gateway_name,
        'url_path': url_path,
        'connection': CONNECTION.CHANNEL,
        'transport': URL_TYPE.PLAIN_HTTP,
        'is_active': is_active,
        'is_internal': True,
        'data_format': DATA_FORMAT.JSON,
        'service': mcp_service_name,
        'security_groups': security_groups,
    }

    if existing:
        payload['id'] = existing.id
        service_name = 'zato.http-soap.edit'
        logger.info('on_mcp_gateway_create_edit: editing HTTPSOAP id=%s name=%s -> %s', existing.id, lookup_name, gateway_name)
    else:
        service_name = 'zato.http-soap.create'
        logger.info('on_mcp_gateway_create_edit: creating HTTPSOAP name=%s url_path=%s', gateway_name, url_path)

    service.invoke(service_name, payload)

    # The group is renamed only once the channel has been saved under the new name
    if group_id_to_rename is not None:
        new_group_name = get_mcp_group_name(gateway_name)
        service.server.groups_manager.edit_group(group_id_to_rename, Groups.Type.API_Clients, new_group_name)
        logger.info('on_mcp_gateway_create_edit: renamed group id=%s to %s', group_id_to_rename, new_group_name)

# ################################################################################################################################
# ################################################################################################################################

def on_mcp_gateway_delete(service:'any_', session:'any_', gateway_name:'str') -> 'None':
    """ Removes the HTTPSOAP channel associated with an MCP gateway.
    Also removes the auto-created security group named mcp.<gateway_name>.
    Called when an MCP generic connection is deleted.
    """
    from zato.common.api import CONNECTION

    # Remove the HTTPSOAP channel by invoking the standard delete service - this both deletes
    # the database row and publishes the config event that removes the URL path
    # from the live request dispatcher, so requests to the deleted channel get 404 ..
    if channel := get_mcp_gateway_channel(session, gateway_name):
        payload = {
            'id': channel.id,
            'connection': CONNECTION.CHANNEL,
            'should_raise_if_missing': False,
        }
        _ = service.invoke('zato.http-soap.delete', payload)

    # .. and remove the gateway's own group through the groups service, which also removes it from every
    # .. other channel and gateway that uses it - the gateway being deleted is left out, since its OAuth
    # .. settings no longer matter.
    if group := _get_group(session, get_mcp_group_name(gateway_name)):
        _ = service.invoke('zato.groups.delete', {
            'id': group.id,
            'skip_gateway_name': gateway_name,
        })

# ################################################################################################################################
# ################################################################################################################################
