
# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone
from json import dumps, loads
from logging import getLogger
from time import time

# dateutil
from dateutil.parser import parse as dt_parse

# Requests
from requests import post as requests_post

# Zato
from zato.cache import KeyExpiredError
from zato.common.api import CACHE, Data_Format, ZATO_NOT_GIVEN
from zato.common.model.security import BearerTokenConfig, BearerTokenInfo, BearerTokenInfoResult
from zato.common.util.api import parse_extra_into_dict

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.cache import Entry
    from zato.common.typing_ import any_, dtnone, intnone, stranydict
    from zato.server.base.parallel import ParallelServer
    from zato.server.connection.cache import Cache
    Entry = Entry

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class BearerTokenManager:

    # Type hints
    cache: 'Cache'

    # This is where we store the tokens
    cache_name = CACHE.Default_Name.Bearer_Token

    def __init__(self, server:'ParallelServer') -> None:
        self.server = server
        self.security_facade = server.security_facade
        self.set_cache()

    def set_cache(self):
        cache_api = self.server.worker_store.cache_api
        try:
            self.cache = cache_api.get_builtin_cache(self.cache_name)
        except KeyError:
            self.cache = None # type: ignore

# ################################################################################################################################

    def _get_bearer_token_config(self, sec_def:'stranydict') -> 'BearerTokenConfig':

        # Scopes require preprocessing ..
        scopes = (sec_def['scopes'] or '').splitlines()
        scopes = [elem.strip() for elem in scopes]
        scopes = ' '.join(scopes)

        # .. same goes for extra fields ..
        extra_fields = sec_def['extra_fields'] or ''
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
            msg  = f'Bearer token for `{config.sec_def_name}` could not be obtained from {config.auth_server_url} -> '
            msg += f'{response.status_code} -> {response.text}'
            raise Exception(msg)

        # .. if we are here, it means that we can load the JSON response ..
        data:'stranydict' = loads(response.text)

        # .. turn into a business object that represents the token ..
        info = self._build_bearer_token_info(config.sec_def_name, data)

        msg  = f'Bearer token received for `{config.sec_def_name}`'
        msg += f'; expires_in={info.expires_in_sec} ({info.expires_in} -> {info.expiration_time} UTC)'
        msg += f'; scopes={info.scopes}'
        logger.info(msg)

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

    def _has_bearer_token_in_cache(self, sec_def_name:'str', scopes:'str') -> 'bool':

        # Build a cache key ..
        key = self._get_cache_key(sec_def_name, scopes)

        # .. check if it exists ..
        has_key = key in self.cache

        return has_key

# ################################################################################################################################

    def _get_bearer_token_from_cache(self, sec_def_name:'str', scopes:'str') -> 'any_':

        # Build a cache cache key ..
        key = self._get_cache_key(sec_def_name, scopes)

        # .. try to get the token information from our cache ..
        try:
            cache_entry = self.cache.get(key, details=True) # type: Entry
        except KeyExpiredError:

            # ..this key has already expired and we cannot get it ..
            logger.info('Ignoring expired Bearer token key -> %s', key)

            # .. return None explicitly to indicate that there is no such key ..
            return None

        else:
            # .. if we are here, we return the key to our caller but only if it actually exists.
            if cache_entry and cache_entry != ZATO_NOT_GIVEN:
                return cache_entry

# ################################################################################################################################

    def _store_bearer_token_in_cache(self, info:'BearerTokenInfo', scopes:'str') -> 'int':

        # Build a cache cache key ..
        key = self._get_cache_key(info.sec_def_name, scopes)

        # .. make it expire in half the time the token will be valid for ..
        # .. or in one minute in case the expiration time is not available ..
        if info.expires_in_sec:
            expiry = info.expires_in_sec / 2
        else:
            expiry = 60

        # .. store the token ..
        self.cache.set(key, info, expiry=expiry)

        # .. make it known when exactly the key will expire ..
        expiry_in = timedelta(seconds=expiry)
        expiry_time = datetime.now(tz=timezone.utc) + expiry_in

        # .. log what we have done ..
        msg  = f'Bearer token for `{info.sec_def_name}` cached under key `{key}`'
        msg += f'; expiry={expiry} ({expiry_in} -> {expiry_time} UTC)'
        logger.info(msg)

        # .. and return the details to the caller.
        return expiry # type: ignore

# ################################################################################################################################

    def _get_bearer_token_info_impl(
        self,
        config,      # type: BearerTokenConfig
        scopes,      # type: str
        data_format, # type:str
    ) -> 'BearerTokenInfoResult':

        # Local variables
        result = BearerTokenInfoResult()

        # If we have the token in our cache, we can return it immediately ..
        if cache_entry := self._get_bearer_token_from_cache(config.sec_def_name, scopes):

            # .. assign the actual value ..
            result.info = cache_entry.value

            # .. indicate that it came from the cache ..
            result.is_cache_hit = True
            result.cache_hits = cache_entry.hits

            # .. build the remaining expiration time, in seconds ..
            # .. rounded down to make sure it does not take too much log space  ..
            cache_expiry = cache_entry.expires_at - time()
            cache_expiry = round(cache_expiry, 2)

            # .. now, can assign the expiration time ..
            result.cache_expiry = cache_expiry

            # .. and return the result to the caller.
            return result

        # .. we are here if the token was not in the cache ..
        else:

            # .. since the token was not cache, we need to obtain it from the auth server ..
            info = self._get_bearer_token_from_auth_server(config, scopes, data_format)

            # .. then we can cache it ..
            expiry = self._store_bearer_token_in_cache(info, scopes)

            # .. build the result ..
            result.info = info
            result.is_cache_hit = False
            result.cache_expiry = expiry

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
# ################################################################################################################################
