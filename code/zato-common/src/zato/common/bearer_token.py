
# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from datetime import datetime, timedelta, timezone
from json import dumps, loads
from logging import getLogger
from traceback import format_exc

# dateutil
from dateutil.parser import parse as dt_parse

# Requests
from requests import post as requests_post

# Zato
from zato.common.api import Data_Format, GENERIC, OAuth
from zato.common.exception import BackendInvocationError
from zato.common.json_internal import loads as json_loads_internal
from zato.common.odb.model import SecurityBase
from zato.common.model.security import BearerTokenConfig, BearerTokenInfo, BearerTokenInfoResult
from zato.common.private_key_jwt import build_assertion, load_private_key, PrivateKeyJWTError
from zato.common.util.api import parse_extra_into_dict

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes
    from zato.common.typing_ import any_, dtnone, intnone, stranydict, strlist
    from zato.server.base.parallel import ParallelServer
    from zato.server.connection.cache import CacheAPI

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# The revision a definition has before it is ever edited, changed or deleted.
Initial_Revision = 0

# The cache expiry of a token whose response did not say how long it is valid for.
Default_Cache_Expiry_Seconds = 60

# The opaque fields a private key JWT definition carries, each with the value an older definition reads as.
Private_Key_JWT_Fields = {
    'client_auth_method': OAuth.Default.Client_Auth_Method,
    'private_key': '',
    'jwt_algorithm': OAuth.Default.JWT_Algorithm,
    'key_id': '',
    'assertion_audience': '',
    'certificate': '',
}

# ################################################################################################################################
# ################################################################################################################################

def normalize_scopes(scopes:'str') -> 'str':
    """ Turns a multi-line scopes string into the single-line form OAuth requests carry -
    each line is stripped of surrounding whitespace, empty lines are dropped and the rest
    is joined with single spaces.
    """
    scope_list:'strlist' = []

    for scope in scopes.splitlines():
        scope = scope.strip()

        if scope:
            scope_list.append(scope)

    out = ' '.join(scope_list)
    return out

# ################################################################################################################################
# ################################################################################################################################

class BearerTokenManager:

    cache: 'CacheAPI'

    def __init__(self, server:'ParallelServer') -> 'None':
        self.server = server
        self.security_facade = server.security_facade
        self.cache = server.config_manager.cache_api

        # Each definition's revision is part of its cache key - bumping it makes all its cached tokens unreachable
        self.revisions:'dict[str, int]' = {}

        # Parsed private keys by definition name, along with the encrypted text each was parsed from
        self.private_keys:'dict[str, tuple[str, PrivateKeyTypes]]' = {}

# ################################################################################################################################

    def invalidate(self, sec_def_name:'str') -> 'None':
        """ Forgets everything cached for a definition - its tokens stop being found and its key is parsed anew.
        """
        revision = self.revisions.get(sec_def_name)
        if revision is None:
            revision = Initial_Revision

        self.revisions[sec_def_name] = revision + 1
        _ = self.private_keys.pop(sec_def_name, None)

# ################################################################################################################################

    def _get_private_key(self, config:'BearerTokenConfig') -> 'PrivateKeyTypes':
        """ Returns the parsed private key of a definition, decrypting and parsing it on first use only.
        """
        if not config.private_key:
            raise PrivateKeyJWTError(f'Bearer token definition `{config.sec_def_name}` has no private key')

        # .. a key parsed earlier is reused as long as the stored text has not changed ..
        cached = self.private_keys.get(config.sec_def_name)
        if cached and cached[0] == config.private_key:
            return cached[1]

        # .. otherwise, the key is decrypted and parsed now ..
        private_key_pem = self.server.decrypt(config.private_key)
        key = load_private_key(private_key_pem)

        # .. and kept for the next call.
        self.private_keys[config.sec_def_name] = (config.private_key, key)

        return key

