# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class AS2Error:
    """ Disposition modifiers from RFC 4130 section 7.4.3 and RFC 5402 that this implementation raises or recognizes.
    An MDN carries one of these after "processed/error:" or "failed/failure:" to say what went wrong.
    """
    Decryption_Failed             = 'decryption-failed'
    Authentication_Failed         = 'authentication-failed'
    Integrity_Check_Failed        = 'integrity-check-failed'
    Insufficient_Message_Security = 'insufficient-message-security'
    Unexpected_Processing_Error   = 'unexpected-processing-error'
    Decompression_Failed          = 'decompression-failed'

    # The additional registry modifiers of the AS2 specification modernization draft,
    # recognized on input as known values.
    Duplicate_Filename            = 'duplicate-filename'
    Illegal_Filename              = 'illegal-filename'
    Invalid_Message_ID            = 'invalid-message-id'
    Unknown_Trading_Relationship  = 'unknown-trading-relationship'
    Unknown_Trading_Partner       = 'unknown-trading-partner'

# ################################################################################################################################
# ################################################################################################################################

class Failure:
    """ Failure descriptions for "failed/Failure:" dispositions, which RFC 4130 reserves
    for problems with the MDN request itself rather than with content processing.
    """
    Unsupported_Format         = 'unsupported format'
    Unsupported_MIC_Algorithms = 'unsupported MIC-algorithms'

# ################################################################################################################################
# ################################################################################################################################

class DigestAlgorithm:
    """ Digest algorithms for signatures and MIC values, in their RFC 5751 spelling.
    SHA-1 exists only for legacy partners that cannot do better.
    """
    SHA1   = 'sha-1'
    SHA256 = 'sha-256'
    SHA384 = 'sha-384'
    SHA512 = 'sha-512'

# ################################################################################################################################
# ################################################################################################################################

class EncryptionAlgorithm:
    """ Content encryption algorithms for outgoing messages. The CBC ones are the interop baseline,
    the GCM ones use CMS AuthEnvelopedData and are opt-in per partner, never the default.
    """
    AES_128_CBC = 'aes-128-cbc'
    AES_256_CBC = 'aes-256-cbc'
    AES_128_GCM = 'aes-128-gcm'
    AES_256_GCM = 'aes-256-gcm'

# ################################################################################################################################
# ################################################################################################################################

class MDNMode:
    """ How the receiver is to deliver its MDN - not at all, on the HTTP response,
    or asynchronously to a separate URL.
    """
    None_ = 'none'
    Sync  = 'sync'
    Async = 'async'

# ################################################################################################################################
# ################################################################################################################################

class TransferMode:
    """ How the HTTP request body is framed - with a Content-Length header, with chunked
    transfer encoding, or with chunking only above a configurable size threshold.
    """
    Content_Length = 'content-length'
    Chunked        = 'chunked'
    Threshold      = 'threshold'

# ################################################################################################################################
# ################################################################################################################################

class DeliveryKind:
    """ The reliability taxonomy of repeated delivery attempts - a retry reuses the same attempt
    after a transport error, a resend carries the same content and the same Message-ID because
    no MDN arrived, and a resubmit is an operator action with a new Message-ID.
    """
    Retry    = 'retry'
    Resend   = 'resend'
    Resubmit = 'resubmit'

# ################################################################################################################################
# ################################################################################################################################

class Default:
    """ Default algorithm and configuration choices for outgoing messages.
    """
    Digest_Algorithm     = DigestAlgorithm.SHA256
    Encryption_Algorithm = EncryptionAlgorithm.AES_256_CBC

    # The AS2-Version header value of outgoing messages - pinnable per partner for legacy peers,
    # while inbound never rejects on version and an absent version means 1.0.
    AS2_Version = '1.2'

    # The Content-Type of outgoing payloads unless the partnership names another one.
    Content_Type = 'application/edi-x12'

    # The Subject header of outgoing messages.
    Subject = 'AS2 message'

    # How long outbound HTTP requests may take, in seconds.
    HTTP_Timeout_Seconds = 60

    # Above this many bytes the threshold transfer mode switches to chunked framing.
    Chunked_Threshold_Bytes = 10 * 1024 * 1024

    # What every outgoing message advertises in its EDIINT-Features header - real capabilities
    # only, informational per its RFC, and inbound values never drive behavior.
    EDIINT_Features = 'multiple-attachments, AS2-Reliability'

# ################################################################################################################################
# ################################################################################################################################

class AS2Exception(Exception):
    """ Base class for all AS2-related exceptions.
    """

# ################################################################################################################################
# ################################################################################################################################

class AS2ProtocolException(AS2Exception):
    """ Raised when an incoming message violates the AS2 rules. Carries the RFC 4130 disposition modifier
    so that the inbound pipeline can produce the matching MDN disposition.
    """
    def __init__(self, modifier:'str', detail:'str') -> 'None':
        super().__init__(f'{modifier} {detail}')
        self.modifier = modifier
        self.detail = detail

# ################################################################################################################################
# ################################################################################################################################

class AS2SecurityException(AS2ProtocolException):
    """ Raised when signature verification, decryption or certificate validation fails.
    """

# ################################################################################################################################
# ################################################################################################################################
