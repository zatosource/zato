# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
from gevent.lock import RLock

# Requests
from requests import post as requests_post

# Zato
from zato.common.util.expiring_dict import ExpiringDict

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_, dictnone, intanydict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    TTL = 40 * 60             # 40 minutes in seconds
    Impl_Cleanup_Interval = 5 # In seconds

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
        username,        # type: str
        secret,          # type: str
        auth_server_url, # type: str
        scopes           # type: str
    ) -> 'None':

        self.username = username
        self.secret = secret
        self.auth_server_url = auth_server_url
        self.scopes = scopes

# ################################################################################################################################

    def obtain_token(self) -> 'dictnone':

        post_data = {
            'grant_type': 'client_credentials',
            'scope': self.scopes,
        }

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

    def get(self, item_id:'int') -> 'stranydict':
        return self._impl.get(item_id)

# ################################################################################################################################

    def set(self, item_id:'int') -> 'None':
        self._lock_dict[item_id] = RLock()
        token = ModuleCtx.Test_Token
        self._impl.set(item_id, token)

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
