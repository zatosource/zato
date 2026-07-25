# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# lxml
from lxml import etree

# Zato
from zato.common.soap.common import Envelope_NS, FaultCode, Must_Understand_True_Values, Must_Understand_Value, NS, \
    Role_Next, SOAPException, SOAPFault, SOAPMustUnderstandException, SOAPVersion, Version_By_NS
from zato.common.soap.message import parse, serialize, SOAPMessage
from zato.common.util.xml_.core import element_text, qname, xml_parser

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.soap.message import bytes_by_content_id
    from zato.common.typing_ import any_, anylist, anyset, strlist, strnone
    any_ = any_
    anylist = anylist
    anyset = anyset
    bytes_by_content_id = bytes_by_content_id
    strlist = strlist
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

# The fault code local names of each SOAP version, keyed by the version-independent names. Only
# Sender and Receiver are spelled differently between the two - the other three required codes
# carry the same local name in both, which is why they repeat here rather than being special-cased.
_fault_code_names = {
    SOAPVersion.V11: {
        FaultCode.Sender:              'Client',
        FaultCode.Receiver:            'Server',
        FaultCode.VersionMismatch:     'VersionMismatch',
        FaultCode.MustUnderstand:      'MustUnderstand',
        FaultCode.DataEncodingUnknown: 'DataEncodingUnknown',
    },
    SOAPVersion.V12: {
        FaultCode.Sender:              'Sender',
        FaultCode.Receiver:            'Receiver',
        FaultCode.VersionMismatch:     'VersionMismatch',
        FaultCode.MustUnderstand:      'MustUnderstand',
        FaultCode.DataEncodingUnknown: 'DataEncodingUnknown',
    },
}


_security_nsmap = {
    'wsse': NS.WSSE,
    'wsu':  NS.WSU,
}

_xml_lang = '{http://www.w3.org/XML/1998/namespace}lang'

# The prefix a fault subcode's namespace is bound to, suffixed with the subcode's position in the
# chain so that a chain drawn from several namespaces binds each one separately.
_subcode_prefix = 'sub'

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

def find_header(envelope:'any_') -> 'any_':
    """ Returns the Header element of an envelope, or None when the message came without one.

    This is what every read of a received document uses. A header is optional on the wire, so its
    absence is a normal message rather than something to repair - and repairing it would mean
    modifying a document the caller is only inspecting, which then serialises back differently
    from what arrived and invalidates any signature over the envelope.
    """
    out = envelope.find(qname(Envelope_NS[get_version(envelope)], 'Header'))
    return out

# ################################################################################################################################

def get_header(envelope:'any_') -> 'any_':
    """ Returns the Header element of an envelope, creating it if there is none.

    Only callers that are about to add a header block use this - a caller that merely reads uses
    find_header, which leaves the document alone.
    """
    version = get_version(envelope)
    header = find_header(envelope)

    if header is None:
        header = etree.Element(qname(Envelope_NS[version], 'Header'))
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

def _is_must_understand(header_block:'any_', version:'str') -> 'bool':
    """ Says whether a header block is marked mustUnderstand.
    """
    namespace = Envelope_NS[version]
    value = header_block.get(qname(namespace, 'mustUnderstand'))

    if value is None:
        return False

    # SOAP 1.1 writes 1 and 0, 1.2 writes true and false, and 1.2 also accepts 1 and 0 - so both
    # spellings are read whatever the version, rather than only the one the version prefers.
    out = value.strip() in Must_Understand_True_Values
    return out

# ################################################################################################################################

def _is_targeted_at_this_node(header_block:'any_', version:'str') -> 'bool':
    """ Says whether a header block is addressed to this node.

    A block carrying no actor or role is addressed to whichever node receives it next, which is us.
    A block addressed to the "next" role is also ours. Anything else names a role we do not play,
    so the block travels through us untouched and its mustUnderstand does not apply to us.
    """
    namespace = Envelope_NS[version]

    if version == SOAPVersion.V11:
        target = header_block.get(qname(namespace, 'actor'))
    else:
        target = header_block.get(qname(namespace, 'role'))

    if target is None:
        return True

    out = target.strip() == Role_Next[version]
    return out

# ################################################################################################################################

