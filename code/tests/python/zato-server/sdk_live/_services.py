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
