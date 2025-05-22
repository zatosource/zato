# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import os

# Gunicorn
import gunicorn.app.base

# ################################################################################################################################
# ################################################################################################################################

class OpenAPIServer(gunicorn.app.base.BaseApplication):
    """ Gunicorn application to serve the OpenAPI Swagger UI.
    """
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

# ################################################################################################################################

def run_server():
    """ Runs the OpenAPI Swagger UI server using Gunicorn.
    """
    # Set Django settings module
    _ = os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zato.openapi.app.settings')

    # Import the WSGI application
    from zato.openapi.app.wsgi import application

    # Configure Gunicorn
    options = {
        'bind': '0.0.0.0:8088',
        'workers': 3,
        'worker_class': 'sync',
        'timeout': 30,
        'accesslog': '-',
        'errorlog': '-',
        'loglevel': 'info',
    }

    # Run the server
    OpenAPIServer(application, options).run()

# ################################################################################################################################

if __name__ == '__main__':
    run_server()

# ################################################################################################################################
# ################################################################################################################################
