# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_, noreturn

    callable_ = callable_
    noreturn = noreturn

# ################################################################################################################################
# ################################################################################################################################

class _ReplacedState:
    """ What a process that an arbiter started calls once it learns that this server is no longer the active one,
    which tells its arbiter to drain its processes.
    """
    on_replaced: 'callable_ | None' = None

# ################################################################################################################################
# ################################################################################################################################

class PubSubReplaced(Exception):
    """ Raised by every transaction of a server that is no longer the active one, either because another server
    raised the generation of the pub/sub database or because the node of this server is no longer active.
    """

# ################################################################################################################################

def set_on_replaced(on_replaced:'callable_') -> 'None':
    """ Makes every later PubSubReplaced of this process call on_replaced before it is raised.
    """
    _ReplacedState.on_replaced = on_replaced

# ################################################################################################################################

def raise_replaced(message:'str') -> 'noreturn':
    """ Raises PubSubReplaced, after it tells the arbiter of this process, if the process has one.
    """
    if on_replaced := _ReplacedState.on_replaced:
        on_replaced()

    raise PubSubReplaced(message)

# ################################################################################################################################
# ################################################################################################################################
