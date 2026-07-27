# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps
from logging import getLogger
from traceback import format_exc

# Django
from django.http import HttpResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.common.api import CONNECTION, GENERIC, URL_TYPE
from zato.common.destination.constants import DestinationType

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, strlist

    anylist = anylist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

# Which generic connection type each destination type reads its connections from. REST and e-mail
# are not generic connections, so they are not here - each has a list service of its own.
_generic_type = {
    DestinationType.MLLP: GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP,
    DestinationType.FHIR: GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR,
}

# What lists the e-mail connections a destination may deliver through
_smtp_service = 'zato.email.smtp.get-list'

# What lists the REST connections a destination may deliver through
_rest_service = 'zato.http-soap.get-list'

# ################################################################################################################################
# ################################################################################################################################

def _get_names(req:'any_', service:'str', request:'any_') -> 'strlist':
    """ Returns the name of every connection one list service reports, in the order it reports them.
    A type whose service cannot be reached contributes no names rather than failing the whole list,
    because a destination of another type is still to be pickable.
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

def _get_rest_names(req:'any_') -> 'strlist':
    """ Returns the outgoing REST connections, which is what a REST destination delivers through.
    """
    request = {
        'cluster_id': req.zato.cluster_id,
        'connection': CONNECTION.OUTGOING,
        'transport': URL_TYPE.PLAIN_HTTP,
    }

    out = _get_names(req, _rest_service, request)
    return out

# ################################################################################################################################

def _get_generic_names(req:'any_', destination_type:'str') -> 'strlist':
    """ Returns the outgoing connections of one generic type - the MLLP and FHIR destinations.
    """
    request = {
        'cluster_id': req.zato.cluster_id,
        'type_': _generic_type[destination_type],
        'paginate': False,
    }

    out = _get_names(req, 'zato.generic.connection.get-list', request)
    return out

# ################################################################################################################################

def _get_smtp_names(req:'any_') -> 'strlist':
    """ Returns the e-mail connections, which is what an e-mail destination delivers through.
    """
    request = {
        'cluster_id': req.zato.cluster_id,
    }

    out = _get_names(req, _smtp_service, request)
    return out

# ################################################################################################################################

def _as_rows(names:'strlist') -> 'anylist':
    """ Turns connection names into what the destinations tab reads them as - one object per
    connection, named by the only thing a destination stores about it.
    """
    out:'anylist' = [{'name': name} for name in names]
    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def get_connection_list(req:'any_') -> 'HttpResponse':
    """ Returns the connections that a channel's destinations can be pointed at, grouped by
    destination type - one round trip per type, made once per page the destinations tab is on.
    """
    connection_list = {
        DestinationType.REST: _as_rows(_get_rest_names(req)),
        DestinationType.MLLP: _as_rows(_get_generic_names(req, DestinationType.MLLP)),
        DestinationType.FHIR: _as_rows(_get_generic_names(req, DestinationType.FHIR)),
        DestinationType.SMTP: _as_rows(_get_smtp_names(req)),
    }

    data = dumps(connection_list)
    data = data.encode('utf-8')

    out = HttpResponse(data, content_type='application/json')
    return out

# ################################################################################################################################
# ################################################################################################################################