def check_must_understand(envelope:'any_', understood_namespaces:'anyset') -> 'None':
    """ Raises SOAPMustUnderstandException when the message carries a mandatory header block this
    node does not understand.

    A SOAP node that emits mustUnderstand but never honours it inbound is not a conforming node:
    the whole point of the attribute is that the sender may rely on the receiver either processing
    the block or refusing the message, and silently ignoring it means a sender's security or
    routing requirement is dropped without anybody being told.

    Understanding is decided by namespace rather than by element name, because a node that
    implements a specification implements all of that specification's header blocks.
    """
    version = get_version(envelope)
    header = find_header(envelope)

    # A message without a header carries no mandatory blocks to begin with.
    if header is None:
        return

    not_understood = []

    for header_block in header:

        # Comments and processing instructions carry a callable tag rather than a string one.
        if not isinstance(header_block.tag, str):
            continue

        if not _is_must_understand(header_block, version):
            continue

        if not _is_targeted_at_this_node(header_block, version):
            continue

        block_namespace, _, _ = header_block.tag.rpartition('}')
        block_namespace = block_namespace[1:]

        if block_namespace not in understood_namespaces:
            not_understood.append(header_block.tag)

    if not_understood:
        raise SOAPMustUnderstandException(f'Mandatory header blocks not understood -> {not_understood}')

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
    envelope = etree.fromstring(data, xml_parser)

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

def _add_subcodes(fault_code:'any_', namespace:'str', subcodes:'strlist') -> 'None':
    """ Adds a chain of SOAP 1.2 Subcode elements under a Code, each one nested inside the previous.

    The subcodes arrive in Clark notation and leave as QNames, so each one needs its namespace bound
    to a prefix. The prefix is generated per position rather than taken from a fixed table, since a
    subcode may come from any specification and this module has no business knowing which.
    """
    parent = fault_code

    for position, subcode in enumerate(subcodes):

        subcode_namespace, _, local_name = subcode[1:].partition('}')
        prefix = f'{_subcode_prefix}{position}'

        subcode_element = etree.SubElement(parent, qname(namespace, 'Subcode'))

        # The prefix is declared on the Value element itself, which is where the QName it resolves
        # against lives - declaring it further up would work too but would leave the binding and
        # the text that depends on it in different places.
        value = etree.SubElement(subcode_element, qname(namespace, 'Value'), nsmap={prefix: subcode_namespace})
        value.text = f'{prefix}:{local_name}'

        # The next subcode refines this one, so it nests inside it.
        parent = subcode_element

# ################################################################################################################################

