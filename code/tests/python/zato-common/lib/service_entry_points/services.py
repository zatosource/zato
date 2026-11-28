# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The services of the service entry point tests, deployed to a test server through its pickup directory. Each service
# under test records what it received and what it computed, and returns the same result, whichever entry point
# invoked it - self.invoke, self.pubsub, a REST, SOAP or MLLP channel or Dashboard.

# Zato
from zato.common.hl7.mllp.preprocess import parse_with_channel_defaults
from zato.common.test.received_store import read_items, record
from zato.common.test.service_entry_points.models import Order, RecordKey, ResponseKey, ServiceName, snapshot, Store
from zato.common.typing_ import cast_
from zato.server.service import AsIs, Bool, Date, DateTime, Decimal, Dict, Float, Int, List, Service, UUID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    from zato.hl7v2 import HL7Message

    HL7Message = HL7Message

# ################################################################################################################################
# ################################################################################################################################

# The fields of an HL7 v2 message that the HL7 service records, MSH-10 aside, which is the ID of the request
_hl7_paths = ('MSH.3', 'MSH.4', 'MSH.5', 'MSH.6', 'MSH.7', 'MSH.9', 'MSH.12', 'PID.3', 'PID.5', 'PID.7', 'PID.8', 'PV1.3')

# The segment separator of HL7 v2
_hl7_segment_separator = '\r'

# ################################################################################################################################
# ################################################################################################################################

def _record(service:'Service', request_id:'str', received:'any_', result:'any_') -> 'None':
    """ Appends what a service under test received and what it computed to the store of the tests.
    """
    item = {
        RecordKey.Request_ID: request_id,
        RecordKey.Service: service.name,
        RecordKey.Channel_Type: service.channel.type,
        RecordKey.Channel_Name: service.channel.name,
        RecordKey.Input: snapshot(received),
        RecordKey.Result: result,
    }

    record(service, Store.Records, item)

# ################################################################################################################################
# ################################################################################################################################

class TypedOrder(Service):
    """ Computes the summary of an order out of an input with an element of every declared type.
    """
    name = ServiceName.Typed

    input = 'request_id', Int('quantity'), Bool('is_priority'), Float('weight'), Decimal('unit_price'), \
        Date('ship_date'), DateTime('ordered_at'), UUID('order_id'), List('tags'), Dict('address'), 'customer_name', \
        'has_gift_wrap', 'item_count', '-notes'

    def handle(self) -> 'None':

        request = self.request.input

        received = {
            'request_id': request.request_id,
            'quantity': request.quantity,
            'is_priority': request.is_priority,
            'weight': request.weight,
            'unit_price': request.unit_price,
            'ship_date': request.ship_date,
            'ordered_at': request.ordered_at,
            'order_id': request.order_id,
            'tags': request.tags,
            'address': request.address,
            'customer_name': request.customer_name,
            'has_gift_wrap': request.has_gift_wrap,
            'item_count': request.item_count,
            'notes': request.notes,
        }

        # The arithmetic works on the types the input declares ..
        total = request.unit_price * request.quantity
        shipping_weight = request.weight * request.quantity
        tags = ' '.join(request.tags)

        # .. and the result is text throughout, which every channel carries the same way.
        result = {
            'order_id': request.order_id,
            'customer_name': request.customer_name,
            'total': str(total),
            'shipping_weight': str(shipping_weight),
            'is_priority': str(request.is_priority),
            'has_gift_wrap': str(request.has_gift_wrap),
            'item_count': str(request.item_count),
            'ship_date': request.ship_date,
            'ordered_at': request.ordered_at,
            'tags': tags,
            'city': request.address['city'],
            'notes': str(request.notes),
        }

        _record(self, request.request_id, received, result)

        self.response.payload = result

# ################################################################################################################################
# ################################################################################################################################

class ModelOrder(Service):
    """ Computes the summary of an order out of a model input with a nested model and a list of models.
    """
    name = ServiceName.Model_Input

    class IO:
        input = Order

    def handle(self) -> 'None':

        order:'Order' = self.request.input

        total_quantity = 0
        skus = []

        for item in order.items:
            total_quantity += item.quantity
            skus.append(item.sku)

        result = {
            'order_number': order.order_number,
            'priority': str(order.priority),
            'ship_date': order.ship_date.isoformat(),
            'ordered_at': order.ordered_at.isoformat(),
            'city': order.address.city,
            'skus': ' '.join(skus),
            'total_quantity': str(total_quantity),
            'notes': str(order.notes),
        }

        _record(self, order.request_id, order, result)

        self.response.payload = result

# ################################################################################################################################
# ################################################################################################################################

class FreeFormOrder(Service):
    """ Computes the summary of an order out of an input without any declaration.
    """
    name = ServiceName.Free_Form

    def handle(self) -> 'None':

        request:'stranydict' = self.request.input.to_dict()
        address = request['address']
        tags = ' '.join(request['tags'])

        result = {
            'customer_name': request['customer_name'],
            'segment': request['segment'],
            'city': address['city'],
            'tags': tags,
            'field_count': str(len(request)),
        }

        _record(self, request['request_id'], request, result)

        self.response.payload = result

# ################################################################################################################################
# ################################################################################################################################

class HL7Admission(Service):
    """ Parses an HL7 v2 admission from its ER7 text and answers with an acknowledgment built of its header.
    """
    name = ServiceName.HL7

    def handle(self) -> 'None':

        # A single message, unlike a batch, always comes back parsed
        message = parse_with_channel_defaults(self.request.input)
        message = cast_('HL7Message', message)

        control_id = message.get('MSH.10')

        received:'stranydict' = {}

        for path in _hl7_paths:
            received[path] = message.get(path)

        # The acknowledgment swaps the sender and the receiver of the message and repeats its control ID ..
        msh_fields = [
            'MSH',
            '^~\\&',
            str(received['MSH.5']),
            str(received['MSH.6']),
            str(received['MSH.3']),
            str(received['MSH.4']),
            str(received['MSH.7']),
            '',
            'ACK',
            control_id,
            'P',
            str(received['MSH.12']),
        ]

        msh_line = '|'.join(msh_fields)
        msa_line = f'MSA|AA|{control_id}'

        # .. and its text starts with MSH, which is what an MLLP channel sends back as it is.
        ack = _hl7_segment_separator.join([msh_line, msa_line])

        _record(self, control_id, received, ack)

        self.response.payload = ack

# ################################################################################################################################
# ################################################################################################################################

class InvokeDriver(Service):
    """ Invokes a service under test with self.invoke and returns its response.
    """
    name = ServiceName.Invoke_Driver

    input = 'target', AsIs('payload')

    def handle(self) -> 'None':

        response = self.invoke(self.request.input.target, self.request.input.payload)

        self.response.payload = {
            ResponseKey.Response: response,
        }

# ################################################################################################################################
# ################################################################################################################################

class PublishDriver(Service):
    """ Publishes a request with self.pubsub to a topic or to a service by its name, as a model on request.
    """
    name = ServiceName.Publish_Driver

    input = 'destination', AsIs('payload'), '-should_publish_model'

    def handle(self) -> 'None':

        payload = self.request.input.payload

        if self.request.input.should_publish_model:
            payload = Order.from_dict(payload)

        _ = self.pubsub.publish(self.request.input.destination, payload)

# ################################################################################################################################
# ################################################################################################################################

class Read(Service):
    """ Returns every record that the services under test wrote.
    """
    name = ServiceName.Read

    def handle(self) -> 'None':

        self.response.payload = {
            ResponseKey.Records: read_items(self, Store.Records),
        }

# ################################################################################################################################
# ################################################################################################################################
