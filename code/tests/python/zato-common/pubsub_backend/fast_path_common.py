# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# gevent
from gevent import sleep

# Zato
from zato.common.pubsub.sql.fast_path import FastPath

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection
    from zato.common.pubsub.sql.backend import SQLPubSubBackend
    from zato.common.pubsub.sql.fast_path import FastPathClaims, intpublicationdict, PushTarget
    from zato.common.typing_ import anylist, callable_, callnone, strlist

# ################################################################################################################################
# ################################################################################################################################

# How long one wait for an expected outcome may take at most, in seconds
Wait_Timeout_Seconds = 30

# How long one polling sleep is, in seconds
_poll_interval_seconds = 0.01

# ################################################################################################################################
# ################################################################################################################################

class ClaimFailed(Exception):
    """ Raised by a claim that a scenario fails on purpose, after the claim inserted its rows.
    """

# ################################################################################################################################
# ################################################################################################################################

class HookedFastPath(FastPath):
    """ The fast path of a backend that a scenario observes - it records the sub keys of the push greenlets that
    registered, runs a hook after each claim and fails the given number of claims after their inserts.
    """
    fail_count: 'int'
    on_claimed: 'callnone'
    registered_push_keys: 'strlist'

    def claim(
        self,
        claims:'FastPathClaims',
        connection:'Connection',
        published:'intpublicationdict',
        delivery_rows:'anylist',
        ) -> 'anylist':

        out = super().claim(claims, connection, published, delivery_rows)

        if self.on_claimed:
            self.on_claimed()

        if self.fail_count > 0:
            self.fail_count -= 1
            raise ClaimFailed('Claim failed on purpose')

        return out

# ################################################################################################################################

    def add_push_target(self, sub_key:'str', max_messages:'int', max_len:'int') -> 'PushTarget':
        self.registered_push_keys.append(sub_key)

        out = super().add_push_target(sub_key, max_messages, max_len)
        return out

# ################################################################################################################################
# ################################################################################################################################

def install_hooked_fast_path(backend:'SQLPubSubBackend') -> 'HookedFastPath':
    """ Gives the backend and its writer a fast path that the scenario observes, in place of the one they share.
    """
    out = HookedFastPath(
        subscription_list=backend.subscription_list,
        payload_cache=backend.payload_cache,
        get_sub_event=backend.get_sub_event,
        on_leased=backend._on_leased,
        build_message=backend._build_message_from_row,
        load_payload=backend._load_payload_from_row,
    )

    out.fail_count = 0
    out.on_claimed = None
    out.registered_push_keys = []

    backend.fast_path = out
    backend._writer.fast_path = out

    return out

# ################################################################################################################################

def wait_until(condition:'callable_', description:'str') -> 'None':
    """ Polls until the condition holds, failing if it does not in time.
    """
    deadline = monotonic() + Wait_Timeout_Seconds

    while monotonic() < deadline:

        if condition():
            return

        sleep(_poll_interval_seconds)

    raise AssertionError(f'Timed out waiting until {description}')

# ################################################################################################################################
# ################################################################################################################################
