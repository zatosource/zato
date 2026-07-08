# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64encode
from copy import deepcopy
from datetime import date, datetime
from decimal import Decimal

# lxml
from lxml import etree

# pytest
import pytest

# Zato
from zato.common.soap.message import parse, serialize, SOAPMessage
from zato.common.util.xml_.core import XMLException

# ################################################################################################################################
# ################################################################################################################################

# The CDC IIS transport namespace - the national immunization submission WSDL.
_ns_cdc = 'urn:cdc:iisb:2011'

# The IHE XDS registry namespace - TEFCA, eHealth Exchange and the German ePA all build on it.
_ns_rim = 'urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0'

# The IHE XCPD patient discovery namespace - HL7v3.
_ns_hl7v3 = 'urn:hl7-org:v3'

# ################################################################################################################################
# ################################################################################################################################

def _roundtrip(message, tag, default_namespace=None):
    """ Serializes a message and parses the resulting wire bytes back.
    """
    element = serialize(message, tag, default_namespace)
    data = etree.tostring(element)

    out = parse(data)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestCDCIIS:
    """ The CDC IIS transport - SOAP body parameters per the CDC WSDL,
    as required by the MIIC, Florida SHOTS, CAIR2 and other state onboarding specs.
    """

    def test_submit_single_message(self):
        request = SOAPMessage()
        request.namespace = _ns_cdc

        request.username = 'MYUSERNAME'
        request.password = 'MYPASSWORD'
        request.hl7Message = 'MSH|^~\\&|MYEHR|MYCLINIC|MIIC|MIIC|20260401||VXU^V04^VXU_V04|12345|P|2.5.1'

        element = serialize(request, 'submitSingleMessage')

        assert element.tag == f'{{{_ns_cdc}}}submitSingleMessage'

        # The CDC WSDL expects the body parameters in exactly this order.
        children = [child.tag for child in element]
        assert children == [
            f'{{{_ns_cdc}}}username',
            f'{{{_ns_cdc}}}password',
            f'{{{_ns_cdc}}}hl7Message',
        ]

        assert element[0].text == 'MYUSERNAME'
        assert element[2].text.startswith('MSH|')

    def test_connectivity_test(self):
        request = SOAPMessage()
        request.namespace = _ns_cdc
        request.echoBack = 'ping'

        result = _roundtrip(request, 'connectivityTest')

        assert result.echoBack == 'ping'

# ################################################################################################################################
# ################################################################################################################################

class TestIHEMetadata:
    """ IHE XDS/XCA document metadata - rim:Slot elements with attributes,
    the shape TEFCA QHINs and the Swiss EPD exchange documents in.
    """

    def test_slot_with_attribute_and_children(self):
        request = SOAPMessage()
        request.namespace = _ns_rim

        request.Slot['name'] = 'creationTime'
        request.Slot.ValueList.Value = '20260401123000'

        element = serialize(request, 'ExtrinsicObject')

        slot = element[0]
        assert slot.tag == f'{{{_ns_rim}}}Slot'
        assert slot.get('name') == 'creationTime'

        value = slot[0][0]
        assert value.tag == f'{{{_ns_rim}}}Value'
        assert value.text == '20260401123000'

    def test_repeated_elements(self):
        request = SOAPMessage()
        request.namespace = _ns_rim

        request.ValueList.Value = ['urn:oid:1.2.840.114350', 'urn:oid:1.2.840.114351']

        element = serialize(request, 'Slot')
        values = element[0]

        assert len(values) == 2
        assert values[0].text == 'urn:oid:1.2.840.114350'
        assert values[1].text == 'urn:oid:1.2.840.114351'

    def test_repeated_elements_parse_back_as_list(self):
        request = SOAPMessage()
        request.namespace = _ns_rim
        request.ValueList.Value = ['first', 'second', 'third']

        result = _roundtrip(request, 'Slot')

        assert result.ValueList.Value == ['first', 'second', 'third']

# ################################################################################################################################
# ################################################################################################################################

