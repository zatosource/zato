# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# lxml
from lxml import etree

# Zato
from zato.common.soap.common import Envelope_NS, FaultCode, Must_Understand_Value, NS, SOAPException, SOAPFault, \
    SOAPVersion, Version_By_NS
from zato.common.soap.message import parse, serialize, SOAPMessage
from zato.common.util.xml_.core import qname

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.soap.message import bytes_by_content_id
    from zato.common.typing_ import any_, anylist, strnone
    any_ = any_
    anylist = anylist
    bytes_by_content_id = bytes_by_content_id
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

# The fault code local names of each SOAP version, keyed by the version-independent names.
_fault_code_names = {
    SOAPVersion.V11: {
        FaultCode.Sender:   'Client',
        FaultCode.Receiver: 'Server',
    },
    SOAPVersion.V12: {
        FaultCode.Sender:   'Sender',
        FaultCode.Receiver: 'Receiver',
    },
}

_security_nsmap = {
    'wsse': NS.WSSE,
    'wsu':  NS.WSU,
}

_xml_lang = '{http://www.w3.org/XML/1998/namespace}lang'

# ################################################################################################################################
# ################################################################################################################################

def build_envelope(version:'str') -> 'any_':
    """ Returns a new envelope of the given SOAP version with an empty header and an empty body.
    """
    namespace = Envelope_NS[version]
    nsmap = {'soap': namespace}

    envelope = etree.Element(qname(namespace, 'Envelope'), nsmap=nsmap)
    _ = etree.SubElement(envelope, qname(namespace, 'Header'))
    _ = etree.SubElement(envelope, qname(namespace, 'Body'))

    return envelope

# ################################################################################################################################

def get_version(envelope:'any_') -> 'str':
    """ Returns the SOAP version of an envelope, derived from its root namespace.
    """
    namespace, _, local_name = envelope.tag.rpartition('}')
    namespace = namespace[1:]

    if local_name != 'Envelope':
        raise SOAPException(f'Not a SOAP envelope, root element is `{local_name}`')

    if namespace not in Version_By_NS:
        raise SOAPException(f'Not a SOAP envelope, unknown namespace `{namespace}`')

    out = Version_By_NS[namespace]
    return out

# ################################################################################################################################

def get_header(envelope:'any_') -> 'any_':
    """ Returns the Header element of an envelope, creating it if the message came without one.
    """
    version = get_version(envelope)
    namespace = Envelope_NS[version]

    header = envelope.find(qname(namespace, 'Header'))

    # A header is optional on the wire, so an envelope may genuinely lack one.
    if header is None:
        header = etree.Element(qname(namespace, 'Header'))
        envelope.insert(0, header)

    return header

# ################################################################################################################################

def get_body(envelope:'any_') -> 'any_':
    """ Returns the Body element of an envelope.
    """
    version = get_version(envelope)
    namespace = Envelope_NS[version]

    body = envelope.find(qname(namespace, 'Body'))

    if body is None:
        raise SOAPException('Envelope has no Body element')

    return body

# ################################################################################################################################

def set_must_understand(element:'any_', version:'str') -> 'None':
    """ Marks a header block with the mustUnderstand attribute in the form the SOAP version requires.
    """
    namespace = Envelope_NS[version]
    element.set(qname(namespace, 'mustUnderstand'), Must_Understand_Value[version])

# ################################################################################################################################

def get_security_header(envelope:'any_') -> 'any_':
    """ Returns the wsse:Security header block of an envelope, creating it if needed.
    """
    version = get_version(envelope)
    header = get_header(envelope)

    security = header.find(qname(NS.WSSE, 'Security'))

    if security is None:
        security = etree.SubElement(header, qname(NS.WSSE, 'Security'), nsmap=_security_nsmap)
        set_must_understand(security, version)

    return security

# ################################################################################################################################
# ################################################################################################################################

def attach_body(envelope:'any_', message:'SOAPMessage', tag:'str', xop_parts:'any_'=None) -> 'any_':
    """ Serializes a message under the given wrapper tag and places it in the envelope's body.
    Returns the serialized body child element.
    """
    body = get_body(envelope)

    element = serialize(message, tag, xop_parts=xop_parts)
    body.append(element)

    return element

# ################################################################################################################################

def parse_envelope(data:'bytes') -> 'any_':
    """ Parses incoming bytes into an envelope element, checking that it really is one.
    """
    envelope = etree.fromstring(data)

    # This raises SOAPException when the root element is not a SOAP envelope.
    _ = get_version(envelope)

    return envelope

