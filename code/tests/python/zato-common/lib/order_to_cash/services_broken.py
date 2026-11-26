# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The source of a version of the fulfillment of the order-to-cash integration that has a syntax error,
# which a test writes to the pickup directory to check that a failed deployment leaves the previous version in effect.
# The source is kept as text so that the module itself remains importable by the tools that compile the test tree.

Source = """# -*- coding: utf-8 -*-

# Zato
from zato.common.test.order_to_cash.models import ServiceName
from zato.server.service import Service

class Fulfillment(Service):
    name = ServiceName.Fulfillment

    def handle(self) -> 'None'
        self.logger.info('This version cannot be deployed')
"""
