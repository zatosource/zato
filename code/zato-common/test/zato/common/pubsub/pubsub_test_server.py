# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import argparse
from logging import basicConfig, getLogger, INFO

# gevent
import gevent
from gevent import monkey; monkey.patch_all()

# gunicorn
from gunicorn.app.base import BaseApplication

# Zato
from zato.common.test.zato.common.pubsub.config import load_config
from zato.common.test.zato.common.pubsub.server import PubSubTestServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Dict, Optional
    from zato.common.test.zato.common.pubsub.config import AppConfig

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class GunicornApp(BaseApplication):
    """ Gunicorn application wrapper for the PubSub Test Server.
    """
    def __init__(self, app:'PubSubTestServer', options:'dict'=None) -> 'None':
        """ Initialize with app instance and options.
        """
        self.options = options or {}
        self.application = app
        super(GunicornApp, self).__init__()

    def load_config(self) -> 'None':
        """ Load Gunicorn configuration from provided options.
        """
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)

    def load(self) -> 'PubSubTestServer':
        """ Return the WSGI application.
        """
        return self.application

# ################################################################################################################################
# ################################################################################################################################

def parse_args() -> 'argparse.Namespace':
    """ Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='Zato PubSub Test Server')
    parser.add_argument('--config', type=str, required=True, help='Path to YAML config file')
    parser.add_argument('--log-level', type=str, default='INFO',
                      choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                      help='Log level')
    parser.add_argument('--workers', type=int, default=1, help='Number of Gunicorn worker processes')
    parser.add_argument('--timeout', type=int, default=30, help='Gunicorn worker timeout in seconds')
    parser.add_argument('--use-gunicorn', action='store_true', help='Use Gunicorn server')

    return parser.parse_args()

# ################################################################################################################################
# ################################################################################################################################

def setup_logging(log_level:'str'='INFO') -> 'None':
    """ Configure the logging system.
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    basicConfig(level=getattr(INFO, log_level, INFO), format=log_format)

# ################################################################################################################################
# ################################################################################################################################

def run_with_gevent(app:'PubSubTestServer') -> 'None':
    """ Run the server with gevent's WSGIServer.
    """
    app.run()

# ################################################################################################################################
# ################################################################################################################################

def run_with_gunicorn(app:'PubSubTestServer', workers:'int'=1, timeout:'int'=30) -> 'None':
    """ Run the server with Gunicorn.
    """
    options = {
        'bind': f"{app.config.server.host}:{app.config.server.port}",
        'workers': workers,
        'timeout': timeout,
        'worker_class': 'gevent',
    }

    logger.info(f"Starting Gunicorn with {workers} workers on {options['bind']}")
    GunicornApp(app, options).run()

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':
    """ Main entry point for the PubSub Test Server.
    """
    # Parse command line arguments
    args = parse_args()

    # Setup logging
    setup_logging(args.log_level)

    # Load configuration
    logger.info(f"Loading configuration from {args.config}")
    config = load_config(args.config)

    # Create server instance
    app = PubSubTestServer(config)

    # Run the server
    if args.use_gunicorn:
        run_with_gunicorn(app, args.workers, args.timeout)
    else:
        run_with_gevent(app)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == "__main__":
    main()

# ################################################################################################################################
# ################################################################################################################################
