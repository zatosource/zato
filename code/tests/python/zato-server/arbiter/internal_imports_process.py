# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A process that imports the modules of a server as its arbiter does, imports the modules of the internal services,
# and writes to its standard output the modules that are not imported and the outcome of the check before the fork.

# stdlib
import json
import sys

# Zato
import zato.server.main # noqa: F401
from zato.common.util.api import find_internal_modules
from zato.server.arbiter_config import ArbiterError
from zato.server.arbiter_start import check_fork_ready, import_internal_service_modules, stop_threadpool
from zato.server.service import internal

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strlist

    anydict = anydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':

    # The modules are imported ..
    import_internal_service_modules()

    module_names = find_internal_modules(internal)
    missing_modules:'strlist' = []

    for module_name in module_names:
        if module_name not in sys.modules:
            missing_modules.append(module_name)

    # .. the arbiter stops the threads of the resolver before the fork, as run_arbiter does ..
    stop_threadpool()

    # .. and the check before the fork either passes or names what it found.
    try:
        check_fork_ready()
    except ArbiterError as e:
        fork_ready_error = str(e)
    else:
        fork_ready_error = ''

    module_count = len(module_names)

    result:'anydict' = {
        'module_count': module_count,
        'missing_modules': missing_modules,
        'fork_ready_error': fork_ready_error,
    }

    output = json.dumps(result)
    _ = sys.stdout.write(output)
    _ = sys.stdout.flush()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
