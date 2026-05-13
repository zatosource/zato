
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
from zato.common.api import Data_Format, GENERIC, ZATO_NOT_GIVEN
from zato.common.exception import BackendInvocationError
from zato.common.json_internal import loads as json_loads_internal
from zato.common.odb.model import SecurityBase
from zato.common.model.security import BearerTokenConfig, BearerTokenInfo, BearerTokenInfoResult
from zato.common.util.api import parse_extra_into_dict

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, dtnone, intnone, stranydict
    from zato.server.base.parallel import ParallelServer
    from zato.server.connection.cache import CacheAPI

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class BearerTokenManager:

    cache: 'CacheAPI'

    def __init__(self, server:'ParallelServer') -> 'None':
        self.server = server
        self.security_facade = server.security_facade
        self.cache = server.config_manager.cache_api

# ################################################################################################################################

    def _get_bearer_token_config(self, sec_def:'stranydict') -> 'BearerTokenConfig':

        # Scopes require preprocessing ..
        scopes = (sec_def.get('scopes') or '').splitlines()
        scopes = [elem.strip() for elem in scopes]
        scopes = ' '.join(scopes)

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

        # .. and return it to our caller.
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
        request = {
            config.client_id_field: config.username,
            config.client_secret_field: config.password,
            'grant_type': config.grant_type,
            'scope': config.scopes
        }

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

        # Build the cache key ..
        key = f'zato.sec.bearer-token.{sec_def_name}.{scopes}.{audience}'

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
            expiry = 60

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
            expiry = self._store_bearer_token_in_cache(info, scopes)

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

    def get_bearer_token_from_odb(self, odb, security_id='', raw_params=None):

        try:
            if raw_params:
                sec_def = {
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
            else:
                sec_def = None
                with closing(odb.session()) as session:
                    sec_row = session.query(SecurityBase).filter_by(id=security_id).first()
                    if sec_row:
                        opaque = getattr(sec_row, GENERIC.ATTR_NAME, None)
                        opaque = json_loads_internal(opaque) if opaque else {}
                        sec_def = {
                            'id': sec_row.id,
                            'name': sec_row.name,
                            'username': sec_row.username or '',
                            'password': sec_row.password or '',
                            'auth_server_url': opaque.get('auth_server_url', ''),
                            'client_id_field': opaque.get('client_id_field', 'client_id'),
                            'client_secret_field': opaque.get('client_secret_field', 'client_secret'),
                            'grant_type': opaque.get('grant_type', 'client_credentials'),
                            'scopes': opaque.get('scopes', ''),
                            'extra_fields': opaque.get('extra_fields', ''),
                            'data_format': opaque.get('data_format', 'json'),
                        }

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
