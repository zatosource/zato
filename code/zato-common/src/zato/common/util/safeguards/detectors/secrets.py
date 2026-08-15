# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from re import ASCII, compile as re_compile

# piigex
from piigex.detectors import register
from piigex.detectors.base import Detector

# ################################################################################################################################
# ################################################################################################################################

# The region every credential detector below registers under -
# it is not a land and stays out of the PII land and detector choices.
Region_Secrets = 'secrets'

# ################################################################################################################################
# ################################################################################################################################

class _SecretDetector(Detector):
    """ What every credential detector below shares - the region, the feasibility
    and the pass-through validation and normalization.
    """

    region          = Region_Secrets
    feasibility     = 'high'
    default_enabled = True

    def validate(self, candidate:'str') -> 'bool':
        return True

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        return candidate

# ################################################################################################################################
# ################################################################################################################################

class PrivateKeyDetector(_SecretDetector):
    """ A PEM private key block, whole - the BEGIN header, the base64 body across its lines
    and the END footer, for RSA, EC, OpenSSH and unqualified PKCS#8 keys alike.
    """
    name  = 'secret_private_key'
    token = 'SECRET_PRIVATE_KEY'

    pattern = re_compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----[A-Za-z0-9+/=\s]+-----END [A-Z ]*PRIVATE KEY-----', ASCII)

# ################################################################################################################################
# ################################################################################################################################

class AWSAccessKeyDetector(_SecretDetector):
    """ An AWS access key ID - the AKIA or ASIA prefix followed by sixteen upper-case
    alphanumerics, standing on its own.
    """
    name  = 'secret_aws_access_key'
    token = 'SECRET_AWS_ACCESS_KEY'

    pattern = re_compile(r'(?<![A-Z0-9])(?:AKIA|ASIA)[0-9A-Z]{16}(?![0-9A-Z])', ASCII)

# ################################################################################################################################
# ################################################################################################################################

class JWTDetector(_SecretDetector):
    """ A JSON Web Token - three dot-separated base64url segments, the first of which
    always starts with the encoding of an opening JSON brace.
    """
    name  = 'secret_jwt'
    token = 'SECRET_JWT'

    pattern = re_compile(r'eyJ[A-Za-z0-9_-]{6,}\.[A-Za-z0-9_-]{6,}\.[A-Za-z0-9_-]{10,}', ASCII)

# ################################################################################################################################
# ################################################################################################################################

class BearerValueDetector(_SecretDetector):
    """ A bearer credential written out with its scheme - the word Bearer followed by
    the token itself, long enough to be one.
    """
    name  = 'secret_bearer'
    token = 'SECRET_BEARER'

    pattern = re_compile(r'Bearer +[A-Za-z0-9._~+/-]{16,}=*', ASCII)

# ################################################################################################################################
# ################################################################################################################################

class ConnectionStringDetector(_SecretDetector):
    """ A connection string carrying an inline password - scheme, user, the colon,
    the password and the at-sign with the host behind it.
    """
    name  = 'secret_connection_string'
    token = 'SECRET_CONNECTION_STRING'

    pattern = re_compile(r'[a-z][a-z0-9+.-]*://[^:/@\s]+:[^@\s]+@[^\s"\']+', ASCII)

# ################################################################################################################################
# ################################################################################################################################

class APITokenDetector(_SecretDetector):
    """ A bare API token of a well-known prefixed shape - OpenAI and Stripe style sk- and rk-,
    GitHub gh*_ tokens, Slack xox tokens and GitLab personal access tokens.
    """
    name  = 'secret_api_token'
    token = 'SECRET_API_TOKEN'

    # One alternative per token family - OpenAI and Stripe, GitHub, Slack, GitLab
    _shapes = [
        r'(?<![A-Za-z0-9])(?:sk|rk)-[A-Za-z0-9_-]{20,}',
        r'(?<![A-Za-z0-9])gh[pousr]_[A-Za-z0-9]{20,}',
        r'(?<![A-Za-z0-9])xox[abps]-[A-Za-z0-9-]{10,}',
        r'(?<![A-Za-z0-9])glpat-[A-Za-z0-9_-]{20,}',
    ]

    pattern = re_compile('|'.join(_shapes), ASCII)

# ################################################################################################################################
# ################################################################################################################################

register(PrivateKeyDetector())
register(AWSAccessKeyDetector())
register(JWTDetector())
register(BearerValueDetector())
register(ConnectionStringDetector())
register(APITokenDetector())

# ################################################################################################################################
# ################################################################################################################################
