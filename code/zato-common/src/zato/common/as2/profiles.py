# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.as2.common import DigestAlgorithm, EncryptionAlgorithm, MDNMode
from zato.common.as2.partnership import new_partnership, Partnership

# ################################################################################################################################
# ################################################################################################################################

# The AS2 identifiers the FDA Electronic Submissions Gateway routes on - the production one
# and its test counterpart, carried in AS2-To or in the X-Cyclone-True-Receiver header.
FDA_Production_Identifier = 'ZZFDA'
FDA_Test_Identifier       = 'ZZFDATST'

# The Content-Type of EPCIS XML payloads, the document format the US pharmaceutical
# supply chain exchanges under DSCSA.
EPCIS_Content_Type = 'application/xml'

# ################################################################################################################################
# ################################################################################################################################

def new_default_partnership() -> 'Partnership':
    """ A partnership preset for the standard retail mandate - signing with SHA-256,
    AES-128-CBC encryption, compression and a synchronous signed MDN.
    """

    # Our response to produce
    out = new_partnership()

    # These are already the defaults - restated here so that the preset
    # stays correct even if the defaults ever change.
    out.sign = True
    out.sign_algorithm = DigestAlgorithm.SHA256
    out.encrypt = True
    out.mdn_mode = MDNMode.Sync
    out.mdn_signed = True
    out.mdn_mic_algorithms = [DigestAlgorithm.SHA256]

    out.encryption_algorithm = EncryptionAlgorithm.AES_128_CBC
    out.compress = True

    return out

# ################################################################################################################################

def new_walmart_partnership() -> 'Partnership':
    """ A partnership preset for Walmart suppliers - direct AS2 with no VAN in between,
    SHA-256 signing only because Walmart's GEM team accepts nothing else, and a synchronous
    signed SHA-256 MDN, never an asynchronous one. Walmart accepts self-signed certificates
    with RSA keys of 2048 bits or more, compression is optional and stays off here.
    """

    # Our response to produce
    out = new_partnership()

    out.sign = True
    out.sign_algorithm = DigestAlgorithm.SHA256
    out.encrypt = True
    out.encryption_algorithm = EncryptionAlgorithm.AES_128_CBC
    out.compress = False

    out.mdn_mode = MDNMode.Sync
    out.mdn_signed = True
    out.mdn_mic_algorithms = [DigestAlgorithm.SHA256]

    return out

# ################################################################################################################################

def new_sha1_3des_partnership() -> 'Partnership':
    """ A partnership preset for old partners that require SHA-1 and 3DES and cannot
    do better - SHA-1 signatures, 3DES-CBC encryption in both directions
    and a SHA-1 MDN MIC.
    """

    # Our response to produce
    out = new_partnership()

    out.sign = True
    out.sign_algorithm = DigestAlgorithm.SHA1
    out.encrypt = True
    out.encryption_algorithm = EncryptionAlgorithm.DES_EDE3_CBC

    out.mdn_mode = MDNMode.Sync
    out.mdn_signed = True
    out.mdn_mic_algorithms = [DigestAlgorithm.SHA1]

    return out

# ################################################################################################################################

def new_fda_esg_partnership() -> 'Partnership':
    """ A partnership preset for the FDA Electronic Submissions Gateway - HTTPS on port 4080,
    an asynchronous signed MDN, signing always on and encryption to the FDA certificate
    with AES-CBC, never GCM, which the gateway rejects. Keys are RSA of 2048 or 3072 bits.

    The caller still sets: the endpoint URL, our own identifier and the URL
    the gateway is to deliver its asynchronous MDNs to.
    """

    # Our response to produce
    out = new_partnership()

    out.as2_to = FDA_Production_Identifier

    out.sign = True
    out.sign_algorithm = DigestAlgorithm.SHA256
    out.encrypt = True
    out.encryption_algorithm = EncryptionAlgorithm.AES_256_CBC

    out.mdn_mode = MDNMode.Async
    out.mdn_signed = True
    out.mdn_mic_algorithms = [DigestAlgorithm.SHA256]

    return out

# ################################################################################################################################

def new_dscsa_partnership() -> 'Partnership':
    """ A partnership preset for DSCSA exchanges in the US pharmaceutical supply chain -
    EPCIS XML payloads with signing, encryption and a synchronous signed MDN,
    the non-repudiation posture the program's traceability requirements call for.
    """

    # Our response to produce
    out = new_partnership()

    out.content_type = EPCIS_Content_Type

    out.sign = True
    out.sign_algorithm = DigestAlgorithm.SHA256
    out.encrypt = True
    out.encryption_algorithm = EncryptionAlgorithm.AES_128_CBC

    out.mdn_mode = MDNMode.Sync
    out.mdn_signed = True
    out.mdn_mic_algorithms = [DigestAlgorithm.SHA256]

    return out

# ################################################################################################################################
# ################################################################################################################################
