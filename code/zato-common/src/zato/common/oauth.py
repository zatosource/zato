# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK
from json import loads

# gevent
from gevent.lock import RLock

# Requests
from requests import post as requests_post

# Zato
from zato.common.util.expiring_dict import ExpiringDict

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_, dictnone, intanydict, stranydict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    TTL = 40 * 60             # 40 minutes in seconds
    Impl_Cleanup_Interval = 5 # In seconds

    # This is used to join multiple scopes in an HTTP call that requests a new token to be generated
    Scopes_Separator = ' '

    # How many seconds to wait for the auth server to reply when requesting a new token
    Auth_Reply_Timeout = 20

    Test_Token = {
        'token_type': 'Bearer',
        'expires_in': 3600,
        'access_token': 'abc',
        'scope': 'zato.access'
    }

# ################################################################################################################################
# ################################################################################################################################

class OAuthTokenClient:

    def __init__(
        self,
        conn_name,       # type: str
        username,        # type: str
        secret,          # type: str
        auth_server_url, # type: str
        scopes           # type: str
    ) -> 'None':

        self.conn_name = conn_name
        self.username = username
        self.secret = secret
        self.auth = (self.username, self.secret)
        self.auth_server_url = auth_server_url
        self.scopes = (scopes or '').splitlines()

# ################################################################################################################################

    @staticmethod
    def from_config(config:'stranydict') -> 'OAuthTokenClient':
        out = OAuthTokenClient(**config)
        return out

# ################################################################################################################################

    @staticmethod
    def obtain_from_config(config:'stranydict') -> 'dictnone':
        client = OAuthTokenClient.from_config(config)
        token = client.obtain_token()
        return token

# ################################################################################################################################

    def obtain_token(self) -> 'dictnone':

        # All the metadata headers ..
        headers = {
            'Accept': 'application/json',
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        # .. POST data to request a new token ..
        post_data = {
            'grant_type': 'client_credentials',
            'scope': ModuleCtx.Scopes_Separator.join(self.scopes)
        }

        # .. request the token now ..
        response = requests_post(
            url=self.auth_server_url,
            auth=self.auth,
            data=post_data,
            headers=headers,
            verify=None,
            timeout=ModuleCtx.Auth_Reply_Timeout,
        )

        # .. make sure the response is as expected ..
        if response.status_code != OK:
            msg = 'OAuth token for `{}` ({}) could not be obtained -> {} -> {}'.format(
                self.conn_name,
                self.auth_server_url,
                response.status_code,
                response.text
            )
            raise ValueError(msg)

        # .. if we are here, it means that we do have a token,
        # .. so we can load it from JSON ..
        data = loads(response.text)

        # .. and return it to our caller.
        return data

# ################################################################################################################################
# ################################################################################################################################

class OAuthStore:

    def __init__(
        self,
        get_config_func, # type: callable_
        obtain_item_func, # type: callable_
    ) -> 'None':

        # This callable will return an OAuth definition's configuration based on its ID
        self.get_config_func = get_config_func

        # This callable is used to obtain an OAuth token from an auth server
        self.obtain_item_func = obtain_item_func

        # Keys are OAuth definition IDs and values are RLock objects
        self._lock_dict = {} # type: intanydict

        # This is where we actually keep tokens
        self._impl = ExpiringDict(ttl=ModuleCtx.TTL, interval=ModuleCtx.Impl_Cleanup_Interval)

# ################################################################################################################################

    def _get(self, item_id:'int') -> 'dictnone':
        item = self._impl.get(item_id)
        return item

# ################################################################################################################################

    def get(self, item_id:'int') -> 'dictnone':

        # This may be potentially missing ..
        item = self._get(item_id)

        # .. if it does not, we need to obtain it ..
        if not item:
            self.set(item_id)

            # .. now, we know that it will exist ..
            item = self._get(item_id)

        # .. finally, we can return it to our caller.
        return item

# ################################################################################################################################

    def _obtain_item(self, item_id:'int') -> 'dictnone':

        # We are going to keep iterating until we do obtain the item
        # or until we can no longer find the configuration for this item,
        # e.g. because it has been already deleted.
        while True:

            # Try to look the configuration by ID ..
            config = self.get_config_func(item_id)

            # .. if it is not found, it means that it no longer exists,
            # .. for instance, because it has been already deleted,
            # .. in which case, we have nothing to return ..
            if not config:
                return

            # .. if we are here, it means that configuration exists ..
            # .. so we can obtain the item now ..
            item = self.obtain_item_func(config)

            # .. return the obtained item, no matter what it was.
            return item

# ################################################################################################################################

    def set(self, item_id:'int') -> 'None':

        # First, try to obtain the item ..
        item = self._obtain_item(item_id)

        # .. if we do not have it, we can already return ..
        if not item:
            return

        # .. otherwise, we populate the expected data structures.
        else:
            self._lock_dict[item_id] = RLock()
            self._impl.set(item_id, item)

# ################################################################################################################################

    def delete(self, item_id:'int') -> 'None':

        # We still have the per-item lock here ..
        with self._lock_dict[item_id]:

            # .. remove the definition from the underlying implementation ..
            self._impl.delete(item_id)

        # .. finally, remove our own lock now.
        _ = self._lock_dict.pop(item_id, None)

# ################################################################################################################################
# ################################################################################################################################
