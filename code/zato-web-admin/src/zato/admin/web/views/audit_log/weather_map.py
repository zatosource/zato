# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The weather map page - the whole estate of connections drawn as a generated world,
one landmass per connection type, one city per connection.
"""

# stdlib
import json
import logging
import os
from traceback import format_exc

# PyYAML
import yaml

# Django
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.admin.web.views.audit_log.columns import _object_page_url, _source_label, _source_page_url
from zato.common.api import CONNECTION, GENERIC, URL_TYPE
from zato.common.audit_log.common import AuditSource
from zato.common.defaults import default_cluster_id

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, strlist
    any_ = any_
    anylist = anylist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Most connection types are generic connections, all listed by this one service
_generic_service = 'zato.generic.connection.get-list'

# Which service lists each source's connections and with what request beyond the cluster id.
# Every source here is an audit source, so every city and continent can lead into the log.
_inventory_services = [

    (AuditSource.REST_Channel, 'zato.http-soap.get-list',
        {'connection': CONNECTION.CHANNEL, 'transport': URL_TYPE.PLAIN_HTTP}),

    (AuditSource.REST_Outgoing, 'zato.http-soap.get-list',
        {'connection': CONNECTION.OUTGOING, 'transport': URL_TYPE.PLAIN_HTTP}),

    (AuditSource.MLLP_Channel, _generic_service,
        {'type_': GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP, 'paginate': False}),

    (AuditSource.MLLP_Outgoing, _generic_service,
        {'type_': GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP, 'paginate': False}),

    (AuditSource.FHIR, _generic_service,
        {'type_': GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR, 'paginate': False}),

    (AuditSource.Email_IMAP, 'zato.email.imap.get-list',
        {'paginate': False, 'cur_page': 1}),

    (AuditSource.Email_SMTP, 'zato.email.smtp.get-list',
        {'paginate': False, 'cur_page': 1}),

    (AuditSource.PubSub, 'zato.pubsub.topic.get-list', {}),

    (AuditSource.SQL_Outgoing, 'zato.outgoing.sql.get-list', {}),
]

# ################################################################################################################################
# ################################################################################################################################

def _get_names(req:'any_', service:'str', request:'any_') -> 'strlist':
    """ Returns the name of every connection one list service reports. A type whose service
    cannot be reached contributes no names rather than failing the whole map - the other
    continents are still to be drawn.
    """
    out:'strlist' = []

    try:
        response = req.zato.client.invoke(service, request)
    except Exception:
        logger.warning('Could not read the connection list from `%s`; e:`%s`', service, format_exc())
        return out

    if not response.ok:
        logger.warning('Could not read the connection list from `%s`; details:`%s`', service, response.details)
        return out

    # A cluster with no connection of that type at all answers with nothing to iterate over
    if not response.data:
        return out

    for item in response.data:
        out.append(item.name)

    return out

# ################################################################################################################################

def _get_inventory(req:'any_') -> 'anylist':
    """ Returns every connection the cluster is configured with, grouped by source - one
    round trip per type. A type with no connections draws no landmass, so it is not returned.
    """
    out:'anylist' = []

    for source, service, request_extras in _inventory_services:

        request = {'cluster_id': req.zato.cluster_id}
        request.update(request_extras)

        names = _get_names(req, service, request)

        if names:
            names.sort()
            out.append({'source': source, 'label': _source_label[source], 'objects': names})

    return out

# ################################################################################################################################
# ################################################################################################################################

# The map may be drawn out of a static enmasse file instead of the live cluster -
# point this environment variable to the file to use it.
_enmasse_path_env = 'Zato_Weather_Map_Enmasse_Path'

# Which enmasse section feeds which audit source
_enmasse_sections = [
    (AuditSource.REST_Channel, 'channel_rest'),
    (AuditSource.REST_Outgoing, 'outgoing_rest'),
    (AuditSource.SQL_Outgoing, 'outconn_sql'),
]

# ################################################################################################################################

def _get_enmasse_inventory(path:'str') -> 'anylist':
    """ Returns the inventory read from a static enmasse file - each section's item names
    become that source's connections.
    """
    out:'anylist' = []

    with open(path) as file_:
        config = yaml.safe_load(file_)

    for source, section in _enmasse_sections:

        items = config[section]

        # An empty enmasse section is parsed as None rather than as an empty list
        if not items:
            continue

        names:'strlist' = []

        for item in items:
            names.append(item['name'])

        names.sort()
        out.append({'source': source, 'label': _source_label[source], 'objects': names})

    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req:'any_') -> 'TemplateResponse':
    """ The weather map page. The page is a shell - the world is generated in the browser
    out of the inventory rendered into it, deterministically, so one configuration always
    draws one and the same map.
    """
    enmasse_path = os.environ.get(_enmasse_path_env)

    if enmasse_path:
        inventory = _get_enmasse_inventory(enmasse_path)
    else:
        inventory = _get_inventory(req)

    return_data = {
        'cluster_id': default_cluster_id,
        'inventory_json': json.dumps(inventory),
        'source_links_json': json.dumps(_source_page_url),
        'object_links_json': json.dumps(_object_page_url),
        'zato_clusters': True,
        'zato_template_name': 'zato/audit-log-weather-map.html',
    }

    out = TemplateResponse(req, 'zato/audit-log-weather-map.html', return_data)

    return out

# ################################################################################################################################
# ################################################################################################################################
