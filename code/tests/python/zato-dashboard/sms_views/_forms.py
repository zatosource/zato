# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The form data the SMS pages post - every field the create and edit views read, with the values one test overrides.

# stdlib
from json import loads

# Zato
from zato.admin.web import alerts_tab, delivery_tab, sms_tab
from zato.admin.web.alerts_tab_lines import Checkbox_On_Value
from zato.admin.web.views.channel import sms as channel_views
from zato.admin.web.views.outgoing import sms as outgoing_views
from zato.common.alerting.object_config import alert_type_sms_outgoing, storage_name
from zato.common.api import GENERIC, SMS

# Test support
from live_sms.suite import Africas_Talking_API_Key, Africas_Talking_Username, Infobip_API_Key, Infobip_Username, \
    Twilio_Account_SID, Twilio_Auth_Token, Vonage_API_Key, Vonage_API_Secret, Vonage_Signature_Secret
from request_stub import new_request

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.client import ZatoClient
    from zato.common.typing_ import any_, anydict, stranydict

# ################################################################################################################################
# ################################################################################################################################

# The name prefix of the connections the tests create, removed after each test
Name_Prefix = 'test.views.'

Outgoing_Type = GENERIC.CONNECTION.TYPE.OUTCONN_SMS
Channel_Type = GENERIC.CONNECTION.TYPE.CHANNEL_SMS

# The sender of each provider's connection, in the form the provider expects
Senders = {
    SMS.Provider.Twilio: '+15005550006',
    SMS.Provider.Vonage: '12025550100',
    SMS.Provider.Infobip: 'ZatoSMS',
    SMS.Provider.Africas_Talking: '+12025550100',
}

# The credentials of each provider's connection, matching the simulators
Credentials = {
    SMS.Provider.Twilio: (Twilio_Account_SID, Twilio_Auth_Token),
    SMS.Provider.Vonage: (Vonage_API_Key, Vonage_API_Secret),
    SMS.Provider.Infobip: (Infobip_Username, Infobip_API_Key),
    SMS.Provider.Africas_Talking: (Africas_Talking_Username, Africas_Talking_API_Key),
}

# The service a channel points to
Channel_Service = 'zato.ping'

# The form prefix of an edit view
Edit_Prefix = 'edit-'

# ################################################################################################################################
# ################################################################################################################################

def outgoing_name(provider:'str') -> 'str':
    out = Name_Prefix + 'out.' + provider
    return out

# ################################################################################################################################

def channel_name(suffix:'str') -> 'str':
    out = Name_Prefix + 'in.' + suffix
    return out

# ################################################################################################################################

def new_alert_post_data() -> 'stranydict':
    """ The Alerts tab's fields as the page posts them - each default as text, an enabled checkbox as the browser's value
    and a disabled checkbox omitted.
    """
    out = {}

    checkbox_names = alerts_tab.get_checkbox_field_names(alert_type_sms_outgoing)

    for name, value in alerts_tab.get_form_defaults(alert_type_sms_outgoing).items():
        field_name = storage_name(name)

        if field_name in checkbox_names:
            if value:
                out[field_name] = Checkbox_On_Value
        else:
            out[field_name] = str(value)

    return out

# ################################################################################################################################

def new_provider_post_data(provider:'str', host:'str') -> 'stranydict':
    """ The Provider section's fields, shared by the outgoing connection's and the channel's forms.
    """
    username, password = Credentials[provider]

    out = {
        SMS.Field_Provider: provider,
        SMS.Field_Host: host,
        SMS.Field_Username: username,
        SMS.Field_Secret: password,
        SMS.Field_Sender: Senders[provider],
        SMS.Field_Signature_Secret: '',
    }

    if provider == SMS.Provider.Vonage:
        out[SMS.Field_Signature_Secret] = Vonage_Signature_Secret

    return out

# ################################################################################################################################

def new_outgoing_post_data(provider:'str', host:'str', prefix:'str'='', **overrides:'any_') -> 'stranydict':
    """ The form data of one outgoing SMS connection.
    """
    values:'stranydict' = new_alert_post_data()

    values.update(new_provider_post_data(provider, host))

    values.update({
        'name': outgoing_name(provider),
        'is_active': 'on',
        SMS.Field_Channel_Name: '',
        SMS.Field_Pool_Size: str(SMS.Default_Pool_Size),
        SMS.Field_Timeout: str(SMS.Default_Timeout),
        sms_tab.Timeout_Unit_Field_Name: delivery_tab.Duration_Unit_Smallest,
    })

    values.update(overrides)

    out = {}

    for key, value in values.items():
        out[prefix + key] = value

    return out

# ################################################################################################################################

def new_channel_post_data(name:'str', provider:'str', host:'str', prefix:'str'='', **overrides:'any_') -> 'stranydict':
    """ The form data of one SMS channel, a webhook channel by default. The Provider section's fields describe
    the outgoing connection the view creates along with the channel, an edit names the stored one through
    outconn_name and outconn_id.
    """
    values:'stranydict' = new_provider_post_data(provider, host)

    values.update({
        'name': name,
        'is_active': 'on',
        SMS.Field_Outconn_Name: '',
        sms_tab.Outconn_ID_Field_Name: '',
        SMS.Field_Service: Channel_Service,
        SMS.Field_Receive_Mode: SMS.Receive_Mode.Webhook,
        SMS.Scheduler.Field_Run_Every: str(SMS.Scheduler.Default_Run_Every),
        SMS.Scheduler.Field_Run_Unit: sms_tab.poll_unit_for_form(SMS.Scheduler.Default_Run_Unit),
    })

    values.update(overrides)

    out = {}

    for key, value in values.items():
        out[prefix + key] = value

    return out

# ################################################################################################################################
# ################################################################################################################################

def read_create_edit_response(response:'any_') -> 'anydict':
    """ Reads the JSON response of a create or edit view - the object's id and name, and for a channel,
    the id and the name of its outgoing connection.
    """
    assert response.status_code == 200, (response.status_code, response.content)

    out = loads(response.content)
    return out

# ################################################################################################################################

def create_outgoing(client:'ZatoClient', provider:'str', host:'str', **overrides:'any_') -> 'anydict':
    """ Creates one outgoing connection through the create view and returns the view's response.
    """
    post_data = new_outgoing_post_data(provider, host, **overrides)
    request = new_request(client, post_data)

    response = outgoing_views.Create()(request)

    out = read_create_edit_response(response)
    return out

# ################################################################################################################################

def create_channel(client:'ZatoClient', name:'str', provider:'str', host:'str', **overrides:'any_') -> 'anydict':
    """ Creates one channel, and the outgoing connection of its Provider section, through the create view
    and returns the view's response.
    """
    post_data = new_channel_post_data(name, provider, host, **overrides)
    request = new_request(client, post_data)

    response = channel_views.Create()(request)

    out = read_create_edit_response(response)
    return out

# ################################################################################################################################

def list_items(client:'ZatoClient', view:'any_', type_:'str') -> 'anydict':
    """ The rows of a list page, by name. The view reads them from the server and builds each row without the page's
    forms, whose URL reversal needs the Dashboard's URL configuration.
    """
    request = new_request(client, get_data={'cluster': '1', 'type_': type_}, method='GET')

    view.req = request
    view.fetch_cluster_id()
    view.set_input()

    assert view.can_invoke_admin_service() is True

    view.before_invoke_admin_service()
    response = view.invoke_admin_service()
    assert response.ok is True, response.details

    view.handle_item_list(response.data, True)

    out = {}

    for item in view.items:
        out[item.name] = item

    return out

# ################################################################################################################################
# ################################################################################################################################
