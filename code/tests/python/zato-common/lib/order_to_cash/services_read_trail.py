# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.test.order_to_cash.models import ServiceName, Store
from zato.common.test.received_store import read_items
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class ReadTrail(Service):
    """ Returns the steps that the services of the order-to-cash integration recorded and the entries of its ledger.
    """
    name = ServiceName.Read_Trail

    def handle(self) -> 'None':

        self.response.payload = {
            'trail': read_items(self, Store.Trail),
            'ledger': read_items(self, Store.Ledger),
        }

# ################################################################################################################################
# ################################################################################################################################
