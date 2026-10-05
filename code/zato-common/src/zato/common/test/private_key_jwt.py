# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone

# cryptography
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import Encoding, load_pem_private_key, NoEncryption, PrivateFormat
from cryptography.x509.oid import NameOID

# ################################################################################################################################
# ################################################################################################################################

# The environment variable the enmasse template reads the test private key from.
Env_Var_Private_Key = 'EnmasseBearerTokenPrivateKey'

# The name of the private key JWT definition in the enmasse template.
Template_Definition_Name = 'enmasse.bearer_token.private_key_jwt'

# The public exponent every RSA key is generated with.
RSA_Public_Exponent = 65537

# The size of each RSA key, in bits.
RSA_Key_Size = 2048

# How long a self-signed test certificate stays valid.
Certificate_Validity = timedelta(days=1)

# ################################################################################################################################
# ################################################################################################################################

def _to_pem(key:'rsa.RSAPrivateKey | ec.EllipticCurvePrivateKey') -> 'str':
    out = key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()).decode('utf8')
    return out

# ################################################################################################################################

def generate_rsa_private_key_pem() -> 'str':
    """ Returns a fresh RSA private key in PEM form - for RS256, RS384 and PS256.
    """
    key = rsa.generate_private_key(RSA_Public_Exponent, RSA_Key_Size)
    out = _to_pem(key)
    return out

# ################################################################################################################################

def generate_ec_private_key_pem() -> 'str':
    """ Returns a fresh P-384 EC private key in PEM form - for ES384.
    """
    key = ec.generate_private_key(ec.SECP384R1())
    out = _to_pem(key)
    return out

# ################################################################################################################################

def generate_self_signed_certificate_pem(private_key_pem:'str', common_name:'str'='zato.test') -> 'str':
    """ Returns a self-signed certificate for the given private key, in PEM form.
    """
    key = load_pem_private_key(private_key_pem.encode('utf8'), password=None)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])
    now = datetime.now(timezone.utc)

    builder = x509.CertificateBuilder()
    builder = builder.subject_name(name)
    builder = builder.issuer_name(name)
    builder = builder.public_key(key.public_key()) # type: ignore[arg-type]
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.not_valid_before(now)
    builder = builder.not_valid_after(now + Certificate_Validity)

    certificate = builder.sign(key, SHA256()) # type: ignore[arg-type]
    out = certificate.public_bytes(Encoding.PEM).decode('utf8')

    return out

# ################################################################################################################################
# ################################################################################################################################
