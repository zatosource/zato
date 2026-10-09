# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The create, edit, list and delete views of SMS channels, called directly against a live server. A channel's form
# carries the Provider section of an outgoing connection, which the views create and edit along with the channel.

# stdlib
import os

# Zato
import zato.admin
from zato.admin.web import sms_tab
from zato.admin.web.views.channel import sms as channel_views
from zato.common.api import SMS
from zato.common.sms.config import get_webhook_path

# Test support
from _forms import channel_name, Channel_Service, Channel_Type, create_channel, Credentials, Edit_Prefix, list_items, \
    new_channel_post_data, Outgoing_Type, read_create_edit_response, Senders
from request_stub import new_request

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from _suite import DashboardSuite
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

# The list page's template and the include that builds each row's DLQ link, with the queue type of the link
Templates_Directory = os.path.join(os.path.dirname(zato.admin.__file__), 'templates')
Template_Path = os.path.join(Templates_Directory, 'zato', 'channel', 'sms.html')
DLQ_Link_Include = 'zato/include/channel-dlq-link.html'
DLQ_Link_Conn_Type = 'sms-channel'

# The URL pattern of a row's DLQ link, as in the include's source
DLQ_Link_Source = '/zato/channel/delivery/{{ conn_type }}/{{ item.id }}/?cluster={{ cluster_id }}&amp;tab=dlq'

# The polling schedule set by the edit view
Edited_Run_Every = 5

# The sender set by the edit view
Edited_Sender = '+12025550177'

# The server's error for an unknown receive mode
Receive_Mode_Error_Text = 'is not one of'

# ################################################################################################################################
# ################################################################################################################################

def _create_twilio_channel(dashboard:'DashboardSuite', name:'str', **overrides:'any_') -> 'anydict':
    """ Creates a channel whose outgoing connection sends through the Twilio simulator.
    """
    out = create_channel(dashboard.client, name, SMS.Provider.Twilio, dashboard.simulators.twilio.url, **overrides)
    return out

# ################################################################################################################################

def _edit_post_data(dashboard:'DashboardSuite', created:'anydict', name:'str', **overrides:'any_') -> 'anydict':
    """ The form data of an edit of a channel the create view answered with, the secrets left empty.
    """
    out = new_channel_post_data(
        name,
        SMS.Provider.Twilio,
        dashboard.simulators.twilio.url,
        prefix=Edit_Prefix,
        secret='',
        outconn_name=created[SMS.Field_Outconn_Name],
        outconn_id=str(created[sms_tab.Outconn_ID_Field_Name]),
        **overrides,
    )
    out['id'] = created['id']

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_the_create_view_creates_a_webhook_channel_and_its_outgoing_connection(dashboard:'DashboardSuite') -> 'None':
    """ The channel the view creates names its service, receives by webhook and has an outgoing connection
    of its own name with the Provider section's fields, which in turn reports to the channel.
    """
    name = channel_name('webhook')
    username, _ = Credentials[SMS.Provider.Twilio]

    created = _create_twilio_channel(dashboard, name)

    assert created['name'] == name
    assert created['id']
    assert created[SMS.Field_Outconn_Name] == name
    assert created[sms_tab.Outconn_ID_Field_Name]

    item = dashboard.find_connection(Channel_Type, name)
    assert item is not None

    assert item['id'] == int(created['id'])
    assert item['is_active'] is True
    assert item[SMS.Field_Outconn_Name] == name
    assert item[SMS.Field_Service] == Channel_Service
    assert item[SMS.Field_Receive_Mode] == SMS.Receive_Mode.Webhook

    outconn = dashboard.find_connection(Outgoing_Type, name)
    assert outconn is not None

    assert outconn['id'] == created[sms_tab.Outconn_ID_Field_Name]
    assert outconn[SMS.Field_Provider] == SMS.Provider.Twilio
    assert outconn[SMS.Field_Host] == dashboard.simulators.twilio.url
    assert outconn[SMS.Field_Username] == username
    assert outconn[SMS.Field_Sender] == Senders[SMS.Provider.Twilio]
    assert outconn[SMS.Field_Channel_Name] == name

# ################################################################################################################################

def test_a_receive_mode_outside_the_two_is_rejected_and_the_outgoing_connection_is_removed(dashboard:'DashboardSuite') -> 'None':
    """ A receive mode other than webhook or polling is rejected by the server, the view returns the error
    and the outgoing connection created for the channel is removed again.
    """
    name = channel_name('invalid-mode')

    post_data = new_channel_post_data(
        name, SMS.Provider.Twilio, dashboard.simulators.twilio.url, receive_mode='carrier-pigeon')
    request = new_request(dashboard.client, post_data)

    response = channel_views.Create()(request)

    assert response.status_code == 500, (response.status_code, response.content)
    assert Receive_Mode_Error_Text in response.content.decode('utf8'), response.content

    assert dashboard.find_connection(Channel_Type, name) is None
    assert dashboard.find_connection(Outgoing_Type, name) is None

# ################################################################################################################################

def test_a_missing_host_on_infobip_is_rejected_before_the_channel_is_created(dashboard:'DashboardSuite') -> 'None':
    """ The outgoing connection is validated first, so a rejected Provider section creates nothing.
    """
    name = channel_name('no-host')

    post_data = new_channel_post_data(name, SMS.Provider.Infobip, '')
    request = new_request(dashboard.client, post_data)

    response = channel_views.Create()(request)

    assert response.status_code == 500, (response.status_code, response.content)
    assert 'requires a host' in response.content.decode('utf8'), response.content

    assert dashboard.find_connection(Channel_Type, name) is None
    assert dashboard.find_connection(Outgoing_Type, name) is None