# ################################################################################################################################

def parse_body(envelope:'any_', parts:'bytes_by_content_id | None'=None) -> 'SOAPMessage':
    """ Returns the body of an envelope as a dot-accessed message - its children
    are the body's child elements, accessed by their local names.
    """
    body = get_body(envelope)

    out = parse(body, parts)
    return out

# ################################################################################################################################

def to_bytes(envelope:'any_') -> 'bytes':
    """ Serializes an envelope to wire bytes with an XML declaration.
    """
    out = etree.tostring(envelope, xml_declaration=True, encoding='UTF-8')
    return out

# ################################################################################################################################
# ################################################################################################################################

def build_fault(version:'str', code:'str', reason:'str', detail:'SOAPMessage | None'=None) -> 'any_':
    """ Returns a new envelope carrying a fault of the given SOAP version. The code is one
    of the version-independent FaultCode names, mapped to what each fault dialect expects.
    """
    namespace = Envelope_NS[version]
    code_name = _fault_code_names[version][code]

    envelope = build_envelope(version)
    body = get_body(envelope)

    fault = etree.SubElement(body, qname(namespace, 'Fault'))

    # The 1.1 dialect uses unqualified lowercase elements with a QName code ..
    if version == SOAPVersion.V11:

        fault_code = etree.SubElement(fault, 'faultcode')
        fault_code.text = f'soap:{code_name}'

        fault_string = etree.SubElement(fault, 'faultstring')
        fault_string.text = reason

        if detail is not None:
            detail_element = serialize(detail, 'detail')
            fault.append(detail_element)

    # .. and the 1.2 one uses namespace-qualified Code/Value and Reason/Text.
    else:

        fault_code = etree.SubElement(fault, qname(namespace, 'Code'))
        fault_value = etree.SubElement(fault_code, qname(namespace, 'Value'))
        fault_value.text = f'soap:{code_name}'

        fault_reason = etree.SubElement(fault, qname(namespace, 'Reason'))
        fault_text = etree.SubElement(fault_reason, qname(namespace, 'Text'))
        fault_text.set(_xml_lang, 'en')
        fault_text.text = reason

        if detail is not None:

            # The children of the detail message move into the namespace-qualified Detail element.
            detail_element = etree.SubElement(fault, qname(namespace, 'Detail'))
            serialized = serialize(detail, 'detail')

            for child in serialized:
                detail_element.append(child)

    return envelope

# ################################################################################################################################

def _strip_qname_prefix(value:'str') -> 'str':
    """ Strips the namespace prefix from a QName in text content, e.g. soap:Client becomes Client.
    """
    _, _, out = value.rpartition(':')
    return out

# ################################################################################################################################

def parse_fault(envelope:'any_') -> 'SOAPFault | None':
    """ Returns the fault an envelope carries as a SOAPFault, or None when there is no fault.
    """
    version = get_version(envelope)
    namespace = Envelope_NS[version]
    body = get_body(envelope)

    fault = body.find(qname(namespace, 'Fault'))

    if fault is None:
        return None

    detail = SOAPMessage()

    # The 1.1 dialect ..
    if version == SOAPVersion.V11:

        fault_code = fault.find('faultcode')
        code = _strip_qname_prefix(fault_code.text)

        fault_string = fault.find('faultstring')
        reason = fault_string.text

        detail_element = fault.find('detail')
        if detail_element is not None:
            detail = parse(detail_element)

    # .. and the 1.2 one.
    else:

        fault_code = fault.find(qname(namespace, 'Code'))
        fault_value = fault_code.find(qname(namespace, 'Value'))
        code = _strip_qname_prefix(fault_value.text)

        fault_reason = fault.find(qname(namespace, 'Reason'))
        fault_text = fault_reason.find(qname(namespace, 'Text'))
        reason = fault_text.text

        detail_element = fault.find(qname(namespace, 'Detail'))
        if detail_element is not None:
            detail = parse(detail_element)

    out = SOAPFault(code, reason, detail)
    return out

# ################################################################################################################################

def raise_for_fault(envelope:'any_') -> 'None':
    """ Raises SOAPFault if the envelope carries a fault, otherwise does nothing.
    """
    if fault := parse_fault(envelope):
        raise fault

# ################################################################################################################################
# ################################################################################################################################
