# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The names, the messages and the input snapshots of the service entry point tests. The services under test run
# in a test server, which rebuilds the messages of this module on delivery, and the tests run in the test process,
# and both import this module.

# stdlib
from dataclasses import dataclass, fields
from datetime import date, datetime

# Zato
from zato.common.marshal_.api import Model
from zato.common.typing_ import list_, strnone

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class ServiceName:
    """ The services under test, the drivers that invoke them and the reader of what they recorded.
    """
    Typed          = 'test.service-entry-points.typed'
    Model_Input    = 'test.service-entry-points.model'
    Free_Form      = 'test.service-entry-points.free-form'
    HL7            = 'test.service-entry-points.hl7'
    Invoke_Driver  = 'test.service-entry-points.invoke-driver'
    Publish_Driver = 'test.service-entry-points.publish-driver'
    Read           = 'test.service-entry-points.read'

# ################################################################################################################################

class Topic:
    """ The topics whose push subscriptions deliver to the services under test, one topic per service.
    """
    Typed       = 'test.service-entry-points.typed'
    Model_Input = 'test.service-entry-points.model'
    Free_Form   = 'test.service-entry-points.free-form'
    HL7         = 'test.service-entry-points.hl7'

# ################################################################################################################################

class Store:
    """ The store of zato.common.test.received_store that the services under test write to.
    """
    Records = 'service-entry-points'

# ################################################################################################################################

class RecordKey:
    """ The keys of each record that a service under test writes.
    """
    Request_ID   = 'request_id'
    Service      = 'service'
    Channel_Type = 'channel_type'
    Channel_Name = 'channel_name'
    Input        = 'input'
    Result       = 'result'

# ################################################################################################################################

class ResponseKey:
    """ The keys of the responses of the drivers and of the reader.
    """
    Response = 'response'
    Records  = 'records'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Address(Model):
    street: str
    city: str
    postal_code: str

# ################################################################################################################################

@dataclass(init=False)
class OrderItem(Model):
    sku: str
    quantity: int

# ################################################################################################################################

@dataclass(init=False)
class Order(Model):
    request_id: str
    order_number: str
    priority: int
    ship_date: date
    ordered_at: datetime
    address: Address
    items: list_[OrderItem]
    notes: strnone = None

# ################################################################################################################################
# ################################################################################################################################

def snapshot(value:'any_') -> 'any_':
    """ Returns what a service received as plain JSON - the Python type of each value next to its text,
    with dicts by their sorted keys, lists in their order and models field by field.
    """
    if isinstance(value, Model):
        model_fields = {}

        for field in fields(value):
            field_value = getattr(value, field.name)
            model_fields[field.name] = snapshot(field_value)

        out = {
            'model': type(value).__name__,
            'fields': model_fields,
        }

    elif isinstance(value, dict):
        out = {}

        for key in sorted(value):
            out[key] = snapshot(value[key])

    elif isinstance(value, list):
        out = []

        for item in value:
            item_snapshot = snapshot(item)
            out.append(item_snapshot)

    else:
        type_name = type(value).__name__
        out = [type_name, str(value)]

    return out

# ################################################################################################################################
# ################################################################################################################################
