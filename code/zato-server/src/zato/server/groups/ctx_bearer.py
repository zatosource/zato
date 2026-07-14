# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from operator import attrgetter

# Zato
from zato.common.bearer_token_verifier import BearerTokenVerifier, build_verify_config
from zato.common.crypto.api import is_string_equal

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from gevent.lock import RLock
    from zato.common.model.security import BearerTokenVerifyConfig
    from zato.common.typing_ import boolnone, callable_, dict_, intnone, stranydict
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Sorts bearer token definitions by their names so JWT matching is deterministic
_by_sec_def_name = attrgetter('verify_config.sec_def_name')

# ################################################################################################################################
# ################################################################################################################################

class _BearerTokenSecDef:
    security_id: 'int'
    verify_config: 'BearerTokenVerifyConfig'

# ################################################################################################################################
# ################################################################################################################################

bearer_sec_def_list = list[_BearerTokenSecDef]

# ################################################################################################################################
# ################################################################################################################################

class BearerTokenCtx:
    """ Bearer token functionality mixed into SecurityGroupsCtx - a third credential container
    next to Basic Auth and API keys, with the same lifecycle.
    """
    # These are provided by SecurityGroupsCtx
    server: 'ParallelServer'
    _lock: 'RLock'
    _after_auth_created: 'callable_'
    _after_auth_deleted: 'callable_'

    # Maps security IDs to _BearerTokenSecDef objects
    bearer_token_credentials: 'dict_[int, _BearerTokenSecDef]'

    # Built on first use because the cache it needs may not exist yet when we are created
    _bearer_token_verifier: 'BearerTokenVerifier | None'

# ################################################################################################################################

    def _get_bearer_token_verifier(self) -> 'BearerTokenVerifier':
        """ Returns the bearer token verifier, building it on first use.
        """
        if not self._bearer_token_verifier:
            self._bearer_token_verifier = BearerTokenVerifier(self.server.config_manager.cache_api)

        return self._bearer_token_verifier

# ################################################################################################################################

    def check_security_bearer_token(self, cid:'str', channel_name:'str', token:'str') -> 'intnone':

        # Our response to produce
        out = None

        # Split the definitions into the static ones and the JWT ones ..
        static_items:'bearer_sec_def_list' = []
        jwt_items:'bearer_sec_def_list' = []

        for item in self.bearer_token_credentials.values():
            if item.verify_config.static_token:
                static_items.append(item)
            elif item.verify_config.audience:
                jwt_items.append(item)

        # .. static tokens go first, compared against every entry without stopping early ..
        # .. so that the time taken does not reveal whether a token exists or how much of it matched ..
        for item in static_items:
            if is_string_equal(token, item.verify_config.static_token):
                out = item.security_id

        # .. JWT definitions are tried in deterministic name order and the first full match wins ..
        if out is None:
            verifier = self._get_bearer_token_verifier()
            jwt_items.sort(key=_by_sec_def_name)

            for item in jwt_items:
                claims = verifier.verify(cid, channel_name, token, item.verify_config)
                if claims is not None:
                    out = item.security_id
                    break

        if out is None:
            logger.info(f'Invalid bearer token; channel={channel_name}; cid={cid}')

        return out

# ################################################################################################################################

    def _get_bearer_token_by_security_id(self, security_id:'int') -> '_BearerTokenSecDef | None':

        return self.bearer_token_credentials.get(security_id)

# ################################################################################################################################

    def _create_bearer_token(self, security_id:'int', sec_def:'stranydict') -> 'None':

        # Build a business object containing all the data needed in runtime ..
        item = _BearerTokenSecDef()
        item.security_id = security_id
        item.verify_config = build_verify_config(sec_def)

        # .. and add the business object to our container.
        self.bearer_token_credentials[security_id] = item

# ################################################################################################################################

    def _delete_bearer_token(self, security_id:'int') -> 'boolnone':

        # Continue only if we recognize such a bearer token definition ..
        if self._get_bearer_token_by_security_id(security_id):

            # .. delete the definition itself ..
            _ = self.bearer_token_credentials.pop(security_id, None)

            # .. remove it from maps too ..
            self._after_auth_deleted(security_id)

            # .. and indicate to our caller that we are done.
            return True

# ################################################################################################################################

    def delete_bearer_token(self, security_id:'int') -> 'None':
        _ = self._delete_bearer_token(security_id)

# ################################################################################################################################

    def set_bearer_token(self, security_id:'int', sec_def:'stranydict') -> 'None':

        # Continue only if we recognize such a bearer token definition ..
        if self._get_bearer_token_by_security_id(security_id):

            # .. and replace it with one built out of the newest definition.
            self._create_bearer_token(security_id, sec_def)

# ################################################################################################################################

    def _on_bearer_token_created(self, group_id:'int', security_id:'int', sec_def:'stranydict') -> 'None':

        # Create the base object ..
        self._create_bearer_token(security_id, sec_def)

        # .. and populate common containers.
        self._after_auth_created(group_id, security_id)

# ################################################################################################################################

    def on_bearer_token_created(self, group_id:'int', security_id:'int', sec_def:'stranydict') -> 'None':

        with self._lock:
            self._on_bearer_token_created(group_id, security_id, sec_def)

# ################################################################################################################################

    def set_current_bearer_token(self, security_id:'int', sec_def:'stranydict') -> 'None':
        with self._lock:
            self.set_bearer_token(security_id, sec_def)

# ################################################################################################################################

    def _on_bearer_token_deleted(self, security_id:'int') -> 'None':
        _ = self._delete_bearer_token(security_id)

# ################################################################################################################################

    def on_bearer_token_deleted(self, security_id:'int') -> 'None':
        with self._lock:
            _ = self._delete_bearer_token(security_id)

# ################################################################################################################################
# ################################################################################################################################
