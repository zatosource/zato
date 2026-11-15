# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The runner of the services that change configuration. In a worker of a multi-process server, the runner forwards
# such an invocation to the config process, and in the config process, it runs the invocation as the only change
# in progress. A process without a runner runs such a service as it runs any other.

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_

    callable_ = callable_

# ################################################################################################################################
# ################################################################################################################################

# The runner of the current process, called with the invoking service, the invoked one, the channel and the request context
_config_runner:'callable_ | None' = None

# ################################################################################################################################
# ################################################################################################################################

def bind_config_runner(runner:'callable_') -> 'None':
    global _config_runner
    _config_runner = runner

# ################################################################################################################################

def get_config_runner() -> 'callable_ | None':
    return _config_runner

# ################################################################################################################################
# ################################################################################################################################
