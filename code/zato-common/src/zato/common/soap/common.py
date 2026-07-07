# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.util.xml_.constants import NS as CommonNS

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.soap.message import SOAPMessage
    SOAPMessage = SOAPMessage

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

# ################################################################################################################################
# ################################################################################################################################

class FaultCode:
    """ Version-independent fault code names - they map to soap:Client and soap:Server in 1.1
    and to soap:Sender and soap:Receiver in 1.2.
    """
    Sender   = 'Sender'
    Receiver = 'Receiver'

# ################################################################################################################################
# ################################################################################################################################

class SOAPException(Exception):
    """ Base class for all SOAP-related exceptions.
    """

# ################################################################################################################################
# ################################################################################################################################

class SOAPSecurityException(SOAPException):
    """ Raised when WS-Security processing of an incoming message fails.
    """

# ################################################################################################################################
# ################################################################################################################################

class SOAPFault(SOAPException):
    """ A SOAP fault of either version, surfaced as one exception type -
    code and reason are strings and detail is a dot-accessed SOAPMessage.
    """
    def __init__(self, code:'str', reason:'str', detail:'SOAPMessage') -> 'None':
        super().__init__(f'{code} {reason}')
        self.code = code
        self.reason = reason
        self.detail = detail

# ################################################################################################################################
# ################################################################################################################################
