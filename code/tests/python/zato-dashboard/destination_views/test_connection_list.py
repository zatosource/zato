# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The destinations tab picks connections out of what one endpoint reports, one group per
# destination type, so what that endpoint reads them from and the shape it answers in are
# what the tab is built on.

# stdlib
from json import loads

# Zato
from zato.admin.web.views.destinations import get_connection_list
from zato.common.api import GENERIC

# Test support
from request_stub import new_request

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_rest_service = 'zato.http-soap.get-list'
_generic_service = 'zato.generic.connection.get-list'
_smtp_service = 'zato.email.smtp.get-list'

# ################################################################################################################################
# ################################################################################################################################

def _new_request_with_connections() -> 'any_':
    """ Builds a request whose server reports one connection of every kind a destination
    may deliver through.
    """
    out = new_request()

    out.zato.client.set_response(_rest_service, [{'name': 'test.rest.billing'}])
    out.zato.client.set_response(_generic_service, [{'name': 'test.hl7.forward'}])
    out.zato.client.set_response(_smtp_service, [{'name': 'test.smtp.alerts'}])

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_every_destination_type_is_grouped_on_its_own() -> 'None':
    """ The tab reads its rows from four groups, keyed by the destination types it offers.
    """
    request = _new_request_with_connections()

    response = get_connection_list(request)
    data = loads(response.content)

    assert sorted(data) == ['hl7-fhir', 'hl7-mllp', 'rest', 'smtp']

    assert data['rest'] == [{'name': 'test.rest.billing'}]
    assert data['smtp'] == [{'name': 'test.smtp.alerts'}]

# ################################################################################################################################

def test_the_rest_connections_are_the_outgoing_ones() -> 'None':
    """ A REST destination delivers through an outgoing connection, never through a channel.
    """
    request = _new_request_with_connections()

    _ = get_connection_list(request)
    sent = request.zato.client.get_request(_rest_service)

    assert sent['connection'] == 'outgoing'
    assert sent['transport'] == 'plain_http'

# ################################################################################################################################

def test_mllp_and_fhir_read_their_own_generic_types() -> 'None':
    """ The two HL7 destination types are generic connections, each read by its own type.
    """
    request = _new_request_with_connections()

    _ = get_connection_list(request)

    types_asked_for = []

    for service, sent in request.zato.client.invocations:
        if service == _generic_service:
            types_asked_for.append(sent['type_'])

    assert types_asked_for == [
        GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP,
        GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR,
    ]

# ################################################################################################################################

def test_a_type_with_no_connections_is_reported_as_empty() -> 'None':
    """ A cluster with no connection of one kind still offers the other kinds, that group
    simply being empty.
    """
    request = new_request()
    request.zato.client.set_response(_rest_service, [{'name': 'test.rest.billing'}])

    response = get_connection_list(request)
    data = loads(response.content)

    assert data['rest'] == [{'name': 'test.rest.billing'}]
    assert data['smtp'] == []
    assert data['hl7-mllp'] == []
    assert data['hl7-fhir'] == []

# ################################################################################################################################

def test_a_service_that_cannot_be_reached_leaves_its_group_empty() -> 'None':
    """ One list service failing never takes the whole tab down - a destination of another
    type is still to be pickable.
    """
    request = new_request()
    request.zato.client.set_response(_rest_service, None, is_ok=False, details='Server is down')
    request.zato.client.set_response(_smtp_service, [{'name': 'test.smtp.alerts'}])

    response = get_connection_list(request)
    data = loads(response.content)

    assert data['rest'] == []
    assert data['smtp'] == [{'name': 'test.smtp.alerts'}]

# ################################################################################################################################
# ################################################################################################################################
