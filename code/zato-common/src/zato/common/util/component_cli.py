# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

import sys
import os
from logging import basicConfig, getLogger, INFO

from zato.common.util.updates import Updater, UpdaterConfig

logger = getLogger(__name__)

def main() -> 'int':
    """ Main entry point for component management CLI.
    """
    basicConfig(level=INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if len(sys.argv) < 2:
        logger.error('Usage: component_cli.py <action> [component_name]')
        logger.error('Actions: stop-scheduler, restart-scheduler, stop-server, restart-server-with-scheduler')
        return 1

    action = sys.argv[1]

    config = UpdaterConfig()
    updater = Updater(config)

    if action == 'stop-scheduler':
        component_path = updater.get_component_path('scheduler')
        port = updater.get_component_port('scheduler')
        result = updater.stop_component('scheduler', component_path, port)

    elif action == 'restart-scheduler':
        component_path = updater.get_component_path('scheduler')
        port = updater.get_component_port('scheduler')
        result = updater.restart_component('scheduler', component_path, port, check_changes=False)

    elif action == 'stop-server':
        component_path = updater.get_component_path('server')
        port = updater.get_component_port('server')
        result = updater.stop_component('server', component_path, port)

    elif action == 'restart-server-with-scheduler':
        server_path = updater.get_component_path('server')
        server_port = updater.get_component_port('server')
        scheduler_path = updater.get_component_path('scheduler')
        scheduler_port = updater.get_component_port('scheduler')

        server_result = updater.stop_component('server', server_path, server_port)
        if not server_result['success']:
            logger.error('Failed to stop server: {}'.format(server_result.get('error', 'Unknown error')))
            return 1

        scheduler_result = updater.stop_component('scheduler', scheduler_path, scheduler_port)
        if not scheduler_result['success']:
            logger.error('Failed to stop scheduler: {}'.format(scheduler_result.get('error', 'Unknown error')))
            return 1

        server_result = updater.start_component('server', server_path)
        if not server_result['success']:
            logger.error('Failed to start server: {}'.format(server_result.get('error', 'Unknown error')))
            return 1

        scheduler_result = updater.start_component('scheduler', scheduler_path)
        if not scheduler_result['success']:
            logger.error('Failed to start scheduler: {}'.format(scheduler_result.get('error', 'Unknown error')))
            return 1

        result = {'success': True}

    elif action == 'stop-dashboard':
        component_path = updater.get_component_path('dashboard')
        port = updater.get_component_port('dashboard')
        result = updater.stop_component('dashboard', component_path, port)

    elif action == 'restart-dashboard':
        component_path = updater.get_component_path('dashboard')
        port = updater.get_component_port('dashboard')
        result = updater.restart_component('dashboard', component_path, port, check_changes=False)

    else:
        logger.error('Unknown action: {}'.format(action))
        return 1

    if not result['success']:
        logger.error('Action {} failed: {}'.format(action, result.get('error', 'Unknown error')))
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())
