# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The corpus of payload behaviors, written once - every channel boundary runs
the same cases and expects the same canonical values on its side of the wire.
"""

# stdlib
from dataclasses import dataclass
from unittest.mock import MagicMock

# Zato
from zato.common import SOAPMessage
from zato.common.api import DATA_FORMAT
from zato.common.marshal_.api import Model
from zato.common.marshal_.io import DataClassIO
from zato.common.typing_ import any_, anydictnone
from zato.input_output import IOProcessor
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callnone
    callnone = callnone

# ################################################################################################################################
# ################################################################################################################################

# The behavior families - which boundaries run a case depends on its family.
Family_Dict   = 'dict'
Family_String = 'string'
Family_SOAP   = 'soap'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PayloadCase:
    """ One behavior of the corpus - a service class, the request to send it
    and the canonical value expected on the caller's side of the boundary.
    """
    name: str
    service_class: any_
    request: any_
    expected: any_
    family: str
    data_format: str

    # True for cases whose live response is a model or a list of models -
    # boundaries whose wire encoder cannot serialize live models skip these.
    is_model_shaped: bool

    # Used by the invoke boundary only.
    as_bunch: bool
    invoke_kwargs: anydictnone

    # An optional callable(test, result) with case-specific assertions -
    # when it is given, it replaces the default comparison against expected.
    verify: 'callnone'

# ################################################################################################################################

def make_case(
    name,          # type: str
    service_class, # type: any_
    *,
    request=None,       # type: any_
    expected=None,      # type: any_
    family=Family_Dict, # type: str
    data_format=DATA_FORMAT.DICT, # type: str
    is_model_shaped=False, # type: bool
    as_bunch=False,        # type: bool
    invoke_kwargs=None,    # type: anydictnone
    verify=None            # type: callnone
    ) -> 'PayloadCase':
    """ Builds one corpus case with all its fields filled in.
    """

    # Our response to produce
    out = PayloadCase()

    out.name = name
    out.service_class = service_class
    out.request = request
    out.expected = expected
    out.family = family
    out.data_format = data_format
    out.is_model_shaped = is_model_shaped
    out.as_bunch = as_bunch
    out.invoke_kwargs = invoke_kwargs
    out.verify = verify

    return out

# ################################################################################################################################
# ################################################################################################################################

class CorpusService(Service):
    """ The class-level boilerplate every corpus service shares - what ServiceStore
    would normally set up during deployment.
    """
    _config_manager = MagicMock()
    _config_store = MagicMock()
    amqp = MagicMock()

    has_io = False
    component_enabled_email = False
    component_enabled_odoo = False

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class OrderStatus(Model):
    customer_id: str
    status: str

# ################################################################################################################################
# ################################################################################################################################

class FreeFormDetailsService(CorpusService):
    """ Zero declarations - the payload is a free-form message built through dot access.
    """
    _Service__service_name = 'orders.free-form-details'
    _Service__service_impl_name = 'orders.api.FreeFormDetailsService'

    def handle(self) -> 'None':
        self.response.payload.order.details.total = 123

# ################################################################################################################################

class DictAssignmentService(CorpusService):
    """ Zero declarations - a plain dict assigned to the payload replaces the free-form message.
    """
    _Service__service_name = 'orders.dict-assignment'
    _Service__service_impl_name = 'orders.api.DictAssignmentService'

    def handle(self) -> 'None':
        self.response.payload = {'customer_id': 'C-1001', 'status': 'confirmed'}

# ################################################################################################################################

class OrderSubtreeService(CorpusService):
    """ A string-based output declaration - the declared name vivifies a message subtree.
    """
    _Service__service_name = 'orders.declared-subtree'
    _Service__service_impl_name = 'orders.api.OrderSubtreeService'

    output = 'order'

    def handle(self) -> 'None':
        self.response.payload.order.customer_id = 'C-1001'
        self.response.payload.order.status = 'confirmed'

# The real I/O processor attaches the declaration the same way deployment does.
_ = IOProcessor.attach_io(MagicMock(), OrderSubtreeService)
OrderSubtreeService.has_io = True

# ################################################################################################################################

class OrderModelService(CorpusService):
    """ A dataclass output declaration - the payload vivifies a model instance on first access.
    """
    _Service__service_name = 'orders.model-output'
    _Service__service_impl_name = 'orders.api.OrderModelService'

    class IO:
        output = OrderStatus

    def handle(self) -> 'None':
        self.response.payload.customer_id = 'C-1001'
        self.response.payload.status = 'confirmed'

_ = DataClassIO.attach_io(MagicMock(), OrderModelService)
OrderModelService.has_io = True

# ################################################################################################################################

class OrderModelListService(CorpusService):
    """ Zero declarations - a list of model instances assigned to the payload.
    """
    _Service__service_name = 'orders.model-list'
    _Service__service_impl_name = 'orders.api.OrderModelListService'

    def handle(self) -> 'None':

        first = OrderStatus.__new__(OrderStatus)
        first.customer_id = 'C-1001'
        first.status = 'confirmed'

        second = OrderStatus.__new__(OrderStatus)
        second.customer_id = 'C-1002'
        second.status = 'new'

        self.response.payload = [first, second]

# ################################################################################################################################

class NoResponseService(CorpusService):
    """ Zero declarations and no payload assignment - the response stays empty.
    """
    _Service__service_name = 'orders.no-response'
    _Service__service_impl_name = 'orders.api.NoResponseService'

    def handle(self) -> 'None':
        pass

# ################################################################################################################################

class PlainTextService(CorpusService):
    """ A plain string assigned to the payload passes through every channel unchanged.
    """
    _Service__service_name = 'notifications.plain-text'
    _Service__service_impl_name = 'notifications.api.PlainTextService'

    def handle(self) -> 'None':
        self.response.payload = 'Your order has been received'

# ################################################################################################################################

_hl7_ack = 'MSH|^~\\&|IIS|STATE|MYAPP|MYFAC|20260721||ACK^V04^ACK|CTRL-0001|P|2.5.1\rMSA|AA|CTRL-0001'

class HL7ACKService(CorpusService):
    """ An ER7 acknowledgment - a string payload in the HL7 wire format.
    """
    _Service__service_name = 'hl7.ack'
    _Service__service_impl_name = 'hl7.api.HL7ACKService'

    def handle(self) -> 'None':
        self.response.payload = _hl7_ack

# ################################################################################################################################

_edifact_interchange = \
    "UNB+UNOC:3+SENDER+RECIPIENT+260721:0930+REF-0001'UNH+1+ORDERS:D:96A:UN'UNT+2+1'UNZ+1+REF-0001'"

class EDIFACTOrdersService(CorpusService):
    """ A serialized EDIFACT interchange - a string payload in the EDIFACT wire format.
    """
    _Service__service_name = 'edifact.orders'
    _Service__service_impl_name = 'edifact.api.EDIFACTOrdersService'

    def handle(self) -> 'None':
        self.response.payload = _edifact_interchange

# ################################################################################################################################

class SOAPOrderStatusService(CorpusService):
    """ A SOAP message built through dot access - its channel wraps it in an envelope
    matching the request.
    """
    _Service__service_name = 'orders.soap-status'
    _Service__service_impl_name = 'orders.api.SOAPOrderStatusService'

    def handle(self) -> 'None':

        message = SOAPMessage()
        message.status = 'Accepted'
        message.details.total = 123

        self.response.payload = message

# ################################################################################################################################
# ################################################################################################################################

case_list = list['PayloadCase']

# ################################################################################################################################

def build_corpus_cases() -> 'case_list':
    """ Returns the corpus - the dict family, the string family and the SOAP-specific case.
    """
    out = []

    # The dict family ..
    out.append(make_case('free-form-nested', FreeFormDetailsService,
        request={'customer_id': 'C-1001'},
        expected={'order': {'details': {'total': 123}}}))

    out.append(make_case('dict-assignment', DictAssignmentService,
        request={'customer_id': 'C-1001'},
        expected={'customer_id': 'C-1001', 'status': 'confirmed'}))

    out.append(make_case('string-output-subtree', OrderSubtreeService,
        request={'customer_id': 'C-1001'},
        expected={'order': {'customer_id': 'C-1001', 'status': 'confirmed'}}))

    out.append(make_case('model-output', OrderModelService,
        request={'customer_id': 'C-1001'},
        expected={'customer_id': 'C-1001', 'status': 'confirmed'},
        is_model_shaped=True))

    out.append(make_case('list-of-models', OrderModelListService,
        request={'customer_id': 'C-1001'},
        expected=[
            {'customer_id': 'C-1001', 'status': 'confirmed'},
            {'customer_id': 'C-1002', 'status': 'new'},
        ],
        is_model_shaped=True))

    out.append(make_case('empty-payload', NoResponseService,
        request={'customer_id': 'C-1001'},
        expected=''))

    # .. the string family ..
    out.append(make_case('plain-text', PlainTextService,
        request='Please confirm the order',
        expected='Your order has been received',
        family=Family_String))

    out.append(make_case('hl7-ack', HL7ACKService,
        request='MSH|^~\\&|MYAPP|MYFAC|IIS|STATE|20260721||VXU^V04^VXU_V04|CTRL-0001|P|2.5.1',
        expected=_hl7_ack,
        family=Family_String))

    out.append(make_case('edifact-interchange', EDIFACTOrdersService,
        request='Send the current interchange',
        expected=_edifact_interchange,
        family=Family_String))

    # .. and the SOAP-specific case - a message built through dot access,
    # enveloped by the channel and decoded back from the envelope.
    out.append(make_case('soap-message', SOAPOrderStatusService,
        request='',
        expected={'status': 'Accepted', 'details': {'total': 123}},
        family=Family_SOAP))

    return out

# ################################################################################################################################
# ################################################################################################################################
