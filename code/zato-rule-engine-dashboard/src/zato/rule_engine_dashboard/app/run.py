# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os

# gunicorn
import gunicorn.app.base

# Zato
from zato.rule_engine_dashboard.app.bootstrap import bootstrap

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The dashboard binds on this address unless the environment overrides it
Env_Host = 'Zato_Rule_Engine_Dashboard_Host'
Env_Port = 'Zato_Rule_Engine_Dashboard_Port'

Default_Host = '0.0.0.0'
Default_Port = '8092'

# How many worker processes answer requests
_worker_count = 3

# ################################################################################################################################
# ################################################################################################################################

class DashboardServer(gunicorn.app.base.BaseApplication):
    """ The gunicorn application serving the rule engine dashboard.
    """
    def __init__(self, app:'any_', options:'anydict') -> 'None':
        self.options = options
        self.application = app
        super().__init__()

    def load_config(self) -> 'None':
        for key, value in self.options.items():
            self.cfg.set(key.lower(), value) # type: ignore[union-attr]

    def load(self) -> 'any_':
        return self.application

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':
    """ The entry point - bootstraps the application and serves it.
    """
    # Django, its tables, the root account and the rule engine's storage all come up first ..
    bootstrap()

    # .. the WSGI application can only be built once Django is configured ..

    # Django
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()

    if host := os.environ.get(Env_Host):
        pass
    else:
        host = Default_Host

    if port := os.environ.get(Env_Port):
        pass
    else:
        port = Default_Port

    # .. the application is preloaded in the master process so that all workers
    # .. share the same session signing key ..
    options = {
        'bind': f'{host}:{port}',
        'workers': _worker_count,
        'preload_app': True,
        'accesslog': '-',
        'errorlog': '-',
        'loglevel': 'info',
    }

    # .. and the server takes over from here.
    logger.info('Starting the rule engine dashboard on %s', options['bind'])
    DashboardServer(application, options).run()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
