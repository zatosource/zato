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
    """ Main entry point for the cron updater.
    """
    basicConfig(level=INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    config = UpdaterConfig()
    updater = Updater(config)

    #if not updater.should_run_scheduled_update():
    #    logger.info('No scheduled update needed at this time')
    #    return 0

    if not updater.acquire_lock():
        logger.info('Update already in progress')
        return 0

    try:
        schedule_result = updater.load_schedule()
        schedule_frequency = None
        if schedule_result['success'] and schedule_result.get('schedule'):
            schedule_frequency = schedule_result['schedule'].get('frequency', 'daily')

        result = updater.download_and_install(update_type='auto', schedule=schedule_frequency)

        if not result['success']:
            logger.error('Scheduled update failed: {}'.format(result.get('error', 'Unknown error')))
            return 1

        restart_result = updater.restart_all_components()

        if not restart_result['success']:
            logger.error('Component restart failed: {}'.format(restart_result.get('error', 'Unknown error')))
            return 1

        try:
            version_from = result.get('version_from', '')
            version_to = result.get('version_to', '')
            schedule = result.get('schedule', '')
            url = f'https://zato.io/support/updates/info-4.1.json?from={version_from}&to={version_to}&mode=auto'
            if schedule:
                url += f'&schedule={schedule}'
            requests.get(url, timeout=2)
        except Exception:
            pass

        return 0
    finally:
        updater.release_lock()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    sys.exit(main())

# ################################################################################################################################
# ################################################################################################################################
