# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from urllib.parse import urlsplit

# PyJWT
from jwt import decode as jwt_decode, get_unverified_header, PyJWK
from jwt.exceptions import ExpiredSignatureError, InvalidAudienceError, InvalidIssuerError, InvalidSignatureError, \
    InvalidTokenError

# Requests
from requests import get as requests_get

# Zato
from zato.common.crypto.api import is_string_equal
from zato.common.model.security import BearerTokenVerifyConfig
from zato.common.util.api import parse_extra_into_dict

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydictnone, stranydict
    from zato.server.connection.cache import CacheAPI

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The one signature algorithm inbound JWTs may use
JWT_Algorithm = 'RS256'

# How long fetched JWKS documents stay in the cache, in seconds
JWKS_Cache_TTL = 3600

# The case-insensitive prefix inbound Authorization headers carry
Bearer_Prefix = 'bearer '

# Where an issuer publishes its discovery document
Well_Known_Path = '/.well-known/openid-configuration'

# Timeout for JWKS and discovery document requests, in seconds
_http_timeout = 10

# Cache keys for JWKS documents start with this prefix
_jwks_cache_key_prefix = 'zato.sec.bearer-token.jwks.'

# What jwt_decode must always validate
_decode_options:'any_' = {'require': ['exp', 'iss', 'aud']}

# ################################################################################################################################
# ################################################################################################################################

def extract_bearer_token(auth_header:'str') -> 'str':
    """ Returns the token from an Authorization header carrying a case-insensitive Bearer prefix,
    or an empty string if the header does not carry one.
    """
    # No header means no token at all ..
    if not auth_header:
        return ''

    # .. the prefix comparison is case-insensitive, per RFC 6750 ..
    prefix_length = len(Bearer_Prefix)
    prefix = auth_header[:prefix_length]

    if prefix.lower() != Bearer_Prefix:
        return ''

    # .. and whatever follows the prefix is the token itself.
    out = auth_header[prefix_length:].strip()
    return out

# ################################################################################################################################
# ################################################################################################################################

def parse_claims(claims:'any_') -> 'stranydict':
    """ Turns the claims configuration - a dict, a list of name=value entries or a multi-line name=value string -
    into a dict of claim name to required value pairs.
    """
    # Our response to produce
    out:'stranydict' = {}

    # No configuration means no claims to match ..
    if not claims:
        return out

    # .. a dict can be used as-is ..
    if isinstance(claims, dict):
        out.update(claims)
        return out

    # .. a list of name=value entries becomes a multi-line string first ..
    if isinstance(claims, list):
        claims = '\n'.join(claims)

    # .. and a multi-line string is parsed the same way extra fields are.
    parsed = parse_extra_into_dict(claims, convert_bool=False)
    out.update(parsed)

    return out

# ################################################################################################################################
# ################################################################################################################################

def build_verify_config(sec_def:'stranydict') -> 'BearerTokenVerifyConfig':
    """ Builds a verification config out of a Bearer token security definition,
    deriving the issuer and the JWKS URL if they are not set explicitly.
    """
    # Our response to produce
    out = BearerTokenVerifyConfig()

    out.security_id = sec_def['id']
    out.sec_def_name = sec_def['name']

    # Static definitions carry the exact expected token ..
    out.static_token = sec_def.get('static_token') or ''

    # .. the issuer defaults to the base of the token endpoint ..
    issuer = sec_def.get('issuer') or ''

    if not issuer:
        if auth_server_url := sec_def.get('auth_server_url'):
            split = urlsplit(auth_server_url)
            issuer = f'{split.scheme}://{split.netloc}'

    out.issuer = issuer

    # .. the JWKS URL defaults to the issuer's well-known discovery path ..
    jwks_url = sec_def.get('jwks_url') or ''

    if not jwks_url:
        if issuer:
            jwks_url = issuer.rstrip('/') + Well_Known_Path

    out.jwks_url = jwks_url

    # .. the audience is required for a definition to match inbound JWTs at all ..
    out.audience = sec_def.get('audience') or ''

    # .. and claims are optional name and required-value pairs.
    out.claims = parse_claims(sec_def.get('claims'))

    return out

# ################################################################################################################################
# ################################################################################################################################

class BearerTokenVerifier:
    """ Verifies inbound bearer tokens - static ones by a constant-time comparison
    and JWT ones locally against the issuer's JWKS keys, with no per-request calls to the IdP.
    """

    def __init__(self, cache:'CacheAPI') -> 'None':
        self.cache = cache

