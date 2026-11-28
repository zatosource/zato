# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The canonical request of each service under test, rendered as the body that each entry point carries - a dict
# for self.invoke and self.pubsub, a JSON document for REST and Dashboard, a SOAP 1.1 or SOAP 1.2 envelope
# and an ER7 message for HL7 v2.

# stdlib
import os
from json import dumps
from typing import NamedTuple
from xml.sax.saxutils import escape

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.conftest_base_pubsub import render_template
from zato.common.test.service_entry_points.models import ServiceName, Topic
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strdict

# ################################################################################################################################
# ################################################################################################################################

_here = os.path.dirname(os.path.abspath(__file__))

# The prefix of every request ID - an ID fits MSH-10, which HL7 v2.5 limits to 20 characters
_request_id_prefix = 'SEP'

# ################################################################################################################################
# ################################################################################################################################

class Module:
    """ The name under which the services are deployed.
    """
    File_Name = 'service_entry_points.py'

# ################################################################################################################################

class Source:
    """ The files of the library.
    """
    Services = os.path.join(_here, 'services.py')
    Enmasse  = os.path.join(_here, 'enmasse.yaml')

# ################################################################################################################################

class Caller:
    """ The security definition of the REST and SOAP channels.
    """
    Name     = 'test.service-entry-points.caller'
    Username = 'test.service-entry-points.caller'

# ################################################################################################################################

class SOAPVersion:
    """ The SOAP versions of the SOAP channels.
    """
    V11 = '1.1'
    V12 = '1.2'

# ################################################################################################################################

class SOAP:
    """ The operation that every SOAP request calls, with its envelopes and media types.
    """
    Action             = 'urn:service-entry-points:submit'
    Operation          = 'SubmitOrder'
    Response_Element   = 'SubmitOrderResponse'
    Operation_NS       = 'urn:service-entry-points'
    Envelope_NS_11     = 'http://schemas.xmlsoap.org/soap/envelope/'
    Envelope_NS_12     = 'http://www.w3.org/2003/05/soap-envelope'
    Content_Type_11    = 'text/xml; charset=utf-8'
    Content_Type_12    = 'application/soap+xml; charset=utf-8; action="urn:service-entry-points:submit"'
    SOAP_Action_Header = '"urn:service-entry-points:submit"'

# ################################################################################################################################

class HL7:
    """ The header values of the canonical HL7 v2 message and the MLLP channel that receives it.
    """
    Channel_Name      = 'test.service-entry-points.mllp.hl7'
    Sending_App       = 'SERVICE_ENTRY_POINTS'
    Content_Type      = 'text/plain; charset=utf-8'
    Segment_Separator = '\r'

# ################################################################################################################################
# ################################################################################################################################

class Kind:
    """ The kinds of input of the services under test.
    """
    Typed     = 'typed'
    Model     = 'model'
    Free_Form = 'free-form'
    HL7       = 'hl7'

# ################################################################################################################################

class Target(NamedTuple):
    """ A service under test and everything that leads to it.
    """
    kind: 'str'
    service_name: 'str'
    topic_name: 'str'
    rest_channel: 'str'
    rest_path: 'str'
    soap_11_channel: 'str'
    soap_11_path: 'str'
    soap_12_channel: 'str'
    soap_12_path: 'str'

# ################################################################################################################################

def _new_target(kind:'str', service_name:'str', topic_name:'str') -> 'Target':
    """ A service under test with the names of its channels, which follow its kind.
    """
    out = Target(
        kind=kind,
        service_name=service_name,
        topic_name=topic_name,
        rest_channel=f'test.service-entry-points.rest.{kind}',
        rest_path=f'/service-entry-points/rest/{kind}',
        soap_11_channel=f'test.service-entry-points.soap11.{kind}',
        soap_11_path=f'/service-entry-points/soap11/{kind}',
        soap_12_channel=f'test.service-entry-points.soap12.{kind}',
        soap_12_path=f'/service-entry-points/soap12/{kind}',
    )

    return out

# ################################################################################################################################

Typed_Target     = _new_target(Kind.Typed, ServiceName.Typed, Topic.Typed)
Model_Target     = _new_target(Kind.Model, ServiceName.Model_Input, Topic.Model_Input)
Free_Form_Target = _new_target(Kind.Free_Form, ServiceName.Free_Form, Topic.Free_Form)
HL7_Target       = _new_target(Kind.HL7, ServiceName.HL7, Topic.HL7)

# The services that take a structured request, which REST and SOAP carry as JSON and XML
Structured_Targets = (Typed_Target, Model_Target, Free_Form_Target)

# Every service under test
All_Targets = (Typed_Target, Model_Target, Free_Form_Target, HL7_Target)

# ################################################################################################################################
# ################################################################################################################################

def new_request_id() -> 'str':
    """ A request ID of its own for each invocation.
    """
    out = _request_id_prefix + CryptoManager.generate_hex_string()
    return out

# ################################################################################################################################

def new_caller_password() -> 'str':
    """ The password of the security definition of the channels.
    """
    out = CryptoManager.generate_password(to_str=True)
    out = cast_('str', out)

    return out

# ################################################################################################################################

def render_definitions(caller_password:'str') -> 'str':
    """ The enmasse definitions of the channels, the topics and the subscriptions.
    """
    placeholders = {
        'caller_password': caller_password,
    }

    out = render_template(Source.Enmasse, placeholders)
    return out