# ################################################################################################################################

    def _build_client_assertion(self, config:'BearerTokenConfig') -> 'str':
        """ Signs a client assertion for a definition - the audience is the token endpoint unless the definition overrides it.
        """
        key = self._get_private_key(config)

        audience = config.assertion_audience
        if not audience:
            audience = config.auth_server_url

        out = build_assertion(key, config.jwt_algorithm, config.username, audience, config.key_id, config.certificate)

        return out

# ################################################################################################################################

    def _get_bearer_token_config(self, sec_def:'stranydict') -> 'BearerTokenConfig':

        # Scopes require preprocessing ..
        scopes = sec_def.get('scopes')
        if scopes is None:
            scopes = ''
        scopes = normalize_scopes(scopes)

        # .. same goes for extra fields ..
        extra_fields = sec_def.get('extra_fields') or ''
        if isinstance(extra_fields, list):
            extra_fields = '\n'.join(extra_fields)
        extra_fields = parse_extra_into_dict(extra_fields)

        # .. build a business object from security definition ..
        out = BearerTokenConfig()
        out.sec_def_name = sec_def['name']
        out.username = sec_def['username']
        out.password = sec_def['password']
        out.scopes = scopes
        out.grant_type = sec_def['grant_type']
        out.extra_fields = extra_fields
        out.auth_server_url = sec_def['auth_server_url']
        out.client_id_field = sec_def['client_id_field']
        out.client_secret_field = sec_def['client_secret_field']

        # .. definitions created before private key JWT existed have none of its fields ..
        # .. and they read as client secret definitions ..
        out.client_auth_method = self._get_opaque_field(sec_def, 'client_auth_method')
        out.private_key = self._get_opaque_field(sec_def, 'private_key')
        out.jwt_algorithm = self._get_opaque_field(sec_def, 'jwt_algorithm')
        out.key_id = self._get_opaque_field(sec_def, 'key_id')
        out.assertion_audience = self._get_opaque_field(sec_def, 'assertion_audience')
        out.certificate = self._get_opaque_field(sec_def, 'certificate')

        # .. and return it to our caller.
        return out

# ################################################################################################################################

    def _get_opaque_field(self, sec_def:'stranydict', name:'str') -> 'str':
        """ Returns an opaque field of a definition, or the value an older definition without it reads as.
        """
        out = sec_def.get(name)
        if not out:
            out = Private_Key_JWT_Fields[name]

        return out

# ################################################################################################################################

    def _build_bearer_token_info(self, sec_def_name:'str', data:'stranydict') -> 'BearerTokenInfo':

        # Local variables
        out = BearerTokenInfo()
        now = datetime.now(tz=timezone.utc)
        expires_in:'timedelta | None' = None
        expires_in_sec:'intnone' = None
        expiration_time:'dtnone' = None

        # These can be built upfront ..
        out.creation_time = now
        out.sec_def_name = sec_def_name
        out.token = data['access_token']
        out.token_type = data['token_type']

        # .. these are optional ..
        out.scopes = data.get('scope') or ''
        out.username = data.get('username') or data.get('userName') or ''

        # .. expiration time may be provided as: ..
        # .. 1) the number of seconds, e.g. "expires_in=86400"
        # .. 2) a datetime string, e.g. ".expires=Fri, 27 Oct 2023 11:22:33 GMT"
        # .. and we need to populate the missing field ourselves ..

        # Case 1)
        if expires_in_sec := data.get('expires_in'):
            expires_in = timedelta(seconds=expires_in_sec)
            expiration_time = now + expires_in

        # Case 2)
        if expires := data.get('.expires'):
            expiration_time = dt_parse(expires)
            expires_in = expiration_time - now
            expires_in_sec = int(expires_in.total_seconds())

        # .. populate the expiration metadata ..
        out.expires_in = expires_in
        out.expires_in_sec = expires_in_sec
        out.expiration_time = expiration_time

        # .. and return it to our caller.
        return out

