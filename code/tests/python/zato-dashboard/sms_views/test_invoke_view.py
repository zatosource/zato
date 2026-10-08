# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Invoke dialog's view of an outgoing SMS connection, sending through a live server to the Twilio simulator.

# stdlib
from json import loads

# Zato
from zato.admin.web.views.outgoing.sms import invoke_outconn
from zato.common.api import SMS

# Test support
from _forms import create_outgoing, Senders
from live_sms.twilio import Error_To_Invalid, Magic_To_Invalid
from request_stub import new_request

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from _suite import DashboardSuite
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# What the dialog posts
Post_Body = 'data-request'
Post_From = 'from_'
Post_To = 'to'

# The recipient and the text of the message
To_Number = '+12025550123'
Message_Text = 'Your order 1234 has shipped'

# A sender given in the dialog for one message
Other_Sender = '+12025550198'

# The prefix of a Twilio message SID
Message_SID_Prefix = 'SM'

# ################################################################################################################################
# ################################################################################################################################

def _invoke(dashboard:'DashboardSuite', conn_id:'str', from_:'str', to:'str', body:'str') -> 'any_':
    """ Calls the invoke view the way the dialog does.
    """
    post_data = {
        Post_From: from_,
        Post_To: to,
        Post_Body: body,
    }

    request = new_request(dashboard.client, post_data)

    # The URL configuration passes the connection's id by keyword
    out = invoke_outconn(request, id=conn_id)
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_the_invoke_view_sends_a_message_and_returns_its_id(dashboard:'DashboardSuite') -> 'None':
    """ The view answers with the message ID the provider assigned and the simulator has the message.
    """
    twilio = dashboard.simulators.twilio
    sender = Senders[SMS.Provider.Twilio]

    created = create_outgoing(dashboard.client, SMS.Provider.Twilio, twilio.url)

    response = _invoke(dashboard, created['id'], sender, To_Number, Message_Text)
    assert response.status_code == 200, (response.status_code, response.content)

    data = loads(response.content)
    assert data['content_type'] == 'application/json'
    assert data['response_time_human'].endswith('s'), data

    result = loads(data['data'])
    assert result['id'].startswith(Message_SID_Prefix), result
    assert result['status'], result
    assert result['raw'], result

    assert len(twilio.sends) == 1, twilio.sends
    send = twilio.sends[0]

    assert send.message_id == result['id']
    assert send.to == To_Number
    assert send.from_ == sender
    assert send.body == Message_Text

# ################################################################################################################################

def test_the_sender_given_in_the_dialog_is_used_for_that_message(dashboard:'DashboardSuite') -> 'None':
    """ A From value other than the connection's sender reaches the provider as that message's sender.
    """
    twilio = dashboard.simulators.twilio

    created = create_outgoing(dashboard.client, SMS.Provider.Twilio, twilio.url)

    response = _invoke(dashboard, created['id'], Other_Sender, To_Number, Message_Text)
    assert response.status_code == 200, (response.status_code, response.content)

    assert len(twilio.sends) == 1, twilio.sends
    assert twilio.sends[0].from_ == Other_Sender

# ################################################################################################################################

def test_a_rejected_message_is_reported_as_an_error(dashboard:'DashboardSuite') -> 'None':
    """ A number the provider rejects answers with a 500 that quotes the provider's error, and nothing was sent.
    """
    twilio = dashboard.simulators.twilio
    sender = Senders[SMS.Provider.Twilio]

    created = create_outgoing(dashboard.client, SMS.Provider.Twilio, twilio.url)

    response = _invoke(dashboard, created['id'], sender, Magic_To_Invalid, Message_Text)
    assert response.status_code == 500, (response.status_code, response.content)

    data = loads(response.content)
    assert data['content_type'] == 'text/plain'
    assert str(Error_To_Invalid) in data['data'], data

    assert twilio.sends == []
    assert len(twilio.rejections) == 1, twilio.rejections

# ################################################################################################################################
# ################################################################################################################################
