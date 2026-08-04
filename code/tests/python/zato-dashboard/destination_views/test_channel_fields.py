# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The three destination fields the MLLP wizard and editor post have to reach the server exactly
# as they were sent and come back the same way, and a new channel handing its messages to neither
# a service nor a destination has to be refused rather than stored with nowhere to deliver.

# stdlib
from http import HTTPStatus
from json import loads

# Zato
from zato.admin.web.views.channel.hl7.mllp import Create, Edit, Index
from zato.common.ext.bunch import bunchify

# Test support
from request_stub import new_channel_post_data, new_destination_list, new_request

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

_create_service = 'zato.generic.connection.create'
_edit_service = 'zato.generic.connection.edit'

# What a saved channel comes back as
_saved_channel = {'id': 123, 'name': 'test.mllp.channel'}

# ################################################################################################################################
# ################################################################################################################################

def _get_sent(response:'any_', request:'any_', service:'str') -> 'anydict':
    """ Returns what the view sent to the server, having first made sure the save went through.
    """
    assert response.status_code == HTTPStatus.OK, response.content

    out = request.zato.client.get_request(service)
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_create_carries_the_destination_fields() -> 'None':
    """ A channel created with destinations sends all three fields on to the server.
    """
    destinations = new_destination_list()

    post_data = new_channel_post_data(
        destinations=destinations,
        respond_from='test.rest.billing',
        delivery_mode='in-order',
    )

    request = new_request(post_data)
    request.zato.client.set_response(_create_service, _saved_channel)

    response = Create()(request)
    sent = _get_sent(response, request, _create_service)

    assert sent['destinations'] == destinations
    assert sent['respond_from'] == 'test.rest.billing'
    assert sent['delivery_mode'] == 'in-order'
    assert sent['service'] == 'test.service'

# ################################################################################################################################

def test_edit_carries_the_destination_fields() -> 'None':
    """ The same three fields survive an edit, which posts them under the form's own prefix.
    """
    destinations = new_destination_list('test.hl7.forward', 'hl7-mllp', options={})

    post_data = new_channel_post_data(
        prefix='edit-',
        destinations=destinations,
        respond_from='test.hl7.forward',
        delivery_mode='same-time',
    )
    post_data['id'] = '123'

    request = new_request(post_data)
    request.zato.client.set_response(_edit_service, _saved_channel)

    response = Edit()(request)
    sent = _get_sent(response, request, _edit_service)

    assert sent['id'] == '123'
    assert sent['destinations'] == destinations
    assert sent['respond_from'] == 'test.hl7.forward'
    assert sent['delivery_mode'] == 'same-time'

# ################################################################################################################################

def test_a_channel_with_no_destinations_sends_them_empty() -> 'None':
    """ A channel that declares no destinations sends the three fields at their empty defaults,
    which is what the Dashboard posts for it.
    """
    post_data = new_channel_post_data()

    request = new_request(post_data)
    request.zato.client.set_response(_create_service, _saved_channel)

    response = Create()(request)
    sent = _get_sent(response, request, _create_service)

    assert sent['destinations'] == ''
    assert sent['respond_from'] == 'service'

# ################################################################################################################################
# ################################################################################################################################

def test_a_service_less_channel_is_saved() -> 'None':
    """ A channel that hands its messages to its destinations alone needs no service.
    """
    destinations = new_destination_list()

    post_data = new_channel_post_data(service='', destinations=destinations)

    request = new_request(post_data)
    request.zato.client.set_response(_create_service, _saved_channel)

    response = Create()(request)
    sent = _get_sent(response, request, _create_service)

    assert sent['service'] == ''
    assert sent['destinations'] == destinations

# ################################################################################################################################

def test_a_channel_with_neither_target_is_refused() -> 'None':
    """ A new channel naming neither a service nor a destination has nowhere to deliver, so it
    is not saved at all - the same rule the enmasse importer enforces.
    """
    post_data = new_channel_post_data(service='')

    request = new_request(post_data)
    response = Create()(request)

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert b'needs a service or at least one destination' in response.content

    assert request.zato.client.invocations == []

# ################################################################################################################################

def test_an_edited_channel_may_have_neither_target() -> 'None':
    """ A stored channel that had its service and its destinations taken away is one someone
    meant to leave that way, and each step of an edit is saved on its own, so the question is
    not put to a save made elsewhere.
    """
    post_data = new_channel_post_data(prefix='edit-', service='')
    post_data['id'] = '123'

    request = new_request(post_data)
    request.zato.client.set_response(_edit_service, _saved_channel)

    response = Edit()(request)
    sent = _get_sent(response, request, _edit_service)

    assert sent['service'] == ''
    assert sent['destinations'] == ''

# ################################################################################################################################

def test_a_service_less_channel_may_not_bridge_to_rest() -> 'None':
    """ The backing REST channel hands each request to the MLLP channel's own service, so a
    channel without one has no bridge to build.
    """
    post_data = new_channel_post_data(service='', destinations=new_destination_list(), use_rest='on')

    request = new_request(post_data)
    response = Create()(request)

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert b'needs a service for its REST bridge' in response.content

# ################################################################################################################################

def test_a_destination_list_that_is_not_json_is_refused() -> 'None':
    """ A service-less channel whose destination list cannot be read declares no destinations,
    so it is refused the same way one with an empty list is.
    """
    post_data = new_channel_post_data(service='', destinations='this is not JSON')

    request = new_request(post_data)
    response = Create()(request)

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert b'needs a service or at least one destination' in response.content

# ################################################################################################################################
# ################################################################################################################################

def test_the_list_page_reads_the_destinations_back() -> 'None':
    """ The list page counts each channel's destinations, which is what its column shows.
    """
    row = {
        'id': 123,
        'name': 'test.mllp.channel',
        'is_active': True,
        'is_internal': False,
        'service': 'test.service',
        'security_name': '',
        'destinations': new_destination_list(),
        'respond_from': 'service',
        'delivery_mode': 'same-time',
    }

    index = Index()
    index.items = []
    index.handle_item_list([bunchify(row)], False)

    item = index.items[0]

    assert item.destination_count == 1
    assert item.respond_from == 'service'
    assert item.delivery_mode == 'same-time'

    # What the page reads the rows back from is the stored text itself
    assert loads(item.destinations)[0]['connection'] == 'test.rest.billing'

# ################################################################################################################################

def test_the_list_page_counts_no_destinations_as_none() -> 'None':
    """ A channel that declares no destinations is counted as having none, its column empty.
    """
    row = {
        'id': 124,
        'name': 'test.mllp.plain',
        'is_active': True,
        'is_internal': False,
        'service': 'test.service',
        'security_name': '',
    }

    index = Index()
    index.items = []
    index.handle_item_list([bunchify(row)], False)

    assert index.items[0].destination_count == 0

# ################################################################################################################################
# ################################################################################################################################