# ################################################################################################################################

    def _build_token_request(self, config:'BearerTokenConfig') -> 'stranydict':
        """ Returns the body of a token request - a private key JWT definition sends a signed assertion
        in place of its client secret, which never leaves the server.
        """
        out = {
            config.client_id_field: config.username,
            'grant_type': config.grant_type,
        }

        if config.client_auth_method == OAuth.Client_Auth_Method.Private_Key_JWT:
            out['client_assertion_type'] = OAuth.Assertion_Type
            out['client_assertion'] = self._build_client_assertion(config)
        else:
            out[config.client_secret_field] = config.password

        return out

# ################################################################################################################################

    def _get_bearer_token_from_auth_server(
        self,
        config, # type: BearerTokenConfig
        scopes, # type: str
        data_format, # type: str
    ) -> 'BearerTokenInfo':

        # Local variables
        _needs_json = data_format == Data_Format.JSON

        # The content type will depend on whether it is JSON or not
        if _needs_json:
            content_type = 'application/json'
        else:
            content_type = 'application/x-www-form-urlencoded'

        # If we have any scopes given explicitly, they will take priority,
        # otherwise, the ones from the configuration (if any), will be used.
        _scopes = scopes or config.scopes

        # Build our outgoing request ..
        request = self._build_token_request(config)

        # .. scopes are optional ..
        if _scopes:
            request['scope'] = _scopes

        # .. extra fields are optional ..
        if config.extra_fields:
            request.update(config.extra_fields)

        # .. the headers that will be sent along with the request ..
        headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': content_type
        }

        # .. potentially, we send JSON requests ..
        if _needs_json:
            request = dumps(request)

        # .. now, send the request to the remote end ..
        response = requests_post(config.auth_server_url, request, headers=headers, verify=None)

        # .. raise an exception if the invocation was not successful ..
        if not response.ok:
            message  = f'Bearer token for `{config.sec_def_name}` could not be obtained from {config.auth_server_url} -> '
            message += f'{response.status_code} -> {response.text}'
            raise BackendInvocationError(None, message, needs_msg=True)

        # .. if we are here, it means that we can load the JSON response ..
        data:'stranydict' = loads(response.text)

        # .. turn into a business object that represents the token ..
        info = self._build_bearer_token_info(config.sec_def_name, data)

        message  = f'Bearer token received for `{config.sec_def_name}`'
        message += f'; expires_in={info.expires_in_sec} ({info.expires_in} -> {info.expiration_time} UTC)'
        message += f'; scopes={info.scopes}'
        logger.info(message)

        # .. which can be now returned to our caller.
        return info

# ################################################################################################################################

    def _get_cache_key(self, sec_def_name:'str', scopes:'str', audience:'str'='') -> 'str':

        # Make sure all values are populated
        scopes = scopes or 'NoScopes'
        audience = audience or 'NoAudience'

        # Tokens obtained before a definition was edited or deleted must not be found again ..
        revision = self.revisions.get(sec_def_name)
        if revision is None:
            revision = Initial_Revision

        # .. build the cache key ..
        key = f'zato.sec.bearer-token.{sec_def_name}.{revision}.{scopes}.{audience}'

        # .. and return it to our caller.
        return key

# ################################################################################################################################

    def _get_bearer_token_from_cache(self, sec_def_name:'str', scopes:'str') -> 'any_':

        # Build a cache key ..
        key = self._get_cache_key(sec_def_name, scopes)

        # .. try to get the token information from our cache ..
        cached_value = self.cache.get(key)

        # .. return it if found, or None otherwise.
        return cached_value

# ################################################################################################################################

    def _store_bearer_token_in_cache(self, info:'BearerTokenInfo', scopes:'str') -> 'int':

        # Build a cache key ..
        key = self._get_cache_key(info.sec_def_name, scopes)

        # .. make it expire in half the time the token will be valid for ..
        # .. or in one minute in case the expiration time is not available ..
        if info.expires_in_sec:
            expiry = info.expires_in_sec / 2
        else:
            expiry = Default_Cache_Expiry_Seconds

        # .. serialize the token info for storage ..
        value = {
            'token': info.token,
            'token_type': info.token_type,
            'sec_def_name': info.sec_def_name,
            'scopes': info.scopes,
            'username': info.username,
            'expires_in_sec': info.expires_in_sec,
        }

        # .. store the token ..
        expiry_int = int(expiry)
        self.cache.set(key, value, expiry=expiry_int)

        # .. make it known when exactly the key will expire ..
        expiry_in = timedelta(seconds=expiry)
        expiry_time = datetime.now(tz=timezone.utc) + expiry_in

        # .. log what we have done ..
        message  = f'Bearer token for `{info.sec_def_name}` cached under key `{key}`'
        message += f'; expiry={expiry} ({expiry_in} -> {expiry_time} UTC)'
        logger.info(message)

        # .. and return the details to the caller.
        return expiry_int

