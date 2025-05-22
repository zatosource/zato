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
    """ Main entry point for the OpenAPI server.
    """
    # Set up Django settings module
    _ = os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zato.openapi.app.settings')

    # Add the parent directory to sys.path so Django can find the settings
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Import Django WSGI application
    from zato.openapi.app.wsgi import application

    # Check if OpenAPI spec exists
    openapi_path = os.environ.get('Zato_OpenAPI_Path', '/tmp/openapi.yaml')
    if not os.path.exists(openapi_path):
        logger.warning('OpenAPI specification file not found at %s', openapi_path)
        logger.info('Please run "make openapi /path/to/services" first')

    # Set up Gunicorn options
    options = {
        'bind': '0.0.0.0:8088',
        'workers': 3,
        'accesslog': '-',  # Log to stdout
        'errorlog': '-',   # Log to stderr
        'loglevel': 'info',
    }

    # Start the server
    logger.info('Starting OpenAPI server on %s', options['bind'])
    logger.info('Serving OpenAPI spec from %s', openapi_path)
    OpenAPIServer(application, options).run()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
