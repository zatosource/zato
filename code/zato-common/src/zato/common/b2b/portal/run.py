# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
from importlib import import_module

# gunicorn
import gunicorn.app.base
import gunicorn.http.wsgi

# Zato
from zato.common.b2b.portal.config import Server_Name
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# ################################################################################################################################
# ################################################################################################################################

Env_Host = 'Zato_B2B_Portal_Host'
Env_Port = 'Zato_B2B_Portal_Port'

Default_Host = '0.0.0.0'
Default_Port = '8186'

_wsgi_module = 'zato.common.b2b.portal.wsgi'

# How many worker processes answer requests
_worker_count = 2

# ################################################################################################################################
# ################################################################################################################################

class PortalServer(gunicorn.app.base.BaseApplication):
    """ The gunicorn application serving the portal.
    """
    def __init__(self, app:'any_', options:'anydict') -> 'None':
        self.options = options
        self.application = app
        super().__init__()

# ################################################################################################################################

    def load_config(self) -> 'None':

        # The base class only fills the configuration in during __init__, so it is always present here.
        config = cast_('any_', self.cfg)

        for key, value in self.options.items():
            config.set(key.lower(), value)

# ################################################################################################################################

    def load(self) -> 'any_':
        return self.application

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':
    """ The entry point - serves the portal.
    """
    wsgi = import_module(_wsgi_module)

    host = os.environ.get(Env_Host, Default_Host)
    port = os.environ.get(Env_Port, Default_Port)

    # The server name is read from these module attributes when each response is written,
    # and the workers inherit the values from the master process.
    gunicorn_wsgi = cast_('any_', gunicorn.http.wsgi)
    gunicorn_wsgi.SERVER = Server_Name
    gunicorn_wsgi.SERVER_SOFTWARE = Server_Name

    options = {
        'bind': f'{host}:{port}',
        'workers': _worker_count,
        'preload_app': True,
        'errorlog': '-',
        'loglevel': 'warning',
    }

    logger.info('Serving on %s', options['bind'])
    PortalServer(wsgi.application, options).run()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