# ################################################################################################################################

    def verify(self, cid:'str', channel_name:'str', token:'str', config:'BearerTokenVerifyConfig') -> 'anydictnone':
        """ Verifies a token against one definition. Returns the token's claims on success -
        an empty dict for static tokens - or None if the token does not match.
        """
        # Static definitions carry the exact expected token ..
        if config.static_token:
            out = self._verify_static(cid, channel_name, token, config)
            return out

        # .. JWT definitions need an audience to be inbound-enabled ..
        elif config.audience:
            out = self._verify_jwt(cid, channel_name, token, config)
            return out

        # .. anything else is an outgoing-only definition that never matches inbound traffic.
        else:
            logger.info('Bearer token definition `%s` is not configured for inbound use; channel=%s; cid=%s',
                config.sec_def_name, channel_name, cid)
            return None

# ################################################################################################################################

    def _verify_static(self, cid:'str', channel_name:'str', token:'str', config:'BearerTokenVerifyConfig') -> 'anydictnone':
        """ Compares the token against the configured static one in constant time.
        """
        if is_string_equal(token, config.static_token):
            return {}
        else:
            logger.info('Invalid static bearer token; sec_def=%s; channel=%s; cid=%s',
                config.sec_def_name, channel_name, cid)
            return None

# ################################################################################################################################

    def _verify_jwt(self, cid:'str', channel_name:'str', token:'str', config:'BearerTokenVerifyConfig') -> 'anydictnone':
        """ Verifies a JWT locally - signature via JWKS, expiry, issuer and audience, then the configured claims.
        """
        # The header can be read without verification - it names the key and the algorithm ..
        try:
            header = get_unverified_header(token)
        except InvalidTokenError as e:
            logger.info('Bearer token is not a valid JWT (%s); sec_def=%s; channel=%s; cid=%s',
                e, config.sec_def_name, channel_name, cid)
            return None

        # .. only the pinned algorithm is ever accepted ..
        algorithm = header.get('alg')

        if algorithm != JWT_Algorithm:
            logger.info('Bearer token uses unsupported algorithm `%s`; sec_def=%s; channel=%s; cid=%s',
                algorithm, config.sec_def_name, channel_name, cid)
            return None

        # .. a key ID is needed to pick the signing key from the JWKS document ..
        key_id = header.get('kid') or ''

        if not key_id:
            logger.info('Bearer token has no key ID; sec_def=%s; channel=%s; cid=%s',
                config.sec_def_name, channel_name, cid)
            return None

        # .. find the signing key, refetching the JWKS document if the key is unknown ..
        key = self._get_signing_key(config.jwks_url, key_id)

        if key is None:
            logger.info('No JWKS key matches key ID `%s` from `%s`; sec_def=%s; channel=%s; cid=%s',
                key_id, config.jwks_url, config.sec_def_name, channel_name, cid)
            return None

        # .. now, the actual verification - signature, expiry, issuer and audience ..
        try:
            claims = jwt_decode(
                token,
                key=key,
                algorithms=[JWT_Algorithm],
                audience=config.audience,
                issuer=config.issuer,
                options=_decode_options,
            )
        except ExpiredSignatureError:
            logger.info('Bearer token has expired; sec_def=%s; channel=%s; cid=%s',
                config.sec_def_name, channel_name, cid)
            return None
        except InvalidAudienceError:
            logger.info('Bearer token has a wrong audience, expected `%s`; sec_def=%s; channel=%s; cid=%s',
                config.audience, config.sec_def_name, channel_name, cid)
            return None
        except InvalidIssuerError:
            logger.info('Bearer token has a wrong issuer, expected `%s`; sec_def=%s; channel=%s; cid=%s',
                config.issuer, config.sec_def_name, channel_name, cid)
            return None
        except InvalidSignatureError:
            logger.info('Bearer token has an invalid signature; sec_def=%s; channel=%s; cid=%s',
                config.sec_def_name, channel_name, cid)
            return None
        except InvalidTokenError as e:
            logger.info('Bearer token is invalid (%s); sec_def=%s; channel=%s; cid=%s',
                e, config.sec_def_name, channel_name, cid)
            return None

        # .. the signature checks out, so the configured claims are matched last ..
        out = self._match_claims(cid, channel_name, claims, config)
        return out

