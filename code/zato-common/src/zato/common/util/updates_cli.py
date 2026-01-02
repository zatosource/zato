# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sys
from logging import basicConfig, getLogger, INFO

# requests
import requests

# Zato
from zato.common.util.updates import Updater, UpdaterConfig

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'int':
    """ Main entry point for the CLI updater.
    """
    basicConfig(level=INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    config = UpdaterConfig()
    updater = Updater(config)
    
    result = updater.download_and_install(update_type='cli')
    
    if not result['success']:
        logger.error('Update failed: {}'.format(result.get('error', 'Unknown error')))
        return 1
    
    restart_result = updater.restart_all_components()
    
    if not restart_result['success']:
        logger.error('Component restart failed: {}'.format(restart_result.get('error', 'Unknown error')))
        return 1
    
    try:
        version_from = result.get('version_from', '')
        version_to = result.get('version_to', '')
        url = f'https://zato.io/support/updates/info-4.1.json?from={version_from}&to={version_to}&mode=cli&schedule=cli'
        requests.get(url, timeout=2)
    except Exception:
        pass
    
    return 0

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    sys.exit(main())

# ################################################################################################################################
# ################################################################################################################################
