# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The first version of the fulfillment of the order-to-cash integration, which ships without a carrier.

# Zato
from zato.common.test.order_to_cash.control import claim_failure, Fault, record_step, wait_step_delay
from zato.common.test.order_to_cash.models import build_ship_notice, Retry, ServiceName, Step, Topic, TransientOutageError
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class Fulfillment(Service):
    """ Allocates the stock of an approved order and publishes its advance ship notice.
    """
    name = ServiceName.Fulfillment

    # The version of the service that the trail records
    trail_version = 1

    def handle(self) -> 'None':

        wait_step_delay(self)

        order = self.request.input
        po_number = order.po_number

        # The warehouse is unavailable for as many attempts as the control files say
        if claim_failure(self, Fault.Fulfillment, po_number):
            raise TransientOutageError(f'The warehouse is unavailable for PO `{po_number}`')

        # Raises UnknownSKUError for a SKU that no warehouse stocks, which every retry raises again
        notice = build_ship_notice(order)

        record_step(self, Step.Fulfillment, po_number, asn_number=notice.asn_number, carrier=notice.carrier,
            version=self.trail_version)

        _ = self.publish(
            Topic.Order_Shipped,
            notice,
            correl_id=po_number,
            max_retries=Retry.Max_Retries,
            retry_sleep_time=Retry.Sleep_Time,
        )

# ################################################################################################################################
# ################################################################################################################################
