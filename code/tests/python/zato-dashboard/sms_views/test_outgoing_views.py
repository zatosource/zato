# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The create, edit, list and delete views of outgoing SMS connections, called directly against a live server.

# pytest
import pytest

# Zato
from zato.admin.web.views.outgoing import sms as outgoing_views
from zato.common.api import HTTP_SOAP, SMS

# Test support
from _forms import create_outgoing, Credentials, Edit_Prefix, list_items, new_outgoing_post_data, outgoing_name, \
    Outgoing_Type, read_create_edit_response, Senders
from request_stub import new_request

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from _suite import DashboardSuite

# ################################################################################################################################
# ################################################################################################################################

# What the edit view changes the sender and the timeout to
Edited_Sender = '+12025550199'
Edited_Timeout = 7

# What the server answers a signature secret on a provider that does not use one with
Signature_Secret_Error_Text = 'does not use a signature secret'

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('provider', SMS.ProviderList)
def test_the_create_view_creates_a_connection_with_the_providers_fields(dashboard:'DashboardSuite', provider:'str') -> 'None':
    """ The connection the view creates has the provider, host, username, sender and the pool and timeout settings
    the form posted, with the credentials stored and never listed again.
    """
    host = dashboard.simulators.by_provider(provider).url
    username, _ = Credentials[provider]

    created = create_outgoing(dashboard.client, provider, host)

    assert created['name'] == outgoing_name(provider)
    assert created['id']

    item = dashboard.find_connection(Outgoing_Type, outgoing_name(provider))
    assert item is not None

    assert item['id'] == int(created['id'])
    assert item['is_active'] is True
    assert item[SMS.Field_Provider] == provider
    assert item[SMS.Field_Host] == host
    assert item[SMS.Field_Username] == username
    assert item[SMS.Field_Sender] == Senders[provider]
    assert item[SMS.Field_Pool_Size] == SMS.Default_Pool_Size
    assert item[SMS.Field_Timeout] == SMS.Default_Timeout

    # The secrets are stored and never listed
    assert SMS.Field_Secret not in item, item
    assert SMS.Field_Password not in item, item
    assert SMS.Field_Signature_Secret not in item, item

# ################################################################################################################################

def test_the_host_defaults_to_the_providers_public_address(dashboard:'DashboardSuite') -> 'None':
    """ A Twilio connection created with the host left empty is stored with the provider's own address.
    """
    _ = create_outgoing(dashboard.client, SMS.Provider.Twilio, '')

    item = dashboard.find_connection(Outgoing_Type, outgoing_name(SMS.Provider.Twilio))
    assert item is not None

    assert item[SMS.Field_Host] == SMS.Default_Host[SMS.Provider.Twilio]

# ################################################################################################################################

def test_a_signature_secret_on_a_provider_without_one_is_rejected(dashboard:'DashboardSuite') -> 'None':
    """ The view answers with the server's error and nothing is created.
    """
    host = dashboard.simulators.twilio.url
    post_data = new_outgoing_post_data(SMS.Provider.Twilio, host, signature_secret='not-for-twilio')
    request = new_request(dashboard.client, post_data)

    response = outgoing_views.Create()(request)

    assert response.status_code == 500, (response.status_code, response.content)
    assert Signature_Secret_Error_Text in response.content.decode('utf8'), response.content

    assert dashboard.find_connection(Outgoing_Type, outgoing_name(SMS.Provider.Twilio)) is None

# ################################################################################################################################

def test_a_missing_host_on_infobip_is_rejected(dashboard:'DashboardSuite') -> 'None':
    """ Infobip accounts each have their own base URL, so a connection without one is refused.
    """
    post_data = new_outgoing_post_data(SMS.Provider.Infobip, '')
    request = new_request(dashboard.client, post_data)

    response = outgoing_views.Create()(request)

    assert response.status_code == 500, (response.status_code, response.content)
    assert 'requires a host' in response.content.decode('utf8'), response.content

    assert dashboard.find_connection(Outgoing_Type, outgoing_name(SMS.Provider.Infobip)) is None

# ################################################################################################################################

def test_the_list_view_shows_every_connection_with_its_provider(dashboard:'DashboardSuite') -> 'None':
    """ The list page's rows have the human-readable provider name and the Delivery tab's defaults filled in.
    """
    for provider in SMS.ProviderList:
        host = dashboard.simulators.by_provider(provider).url
        _ = create_outgoing(dashboard.client, provider, host)

    items = list_items(dashboard.client, outgoing_views.Index(), Outgoing_Type)

    for provider in SMS.ProviderList:
        item = items[outgoing_name(provider)]

        assert item.provider == provider
        assert item.provider_human == SMS.ProviderHuman[provider]
        assert item.sender == Senders[provider]
        assert item.max_retries == HTTP_SOAP.Retry.Default_Max_Retries
        assert item.use_queue is HTTP_SOAP.Queue.Default_Use_Queue
        assert item.use_dlq is HTTP_SOAP.DLQ.Default_Use_DLQ

# ################################################################################################################################

def test_the_edit_view_changes_the_fields_and_keeps_the_secret(dashboard:'DashboardSuite') -> 'None':
    """ An edit with the secret fields left empty keeps the stored credentials, which the simulator still accepts.
    """
    host = dashboard.simulators.twilio.url
    created = create_outgoing(dashboard.client, SMS.Provider.Twilio, host)

    post_data = new_outgoing_post_data(
        SMS.Provider.Twilio,
        host,
        prefix=Edit_Prefix,
        secret='',
        sender=Edited_Sender,
        timeout=str(Edited_Timeout),
    )
    post_data['id'] = created['id']

    request = new_request(dashboard.client, post_data)
    response = outgoing_views.Edit()(request)

    edited = read_create_edit_response(response)
    assert edited['id'] == created['id']

    item = dashboard.find_connection(Outgoing_Type, outgoing_name(SMS.Provider.Twilio))
    assert item is not None

    assert item[SMS.Field_Sender] == Edited_Sender
    assert item[SMS.Field_Timeout] == Edited_Timeout

    # The stored secret still authenticates against the simulator
    ping = dashboard.admin.invoke('zato.generic.connection.ping', {'id': item['id']})
    assert ping['is_success'] is True, ping

# ################################################################################################################################

def test_the_delete_view_removes_the_connection(dashboard:'DashboardSuite') -> 'None':
    """ After the delete view, the connection is no longer listed.
    """
    host = dashboard.simulators.twilio.url
    created = create_outgoing(dashboard.client, SMS.Provider.Twilio, host)

    request = new_request(dashboard.client, id=created['id'])
    response = outgoing_views.Delete()(request)

    assert response.status_code == 200, (response.status_code, response.content)
    assert dashboard.find_connection(Outgoing_Type, outgoing_name(SMS.Provider.Twilio)) is None

# ################################################################################################################################
# ################################################################################################################################
