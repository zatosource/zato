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
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# How many worker processes answer requests
_worker_count = 3

# How many threads each worker process answers requests in, unless the application asks for more
_default_thread_count = 1

# ################################################################################################################################
# ################################################################################################################################

class WebAppServer(gunicorn.app.base.BaseApplication):
    """ The gunicorn application serving one of the standalone Zato web applications.
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

def serve(
    application:'any_',
    app_name:'str',
    env_host:'str',
    env_port:'str',
    default_host:'str',
    default_port:'str',
    thread_count:'int' = _default_thread_count,
    ) -> 'None':
    """ Serves a WSGI application under gunicorn, on the address the environment names.
    With more than one thread, gunicorn uses threaded workers, whose requests can take longer
    than the worker timeout.
    """
    if host := os.environ.get(env_host):
        pass
    else:
        host = default_host

    if port := os.environ.get(env_port):
        pass
    else:
        port = default_port

    # The application is preloaded in the master process so that all workers share the same
    # session signing and credential encryption keys. There is no access log, because every
    # screen and every endpoint says in its own log line what it opened or loaded, for whom,
    # while an access line per static asset says nothing beyond that.
    options = {
        'bind': f'{host}:{port}',
        'workers': _worker_count,
        'threads': thread_count,
        'preload_app': True,
        'errorlog': '-',
        'loglevel': 'info',
    }

    # .. and the server takes over from here.
    logger.info('Starting %s on %s', app_name, options['bind'])
    WebAppServer(application, options).run()

# ################################################################################################################################
# ################################################################################################################################