# ################################################################################################################################

    def _match_claims(
        self,
        cid:'str',
        channel_name:'str',
        claims:'stranydict',
        config:'BearerTokenVerifyConfig',
        ) -> 'anydictnone':
        """ Checks that every configured claim is present in the token with the required value.
        """
        for name in sorted(config.claims):
            expected = config.claims[name]

            # The claim must be there at all ..
            if name not in claims:
                logger.info('Bearer token is missing claim `%s`; sec_def=%s; channel=%s; cid=%s',
                    name, config.sec_def_name, channel_name, cid)
                return None

            actual = claims[name]

            # .. a list-valued claim, such as groups, matches by membership ..
            if isinstance(actual, list):
                if expected not in actual:
                    logger.info('Bearer token claim `%s` does not contain `%s`; sec_def=%s; channel=%s; cid=%s',
                        name, expected, config.sec_def_name, channel_name, cid)
                    return None

            # .. and a scalar claim matches by equality.
            else:
                if actual != expected:
                    logger.info('Bearer token claim `%s` is `%s` instead of `%s`; sec_def=%s; channel=%s; cid=%s',
                        name, actual, expected, config.sec_def_name, channel_name, cid)
                    return None

        # Everything matched so the claims can be handed back to the caller.
        return claims

# ################################################################################################################################

    def _get_signing_key(self, jwks_url:'str', key_id:'str') -> 'any_':
        """ Returns the signing key for the given key ID, refetching the JWKS document
        once if the key is unknown - this is how IdP key rotation is handled without restarts.
        """
        # Try the cached document first ..
        document = self._get_jwks_document(jwks_url, force_refetch=False)
        key = self._find_key(document, key_id)

        # .. an unknown key ID may mean the IdP has rotated its keys, so refetch once.
        if key is None:
            document = self._get_jwks_document(jwks_url, force_refetch=True)
            key = self._find_key(document, key_id)

        return key

# ################################################################################################################################

    def _find_key(self, document:'stranydict', key_id:'str') -> 'any_':
        """ Returns the key matching the given key ID from a JWKS document, or None if there is no match.
        """
        for key_data in document['keys']:
            if key_data.get('kid') == key_id:
                jwk = PyJWK.from_dict(key_data, algorithm=JWT_Algorithm)
                out = jwk.key
                break
        else:
            out = None

        return out

# ################################################################################################################################

    def _get_jwks_document(self, jwks_url:'str', force_refetch:'bool') -> 'stranydict':
        """ Returns the JWKS document for the given URL, from the cache if possible.
        Fetched documents with any keys are cached for JWKS_Cache_TTL seconds.
        """
        cache_key = _jwks_cache_key_prefix + jwks_url

        # The cache is consulted first unless a refetch was requested explicitly ..
        if not force_refetch:
            if cached_document := self.cache.get(cache_key):
                return cached_document

        # .. fetch the document from the IdP ..
        document = self._fetch_jwks_document(jwks_url)

        # .. cache it only if it actually has keys - failures must not lock callers out for the whole TTL ..
        if document['keys']:
            self.cache.set(cache_key, document, expiry=JWKS_Cache_TTL)

        # .. and return it to our caller.
        return document

# ################################################################################################################################

    def _fetch_jwks_document(self, jwks_url:'str') -> 'stranydict':
        """ Fetches a JWKS document over HTTP. If the URL points to a discovery document,
        its jwks_uri is followed to reach the actual keys. Always returns a dict with a keys list.
        """
        response = requests_get(jwks_url, timeout=_http_timeout)

        if not response.ok:
            logger.info('JWKS document could not be fetched from `%s` -> %s -> %s',
                jwks_url, response.status_code, response.text)
            return {'keys': []}

        document = response.json()

        # A discovery document points to the actual JWKS location ..
        if jwks_uri := document.get('jwks_uri'):
            response = requests_get(jwks_uri, timeout=_http_timeout)

            if not response.ok:
                logger.info('JWKS document could not be fetched from `%s` -> %s -> %s',
                    jwks_uri, response.status_code, response.text)
                return {'keys': []}

            document = response.json()

        # .. whatever was fetched must be an actual JWKS document ..
        if 'keys' not in document:
            logger.info('Document from `%s` is not a JWKS document', jwks_url)
            return {'keys': []}

        # .. and it can now be returned to our caller.
        return document

# ################################################################################################################################
# ################################################################################################################################
