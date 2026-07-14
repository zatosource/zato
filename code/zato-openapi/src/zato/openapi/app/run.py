# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import logging
import os
import sys

# gunicorn
import gunicorn.app.base

# ################################################################################################################################
# ################################################################################################################################

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Logger for this module
logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class OpenAPIServer(gunicorn.app.base.BaseApplication):
    """ Custom Gunicorn application for serving OpenAPI spec with Swagger UI.
    """
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None: # type: ignore
                self.cfg.set(key.lower(), value) # type: ignore

    def load(self):
        return self.application

# ################################################################################################################################
# ################################################################################################################################

def main():
    """ Main entry point for the OpenAPI console server.
    """
    # Set up Django settings module
    _ = os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zato.openapi.app.settings')

    # Add the parent directory to sys.path so Django can find the settings
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Import Django WSGI application
    from zato.openapi.app.wsgi import application

    # The console binds on this address unless the environment overrides it
    host = os.environ.get('Zato_OpenAPI_Console_Host', '0.0.0.0')
    port = os.environ.get('Zato_OpenAPI_Console_Port', '8088')

    # Set up Gunicorn options - the application must be preloaded in the master process
    # so that all workers share the same session signing and credential encryption keys.
    options = {
        'bind': f'{host}:{port}',
        'workers': 3,
        'preload_app': True,
        'accesslog': '-',  # Log to stdout
        'errorlog': '-',   # Log to stderr
        'loglevel': 'info',
    }

    # Start the server
    logger.info('Starting the OpenAPI console on %s', options['bind'])
    OpenAPIServer(application, options).run()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
