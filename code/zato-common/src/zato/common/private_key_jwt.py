# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import urlsafe_b64encode
from datetime import datetime, timezone
from hashlib import sha1, sha256
from json import loads

# cryptography
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey, EllipticCurvePublicKey, SECP384R1
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.serialization import Encoding, load_pem_private_key, PublicFormat
from cryptography.x509 import load_pem_x509_certificate

# PyJWT
import jwt
from jwt.algorithms import ECAlgorithm, RSAAlgorithm

# Zato
from zato.common.api import OAuth
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes
    from cryptography.x509 import Certificate
    from zato.common.typing_ import stranydict, strstrdict

# ################################################################################################################################
# ################################################################################################################################

# The algorithms that need an RSA key, as opposed to an EC one.
RSA_Algorithms = (OAuth.JWT_Algorithm.RS256, OAuth.JWT_Algorithm.RS384, OAuth.JWT_Algorithm.PS256)

# The number of bits in the hex form of a jti claim.
JTI_Bits = 128

# ################################################################################################################################
# ################################################################################################################################

class PrivateKeyJWTError(Exception):
    """ Raised when a private key JWT definition cannot be used - the key does not parse, it does not match
    the algorithm or the certificate does not belong to the key.
    """

# ################################################################################################################################
# ################################################################################################################################

def load_private_key(private_key:'str') -> 'PrivateKeyTypes':
    """ Parses a PEM-encoded private key, raising PrivateKeyJWTError if it cannot be read.
    """
    try:
        out = load_pem_private_key(private_key.encode('utf8'), password=None)
    except Exception as e:
        raise PrivateKeyJWTError(f'Private key could not be parsed as PEM -> {e}') from e

    return out

# ################################################################################################################################

def load_certificate(certificate:'str') -> 'Certificate':
    """ Parses a PEM-encoded X.509 certificate, raising PrivateKeyJWTError if it cannot be read.
    """
    try:
        out = load_pem_x509_certificate(certificate.encode('utf8'))
    except Exception as e:
        raise PrivateKeyJWTError(f'Certificate could not be parsed as PEM -> {e}') from e

    return out

# ################################################################################################################################

def validate_algorithm(jwt_algorithm:'str') -> 'None':
    """ Raises PrivateKeyJWTError if the algorithm is not one a client assertion can be signed with.
    """
    if jwt_algorithm not in OAuth.JWT_Algorithms:
        allowed = ', '.join(OAuth.JWT_Algorithms)
        raise PrivateKeyJWTError(f'Unknown JWT algorithm `{jwt_algorithm}`, expected one of {allowed}')

# ################################################################################################################################

def validate_key_for_algorithm(key:'PrivateKeyTypes', jwt_algorithm:'str') -> 'None':
    """ Raises PrivateKeyJWTError if the key is of a different type than the algorithm requires.
    """
    validate_algorithm(jwt_algorithm)

    # .. RS and PS algorithms need an RSA key ..
    if jwt_algorithm in RSA_Algorithms:
        if not isinstance(key, RSAPrivateKey):
            raise PrivateKeyJWTError(f'Algorithm {jwt_algorithm} needs an RSA private key, found {type(key).__name__}')

    # .. and ES384 needs an EC key on the P-384 curve.
    else:
        if not isinstance(key, EllipticCurvePrivateKey):
            raise PrivateKeyJWTError(f'Algorithm {jwt_algorithm} needs an EC private key, found {type(key).__name__}')

        if not isinstance(key.curve, SECP384R1):
            raise PrivateKeyJWTError(f'Algorithm {jwt_algorithm} needs a P-384 key, found curve {key.curve.name}')

# ################################################################################################################################

def validate_certificate_matches_key(certificate:'Certificate', key:'PrivateKeyTypes') -> 'None':
    """ Raises PrivateKeyJWTError if the certificate's public key is not the public half of the private key.
    """
    cert_public = certificate.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
    key_public = key.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)

    if cert_public != key_public:
        raise PrivateKeyJWTError('Certificate does not match the private key')

