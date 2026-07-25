# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.util.xml_.constants import NS as CommonNS
from zato.common.util.xml_.core import XMLSecurityUnsupportedAlgorithm

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.soap.message import SOAPMessage
    from zato.common.typing_ import strlist, strnone
    from zato.common.util.xml_.core import XMLSecurityException
    SOAPMessage = SOAPMessage
    strlist = strlist
    strnone = strnone
    XMLSecurityException = XMLSecurityException

# ################################################################################################################################
# ################################################################################################################################

class NS(CommonNS):
    """ XML namespaces used across SOAP messages - the shared ones plus ebXML Message Service 2.0.
    """
    EBXML2 = 'http://www.oasis-open.org/committees/ebxml-msg/schema/msg-header-2_0.xsd'

# ################################################################################################################################
# ################################################################################################################################

class SOAPVersion:
    """ The two SOAP versions in use.
    """
    V11 = '1.1'
    V12 = '1.2'

# ################################################################################################################################
# ################################################################################################################################

# The envelope namespace of each SOAP version.
Envelope_NS = {
    SOAPVersion.V11: NS.SOAP11,
    SOAPVersion.V12: NS.SOAP12,
}

# The reverse map - version by envelope namespace.
Version_By_NS = {
    NS.SOAP11: SOAPVersion.V11,
    NS.SOAP12: SOAPVersion.V12,
}

# The Content-Type header of a bare envelope of each SOAP version.
Content_Type = {
    SOAPVersion.V11: 'text/xml; charset=utf-8',
    SOAPVersion.V12: 'application/soap+xml; charset=utf-8',
}

# The value of the mustUnderstand attribute of each SOAP version.
Must_Understand_Value = {
    SOAPVersion.V11: '1',
    SOAPVersion.V12: 'true',
}

# What an inbound mustUnderstand attribute may say to mean yes. 1.1 defines 1 and 0, 1.2 defines
# true and false and also accepts 1 and 0, so both spellings are read whatever the version - a
# peer that writes the other version's spelling still means what it says.
Must_Understand_True_Values = {'1', 'true'}

# The role or actor URI meaning "whichever node receives this next", i.e. us. A header block that
# names no target at all also means us - only a block naming some other role travels through.
Role_Next = {
    SOAPVersion.V11: 'http://schemas.xmlsoap.org/soap/actor/next',
    SOAPVersion.V12: 'http://www.w3.org/2003/05/soap-envelope/role/next',
}

# The namespaces of the header blocks this node implements, so a mandatory block in any of them is
# one it understands. Understanding is decided per namespace rather than per element, since
# implementing a specification means implementing its header blocks.
Understood_Header_Namespaces = {
    NS.WSA,
    NS.WSSE,
    NS.WSSE11,
    NS.WSU,
}

# The SOAP version each media type belongs to, so the version a message declares on the transport
# can be compared with the one its envelope namespace declares. The two disagreeing is a
# VersionMismatch: text/xml is 1.1's own media type and application/soap+xml is 1.2's, and neither
# version's binding allows the other's.
Version_By_Media_Type = {
    'text/xml':               SOAPVersion.V11,
    'application/soap+xml':   SOAPVersion.V12,
}

# The Content-Type parameter SOAP 1.2 carries its action in. 1.1 uses a header of its own instead.
Action_Parameter = 'action'

# The header SOAP 1.1 carries its action in. 1.2 uses a Content-Type parameter instead.
SOAP_Action_Header = 'SOAPAction'

# ################################################################################################################################
# ################################################################################################################################

class FaultCode:
    """ Version-independent fault code names. Sender and Receiver map to soap:Client and
    soap:Server in 1.1 and to soap:Sender and soap:Receiver in 1.2. The other three are required
    codes in both versions, spelled the same way in each.
    """
    Sender   = 'Sender'
    Receiver = 'Receiver'

    # The envelope's namespace is not one this node speaks.
    VersionMismatch = 'VersionMismatch'

    # A header marked mustUnderstand and targeted at this node is one it does not recognise.
    MustUnderstand = 'MustUnderstand'

    # The message uses a data encoding this node does not support.
    DataEncodingUnknown = 'DataEncodingUnknown'

# ################################################################################################################################