# ################################################################################################################################

    def _get_bearer_token_info_impl(
        self,
        config,      # type: BearerTokenConfig
        scopes,      # type: str
        data_format, # type:str
    ) -> 'BearerTokenInfoResult':

        # Our response to produce
        result = BearerTokenInfoResult()

        # If we have the token in our cache, we can return it immediately ..
        if cached_value := self._get_bearer_token_from_cache(config.sec_def_name, scopes):

            # .. reconstruct the token info from cached data ..
            info = BearerTokenInfo()
            info.token = cached_value['token']
            info.token_type = cached_value['token_type']
            info.sec_def_name = cached_value['sec_def_name']
            info.scopes = cached_value['scopes']
            info.username = cached_value['username']
            info.expires_in_sec = cached_value['expires_in_sec']

            # .. assign the actual value ..
            result.info = info

            # .. indicate that it came from the cache ..
            result.is_cache_hit = True

            # .. and return the result to the caller.
            return result

        # .. we are here if the token was not in the cache ..
        else:

            # .. since the token was not cached, we need to obtain it from the auth server ..
            info = self._get_bearer_token_from_auth_server(config, scopes, data_format)

            # .. then we can cache it ..
            _ = self._store_bearer_token_in_cache(info, scopes)

            # .. build the result ..
            result.info = info
            result.is_cache_hit = False

            # .. and now, we can return it to our caller.
            return result

# ################################################################################################################################

    def _get_bearer_token_info(self, sec_def:'stranydict', scopes:'str', data_format:'str') -> 'BearerTokenInfoResult':

        # Turn the input security definition into a bearer token configuration ..
        config = self._get_bearer_token_config(sec_def)

        # .. this gets a token either from the server's cache ..
        # .. or from the remote authentication endpoint ..
        result = self._get_bearer_token_info_impl(config, scopes, data_format)

        # .. now, we can return the token to our caller.
        return result

# ################################################################################################################################

    def get_bearer_token_info_by_sec_def_id(
        self,
        sec_def_id,  # type: int
        scopes,      # type: str
        data_format, # type: str
    ) -> 'BearerTokenInfoResult':

        # Get our security definition by its ID ..
        sec_def:'stranydict' = self.security_facade.get_bearer_token_by_id(sec_def_id)

        # .. get a token ..
        result = self._get_bearer_token_info(sec_def, scopes, data_format)

        # .. and return it to our caller now.
        return result

# ################################################################################################################################

    def get_bearer_token_info_by_sec_def_name(
        self,
        sec_def_name, # type: str
        scopes,       # type: str
        data_format,  # type: str
    ) -> 'BearerTokenInfoResult':

        # Get our security definition by its ID ..
        sec_def:'stranydict' = self.security_facade.get_bearer_token_by_name(sec_def_name)

        # .. get a token ..
        result = self._get_bearer_token_info(sec_def, scopes, data_format)

        # .. and return it to our caller now.
        return result

