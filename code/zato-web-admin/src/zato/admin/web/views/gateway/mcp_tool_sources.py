# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import NamedTuple

# Zato
from zato.common.api import GENERIC

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, dictlist, strlist

# ################################################################################################################################
# ################################################################################################################################

# Where each source's leaf lives in the tree - the group labels mirror the dashboard menu,
# and an empty group means the leaf stands at the root.
_group_root = ''
_group_outgoing = 'Outgoing'
_group_cloud = 'Cloud'
_group_microsoft = 'Microsoft'
_group_search = 'Search'

# The order the tree draws the groups in
_group_order = [_group_root, _group_outgoing, _group_cloud, _group_microsoft, _group_search]

# ################################################################################################################################
# ################################################################################################################################

class ToolSource(NamedTuple):
    """ One row of the Tools card's source table - where the leaf lives,
    what it is called and how its connections are listed.
    """

    # The source's own key - the wizard's hidden inputs and the tree rows carry it
    key: str

    # The opaque-config key the gateway stores this source's allow list under
    config_key: str

    # What the tree shows
    label: str

    # What the summary and the review say
    full_label: str

    # Which tree group the leaf stands in
    group: str

# ################################################################################################################################
# ################################################################################################################################

# Every source the Tools card offers - services first, then the connection groups.
Tool_Source_List = [
    ToolSource('services', 'services', 'Services', 'Services', _group_root),
    ToolSource('rest', 'rest_connections', 'REST', 'REST', _group_outgoing),
    ToolSource('soap', 'soap_connections', 'SOAP', 'SOAP', _group_outgoing),
    ToolSource('sql', 'sql_connections', 'SQL', 'SQL', _group_outgoing),
    ToolSource('odoo', 'odoo_connections', 'Odoo', 'Odoo', _group_outgoing),
    ToolSource('sap', 'sap_connections', 'SAP', 'SAP', _group_outgoing),
    ToolSource('confluence', 'confluence_connections', 'Confluence', 'Confluence', _group_cloud),
    ToolSource('microsoft_365', 'microsoft_365_connections', '365', 'Microsoft 365', _group_microsoft),
    ToolSource('microsoft_fabric', 'microsoft_fabric_connections', 'Fabric', 'Microsoft Fabric', _group_microsoft),
    ToolSource(
        'microsoft_power_automate', 'microsoft_power_automate_connections', 'Power Automate', 'Power Automate',
        _group_microsoft),
    ToolSource('microsoft_teams', 'microsoft_teams_connections', 'Teams', 'Microsoft Teams', _group_microsoft),
    ToolSource('es', 'es_connections', 'Elasticsearch', 'Elasticsearch', _group_search),
]

# The connection sources alone - everything the table holds except the services
Connection_Source_List = []

for _source in Tool_Source_List:
    if _source.key != 'services':
        Connection_Source_List.append(_source)

# ################################################################################################################################
# ################################################################################################################################

def _get_service_items(req:'any_') -> 'strlist':
    """ The names of all the deployed non-internal services.
    """

    response = req.zato.client.invoke('zato.service.get-list', {
        'cluster_id': req.zato.cluster_id,
        'name_filter': '*',
        'paginate': False,
    })

    out:'strlist' = []

    for service in response.data:
        name = service['name']

        if name.startswith('zato.') or name.startswith('pub.zato.'):
            continue

        out.append(name)

    out.sort()
    return out

# ################################################################################################################################

def _get_http_soap_items(req:'any_', transport:'str') -> 'strlist':
    """ The names of the outgoing HTTP connections of one transport.
    """

    response = req.zato.client.invoke('zato.http-soap.get-list', {
        'cluster_id': req.zato.cluster_id,
        'connection': 'outgoing',
        'transport': transport,
        'paginate': False,
    })

    out:'strlist' = []

    for item in response.data:
        name = item['name']

        if name.startswith('zato.') or name.startswith('pub.zato.'):
            continue

        out.append(name)

    out.sort()
    return out

# ################################################################################################################################

def _get_rest_items(req:'any_') -> 'strlist':
    out = _get_http_soap_items(req, 'plain_http')
    return out

# ################################################################################################################################

def _get_soap_items(req:'any_') -> 'strlist':
    out = _get_http_soap_items(req, 'soap')
    return out

# ################################################################################################################################

