# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Object section of an MCP gateway's evidence - what the gateway is, read off the ODB as every other object's is,
# so the model reads what the gateway exposes and how it shapes its responses before it reads what the agents did
# with it. The callers are named by their security definitions, never by their credentials.

from __future__ import annotations

# Zato
from zato.common.alerting.explain.settings_info import settings_lines, Off, On
from zato.common.alerting.object_config import alert_type_mcp
from zato.common.api import GENERIC, Groups, MCP
from zato.common.odb.model import GenericConn, GenericObject, SecurityBase
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import anylist, stranydict, strlist
    anylist = anylist
    SASession = SASession
    stranydict = stranydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# What the Type line of the gateway reads as
_type_label = 'MCP gateway'

# What a gateway says of tools, skills or callers it has none of
_none = 'None'

# The safeguard stages a gateway may have on, each with what it reads as in the Safeguards line
_safeguard_flags = (
    ('safeguards_pii_enabled',        'PII removal'),
    ('safeguards_secrets_enabled',    'secrets removal'),
    ('safeguards_normalize_unicode',  'Unicode normalization'),
    ('safeguards_sanitize_markup',    'markup sanitization'),
    ('safeguards_url_policy_enabled', 'URL policy'),
    ('safeguards_strip_nulls',        'null stripping'),
    ('safeguards_collapse_whitespace', 'whitespace collapsing'),
    ('safeguards_strip_base64',       'base64 stripping'),
)

# A member of a security group is stored as `<sec type>-<security id>-<group id>`
_member_name_parts = 3

# ################################################################################################################################
# ################################################################################################################################

def _stored_list(opaque:'stranydict', name:'str') -> 'strlist':
    """ One stored list of the gateway - empty when the gateway was saved before the key existed.
    """
    if name in opaque:
        out = opaque[name]
    else:
        out = []

    return out

# ################################################################################################################################

def _stored_flag(opaque:'stranydict', name:'str') -> 'bool':
    """ One stored flag of the gateway - off when the gateway was saved before the key existed.
    """
    out = opaque.get(name) is True
    return out

# ################################################################################################################################

def _tool_lines(opaque:'stranydict') -> 'anylist':
    """ The tools the gateway exposes - its services by name and its connections by group, with how many in all,
    which is the number the too-many-tools rule reads at the time of the sweep.
    """

    # Our response to produce
    out:'anylist' = []

    services = _stored_list(opaque, 'services')
    tool_count = len(services)

    if services:
        out.append(('Services', ', '.join(services)))

    for key in MCP.Connection_List_Keys:
        connection_names = _stored_list(opaque, key)

        if connection_names:
            label = key.replace('_connections', '').replace('_', ' ').capitalize() + ' connections'
            out.append((label, ', '.join(connection_names)))
            tool_count += len(connection_names)

    out.append(('Tools', tool_count))

    skills = _stored_list(opaque, 'skills')

    if skills:
        out.append(('Skills', ', '.join(skills)))
    else:
        out.append(('Skills', _none))

    return out

# ################################################################################################################################

def _group_ids(session:'SASession', cluster_id:'int', groups:'list') -> 'list':
    """ The ids of the gateway's security groups - a gateway saved through the dashboard stores their ids,
    one imported through enmasse stores their names, so the names are looked up.
    """
    out:'list' = []
    names:'strlist' = []

    for group in groups:
        if isinstance(group, int):
            out.append(group)
        else:
            names.append(group)

    if names:
        group_rows = session.query(GenericObject.id).\
            filter(GenericObject.cluster_id==cluster_id).\
            filter(GenericObject.type_==Groups.Type.Group_Parent).\
            filter(GenericObject.subtype==Groups.Type.API_Clients).\
            filter(GenericObject.name.in_(names)).\
            all()

        for (group_id,) in group_rows:
            out.append(group_id)

    return out

# ################################################################################################################################

def _caller_names(session:'SASession', cluster_id:'int', groups:'list') -> 'strlist':
    """ The names of the security definitions that may call the gateway - the members of its security groups.
    """
    group_ids = _group_ids(session, cluster_id, groups)

    if not group_ids:
        return []

    member_rows = session.query(GenericObject.name).\
        filter(GenericObject.cluster_id==cluster_id).\
        filter(GenericObject.type_==Groups.Type.Group_Member).\
        filter(GenericObject.parent_object_id.in_(group_ids)).\
        all()

    security_ids:'list' = []

    for (member_name,) in member_rows:
        parts = member_name.split('-')

        if len(parts) != _member_name_parts:
            continue

        security_ids.append(int(parts[1]))

    if not security_ids:
        return []

    security_rows = session.query(SecurityBase.name).\
        filter(SecurityBase.cluster_id==cluster_id).\
        filter(SecurityBase.id.in_(security_ids)).\
        order_by(SecurityBase.name).\
        all()

    # Our response to produce
    out:'strlist' = []

    for (security_name,) in security_rows:
        out.append(security_name)

    return out

# ################################################################################################################################

def _shaping_lines(opaque:'stranydict') -> 'anylist':
    """ How the gateway shapes what tools return - whether it validates arguments, what its size cap does and
    which safeguards are on - what a rejection or a truncation in the evidence came from.
    """

    # Our response to produce
    out:'anylist' = []

    out.append(('Input validation', On if _stored_flag(opaque, 'validate_input') else Off))

    max_response_size = opaque.get('max_response_size')

    if max_response_size:
        out.append(('Size cap', f'{max_response_size} tokens, mode {opaque["size_cap_mode"]}'))
    else:
        out.append(('Size cap', Off))

    safeguards:'strlist' = []

    for key, label in _safeguard_flags:
        if _stored_flag(opaque, key):
            safeguards.append(label)

    if safeguards:
        out.append(('Safeguards', ', '.join(safeguards)))
    else:
        out.append(('Safeguards', _none))

    out.append(('Agent filters', On if _stored_flag(opaque, 'allow_agent_filters') else Off))

    return out

# ################################################################################################################################

def describe_mcp_gateway(session:'SASession', cluster_id:'int', name:'str') -> 'anylist | None':
    """ The label and value pairs describing one MCP gateway - its path, the tools and skills it exposes, who may
    call it, how it shapes responses, whether its audit log is on and the alert thresholds it sets of its own.
    None when no MCP gateway goes by the name in the cluster.
    """
    row = session.query(GenericConn).\
        filter(GenericConn.cluster_id==cluster_id).\
        filter(GenericConn.type_==GENERIC.CONNECTION.TYPE.GATEWAY_MCP).\
        filter(GenericConn.name==name).\
        first()

    if row is None:
        return None

    opaque = parse_instance_opaque_attr(row)

    # Our response to produce
    out:'anylist' = []

    out.append(('Name', row.name))
    out.append(('Type', _type_label))
    out.append(('Active', 'yes' if row.is_active else 'no'))

    if 'url_path' in opaque:
        out.append(('Path', opaque['url_path']))

    out.extend(_tool_lines(opaque))

    callers = _caller_names(session, cluster_id, _stored_list(opaque, 'security_groups'))

    if callers:
        out.append(('Callers', ', '.join(callers)))
    else:
        out.append(('Callers', _none))

    out.extend(_shaping_lines(opaque))

    # The alerts read the audit log, so a gateway with it off has nothing for them to count
    out.append(('Audit log', On if _stored_flag(opaque, 'is_audit_log_active') else Off))

    out.extend(settings_lines(alert_type_mcp, opaque))

    return out

# ################################################################################################################################
# ################################################################################################################################
