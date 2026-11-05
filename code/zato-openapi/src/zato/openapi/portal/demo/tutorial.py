# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import os
import sys
from argparse import ArgumentParser

# Zato
from zato.common.typing_ import cast_
from zato.common.util.api import get_client_from_server_conf

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Invoker_Service = 'zato.server.invoker'
    Function_Name   = 'import_demo_tutorial'

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':
    """ Sets up everything the main tutorial builds on a server, the same way the Dashboard does it.
    """
    parser = ArgumentParser()
    _ = parser.add_argument('--server-dir', required=True)
    args = parser.parse_args()

    server_dir = os.path.abspath(os.path.expanduser(args.server_dir))

    # The function name is sent as a dict so that the invoker receives it as a parsed object ..
    client = get_client_from_server_conf(server_dir)
    request = {'func_name': ModuleCtx.Function_Name}
    response = client.invoke(ModuleCtx.Invoker_Service, request)

    # .. the server could not run the import at all ..
    if not response.ok:
        print(response.details)
        sys.exit(1)

    # .. the import ran but either the service or the definitions are not in place ..
    result = cast_('anydict', response.data)

    if not result['service_deployed']:
        print('The tutorial service was not deployed - the hot-deploy listener must be running')
        sys.exit(1)

    if not result['is_ok']:
        print('The tutorial definitions were not imported - the server log has the details')
        sys.exit(1)

    # .. and everything is in place.
    print('API portal sign-in: your Dashboard username and password')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