def _get_sql_items(req:'any_') -> 'strlist':
    """ The names of the outgoing SQL connections.
    """

    response = req.zato.client.invoke('zato.outgoing.sql.get-list', {
        'cluster_id': req.zato.cluster_id,
    })

    out:'strlist' = []

    for item in response.data:
        out.append(item['name'])

    out.sort()
    return out

# ################################################################################################################################

def _get_odoo_items(req:'any_') -> 'strlist':
    """ The names of the outgoing Odoo connections.
    """

    response = req.zato.client.invoke('zato.outgoing.odoo.get-list', {
        'cluster_id': req.zato.cluster_id,
    })

    out:'strlist' = []

    for item in response.data:
        out.append(item['name'])

    out.sort()
    return out

# ################################################################################################################################

def _get_generic_items(req:'any_', type_:'str') -> 'strlist':
    """ The names of the generic connections of one type.
    """

    response = req.zato.client.invoke('zato.generic.connection.get-list', {
        'cluster_id': req.zato.cluster_id,
        'type_': type_,
        'paginate': False,
    })

    out:'strlist' = []

    for item in response.data:
        out.append(item['name'])

    out.sort()
    return out

# ################################################################################################################################

def _get_sap_items(req:'any_') -> 'strlist':
    out = _get_generic_items(req, GENERIC.CONNECTION.TYPE.OUTCONN_SAP)
    return out

def _get_confluence_items(req:'any_') -> 'strlist':
    out = _get_generic_items(req, GENERIC.CONNECTION.TYPE.CLOUD_CONFLUENCE)
    return out

def _get_microsoft_365_items(req:'any_') -> 'strlist':
    out = _get_generic_items(req, GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_365)
    return out

def _get_microsoft_fabric_items(req:'any_') -> 'strlist':
    out = _get_generic_items(req, GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_FABRIC)
    return out

def _get_microsoft_power_automate_items(req:'any_') -> 'strlist':
    out = _get_generic_items(req, GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_POWER_AUTOMATE)
    return out

def _get_microsoft_teams_items(req:'any_') -> 'strlist':
    out = _get_generic_items(req, GENERIC.CONNECTION.TYPE.CHAT_MICROSOFT_TEAMS)
    return out

def _get_es_items(req:'any_') -> 'strlist':
    out = _get_generic_items(req, GENERIC.CONNECTION.TYPE.OUTCONN_ES)
    return out

# ################################################################################################################################
# ################################################################################################################################

# How each source's items are listed
_item_getters = {
    'services': _get_service_items,
    'rest': _get_rest_items,
    'soap': _get_soap_items,
    'sql': _get_sql_items,
    'odoo': _get_odoo_items,
    'sap': _get_sap_items,
    'confluence': _get_confluence_items,
    'microsoft_365': _get_microsoft_365_items,
    'microsoft_fabric': _get_microsoft_fabric_items,
    'microsoft_power_automate': _get_microsoft_power_automate_items,
    'microsoft_teams': _get_microsoft_teams_items,
    'es': _get_es_items,
}

# ################################################################################################################################
# ################################################################################################################################

def get_source_items(req:'any_', source_key:'str') -> 'strlist':
    """ The items one source offers right now.
    """

    getter = _item_getters[source_key]

    out = getter(req)
    return out

# ################################################################################################################################

def build_tool_sources(req:'any_', assigned_by_key:'anydict') -> 'dictlist':
    """ The tree the wizard's Tools card renders from - group nodes mirror the dashboard
    menu, leaves are the sources, each with its items and the names already assigned.
    Sources with nothing to offer are pruned by the card itself.
    """

    # Every leaf, keyed by the tree group it stands in ..
    leaves_by_group:'anydict' = {}

    for source in Tool_Source_List:

        items = get_source_items(req, source.key)

        if (assigned := assigned_by_key.get(source.key)) is None:
            assigned = []

        leaf = {
            'key': source.key,
            'label': source.label,
            'full_label': source.full_label,
            'items': items,
            'assigned': assigned,
        }

        group_leaves = leaves_by_group.setdefault(source.group, [])
        group_leaves.append(leaf)

    # .. and the tree itself, in the dashboard menu's order.
    out:'dictlist' = []

    for group in _group_order:

        if not (group_leaves := leaves_by_group.get(group)):
            continue

        if group == _group_root:
            out.extend(group_leaves)
        else:
            out.append({
                'label': group,
                'children': group_leaves,
            })

    return out

# ################################################################################################################################
# ################################################################################################################################
