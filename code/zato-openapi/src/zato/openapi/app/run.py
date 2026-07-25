# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import logging

# Zato
from zato.common.webapp.server import serve

# The WSGI module configures Django and warms the URL resolver up in this process, which is
# the master one, before any worker forks off it
from zato.openapi.app.wsgi import application

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

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':
    """ The entry point - serves the console.
    """
    serve(application, _app_name, Env_Host, Env_Port, Default_Host, Default_Port)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