class TestXCPD:
    """ IHE XCPD patient discovery - nested HL7v3 structures with per-node text
    and attributes, as TEFCA QHIN-to-QHIN patient discovery requires.
    """

    def test_nested_parameters_with_attributes(self):
        request = SOAPMessage()
        request.namespace = _ns_hl7v3

        request.controlActProcess.queryByParameter.parameterList.livingSubjectName.value['text'] = 'Smith'
        request.controlActProcess.queryByParameter.parameterList.livingSubjectName.value['use'] = 'L'

        element = serialize(request, 'PRPA_IN201305UV02')

        value = element[0][0][0][0][0]
        assert value.tag == f'{{{_ns_hl7v3}}}value'
        assert value.text == 'Smith'
        assert value.get('use') == 'L'

    def test_assignment_order_is_wire_order(self):
        request = SOAPMessage()
        request.namespace = _ns_hl7v3

        parameters = request.controlActProcess.queryByParameter.parameterList
        parameters.livingSubjectAdministrativeGender.value['code'] = 'F'
        parameters.livingSubjectBirthTime.value['value'] = '19800101'
        parameters.livingSubjectName.value['text'] = 'Smith'

        element = serialize(request, 'PRPA_IN201305UV02')
        parameter_list = element[0][0][0]

        names = [child.tag for child in parameter_list]
        assert names == [
            f'{{{_ns_hl7v3}}}livingSubjectAdministrativeGender',
            f'{{{_ns_hl7v3}}}livingSubjectBirthTime',
            f'{{{_ns_hl7v3}}}livingSubjectName',
        ]

# ################################################################################################################################
# ################################################################################################################################

class TestNamespaces:

    def test_per_node_namespace_override(self):
        # An EESSI-style message where one subtree lives in its own namespace.
        request = SOAPMessage()
        request.namespace = 'urn:eessi:business'

        request.Header.SenderId = 'IE:DSP'
        request.Payload['namespace'] = 'urn:eessi:sed'
        request.Payload.SEDType = 'S040'

        element = serialize(request, 'Message')

        assert element[0].tag == '{urn:eessi:business}Header'
        assert element[1].tag == '{urn:eessi:sed}Payload'

        # The override is inherited by the subtree.
        assert element[1][0].tag == '{urn:eessi:sed}SEDType'

    def test_no_namespace_at_all(self):
        request = SOAPMessage()
        request.echoBack = 'ping'

        element = serialize(request, 'connectivityTest')

        assert element.tag == 'connectivityTest'
        assert element[0].tag == 'echoBack'

# ################################################################################################################################
# ################################################################################################################################

class TestValueTypes:

    def test_lexical_forms(self):
        payload = b'PDF-BYTES'

        request = SOAPMessage()
        request.isActive = True
        request.isDeleted = False
        request.count = 27
        request.ratio = 1.5
        request.amount = Decimal('129.95')
        request.when = datetime(2026, 4, 1, 12, 30, 0)
        request.day = date(2026, 4, 1)
        request.document = payload

        element = serialize(request, 'request')

        assert element[0].text == 'true'
        assert element[1].text == 'false'
        assert element[2].text == '27'
        assert element[3].text == '1.5'
        assert element[4].text == '129.95'
        assert element[5].text == '2026-04-01T12:30:00'
        assert element[6].text == '2026-04-01'
        assert element[7].text == b64encode(payload).decode('ascii')

    def test_unsupported_type_is_rejected(self):
        request = SOAPMessage()
        request.value = object()

        with pytest.raises(XMLException):
            _ = serialize(request, 'request')

    def test_none_is_xsi_nil(self):
        request = SOAPMessage()
        request.middleName = None

        result = _roundtrip(request, 'request')

        assert result.middleName is None

# ################################################################################################################################
# ################################################################################################################################

class TestVivification:

    def test_reading_does_not_serialize_empty_nodes(self):
        request = SOAPMessage()
        request.real = 'value'

        # Reading vivifies a node but gives it no content.
        _ = request.phantom.child.grandchild

        element = serialize(request, 'request')

        children = [child.tag for child in element]
        assert children == ['real']

    def test_empty_node_is_falsey(self):
        request = SOAPMessage()

        assert not request.phantom
        assert not request

        request.real = 'value'
        assert request

# ################################################################################################################################
# ################################################################################################################################