# ################################################################################################################################

def read_source(path:'str') -> 'str':
    with open(path) as source_file:
        out = source_file.read()

    return out

# ################################################################################################################################
# ################################################################################################################################

def new_typed_request(request_id:'str') -> 'anydict':
    """ The request of the typed service, with a value for every declared element except the optional one.
    """
    out = {
        'request_id': request_id,
        'quantity': 3,
        'is_priority': True,
        'weight': 2.5,
        'unit_price': 19.99,
        'ship_date': '2026-12-01',
        'ordered_at': '2026-11-28T10:15:00',
        'order_id': '7c9e6679-7425-40de-944b-e07fc1f90ae7',
        'tags': ['express', 'fragile'],
        'address': {
            'street': '100 Main Street',
            'city': 'Springfield',
            'postal_code': '62701',
        },
        'customer_name': 'John Smith',
        'has_gift_wrap': False,
        'item_count': 2,
    }

    return out

# ################################################################################################################################

def new_model_request(request_id:'str') -> 'anydict':
    """ The request of the model service, with a nested model, a list of models and the optional field left out.
    """
    out = {
        'request_id': request_id,
        'order_number': 'PO-2026-0042',
        'priority': 2,
        'ship_date': '2026-12-01',
        'ordered_at': '2026-11-28T10:15:00',
        'address': {
            'street': '100 Main Street',
            'city': 'Springfield',
            'postal_code': '62701',
        },
        'items': [
            {'sku': 'SKU-BOOK-001', 'quantity': 2},
            {'sku': 'SKU-TONER-007', 'quantity': 5},
        ],
    }

    return out

# ################################################################################################################################

def new_free_form_request(request_id:'str') -> 'anydict':
    """ The request of the free-form service. Without a declaration, nothing converts the text of an XML leaf,
    so every value is text, which JSON and XML carry the same way.
    """
    out = {
        'request_id': request_id,
        'customer_name': 'John Smith',
        'segment': 'enterprise',
        'address': {
            'street': '100 Main Street',
            'city': 'Springfield',
            'postal_code': '62701',
        },
        'tags': ['express', 'fragile'],
    }

    return out

# ################################################################################################################################

def new_hl7_message(request_id:'str') -> 'str':
    """ The ER7 text of an admission whose MSH-10 is the request ID.
    """
    segments = [
        f'MSH|^~\\&|{HL7.Sending_App}|GENERAL_HOSPITAL|LAB_SYSTEM|CENTRAL_LAB|20261128101500||ADT^A01^ADT_A01|{request_id}|P|2.5',
        'EVN|A01|20261128101500',
        'PID|1||7788990^^^GENERAL_HOSPITAL^MR||SMITH^JOHN^A||19850315|M',
        'PV1|1|I|ICU^101^A',
    ]

    out = HL7.Segment_Separator.join(segments)
    return out

# ################################################################################################################################

_request_builders = {
    Kind.Typed: new_typed_request,
    Kind.Model: new_model_request,
    Kind.Free_Form: new_free_form_request,
    Kind.HL7: new_hl7_message,
}

def new_request(target:'Target', request_id:'str') -> 'any_':
    """ The canonical request of a service under test.
    """
    builder = _request_builders[target.kind]

    out = builder(request_id)
    return out

# ################################################################################################################################
# ################################################################################################################################

def to_json(request:'anydict') -> 'str':
    out = dumps(request)
    return out

# ################################################################################################################################

def _to_xml(name:'str', value:'any_') -> 'str':
    """ One XML element per value - a dict becomes nested elements and a list becomes repeated elements,
    which is why every list of a canonical request has more than one item.
    """
    if isinstance(value, dict):
        children = ''.join(_to_xml(child_name, child_value) for child_name, child_value in value.items())
        out = f'<{name}>{children}</{name}>'

    elif isinstance(value, list):
        out = ''.join(_to_xml(name, item) for item in value)

    else:
        if isinstance(value, bool):
            text = 'true' if value else 'false'
        else:
            text = str(value)

        out = f'<{name}>{escape(text)}</{name}>'

    return out

# ################################################################################################################################

def to_soap_envelope(request:'anydict', soap_version:'str') -> 'str':
    """ The SOAP envelope of a request, in the given SOAP version.
    """
    if soap_version == SOAPVersion.V11:
        envelope_ns = SOAP.Envelope_NS_11
    else:
        envelope_ns = SOAP.Envelope_NS_12

    elements = ''.join(_to_xml(name, value) for name, value in request.items())
    operation = f'<{SOAP.Operation} xmlns="{SOAP.Operation_NS}">{elements}</{SOAP.Operation}>'

    out = f'<soap:Envelope xmlns:soap="{envelope_ns}"><soap:Header/><soap:Body>{operation}</soap:Body></soap:Envelope>'
    return out

# ################################################################################################################################

def get_soap_headers(soap_version:'str') -> 'strdict':
    """ The HTTP headers of a SOAP request in the given SOAP version.
    """
    if soap_version == SOAPVersion.V11:
        out = {
            'Content-Type': SOAP.Content_Type_11,
            'SOAPAction': SOAP.SOAP_Action_Header,
        }
    else:
        out = {
            'Content-Type': SOAP.Content_Type_12,
        }

    return out

# ################################################################################################################################
# ################################################################################################################################