# ################################################################################################################################

def test_the_list_view_shows_the_provider_the_webhook_path_and_the_dlq_link(dashboard:'DashboardSuite') -> 'None':
    """ Each row has the provider fields of the channel's outgoing connection, the channel's webhook path
    and the id of the DLQ link, and the template renders the DLQ link of the SMS queue type in every row.
    """
    name = channel_name('listed')
    username, _ = Credentials[SMS.Provider.Twilio]

    created = _create_twilio_channel(dashboard, name)

    items = list_items(dashboard.client, channel_views.Index(), Channel_Type)
    item = items[name]

    assert item.id == int(created['id'])
    assert item.outconn_name == name
    assert item.outconn_id == created[sms_tab.Outconn_ID_Field_Name]
    assert item.provider == SMS.Provider.Twilio
    assert item.provider_human == SMS.ProviderHuman[SMS.Provider.Twilio]
    assert item.host == dashboard.simulators.twilio.url
    assert item.username == username
    assert item.sender == Senders[SMS.Provider.Twilio]
    assert item.receive_mode_human == SMS.Receive_Mode_Human[SMS.Receive_Mode.Webhook]
    assert item.webhook_path == get_webhook_path(name)
    assert item.scheduler_run_unit == sms_tab.poll_unit_for_form(SMS.Scheduler.Default_Run_Unit)

    # The page renders the DLQ link of every row under the SMS queue type, built from the row's id
    with open(Template_Path) as f:
        template = f.read()

    include_tag = f'{{% include "{DLQ_Link_Include}" with conn_type="{DLQ_Link_Conn_Type}" %}}'
    assert include_tag in template, template

    with open(os.path.join(Templates_Directory, DLQ_Link_Include)) as f:
        include = f.read()

    assert DLQ_Link_Source in include, include

# ################################################################################################################################

def test_the_edit_view_switches_a_channel_to_polling_and_edits_the_outgoing_connection(dashboard:'DashboardSuite') -> 'None':
    """ An edit that switches the receive mode to polling stores the mode and the schedule, in the scheduler's units,
    and the Provider section's sender reaches the outgoing connection while its empty secret keeps the stored one.
    """
    name = channel_name('edited')

    created = _create_twilio_channel(dashboard, name)

    post_data = _edit_post_data(
        dashboard,
        created,
        name,
        receive_mode=SMS.Receive_Mode.Polling,
        scheduler_run_every=str(Edited_Run_Every),
        sender=Edited_Sender,
    )

    request = new_request(dashboard.client, post_data)
    response = channel_views.Edit()(request)

    edited = read_create_edit_response(response)
    assert edited['id'] == created['id']
    assert edited[SMS.Field_Outconn_Name] == name

    item = dashboard.find_connection(Channel_Type, name)
    assert item is not None

    assert item[SMS.Field_Receive_Mode] == SMS.Receive_Mode.Polling
    assert item[SMS.Scheduler.Field_Run_Every] == Edited_Run_Every
    assert item[SMS.Scheduler.Field_Run_Unit] == SMS.Scheduler.Default_Run_Unit

    outconn = dashboard.find_connection(Outgoing_Type, name)
    assert outconn is not None

    assert outconn['id'] == created[sms_tab.Outconn_ID_Field_Name]
    assert outconn[SMS.Field_Sender] == Edited_Sender

    # The stored secret authenticates against the simulator
    ping = dashboard.admin.invoke('zato.generic.connection.ping', {'id': outconn['id']})
    assert ping['is_success'] is True, ping

    items = list_items(dashboard.client, channel_views.Index(), Channel_Type)
    assert items[name].receive_mode_human == SMS.Receive_Mode_Human[SMS.Receive_Mode.Polling]

# ################################################################################################################################

def test_the_edit_view_renames_the_channel_and_its_outgoing_connection(dashboard:'DashboardSuite') -> 'None':
    """ A channel renamed through the edit view keeps one outgoing connection, renamed with it and reporting to it.
    """
    name = channel_name('renamed-from')
    new_name = channel_name('renamed-to')

    created = _create_twilio_channel(dashboard, name)

    post_data = _edit_post_data(dashboard, created, new_name)

    request = new_request(dashboard.client, post_data)
    response = channel_views.Edit()(request)

    edited = read_create_edit_response(response)
    assert edited[SMS.Field_Outconn_Name] == new_name

    assert dashboard.find_connection(Channel_Type, name) is None
    assert dashboard.find_connection(Outgoing_Type, name) is None

    item = dashboard.find_connection(Channel_Type, new_name)
    assert item is not None
    assert item[SMS.Field_Outconn_Name] == new_name

    outconn = dashboard.find_connection(Outgoing_Type, new_name)
    assert outconn is not None
    assert outconn['id'] == created[sms_tab.Outconn_ID_Field_Name]
    assert outconn[SMS.Field_Channel_Name] == new_name

# ################################################################################################################################

def test_the_delete_view_removes_the_channel(dashboard:'DashboardSuite') -> 'None':
    """ After the delete view, the channel is no longer listed and its outgoing connection remains.
    """
    name = channel_name('deleted')

    created = _create_twilio_channel(dashboard, name)

    request = new_request(dashboard.client, id=created['id'])
    response = channel_views.Delete()(request)

    assert response.status_code == 200, (response.status_code, response.content)
    assert dashboard.find_connection(Channel_Type, name) is None

    outconn = dashboard.find_connection(Outgoing_Type, name)
    assert outconn is not None

# ################################################################################################################################
# ################################################################################################################################