class TestNodeProtocol:
    """ The Python-side behavior of a node - reading back what was assigned,
    string forms, and how the node responds to protocol probes.
    """

    def test_namespace_reads_back(self):
        request = SOAPMessage()

        # A fresh node has no namespace until one is assigned.
        assert request.namespace is None

        request.namespace = _ns_cdc
        assert request.namespace == _ns_cdc

        # The bracket form reads the same value.
        assert request['namespace'] == _ns_cdc

    def test_attribute_reads_back_through_brackets(self):
        slot = SOAPMessage()
        slot['name'] = 'creationTime'
        slot['text'] = '20260401'

        assert slot['name'] == 'creationTime'
        assert slot['text'] == '20260401'

        assert 'name' in slot
        assert 'other' not in slot

        # The reserved keys are not attributes, so they never answer to `in`.
        assert 'text' not in slot

    def test_str_is_the_node_text(self):
        slot = SOAPMessage()

        # A node without text is an empty string, never None.
        assert str(slot) == ''

        slot['text'] = 'PDQ Supplier'
        assert str(slot) == 'PDQ Supplier'

    def test_repr_names_children_and_attributes(self):
        request = SOAPMessage()
        request.facilityID = 'FL0001'
        request['status'] = 'Approved'

        text = repr(request)

        assert 'facilityID' in text
        assert 'status' in text

    def test_underscore_probes_fail_normally(self):
        request = SOAPMessage()

        # Protocol probes such as pickling or deepcopy look for underscore
        # attributes - they must see a normal failure, not a vivified node.
        with pytest.raises(AttributeError):
            _ = request._ipython_canary_method_should_not_exist_

    def test_deepcopy_gives_an_independent_message(self):
        request = SOAPMessage()
        request.namespace = _ns_cdc
        request.facilityID = 'FL0001'

        copied = deepcopy(request)
        copied.facilityID = 'FL9999'

        assert request.facilityID == 'FL0001'
        assert copied.facilityID == 'FL9999'
        assert copied.namespace == _ns_cdc

    def test_list_content_decides_node_truth(self):
        request = SOAPMessage()

        # A list of contentless nodes carries nothing.
        request.classifications = [SOAPMessage(), SOAPMessage()]
        assert not request

        # One list item with real content is enough - even after empty ones.
        slot = SOAPMessage()
        slot.value = 'urn:uuid:1'
        request.classifications = [SOAPMessage(), slot]
        assert request

# ################################################################################################################################
# ################################################################################################################################

class TestParsingEdges:
    """ The wire shapes real registries and gateways produce that a schema-free
    reader has to take in stride.
    """

    def test_comments_are_skipped(self):
        data = b'<response><!-- audit trail --><status>Success</status></response>'

        result = parse(data)

        assert result.status == 'Success'
        assert list(result._children) == ['status']

    def test_empty_leaf_reads_as_empty_string(self):
        data = b'<response><middleName/><familyName>Smith</familyName></response>'

        result = parse(data)

        assert result.middleName == ''
        assert result.familyName == 'Smith'

    def test_mixed_text_and_attributes(self):
        data = b'<response><code system="2.16.840.1.113883">PA</code></response>'

        result = parse(data)

        # An element carrying both an attribute and text keeps both apart.
        assert result.code['system'] == '2.16.840.1.113883'
        assert result.code['text'] == 'PA'
        assert str(result.code) == 'PA'

    def test_whitespace_between_elements_is_formatting(self):
        data = b'<response>\n  <status>Success</status>\n</response>'

        result = parse(data)

        # Pretty-printing whitespace is not text content.
        assert result['text'] is None
        assert result.status == 'Success'

    def test_comment_only_leaf_reads_as_empty_string(self):
        data = b'<response><notes><!-- reviewed --></notes></response>'

        result = parse(data)

        assert result.notes == ''

    def test_nil_false_marker_never_surfaces_as_attribute(self):
        data = (
            b'<response xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            b'<middleName xsi:nil="false" partial="true">Ann</middleName>'
            b'</response>'
        )

        result = parse(data)

        # The xsi:nil marker is a value marker, not data - only the real attribute remains.
        assert 'nil' not in result.middleName
        assert result.middleName['partial'] == 'true'
        assert str(result.middleName) == 'Ann'

# ################################################################################################################################
# ################################################################################################################################
