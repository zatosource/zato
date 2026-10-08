# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The create, edit, list and delete views of SMS channels, called directly against a live server.

# stdlib
import os

# Zato
import zato.admin
from zato.admin.web.views.channel import sms as channel_views
from zato.common.api import SMS
from zato.common.sms.config import get_webhook_path

# Test support
from _forms import channel_name, Channel_Service, Channel_Type, create_channel, create_outgoing, Edit_Prefix, list_items, \
    new_channel_post_data, outgoing_name, Outgoing_Type, read_create_edit_response
from request_stub import new_request

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from _suite import DashboardSuite

# ################################################################################################################################
# ################################################################################################################################

# The list page's template and the include that puts the DLQ link into each row, with the queue type the link opens
Templates_Directory = os.path.join(os.path.dirname(zato.admin.__file__), 'templates')
Template_Path = os.path.join(Templates_Directory, 'zato', 'channel', 'sms.html')
DLQ_Link_Include = 'zato/include/channel-dlq-link.html'
DLQ_Link_Conn_Type = 'sms-channel'

# The URL the include builds the DLQ link of a row from, as the include's source has it
DLQ_Link_Source = '/zato/channel/delivery/{{ conn_type }}/{{ item.id }}/?cluster={{ cluster_id }}&amp;tab=dlq'

# What the edit view changes the polling schedule to
Edited_Run_Every = 5

# What the server answers a receive mode outside the two with
Receive_Mode_Error_Text = 'is not one of'

# ################################################################################################################################
# ################################################################################################################################

def _create_twilio_outgoing(dashboard:'DashboardSuite') -> 'str':
    """ The outgoing connection the channels of a test name.
    """
    _ = create_outgoing(dashboard.client, SMS.Provider.Twilio, dashboard.simulators.twilio.url)

    out = outgoing_name(SMS.Provider.Twilio)
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_the_create_view_creates_a_webhook_channel(dashboard:'DashboardSuite') -> 'None':
    """ The channel the view creates names its outgoing connection and its service and receives by webhook.
    """
    outconn_name = _create_twilio_outgoing(dashboard)
    name = channel_name('webhook')

    created = create_channel(dashboard.client, name, outconn_name)

    assert created['name'] == name
    assert created['id']

    item = dashboard.find_connection(Channel_Type, name)
    assert item is not None

    assert item['id'] == int(created['id'])
    assert item['is_active'] is True
    assert item[SMS.Field_Outconn_Name] == outconn_name
    assert item[SMS.Field_Service] == Channel_Service
    assert item[SMS.Field_Receive_Mode] == SMS.Receive_Mode.Webhook

# ################################################################################################################################

def test_a_channel_naming_no_outgoing_connection_is_rejected(dashboard:'DashboardSuite') -> 'None':
    """ The view answers with the server's error and nothing is created.
    """
    name = channel_name('orphan')
    post_data = new_channel_post_data(name, 'test.views.out.missing')
    request = new_request(dashboard.client, post_data)

    response = channel_views.Create()(request)

    assert response.status_code == 500, (response.status_code, response.content)
    assert 'does not exist' in response.content.decode('utf8'), response.content

    assert dashboard.find_connection(Channel_Type, name) is None

# ################################################################################################################################

def test_a_receive_mode_outside_the_two_is_rejected(dashboard:'DashboardSuite') -> 'None':
    """ A receive mode that is neither webhook nor polling is refused by the server, which the view reports.
    """
    outconn_name = _create_twilio_outgoing(dashboard)
    name = channel_name('bad-mode')

    post_data = new_channel_post_data(name, outconn_name, receive_mode='carrier-pigeon')
    request = new_request(dashboard.client, post_data)

    response = channel_views.Create()(request)

    assert response.status_code == 500, (response.status_code, response.content)
    assert Receive_Mode_Error_Text in response.content.decode('utf8'), response.content

    assert dashboard.find_connection(Channel_Type, name) is None

# ################################################################################################################################

def test_the_list_view_shows_the_webhook_url_and_the_dlq_link(dashboard:'DashboardSuite') -> 'None':
    """ Each row has the channel's webhook URL and the id the DLQ link is built from, and the page's template
    puts the DLQ link of the SMS queue type into every row.
    """
    outconn_name = _create_twilio_outgoing(dashboard)
    name = channel_name('listed')

    created = create_channel(dashboard.client, name, outconn_name)

    items = list_items(dashboard.client, channel_views.Index(), Channel_Type)
    item = items[name]

    assert item.id == int(created['id'])
    assert item.outconn_name == outconn_name
    assert item.receive_mode_human == SMS.Receive_Mode_Human[SMS.Receive_Mode.Webhook]
    assert item.webhook_url == dashboard.server_address + get_webhook_path(name)

    # The page puts the DLQ link into every row under the SMS queue type, and the include builds it from the row's id
    with open(Template_Path) as f:
        template = f.read()

    include_tag = f'{{% include "{DLQ_Link_Include}" with conn_type="{DLQ_Link_Conn_Type}" %}}'
    assert include_tag in template, template

    with open(os.path.join(Templates_Directory, DLQ_Link_Include)) as f:
        include = f.read()

    assert DLQ_Link_Source in include, include

# ################################################################################################################################

def test_the_edit_view_switches_a_channel_to_polling(dashboard:'DashboardSuite') -> 'None':
    """ An edit that switches the receive mode to polling stores the mode and the schedule.
    """
    outconn_name = _create_twilio_outgoing(dashboard)
    name = channel_name('edited')

    created = create_channel(dashboard.client, name, outconn_name)

    post_data = new_channel_post_data(
        name,
        outconn_name,
        prefix=Edit_Prefix,
        receive_mode=SMS.Receive_Mode.Polling,
        scheduler_run_every=str(Edited_Run_Every),
    )
    post_data['id'] = created['id']

    request = new_request(dashboard.client, post_data)
    response = channel_views.Edit()(request)

    edited = read_create_edit_response(response)
    assert edited['id'] == created['id']

    item = dashboard.find_connection(Channel_Type, name)
    assert item is not None

    assert item[SMS.Field_Receive_Mode] == SMS.Receive_Mode.Polling
    assert item[SMS.Scheduler.Field_Run_Every] == Edited_Run_Every
    assert item[SMS.Scheduler.Field_Run_Unit] == SMS.Scheduler.Default_Run_Unit

    items = list_items(dashboard.client, channel_views.Index(), Channel_Type)
    assert items[name].receive_mode_human == SMS.Receive_Mode_Human[SMS.Receive_Mode.Polling]

# ################################################################################################################################

def test_the_delete_view_removes_the_channel(dashboard:'DashboardSuite') -> 'None':
    """ After the delete view, the channel is no longer listed and its outgoing connection remains.
    """
    outconn_name = _create_twilio_outgoing(dashboard)
    name = channel_name('deleted')

    created = create_channel(dashboard.client, name, outconn_name)

    request = new_request(dashboard.client, id=created['id'])
    response = channel_views.Delete()(request)

    assert response.status_code == 200, (response.status_code, response.content)
    assert dashboard.find_connection(Channel_Type, name) is None

    outconn = dashboard.find_connection(Outgoing_Type, outconn_name)
    assert outconn is not None

# ################################################################################################################################
# ################################################################################################################################
