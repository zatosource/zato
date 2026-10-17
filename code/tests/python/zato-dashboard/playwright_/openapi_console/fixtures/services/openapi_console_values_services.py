# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

# Zato
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

# The deterministic values the service always replies with
Created = datetime(2026, 1, 2, 3, 4, 5)
Amount  = Decimal('1.10')

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Order(Model):
    order_id: int
    created:  datetime

# ################################################################################################################################
# ################################################################################################################################

class ValuesOrders(Service):
    """ A service whose responses carry values that only Zato's own JSON serialization handles -
    a date and a decimal number in a dict for GET, and a list of models with dates for POST.
    """
    name = 'api.test.openapi.values.orders'

    def handle_GET(self) -> 'None':
        self.response.payload = {'created': Created, 'amount': Amount}

    def handle_POST(self) -> 'None':

        order_list:'list' = []

        for order_id in (1, 2):
            order = Order()
            order.order_id = order_id
            order.created = Created
            order_list.append(order)

        self.response.payload = order_list

# ################################################################################################################################
# ################################################################################################################################
