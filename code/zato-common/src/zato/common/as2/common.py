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

# ################################################################################################################################
# ################################################################################################################################

class Failure:
    """ Failure descriptions for "failed/Failure:" dispositions, which RFC 4130 reserves
    for problems with the MDN request itself rather than with content processing.
    """
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

class Default:
    """ Default algorithm choices for outgoing messages.
    """
    Digest_Algorithm     = DigestAlgorithm.SHA256
    Encryption_Algorithm = EncryptionAlgorithm.AES_256_CBC

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
