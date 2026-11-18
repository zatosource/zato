# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The services that the repositories linked to an installation run when a server starts, in addition to those
# that the [startup_services] stanza of server.conf lists. Each one runs only on a server that is configured for it.

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_, strlist
    callable_ = callable_
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# Each registered service with the function that returns whether a server is configured for it.
_registry:'list[tuple[str, callable_]]' = []

# ################################################################################################################################
# ################################################################################################################################

def register_startup_service(name:'str', is_configured:'callable_') -> 'None':
    """ Registers a service that a server runs when it starts, if the given function returns True in that server.
    """
    _registry.append((name, is_configured))

# ################################################################################################################################

def get_startup_services() -> 'strlist':
    """ Returns the names of the registered services for which this server is configured.
    """
    out:'strlist' = []

    for name, is_configured in _registry:
        if is_configured():
            out.append(name)

    return out

# ################################################################################################################################
# ################################################################################################################################
