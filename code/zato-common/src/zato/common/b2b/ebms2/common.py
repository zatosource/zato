# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.b2b.common.exceptions import B2BException, B2BProtocolException, B2BSecurityException
from zato.common.soap.common import NS as SOAPNS

# ################################################################################################################################
# ################################################################################################################################

class NS:
    """ The XML namespaces of ebMS 2.0 messages and CPP/A 2.0 documents.
    """
    EB    = SOAPNS.EBXML2
    CPA   = 'http://www.oasis-open.org/committees/ebxml-cppa/schema/cpp-cpa-2_0.xsd'
    SOAP  = SOAPNS.SOAP11
    DS    = SOAPNS.DS
    XLINK = SOAPNS.XLINK
    XML   = 'http://www.w3.org/XML/1998/namespace'

    # The business signal documents of ebBP 2.0.
    EBBP_Signals = 'http://docs.oasis-open.org/ebxml-bp/ebbp-signals-2.0'

# ################################################################################################################################
# ################################################################################################################################

# The value of eb:version on every header and body extension element.
Version = '2.0'

# The SOAPAction HTTP header value every ebMS 2.0 message is sent with.
SOAP_Action_Header = 'SOAPAction'
SOAP_Action_Value = '"ebXML"'

# The Content-Type of the SOAP part, and the type parameter of the multipart/related package.
Root_Content_Type = 'text/xml; charset="UTF-8"'
Root_Media_Type = 'text/xml'
Multipart_Media_Type = 'multipart/related'

# The default code context of eb:Error.
Error_Code_Context = 'urn:oasis:names:tc:ebxml-msg:service:errors'

# The highest sequence number of eb:MessageOrder, after which the numbering restarts from zero.
Max_Sequence_Number = 99999999

# The language of the eb:Description elements this implementation writes.
Description_Language = 'en'

# The protocol name message identities are recorded under in a message store.
Protocol_Name = 'ebms2'

# ################################################################################################################################
# ################################################################################################################################

class Default:
    """ The values used when an agreement does not specify them.
    """
    # How long a received MessageId is remembered for duplicate elimination without a PersistDuration.
    Persist_Duration_Seconds = 86400

    # How long a message waits for its acknowledgment before it is sent again without a RetryInterval.
    Retry_Interval_Seconds = 30

    # The algorithms of a signature that an agreement requires without naming them.
    Signature_Algorithm = 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256'
    Digest_Algorithm    = 'http://www.w3.org/2001/04/xmlenc#sha256'

    # The domain part of the MessageId values this implementation generates.
    Message_Id_Domain = 'ebms2.zato'

    # Whether a message requests an acknowledgment and duplicate elimination when the agreement leaves it
    # to each message and the caller does not decide - a message that is retried needs both.
    Ack_Requested_Per_Message         = True
    Ack_Signature_Requested_Per_Message = False
    Duplicate_Elimination_Per_Message = True

# ################################################################################################################################
# ################################################################################################################################

class Actor:
    """ The SOAP actor URIs ebMS 2.0 targets header elements at.
    """
    Next_MSH     = 'urn:oasis:names:tc:ebxml-msg:actor:nextMSH'
    To_Party_MSH = 'urn:oasis:names:tc:ebxml-msg:actor:toPartyMSH'
    SOAP_Next    = 'http://schemas.xmlsoap.org/soap/actor/next'

# ################################################################################################################################
# ################################################################################################################################

class MSHService:
    """ The service and the actions of the messages that message service handlers exchange between themselves.
    """
    Service = 'urn:oasis:names:tc:ebxml-msg:service'

    Acknowledgment = 'Acknowledgment'
    Message_Error  = 'MessageError'
    Ping           = 'Ping'
    Pong           = 'Pong'
    Status_Request  = 'StatusRequest'
    Status_Response = 'StatusResponse'

# ################################################################################################################################
# ################################################################################################################################