# ################################################################################################################################

def validate_definition(private_key:'str', jwt_algorithm:'str', certificate:'str') -> 'PrivateKeyTypes':
    """ Checks everything a private key JWT definition needs and returns the parsed key.
    """
    validate_algorithm(jwt_algorithm)

    # .. the key itself must parse ..
    key = load_private_key(private_key)

    # .. it must be of the type the algorithm requires ..
    validate_key_for_algorithm(key, jwt_algorithm)

    # .. and if there is a certificate, it must belong to this key.
    if certificate:
        parsed_certificate = load_certificate(certificate)
        validate_certificate_matches_key(parsed_certificate, key)

    return key

# ################################################################################################################################
# ################################################################################################################################

def _base64url(data:'bytes') -> 'str':
    out = urlsafe_b64encode(data).rstrip(b'=').decode('utf8')
    return out

# ################################################################################################################################

def get_thumbprint_headers(certificate:'str') -> 'strstrdict':
    """ Returns the x5t and x5t#S256 headers computed from a PEM certificate's DER form.
    """
    parsed = load_certificate(certificate)
    der = parsed.public_bytes(Encoding.DER)

    out = {
        'x5t': _base64url(sha1(der).digest()),
        'x5t#S256': _base64url(sha256(der).digest()),
    }

    return out

# ################################################################################################################################

def build_assertion_claims(client_id:'str', audience:'str', lifetime:'int'=OAuth.Assertion_Lifetime_Seconds) -> 'stranydict':
    """ Returns the claims of a client assertion - both iss and sub are the client ID and jti is unique per call.
    """
    now = int(datetime.now(timezone.utc).timestamp())

    out = {
        'iss': client_id,
        'sub': client_id,
        'aud': audience,
        'iat': now,
        'exp': now + lifetime,
        'jti': CryptoManager.generate_hex_string(JTI_Bits),
    }

    return out

# ################################################################################################################################

def build_assertion(
    key:'PrivateKeyTypes',
    jwt_algorithm:'str',
    client_id:'str',
    audience:'str',
    key_id:'str'='',
    certificate:'str'='',
) -> 'str':
    """ Signs a client assertion for the token endpoint at the given audience.
    """
    claims = build_assertion_claims(client_id, audience)
    headers = {}

    # .. the kid header lets the server pick the key when it has more than one registered ..
    if key_id:
        headers['kid'] = key_id

    # .. and the thumbprint headers let servers that register certificates, such as Entra ID, find the key.
    if certificate:
        headers.update(get_thumbprint_headers(certificate))

    out = jwt.encode(claims, key, algorithm=jwt_algorithm, headers=headers) # type: ignore[arg-type]

    return out

# ################################################################################################################################
# ################################################################################################################################

def get_public_key_pem(key:'PrivateKeyTypes') -> 'str':
    """ Returns the public half of a private key in PEM form.
    """
    public = key.public_key()
    out = public.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo).decode('utf8')

    return out

# ################################################################################################################################

def get_public_jwk(key:'PrivateKeyTypes', jwt_algorithm:'str', key_id:'str'='') -> 'stranydict':
    """ Returns the public half of a private key as a JWK with its algorithm, use and optional kid.
    """
    public = key.public_key()

    # .. PyJWT knows how to serialize both key families we support ..
    if isinstance(public, RSAPublicKey):
        out = loads(RSAAlgorithm.to_jwk(public))
    elif isinstance(public, EllipticCurvePublicKey):
        out = loads(ECAlgorithm.to_jwk(public))
    else:
        raise PrivateKeyJWTError(f'Unsupported key type {type(public).__name__}')

    out['alg'] = jwt_algorithm
    out['use'] = 'sig'

    if key_id:
        out['kid'] = key_id

    return out

# ################################################################################################################################
# ################################################################################################################################