def build_fault(
    version:'str',
    code:'str',
    reason:'str',
    detail:'SOAPMessage | None'=None,
    subcodes:'strlist | None'=None,
) -> 'any_':
    """ Returns a new envelope carrying a fault of the given SOAP version. The code is one
    of the version-independent FaultCode names, mapped to what each fault dialect expects.

    Subcodes are given in Clark notation, outermost first. SOAP 1.1 has no equivalent construct, so
    a 1.1 fault drops them rather than inventing a place to put them.
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

        if subcodes:
            _add_subcodes(fault_code, namespace, subcodes)

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

def _resolve_code_qname(element:'any_', value:'str', envelope_namespace:'str') -> 'str':
    """ Returns the local name of the QName a fault code arrives as - Client, Sender and so on
    in the spelling the sending dialect uses.

    The prefix is resolved against the element's own namespace declarations rather than stripped.
    A sender is free to bind the envelope namespace to any prefix it likes, and it is equally free
    to put a code of its own in a namespace of its own - stripping the prefix reads `x:Sender` as
    the standard Sender code whatever `x` happens to be bound to. A code that does not resolve to
    the envelope namespace is returned as it arrived, prefix included, so the caller can see that
    it is somebody's own code rather than one of the standard ones.
    """
    value = value.strip()
    prefix, separator, local_name = value.rpartition(':')

    if separator:
        namespace = element.nsmap.get(prefix)
    else:
        # No prefix means the default namespace, which may or may not be declared.
        local_name = value
        namespace = element.nsmap.get(None)

    if namespace != envelope_namespace:
        return value

    out = local_name
    return out

# ################################################################################################################################

def _to_clark_notation(element:'any_', value:'str') -> 'str':
    """ Turns a QName read out of an element's text into Clark notation, resolving its prefix
    against that element's own namespace declarations.

    A subcode may come from any specification, so its prefix is whatever the sender chose. Keeping
    the sender's spelling would make a subcode impossible to compare against a known one, which is
    the only thing a caller ever wants to do with it. A prefix that resolves to nothing is left as
    it arrived, since guessing what the sender meant would be worse than saying it was unresolvable.
    """
    value = value.strip()
    prefix, separator, local_name = value.rpartition(':')

    if separator:
        namespace = element.nsmap.get(prefix)
    else:
        local_name = value
        namespace = element.nsmap.get(None)

    if namespace is None:
        return value

    out = f'{{{namespace}}}{local_name}'
    return out

# ################################################################################################################################

def _parse_fault_11(fault:'any_', namespace:'str') -> 'SOAPFault':
    """ Reads a SOAP 1.1 fault. faultcode and faultstring are mandatory, faultactor and detail
    are not, so a message missing a mandatory one is a malformed fault rather than an attribute
    error somewhere further down.
    """
    fault_code = fault.find('faultcode')

    if fault_code is None:
        raise SOAPException('Fault has no faultcode')

    fault_string = fault.find('faultstring')

    if fault_string is None:
        raise SOAPException('Fault has no faultstring')

    code = _resolve_code_qname(fault_code, element_text(fault_code), namespace)
    reason = element_text(fault_string)

    detail = SOAPMessage()
    detail_element = fault.find('detail')
    if detail_element is not None:
        detail = parse(detail_element)

    actor = None
    fault_actor = fault.find('faultactor')
    if fault_actor is not None:
        actor = element_text(fault_actor)

    out = SOAPFault(code, reason, detail, actor=actor)
    return out

# ################################################################################################################################

def _parse_fault_12(fault:'any_', namespace:'str') -> 'SOAPFault':
    """ Reads a SOAP 1.2 fault, including the Subcode chain, Node and Role that say what went
    wrong more precisely and which node it went wrong at.
    """
    fault_code = fault.find(qname(namespace, 'Code'))

    if fault_code is None:
        raise SOAPException('Fault has no Code')

    fault_value = fault_code.find(qname(namespace, 'Value'))

    if fault_value is None:
        raise SOAPException('Fault Code has no Value')

    code = _resolve_code_qname(fault_value, element_text(fault_value), namespace)

    fault_reason = fault.find(qname(namespace, 'Reason'))

    if fault_reason is None:
        raise SOAPException('Fault has no Reason')

    fault_text = fault_reason.find(qname(namespace, 'Text'))

    if fault_text is None:
        raise SOAPException('Fault Reason has no Text')

    reason = element_text(fault_text)

    # Subcodes nest, each one inside the previous, so the chain is walked rather than searched for -
    # the order matters, since each subcode refines the one it sits inside.
    subcodes = []
    subcode = fault_code.find(qname(namespace, 'Subcode'))

    while subcode is not None:
        subcode_value = subcode.find(qname(namespace, 'Value'))

        if subcode_value is None:
            break

        subcodes.append(_to_clark_notation(subcode_value, element_text(subcode_value)))
        subcode = subcode.find(qname(namespace, 'Subcode'))

    detail = SOAPMessage()
    detail_element = fault.find(qname(namespace, 'Detail'))
    if detail_element is not None:
        detail = parse(detail_element)

    node = None
    node_element = fault.find(qname(namespace, 'Node'))
    if node_element is not None:
        node = element_text(node_element)

    role = None
    role_element = fault.find(qname(namespace, 'Role'))
    if role_element is not None:
        role = element_text(role_element)

    out = SOAPFault(code, reason, detail, subcodes=subcodes, node=node, role=role)
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

    if version == SOAPVersion.V11:
        out = _parse_fault_11(fault, namespace)
    else:
        out = _parse_fault_12(fault, namespace)

    return out

# ################################################################################################################################

def raise_for_fault(envelope:'any_') -> 'None':
    """ Raises SOAPFault if the envelope carries a fault, otherwise does nothing.
    """
    if fault := parse_fault(envelope):
        raise fault

# ################################################################################################################################
# ################################################################################################################################