# The HTTP status each fault code leaves with.
#
# SOAP 1.1 puts every fault on 500 - the specification says so outright, and a 1.1 client reads
# any other status as a transport failure rather than a fault it should parse. SOAP 1.2 changes
# this: a Sender fault means the request was at fault, so it leaves with 400, and everything else
# stays on 500. MustUnderstand and VersionMismatch are the caller's fault too, but the 1.2
# specification names 500 for them, so they keep it.
Fault_HTTP_Status = {
    SOAPVersion.V11: {
        FaultCode.Sender:              500,
        FaultCode.Receiver:            500,
        FaultCode.VersionMismatch:     500,
        FaultCode.MustUnderstand:      500,
        FaultCode.DataEncodingUnknown: 500,
    },
    SOAPVersion.V12: {
        FaultCode.Sender:              400,
        FaultCode.Receiver:            500,
        FaultCode.VersionMismatch:     500,
        FaultCode.MustUnderstand:      500,
        FaultCode.DataEncodingUnknown: 500,
    },
}

# ################################################################################################################################
# ################################################################################################################################

class SOAPException(Exception):
    """ Base class for all SOAP-related exceptions.
    """

# ################################################################################################################################
# ################################################################################################################################

class SOAPMustUnderstandException(SOAPException):
    """ Raised when an incoming message carries a header block marked mustUnderstand, targeted at
    this node, that this node does not implement. It surfaces as a MustUnderstand fault.
    """

# ################################################################################################################################
# ################################################################################################################################

class SOAPVersionMismatchException(SOAPException):
    """ Raised when the SOAP version a message declares on the transport is not the one its envelope
    namespace declares. It surfaces as a VersionMismatch fault, which is the code both versions
    define for exactly this and which tells the sender to retry under the other version.
    """

# ################################################################################################################################
# ################################################################################################################################

class SOAPAddressingException(SOAPException):
    """ Raised when the WS-Addressing headers of an incoming message do not hold up - a required
    block is missing, or one is present more times than the specification allows.

    It carries the fault subcodes WS-Addressing defines for the case, in Clark notation and
    outermost first, because a bare Sender fault does not tell the sender which of its headers to
    correct and the subcode is the whole point of the specification defining them.
    """
    def __init__(self, reason:'str', subcodes:'strlist') -> 'None':
        super().__init__(reason)
        self.reason = reason
        self.subcodes = subcodes

# ################################################################################################################################
# ################################################################################################################################

class SOAPSecurityException(SOAPException):
    """ Raised when WS-Security processing of an incoming message fails.
    """

# ################################################################################################################################
# ################################################################################################################################

class SOAPSecurityUnsupportedAlgorithm(SOAPSecurityException):
    """ Raised when a message uses an algorithm this implementation does not support. This is a
    different thing from a message that fails to verify - the sender's policy and ours disagree,
    rather than the sender being an impostor - and collapsing the two loses the distinction the
    shared primitives raise XMLSecurityUnsupportedAlgorithm to make.
    """

# ################################################################################################################################
# ################################################################################################################################

def as_soap_security_exception(e:'XMLSecurityException') -> 'SOAPSecurityException':
    """ Translates a failure of the shared XML security primitives into the SOAP-level exception
    that says the same thing, keeping the unsupported-algorithm case apart from a plain failure.
    Callers raise the result `from e` so the original cause stays attached.
    """
    if isinstance(e, XMLSecurityUnsupportedAlgorithm):
        out = SOAPSecurityUnsupportedAlgorithm(e.args[0])
    else:
        out = SOAPSecurityException(e.args[0])

    return out

# ################################################################################################################################
# ################################################################################################################################

class SOAPFault(SOAPException):
    """ A SOAP fault of either version, surfaced as one exception type - code and reason are
    strings and detail is a dot-accessed SOAPMessage. The remaining fields say who reported the
    fault and, in 1.2, what it was more precisely: they are what a caller needs to tell a fault
    raised by the endpoint apart from one raised by an intermediary on the way to it.
    """
    def __init__(
        self,
        code:'str',
        reason:'str',
        detail:'SOAPMessage',
        subcodes:'strlist | None'=None,
        actor:'strnone'=None,
        node:'strnone'=None,
        role:'strnone'=None,
        ) -> 'None':
        super().__init__(f'{code} {reason}')
        self.code = code
        self.reason = reason
        self.detail = detail

        # The 1.2 Subcode chain, outermost first - each one refines the one before it.
        if subcodes is None:
            subcodes = []
        self.subcodes = subcodes

        # The 1.1 faultactor - the URI of whatever reported the fault.
        self.actor = actor

        # The 1.2 equivalents: Node is the URI of the node that reported the fault and Role
        # is the role that node was acting in.
        self.node = node
        self.role = role

# ################################################################################################################################
# ################################################################################################################################