class ErrorCode:
    """ The error codes of eb:Error.
    """
    Value_Not_Recognized = 'ValueNotRecognized'
    Not_Supported        = 'NotSupported'
    Inconsistent         = 'Inconsistent'
    Other_XML            = 'OtherXml'
    Delivery_Failure     = 'DeliveryFailure'
    Time_To_Live_Expired = 'TimeToLiveExpired'
    Security_Failure     = 'SecurityFailure'
    MIME_Problem         = 'MimeProblem'
    Unknown              = 'Unknown'

# ################################################################################################################################

class Severity:
    """ The severities of eb:Error, in ascending order.
    """
    Warning = 'Warning'
    Error   = 'Error'

# ################################################################################################################################

class MessageStatus:
    """ The values of eb:messageStatus in eb:StatusResponse.
    """
    Unauthorized   = 'UnAuthorized'
    Not_Recognized = 'NotRecognized'
    Received       = 'Received'
    Processed      = 'Processed'
    Forwarded      = 'Forwarded'

# ################################################################################################################################

class SequenceStatus:
    """ The values of eb:status on eb:SequenceNumber.
    """
    Reset    = 'Reset'
    Continue = 'Continue'

# ################################################################################################################################
# ################################################################################################################################

class SyncReplyMode:
    """ The values of syncReplyMode in a delivery channel.
    """
    No_Reply             = 'none'
    MSH_Signals_Only     = 'mshSignalsOnly'
    Signals_Only         = 'signalsOnly'
    Response_Only        = 'responseOnly'
    Signals_And_Response = 'signalsAndResponse'

# ################################################################################################################################

class PerMessage:
    """ The values of ackRequested, ackSignatureRequested and duplicateElimination in a delivery channel.
    """
    Always      = 'always'
    Never       = 'never'
    Per_Message = 'perMessage'

# ################################################################################################################################

class MessageOrderSemantics:
    """ The values of MessageOrderSemantics in a reliable messaging element.
    """
    Guaranteed     = 'Guaranteed'
    Not_Guaranteed = 'NotGuaranteed'

# ################################################################################################################################

class Direction:
    """ Which side of an exchange the local party is on.
    """
    Send    = 'send'
    Receive = 'receive'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PartyId:
    """ One identifier of a party, with the optional type that says which naming scheme it belongs to.
    """
    value:   str
    id_type: str = ''

    def matches(self, other:'PartyId') -> 'bool':
        """ Says whether two identifiers name the same party - the same value under the same type.
        """
        if self.value == other.value:
            out = self.id_type == other.id_type
        else:
            out = False

        return out

# ################################################################################################################################

party_id_list = list[PartyId]

# ################################################################################################################################

def new_party_id(value:'str', id_type:'str'='') -> 'PartyId':
    """ Returns a party identifier with the given value and type.
    """
    out = PartyId()
    out.value = value
    out.id_type = id_type

    return out

# ################################################################################################################################
# ################################################################################################################################

class EbMS2Exception(B2BProtocolException):
    """ Raised when a message violates the ebMS 2.0 specification or the agreement it is exchanged under.
    The error code is one of ErrorCode and the location names the offending element.
    """

# ################################################################################################################################

class EbMS2SecurityException(B2BSecurityException):
    """ Raised when a signature or a certificate of an ebMS 2.0 message fails verification.
    """
    def __init__(self, detail:'str', location:'str'='') -> 'None':
        super().__init__(ErrorCode.Security_Failure, detail, location)

# ################################################################################################################################

class CPAException(B2BException):
    """ Raised when a CPP/A document is invalid or uses a construct this implementation does not support.
    """
    def __init__(self, element:'str', reason:'str') -> 'None':
        super().__init__(f'{element} -> {reason}')
        self.element = element
        self.reason = reason

# ################################################################################################################################

class CPAUnsupportedException(CPAException):
    """ Raised when a CPP/A document uses a construct that is valid but not supported.
    """

# ################################################################################################################################
# ################################################################################################################################