# ################################################################################################################################

    def _get_sec_def_from_odb(self, odb:'any_', security_id:'any_') -> 'stranydict | None':
        """ Reads a bearer token definition from the database, with its opaque fields included.
        """
        out = None

        with closing(odb.session()) as session:
            sec_row = session.query(SecurityBase).filter_by(id=security_id).first()
            if sec_row:
                opaque = getattr(sec_row, GENERIC.ATTR_NAME, None)
                opaque = json_loads_internal(opaque) if opaque else {}
                out = {
                    'id': sec_row.id,
                    'name': sec_row.name,
                    'username': sec_row.username or '',
                    'password': sec_row.password or '',
                    'auth_server_url': opaque.get('auth_server_url', ''),
                    'client_id_field': opaque.get('client_id_field', OAuth.Default.Client_ID_Field),
                    'client_secret_field': opaque.get('client_secret_field', OAuth.Default.Client_Secret_Field),
                    'grant_type': opaque.get('grant_type', OAuth.Default.Grant_Type),
                    'scopes': opaque.get('scopes', ''),
                    'extra_fields': opaque.get('extra_fields', ''),
                    'data_format': opaque.get('data_format', 'json'),
                }

                # .. the private key JWT fields may be absent from definitions created before they existed.
                for name, default in Private_Key_JWT_Fields.items():
                    out[name] = opaque.get(name, default)

        return out

# ################################################################################################################################

    def _get_sec_def_from_raw_params(self, odb:'any_', security_id:'any_', raw_params:'stranydict') -> 'stranydict':
        """ Builds a bearer token definition from what a Dashboard form holds - a private key left empty
        in the edit form means the key stored in the database is to be used.
        """
        out = {
            'name': raw_params.get('name', ''),
            'username': raw_params['username'],
            'password': raw_params['secret'],
            'auth_server_url': raw_params['auth_server_url'],
            'client_id_field': raw_params['client_id_field'],
            'client_secret_field': raw_params['client_secret_field'],
            'grant_type': raw_params['grant_type'],
            'scopes': raw_params.get('scopes', ''),
            'extra_fields': raw_params.get('extra_fields', ''),
            'data_format': raw_params.get('data_format', 'json'),
        }

        for name, default in Private_Key_JWT_Fields.items():
            out[name] = raw_params.get(name, default)

        # .. the form never shows a stored key, so an empty one has to be read from the database ..
        is_private_key_jwt = out['client_auth_method'] == OAuth.Client_Auth_Method.Private_Key_JWT
        if is_private_key_jwt and (not out['private_key']) and security_id:
            stored = self._get_sec_def_from_odb(odb, security_id)
            if stored:
                out['private_key'] = stored['private_key']

                # .. and the same goes for a certificate left empty.
                if not out['certificate']:
                    out['certificate'] = stored['certificate']

        return out

# ################################################################################################################################

    def get_bearer_token_from_odb(self, odb:'any_', security_id:'any_'='', raw_params:'stranydict | None'=None) -> 'str':

        try:
            if raw_params:
                sec_def = self._get_sec_def_from_raw_params(odb, security_id, raw_params)
            else:
                sec_def = self._get_sec_def_from_odb(odb, security_id)

                if not sec_def:
                    return dumps({
                        'is_ok': False,
                        'error': 'Bearer token definition not found: id=`{}`'.format(security_id)
                    })

            config = self._get_bearer_token_config(sec_def)
            scopes = config.scopes
            data_format = sec_def.get('data_format') or 'json'

            info = self._get_bearer_token_from_auth_server(config, scopes, data_format)

            return dumps({'is_ok': True, 'token': info.token})

        except PrivateKeyJWTError as error:
            return dumps({
                'is_ok': False,
                'error': 'Error while obtaining token',
                'response_body': str(error),
                'response_content_type': 'text/plain',
                'status_code': 0,
            })

        except BackendInvocationError as error:
            return dumps({
                'is_ok': False,
                'error': 'Error while obtaining token',
                'response_body': getattr(error, 'inner_message', '') or str(error),
                'response_content_type': 'text/plain',
                'status_code': 0,
            })

        except Exception:
            traceback = format_exc()
            logger.error('get_bearer_token_from_odb: error: %s', traceback)
            return dumps({
                'is_ok': False,
                'error': 'Error while obtaining token',
                'response_body': traceback,
                'response_content_type': 'text/plain',
                'status_code': 0,
            })

# ################################################################################################################################
# ################################################################################################################################
