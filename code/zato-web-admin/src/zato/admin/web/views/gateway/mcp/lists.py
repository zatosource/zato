# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from json import dumps

# Django
from django.http import HttpResponse

# Zato
from zato.admin.web.util import get_server_directory
from zato.admin.web.views import method_allowed
from zato.admin.web.views.gateway.mcp.common import logger
from zato.common.api import GENERIC, Groups, Sec_Def_Type_Name
from zato.common.skills.api import get_skill_name_list

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdictlist, strset
    any_ = any_
    strdictlist = strdictlist
    strset = strset

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def get_service_list(req:'any_') -> 'HttpResponse':
    """ Returns the list of all non-internal services for the badge picker.
    """

    # The gateway ID is provided when editing an existing gateway ..
    gateway_id = req.GET.get('gateway_id')

    # .. get all deployed services ..
    response = req.zato.client.invoke('zato.service.get-list', {
        'cluster_id': req.zato.cluster_id,
        'name_filter': '*',
        'paginate': False,
    })

    # .. build the current assigned set if editing ..
    assigned_names:'set[str]' = set()
    if gateway_id:
        gateway_response = req.zato.client.invoke('zato.generic.connection.get-list', {
            'cluster_id': req.zato.cluster_id,
            'type_': GENERIC.CONNECTION.TYPE.GATEWAY_MCP,
            'id': gateway_id,
            'paginate': False,
        })
        logger.info('MCP get_service_list: gateway_id=%s, response.ok=%s, data_count=%s',
            gateway_id, gateway_response.ok, len(gateway_response.data) if gateway_response.data else 0)

        if gateway_response.ok and gateway_response.data:
            for gateway_item in gateway_response.data:
                item_id = gateway_item['id']
                item_services = gateway_item.get('services')
                logger.info('MCP get_service_list: item id=%s (%s) vs gateway_id=%s (%s), services=%s',
                    item_id, type(item_id).__name__, gateway_id, type(gateway_id).__name__, item_services)
                if str(item_id) == str(gateway_id):
                    assigned_names = set(item_services or [])
                    logger.info('MCP get_service_list: matched, assigned_names=%s', assigned_names)
                    break
        else:
            logger.info('MCP get_service_list: no data or not ok')

    logger.info('MCP get_service_list: final assigned_names=%s', assigned_names)

    # .. build the output list, skipping internal services ..
    items:'strdictlist' = []
    for service in response.data:
        name = service['name']

        if name.startswith('zato.') or name.startswith('pub.zato.'):
            continue

        items.append({
            'id': name,
            'name': name,
            'is_member': name in assigned_names,
        })

    # .. sort alphabetically ..
    items.sort(key=lambda item: item['name'])

    # .. and return the JSON response.
    out = dumps(items)
    return HttpResponse(out, content_type='application/json') # type: ignore

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def get_security_list(req:'any_') -> 'HttpResponse':
    """ Returns the list of available security definitions (API key, Basic Auth)
    for the security badge picker, with is_member flags set based on the gateway's
    auto-created security group.
    """

    # The gateway ID is provided when editing an existing gateway ..
    gateway_id = req.GET.get('gateway_id')

    # .. get all available security definitions of the supported types ..
    response = req.zato.client.invoke('zato.security.get-list', {
        'sec_type': ['apikey', 'basic_auth'],
        'paginate': False,
    })

    # .. extract the items, skipping built-in and internal entries ..
    items:'strdictlist' = []
    for item in response.data:
        name = item['name']
        if name in {'ide_publisher', 'pubapi'} or 'zato.' in name:
            continue

        sec_type = item['sec_type']
        sec_type_name = Sec_Def_Type_Name[sec_type] # type: ignore
        items.append({
            'id': item['id'],
            'name': name,
            'sec_type': sec_type,
            'sec_type_name': sec_type_name,
            'is_member': False,
        })

    # .. sort by type then name ..
    items.sort(key=lambda elem: (elem['sec_type'], elem['name']))

    # .. if editing, figure out which definitions are already assigned ..
    if gateway_id:

        logger.info('MCP get_security_list: gateway_id=%s', gateway_id)

        # .. look up the gateway's security_groups field ..
        gateway_response = req.zato.client.invoke('zato.generic.connection.get-list', {
            'cluster_id': req.zato.cluster_id,
            'type_': GENERIC.CONNECTION.TYPE.GATEWAY_MCP,
            'paginate': False,
        })

        logger.info('MCP get_security_list: gateway_response.ok=%s, data_count=%s',
            gateway_response.ok, len(gateway_response.data) if gateway_response.data else 0)

        if gateway_response.ok and gateway_response.data:
            for gateway_item in gateway_response.data:
                item_id = gateway_item['id']
                logger.info('MCP get_security_list: item id=%s (%s) vs gateway_id=%s (%s), keys=%s',
                    item_id, type(item_id).__name__, gateway_id, type(gateway_id).__name__,
                    list(gateway_item.keys()))

                if str(item_id) == str(gateway_id):
                    security_groups = gateway_item.get('security_groups', [])
                    logger.info('MCP get_security_list: matched, security_groups=%s', security_groups)

                    if security_groups:
                        group_id = security_groups[0]
                        logger.info('MCP get_security_list: fetching members for group_id=%s', group_id)

                        member_response = req.zato.client.invoke('zato.groups.get-member-list', {
                            'group_type': Groups.Type.API_Clients,
                            'group_id': group_id,
                        })

                        logger.info('MCP get_security_list: member_response.ok=%s, data=%s',
                            member_response.ok, member_response.data)

                        if member_response.ok and member_response.data:
                            member_security_ids = {m['security_id'] for m in member_response.data}
                            logger.info('MCP get_security_list: member_security_ids=%s', member_security_ids)
                            for item in items:
                                if item['id'] in member_security_ids:
                                    item['is_member'] = True
                                    logger.info('MCP get_security_list: marked as assigned: id=%s name=%s', item['id'], item['name'])
                    break

    logger.info('MCP get_security_list: returning %d items, %d assigned',
        len(items), sum(1 for item in items if item['is_member']))

    # .. and return the JSON response.
    out = dumps(items)
    return HttpResponse(out, content_type='application/json') # type: ignore

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def get_skill_list(req:'any_') -> 'HttpResponse':
    """ Returns the list of user skills for the skills badge picker, with is_member
    flags set based on the gateway's allow list.
    """

    # The gateway ID is provided when editing an existing gateway ..
    gateway_id = req.GET.get('gateway_id')

    # .. skills live on disk under the server's config/repo directory ..
    server_directory = get_server_directory()
    repo_location = os.path.join(server_directory, 'config', 'repo')
    skill_names = get_skill_name_list(repo_location)

    # .. build the current allow list if editing ..
    assigned_names:'strset' = set()
    if gateway_id:
        gateway_response = req.zato.client.invoke('zato.generic.connection.get-list', {
            'cluster_id': req.zato.cluster_id,
            'type_': GENERIC.CONNECTION.TYPE.GATEWAY_MCP,
            'paginate': False,
        })

        if gateway_response.ok:
            if gateway_response.data:
                for gateway_item in gateway_response.data:
                    if str(gateway_item['id']) == gateway_id:

                        # A gateway saved without the key serves no skills
                        gateway_skills = gateway_item.get('skills')
                        if gateway_skills is None:
                            gateway_skills = []

                        assigned_names = set(gateway_skills)
                        break

    # .. each skill directory is one badge ..
    items:'strdictlist' = []
    for name in skill_names:
        items.append({
            'id': name,
            'name': name,
            'is_member': name in assigned_names,
        })

    # .. and return the JSON response.
    serialized = dumps(items)
    payload = serialized.encode('utf-8')

    out = HttpResponse(payload, content_type='application/json')
    return out

# ################################################################################################################################
# ################################################################################################################################
