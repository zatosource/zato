# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import logging
from argparse import ArgumentParser
from importlib import import_module

# Zato
from zato.common.util.env import populate_environment_from_file
from zato.common.webapp.server import serve

# ################################################################################################################################
# ################################################################################################################################

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# ################################################################################################################################
# ################################################################################################################################

# The console binds on this address unless the environment overrides it
Env_Host = 'Zato_OpenAPI_Console_Host'
Env_Port = 'Zato_OpenAPI_Console_Port'

Default_Host = '0.0.0.0'
Default_Port = '8088'

# The name the startup line reports
_app_name = 'the OpenAPI console'

# The module that configures Django and builds the WSGI application
_wsgi_module = 'zato.openapi.app.wsgi'

# Each try-it request waits for a server's reply in a thread of its own
_thread_count = 32

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':
    """ The entry point - serves the console.
    """
    parser = ArgumentParser(description='Zato OpenAPI console')
    _ = parser.add_argument('--env-file', default='', help='Path to a file with environment variables to use')
    args = parser.parse_args()

    # The console's modules read their environment variables when they are imported,
    # so the variables from the file are in place before the WSGI module is loaded ..
    _ = populate_environment_from_file(args.env_file)

    # .. the WSGI module configures Django and warms the URL resolver up in this process, which is
    # .. the master one, before any worker forks off it.
    wsgi = import_module(_wsgi_module)

    serve(wsgi.application, _app_name, Env_Host, Env_Port, Default_Host, Default_Port, thread_count=_thread_count)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
