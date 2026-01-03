# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from logging import getLogger

from zato.admin.web.views.settings.utils import json_response, restart_component

logger = getLogger(__name__)

class RestartHandler:

    def __init__(self, updater):
        self.updater = updater

    def _restart(self, req, component_name):
        component_path = self.updater.get_component_path(component_name)
        component_port = self.updater.get_component_port(component_name)
        return restart_component(req, self.updater, component_name, component_path, component_port)

    def restart_scheduler(self, req):
        return self._restart(req, 'scheduler')

    def restart_server(self, req):
        return self._restart(req, 'server')

    def restart_proxy(self, req):
        return self._restart(req, 'proxy')

    def restart_dashboard(self, req):
        import subprocess
        import threading
        import os

        logger.info('restart_dashboard: called from client: {}'.format(req.META.get('REMOTE_ADDR')))

        def restart_after_delay():
            import time
            import redis
            import requests
            from logging import getLogger
            time.sleep(1)

            try:
                r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
                version_from = r.get('zato:update:version_from') or ''
                version_to = r.get('zato:update:version_to') or ''
                schedule = r.get('zato:update:schedule') or 'manual'
                if version_from and version_to:
                    url = f'https://zato.io/support/updates/info-4.1.json?from={version_from}&to={version_to}&mode=manual&schedule={schedule}'
                    _ = requests.get(url, timeout=2)
            except Exception:
                pass

            update_logger = getLogger('zato.common.util.updates')

            update_logger.info('')
            update_logger.info('#' * 80)
            update_logger.info('##' + ' ' * 76 + '##')
            update_logger.info('##' + ' ' * 21 + 'UPDATE COMPLETED' + ' ' * 39 + '##')
            update_logger.info('##' + ' ' * 76 + '##')
            update_logger.info('#' * 80)
            update_logger.info('')

            logger.info('restart_dashboard: executing make restart-dashboard')
            try:
                makefile_dir = os.path.expanduser('~/projects/zatosource-zato/4.1')
                logger.info('restart_dashboard: makefile_dir={}'.format(makefile_dir))
                result = subprocess.run(
                    ['make', 'restart-dashboard'],
                    cwd=makefile_dir,
                    capture_output=True,
                    text=True
                )
                logger.info('restart_dashboard: returncode={}'.format(result.returncode))
                logger.info('restart_dashboard: stdout={}'.format(result.stdout))
                if result.stderr:
                    logger.error('restart_dashboard: stderr={}'.format(result.stderr))
            except Exception as e:
                logger.error('restart_dashboard: failed to execute make: {}'.format(e))

        thread = threading.Thread(target=restart_after_delay, daemon=True)
        thread.start()

        result = {
            'success': True,
            'message': 'Dashboard restarting'
        }
        return json_response(result, success=True)

class ScheduleHandler:

    def __init__(self, updater):
        self.updater = updater

    def save(self, req):
        from zato.common.json_internal import loads
        body = req.body.decode('utf-8')
        schedule_data = loads(body)
        result = self.updater.save_schedule(schedule_data)
        return json_response(result, success=result['success'])

    def load(self, req):
        result = self.updater.load_schedule()
        return json_response(result, success=result['success'])

    def delete(self, req):
        result = self.updater.delete_schedule()
        return json_response(result, success=result['success'])

class AuditLogHandler:

    def __init__(self, updater):
        self.updater = updater

    def get_latest_entry(self, req):
        entries = self.updater.get_audit_log_entries(1)
        if entries:
            return json_response({'success': True, 'entry': entries[0]})
        else:
            return json_response({'success': True, 'entry': None})

    def get_refresh(self, req):
        entries = self.updater.get_audit_log_entries(3)
        return json_response({'success': True, 'entries': entries})
