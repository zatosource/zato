# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class MicrosoftCloudTestSendEmail(Service):
    """ Sends an email through a named Microsoft 365 connection.
    """
    name = 'test.microsoft.cloud.send-email'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        email_from = self.request.raw_request['email_from']
        email_to = self.request.raw_request['email_to']
        subject = self.request.raw_request['subject']
        body = self.request.raw_request['body']

        # Get the connection ..
        conn = self.microsoft.cloud[conn_name]

        # .. access the sender's mailbox ..
        mailbox = conn.mailbox(resource=email_from)

        # .. build our message ..
        message = mailbox.new_message()
        message.to.add(email_to)
        message.subject = subject
        message.body = body

        # .. and send it out.
        is_sent = message.send()

        self.response.payload = json.dumps({'is_sent': is_sent})

# ################################################################################################################################
# ################################################################################################################################

class MicrosoftCloudTestListCalendarEvents(Service):
    """ Lists calendar events through a named Microsoft 365 connection.
    """
    name = 'test.microsoft.cloud.list-calendar-events'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        email = self.request.raw_request['email']

        # Get the connection ..
        conn = self.microsoft.cloud[conn_name]

        # .. access the user's calendar ..
        schedule = conn.schedule(resource=email)
        calendar = schedule.get_default_calendar()

        # .. read its events ..
        events = calendar.get_events(limit=100, include_recurring=False)

        # .. and return their subjects.
        subjects = []
        for event in events:
            subjects.append(event.subject)

        self.response.payload = json.dumps({'subjects': subjects})

# ################################################################################################################################
# ################################################################################################################################

class MicrosoftCloudTestListUsers(Service):
    """ Lists directory users through a named Microsoft 365 connection.
    """
    name = 'test.microsoft.cloud.list-users'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        # Get the connection ..
        conn = self.microsoft.cloud[conn_name]

        # .. access the tenant's directory ..
        directory = conn.directory()

        # .. and return the basic details of each user found.
        users = []
        for user in directory.get_users():
            users.append({
                'mail': user.mail,
                'display_name': user.display_name,
            })

        self.response.payload = json.dumps({'users': users})

# ################################################################################################################################
# ################################################################################################################################

class MicrosoftCloudTestGetOrganization(Service):
    """ Invokes a Graph REST endpoint directly through a named Microsoft 365 connection.
    """
    name = 'test.microsoft.cloud.get-organization'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        # Get the connection ..
        conn = self.microsoft.cloud[conn_name]

        # .. build the endpoint's full address ..
        url = f'{conn.protocol.service_url}organization'

        # .. invoke it directly ..
        response = conn.connection.get(url)

        # .. and return the response as is.
        self.response.payload = json.dumps(response.json())

# ################################################################################################################################
# ################################################################################################################################

class MicrosoftCloudTestPing(Service):
    """ Pings a named Microsoft 365 connection.
    """
    name = 'test.microsoft.cloud.ping'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        conn = self.microsoft.cloud[conn_name]
        conn.ping()

        self.response.payload = json.dumps({'ok': True})

# ################################################################################################################################
# ################################################################################################################################
