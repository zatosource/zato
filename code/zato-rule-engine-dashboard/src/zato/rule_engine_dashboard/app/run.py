# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Django
from django.core.wsgi import get_wsgi_application

# Zato
from zato.common.webapp.server import serve
from zato.rule_engine_dashboard.app.bootstrap import bootstrap

# ################################################################################################################################
# ################################################################################################################################

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# ################################################################################################################################
# ################################################################################################################################

# The dashboard binds on this address unless the environment overrides it
Env_Host = 'Zato_Rule_Engine_Dashboard_Host'
Env_Port = 'Zato_Rule_Engine_Dashboard_Port'

Default_Host = '0.0.0.0'
Default_Port = '8092'

# The name the startup line reports
_app_name = 'the rule engine dashboard'

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':
    """ The entry point - bootstraps the application and serves it.
    """
    # Django, its tables, the root account and the rule engine's storage all come up first ..
    bootstrap()

    # .. the WSGI application can only be built once Django is configured, which bootstrap did ..
    application = get_wsgi_application()

    # .. and the shared server takes over from here.
    serve(application, _app_name, Env_Host, Env_Port, Default_Host, Default_Port)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
