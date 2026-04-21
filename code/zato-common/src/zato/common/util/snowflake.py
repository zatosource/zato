# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

_rust_func = None

def _get_rust_func():
    global _rust_func
    if _rust_func is None:
        try:
            from zato_broker_core import broker_new_cid_pubsub
            _rust_func = broker_new_cid_pubsub
        except ImportError:
            import time, random
            def _fallback_cid(_precision):
                ts = int(time.time() * 1_000_000)
                rnd = random.randint(0, 0xFFFF)
                return f'{ts:016x}{rnd:04x}'
            _rust_func = _fallback_cid
    return _rust_func

# ################################################################################################################################
# ################################################################################################################################

def new_snowflake(suffix:'str', needs_machine_id:'bool'=False) -> 'str':
    return _get_rust_func()(4)

# ################################################################################################################################

def new_snowflake_rust(precision:'int'=4) -> 'str':
    return _get_rust_func()(precision)

# ################################################################################################################################
# ################################################################################################################################
