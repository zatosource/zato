# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from datetime import datetime, timedelta
from http.client import OK
from json import loads

# gevent
from gevent import sleep
from gevent.lock import RLock

# Requests
from requests import post as requests_post

# Zato
from zato.common.typing_ import dataclass

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_, dictnone, intanydict, stranydict, strnone
    callable_ = callable_
    intanydict = intanydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # After how many seconds we will consider a token to have expired
    TTL = 40 * 60

    # This is used to join multiple scopes in an HTTP call that requests a new token to be generated
    Scopes_Separator = ' '

    # How many seconds to wait for the auth server to reply when requesting a new token
    Auth_Reply_Timeout = 20

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class StoreItem:
    parent_id: 'int'
    data: 'any_'
    creation_time: 'datetime'
    expiration_time: 'datetime'

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

        # Extract only the information that the client object expects on input
        client_config = {
            'conn_name': config['name'],
            'username': config['username'],
            'secret': config['password'],
            'auth_server_url': config['auth_server_url'],
            'scopes': config['scopes'],
        }
        out = OAuthTokenClient(**client_config)
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
            msg = 'OAuth token for `{}` ({}) could not be obtained -> code:{} -> {}'.format(
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
        get_config_func,  # type: callable_
        obtain_item_func, # type: callable_
        obtain_sleep_time = 5,          # type: int
        max_obtain_iters  = 1234567890, # type: int
    ) -> 'None':

        # This callable will return an OAuth definition's configuration based on its ID
        self.get_config_func = get_config_func

        # This callable is used to obtain an OAuth token from an auth server
        self.obtain_item_func = obtain_item_func

        # For how many seconds to sleep in each iteration when obtaining a token
        self.obtain_sleep_time = obtain_sleep_time

        # How many times at most we will try to obtain an individual token
        self.max_obtain_iters = max_obtain_iters

        # Keys are OAuth definition IDs and values are RLock objects
        self._lock_dict = {} # type: intanydict

        # This is where we actually keep tokens
        self._impl = {}

# ################################################################################################################################

    def create(self, item_id:'int') -> 'None':
        self._lock_dict[item_id] = RLock()

# ################################################################################################################################

    def _get(self, item_id:'int') -> 'StoreItem | None':
        item = self._impl.get(item_id)
        return item

# ################################################################################################################################

    def get(self, item_id:'int') -> 'StoreItem | None':

        # This will always exist ..
        lock = self._lock_dict[item_id]

        # .. make sure we are the only one trying to get the token ..
        with lock:

            # This may be potentially missing ..
            item = self._get(item_id)

            # .. if it does not, we need to obtain it ..
            if not item:
                item = self._set(item_id)

            # .. if we do have an item, we still need to check whether it is not time to renew it,
            # .. in which we case we need to obtain a new one anyway ..
            else:
                if self._needs_renew(item):
                    item = self._set(item_id)

            # .. finally, we can return it to our caller.
            return item

# ################################################################################################################################

    def get_auth_header(self, item_id:'int') -> 'strnone':
        item = self.get(item_id)
        if item:
            header = '{} {}'.format(item.data['token_type'], item.data['access_token'])
            return header

# ################################################################################################################################

    def _needs_renew(self, item:'StoreItem') -> 'bool':
        now = datetime.utcnow()
        needs_renew = now >= item.expiration_time
        return needs_renew

# ################################################################################################################################

    def _obtain_item(self, item_id:'int') -> 'StoreItem | None':

        # We are going to keep iterating until we do obtain the item,
        # or until we can no longer find the configuration for this item, e.g. because it has been already deleted,
        # or until we run out of iteration attempts.

        # We are just starting out
        current_iter = 0

        # By default, we are to run
        keep_running = True

        while keep_running:

            # Confirm whether we should still continue
            keep_running = current_iter < self.max_obtain_iters

            if not keep_running:
                break

            # First, let's increase it
            current_iter += 1

            # Try to look the configuration by ID ..
            config = self.get_config_func(item_id)

            # .. if it is not found, it means that it no longer exists,
            # .. for instance, because it has been already deleted,
            # .. in which case, we have nothing to return ..
            if not config:
                return

            # .. if we are here, it means that configuration exists ..
            # .. so we can obtain its underlying data now ..
            data = self.obtain_item_func(config)

            # .. if there is no item, we sleep for a while and retry again ..
            if not data:
                sleep(self.obtain_sleep_time)
                continue

            # .. otherwise, return the obtained item, no matter what it was.
            else:
                item = StoreItem()
                item.data = data
                item.parent_id = item_id
                item.creation_time = datetime.utcnow()
                item.expiration_time = item.creation_time + timedelta(seconds=ModuleCtx.TTL)
                return item

# ################################################################################################################################

    def _set(self, item_id:'int') -> 'StoreItem | None':

        # First, try to obtain the item ..
        item = self._obtain_item(item_id)

        # .. if we do not have it, we can explicitly return None ..
        if not item:
            return None

        # .. otherwise ..
        else:

            # .. we populate the expected data structures ..
            self._impl[item_id] = item

            # .. and return the item obtained.
            return item

# ################################################################################################################################

    def delete(self, item_id:'int') -> 'None':

        # We still have the per-item lock here ..
        with self._lock_dict[item_id]:

            # .. remove the definition from the underlying implementation ..
            _ = self._impl.pop(item_id, None)

        # .. finally, remove our own lock now.
        _ = self._lock_dict.pop(item_id, None)

# ################################################################################################################################
# ################################################################################################################################
