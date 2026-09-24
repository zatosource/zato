# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import time
from logging import basicConfig, getLogger, INFO
from traceback import format_exc

# Zato
from zato.common.lets_encrypt.client import obtain
from zato.common.lets_encrypt.config import get_check_interval, get_config, is_enabled
from zato.common.lets_encrypt.state import LockBusy

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Mode:
    Once = 'once'
    Loop = 'loop'

# ################################################################################################################################
# ################################################################################################################################

def run_once(environ:'strstrdict') -> 'None':
    """ Obtains the certificate before HAProxy starts, which is why nothing is reloaded.
    """
    if not is_enabled(environ):
        logger.info('Let\'s Encrypt is not enabled')
        return

    config = get_config(environ)
    _ = obtain(config, needs_reload=False)

# ################################################################################################################################

def run_loop(environ:'strstrdict') -> 'None':
    """ Renews the certificate whenever it is due, for as long as the container runs.
    """
    check_interval = get_check_interval(environ)

    while True:

        # The certificate was obtained a moment ago, when the container started ..
        time.sleep(check_interval)

        # .. Let's Encrypt may have been enabled or disabled in the Dashboard in the meantime ..
        if not is_enabled(environ):
            continue

        # .. and each check reads the configuration again, because the public IP address may have changed too.
        try:
            config = get_config(environ)
            _ = obtain(config, needs_reload=True)
        except LockBusy:
            logger.info('Certificate check skipped, another one is running')
        except Exception:
            logger.warning('Certificate check failed: %s', format_exc())

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    basicConfig(level=INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    environ = dict(os.environ)
    mode = sys.argv[1]

    if mode == Mode.Once:
        run_once(environ)
    elif mode == Mode.Loop:
        run_loop(environ)
    else:
        raise Exception(f'Unknown mode: {mode}')

# ################################################################################################################################
# ################################################################################################################################
