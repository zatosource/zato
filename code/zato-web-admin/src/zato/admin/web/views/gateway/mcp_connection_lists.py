# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps

# Django
from django.http import HttpResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.admin.web.views.gateway.mcp_tool_sources import get_source_items
from zato.common.api import GENERIC

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdictlist, strset

# ################################################################################################################################
# ################################################################################################################################

def _get_gateway_allow_list(req:'any_', gateway_id:'str', config_key:'str') -> 'strset':
    """ The names one gateway's allow list of the given key holds right now.
    """

    out:'strset' = set()

    response = req.zato.client.invoke('zato.generic.connection.get-list', {
        'cluster_id': req.zato.cluster_id,
        'type_': GENERIC.CONNECTION.TYPE.GATEWAY_MCP,
        'paginate': False,
    })

    if response.ok:
        if response.data:
            for gateway_item in response.data:
                if str(gateway_item['id']) == str(gateway_id):

                    # A gateway saved before the key existed exposes nothing under it
                    if (assigned := gateway_item.get(config_key)) is None:
                        assigned = []

                    out = set(assigned)
                    break

    return out

# ################################################################################################################################

def _connection_list_response(req:'any_', source_key:'str', config_key:'str') -> 'HttpResponse':
    """ One source's connections as the badge picker's JSON - each item carries
    whether the gateway being edited, if any, already exposes it.
    """

    # The gateway ID is provided when editing an existing gateway ..
    gateway_id = req.GET.get('gateway_id')

    # .. its allow list is what marks the items as assigned ..
    if gateway_id:
        assigned_names = _get_gateway_allow_list(req, gateway_id, config_key)
    else:
        assigned_names = set()

    # .. every connection of the source is one item ..
    items:'strdictlist' = []

    for name in get_source_items(req, source_key):
        items.append({
            'id': name,
            'name': name,
            'is_member': name in assigned_names,
        })

    # .. and the JSON response goes out.
    serialized = dumps(items)

    out = HttpResponse(serialized, content_type='application/json') # type: ignore
    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def get_rest_list(req:'any_') -> 'HttpResponse':
    """ Returns the outgoing REST connections for the Tools card picker.
    """
    out = _connection_list_response(req, 'rest', 'rest_connections')
    return out

# ################################################################################################################################

@method_allowed('POST')
def get_soap_list(req:'any_') -> 'HttpResponse':
    """ Returns the outgoing SOAP connections for the Tools card picker.
    """
    out = _connection_list_response(req, 'soap', 'soap_connections')
    return out

# ################################################################################################################################

@method_allowed('POST')
def get_sql_list(req:'any_') -> 'HttpResponse':
    """ Returns the outgoing SQL connections for the Tools card picker.
    """
    out = _connection_list_response(req, 'sql', 'sql_connections')
    return out

# ################################################################################################################################

@method_allowed('POST')
def get_odoo_list(req:'any_') -> 'HttpResponse':
    """ Returns the outgoing Odoo connections for the Tools card picker.
    """
    out = _connection_list_response(req, 'odoo', 'odoo_connections')
    return out

# ################################################################################################################################

@method_allowed('POST')
def get_sap_list(req:'any_') -> 'HttpResponse':
    """ Returns the SAP connections for the Tools card picker.
    """
    out = _connection_list_response(req, 'sap', 'sap_connections')
    return out

# ################################################################################################################################

@method_allowed('POST')
def get_confluence_list(req:'any_') -> 'HttpResponse':
    """ Returns the Confluence connections for the Tools card picker.
    """
    out = _connection_list_response(req, 'confluence', 'confluence_connections')
    return out

# ################################################################################################################################

@method_allowed('POST')
def get_microsoft_365_list(req:'any_') -> 'HttpResponse':
    """ Returns the Microsoft 365 connections for the Tools card picker.
    """
    out = _connection_list_response(req, 'microsoft_365', 'microsoft_365_connections')
    return out

# ################################################################################################################################

@method_allowed('POST')
def get_microsoft_fabric_list(req:'any_') -> 'HttpResponse':
    """ Returns the Microsoft Fabric connections for the Tools card picker.
    """
    out = _connection_list_response(req, 'microsoft_fabric', 'microsoft_fabric_connections')
    return out

# ################################################################################################################################

@method_allowed('POST')
def get_microsoft_power_automate_list(req:'any_') -> 'HttpResponse':
    """ Returns the Microsoft Power Automate connections for the Tools card picker.
    """
    out = _connection_list_response(req, 'microsoft_power_automate', 'microsoft_power_automate_connections')
    return out

# ################################################################################################################################

@method_allowed('POST')
def get_microsoft_teams_list(req:'any_') -> 'HttpResponse':
    """ Returns the Microsoft Teams connections for the Tools card picker.
    """
    out = _connection_list_response(req, 'microsoft_teams', 'microsoft_teams_connections')
    return out

# ################################################################################################################################

@method_allowed('POST')
def get_es_list(req:'any_') -> 'HttpResponse':
    """ Returns the Elasticsearch connections for the Tools card picker.
    """
    out = _connection_list_response(req, 'es', 'es_connections')
    return out

# ################################################################################################################################
# ################################################################################################################################
