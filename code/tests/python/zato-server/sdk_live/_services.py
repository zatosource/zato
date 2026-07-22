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

class GetCustomer(Service):
    """ Returns one customer from the CRM gateway.
    """
    name = 'demo.crm.get-customer'

    input = 'customer_id'

    def handle(self) -> 'None':
        conn = self.out.crm['My CRM']
        response = conn.get_customer(self.request.input.customer_id)
        self.response.payload = json.dumps({'response': response})

# ################################################################################################################################
# ################################################################################################################################

class SendMainframeCommand(Service):
    """ Sends one command to the mainframe gateway over a pooled connection.
    """
    name = 'demo.mainframe.send-command'

    input = 'command'

    def handle(self) -> 'None':
        conn = self.out.mainframe['My Mainframe']
        response = conn.send_command(self.request.input.command)
        self.response.payload = json.dumps({'response': response})

# ################################################################################################################################
# ################################################################################################################################

class GetCustomerWithTimeout(Service):
    """ Returns one customer with a short per-call watchdog timeout - for the stall scenario.
    """
    name = 'demo.crm.get-customer-timeout'

    input = 'customer_id'

    def handle(self) -> 'None':
        conn = self.out.crm['My Failure CRM']
        response = conn.get_customer(self.request.input.customer_id, timeout=2)
        self.response.payload = json.dumps({'response': response})

# ################################################################################################################################
# ################################################################################################################################

class GetCustomerFailure(Service):
    """ Returns one customer through the failure-scenario definition.
    """
    name = 'demo.crm.get-customer-failure'

    input = 'customer_id'

    def handle(self) -> 'None':
        conn = self.out.crm['My Failure CRM']
        response = conn.get_customer(self.request.input.customer_id)
        self.response.payload = json.dumps({'response': response})

# ################################################################################################################################
# ################################################################################################################################

class GetCustomerTenant(Service):
    """ Returns one customer using a per-tenant API key resolved at runtime.
    """
    name = 'demo.crm.get-customer-tenant'

    input = 'customer_id', 'api_key'

    def handle(self) -> 'None':
        conn = self.out.crm['My Tenant CRM'].with_config(api_key=self.request.input.api_key)
        response = conn.get_customer(self.request.input.customer_id)
        self.response.payload = json.dumps({'response': response})

# ################################################################################################################################
# ################################################################################################################################

class AuthorizePayment(Service):
    """ Authorizes one payment over the multiplexed connection to the payment switch.
    """
    name = 'demo.payments.authorize'

    input = 'payload'

    def handle(self) -> 'None':
        conn = self.out.payments['My Payments']
        response = conn.authorize(self.request.input.payload)
        self.response.payload = json.dumps({'response': response})

# ################################################################################################################################
# ################################################################################################################################

# Everything the feed connector delivered, shared by the recorder services below -
# module-level state works because all of them live in this one deployed module.
_feed_invoked_messages = []
_feed_topic_messages = []

# ################################################################################################################################
# ################################################################################################################################

class FeedRecorder(Service):
    """ Receives feed messages handed over with the connector's self.invoke.
    """
    name = 'demo.feed.recorder'

    def handle(self) -> 'None':
        message = self.request.raw_request['message']
        _feed_invoked_messages.append(message)

# ################################################################################################################################
# ################################################################################################################################

class FeedTopicRecorder(Service):
    """ Receives feed messages published with the connector's self.publish to this service's topic.
    """
    name = 'demo.feed.topic-recorder'

    def handle(self) -> 'None':
        _feed_topic_messages.append(str(self.request.raw_request))

# ################################################################################################################################
# ################################################################################################################################

class GetFeedMessages(Service):
    """ Returns everything the feed delivered so far, through both delivery paths.
    """
    name = 'demo.feed.get-messages'

    def handle(self) -> 'None':
        self.response.payload = json.dumps({
            'invoked': _feed_invoked_messages,
            'topic': _feed_topic_messages,
        })

# ################################################################################################################################
# ################################################################################################################################

class SendAuditEvent(Service):
    """ Sends one fire-and-forget event to the audit collector.
    """
    name = 'demo.audit.send-event'

    input = 'event'

    def handle(self) -> 'None':
        conn = self.out.audit['My Audit']
        conn.send_event(self.request.input.event)
        self.response.payload = json.dumps({'response': 'sent'})

# ################################################################################################################################
# ################################################################################################################################

class GetStock(Service):
    """ Returns the stock of one item from the Java inventory component.
    """
    name = 'demo.inventory.get-stock'

    input = 'item'

    def handle(self) -> 'None':
        conn = self.out.inventory['My Inventory']
        response = conn.get_stock(self.request.input.item)
        self.response.payload = json.dumps({'response': response})

# ################################################################################################################################
# ################################################################################################################################

class TransformText(Service):
    """ Transforms text through the library running in a clean interpreter of its own.
    """
    name = 'demo.textproc.transform'

    input = 'text'

    def handle(self) -> 'None':
        conn = self.out.textproc['My TextProc']
        response = conn.transform(self.request.input.text)
        self.response.payload = json.dumps({'response': response})

# ################################################################################################################################
# ################################################################################################################################

class GetTunnelAddress(Service):
    """ Returns the tunnel's address from the long-lived CLI session.
    """
    name = 'demo.tunnel.get-address'

    def handle(self) -> 'None':
        conn = self.out.tunnel['My Tunnel']
        response = conn.get_address()
        self.response.payload = json.dumps({'response': response})

# ################################################################################################################################
# ################################################################################################################################

class GetTunnelStatus(Service):
    """ Returns a tunnel's status through the one-shot CLI command.
    """
    name = 'demo.tunnel.get-status'

    input = 'name'

    def handle(self) -> 'None':
        conn = self.out.tunnel['My Tunnel']
        response = conn.get_status(self.request.input.name)
        self.response.payload = json.dumps({'response': response})

# ################################################################################################################################
# ################################################################################################################################
