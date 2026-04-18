# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import getLogger

# Zato
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_service_name_prefix = 'zato.env-variables.'
_env_prefix = 'Zato_Test_Server_'

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):

    name = _service_name_prefix + 'get-list'

    def handle(self):
        items = sorted((key, value) for key, value in os.environ.items() if key.startswith(_env_prefix))
        self.response.payload = {
            'items': [{'key': key, 'value': value} for key, value in items]
        }

# ################################################################################################################################
# ################################################################################################################################

class Test(AdminService):

    name = _service_name_prefix + 'test'

    def handle(self):
        text = self.request.raw_request.get('variables', '')
        allow_delete = self.request.raw_request.get('allow_delete', False)

        if not text.strip():
            self.response.payload = {
                'success': False,
                'error': 'No variables provided',
                'results': [],
                'change_count': 0,
                'delete_count': 0,
            }
            return

        parsed = _parse_env_lines(text)
        results = []
        has_errors = False
        change_count = 0
        delete_count = 0

        submitted_keys = set()
        mentioned_in_errors = set()

        for key, value, raw_line, error in parsed:
            if error:
                has_errors = True
                results.append({
                    'label': raw_line,
                    'status': 'error',
                    'message': error,
                })
                bare = raw_line.strip().split('=')[0].strip()
                if bare:
                    mentioned_in_errors.add(bare)
            else:
                submitted_keys.add(key)
                current = os.environ.get(key)
                if current is None:
                    change_count += 1
                    results.append({
                        'label': key,
                        'status': 'new',
                        'message': value,
                    })
                elif current != value:
                    change_count += 1
                    results.append({
                        'label': key,
                        'status': 'changed',
                        'message': value,
                    })

        if allow_delete:
            current_keys = set(key for key in os.environ.keys() if key.startswith(_env_prefix))
            deleted_keys = sorted(current_keys - submitted_keys - mentioned_in_errors)
            delete_count = len(deleted_keys)
            for key in deleted_keys:
                results.append({
                    'label': key,
                    'status': 'delete',
                    'message': 'Will be deleted',
                })

        self.response.payload = {
            'success': not has_errors,
            'results': results,
            'change_count': change_count,
            'delete_count': delete_count,
        }

# ################################################################################################################################
# ################################################################################################################################

class Save(AdminService):

    name = _service_name_prefix + 'save'

    def handle(self):
        text = self.request.raw_request.get('variables', '')
        allow_delete = self.request.raw_request.get('allow_delete', False)

        if not text.strip():
            self.response.payload = {
                'success': False,
                'error': 'No variables provided',
            }
            return

        parsed = _parse_env_lines(text)
        set_count = 0
        delete_count = 0

        submitted_keys = set()

        for key, value, raw_line, error in parsed:
            if error:
                continue
            submitted_keys.add(key)
            os.environ[key] = value
            set_count += 1

        if allow_delete:
            current_keys = set(key for key in os.environ.keys() if key.startswith(_env_prefix))
            deleted_keys = current_keys - submitted_keys
            for key in deleted_keys:
                del os.environ[key]
                delete_count += 1

        logger.info('save: set %d, deleted %d environment variables', set_count, delete_count)

        self.response.payload = {
            'success': True,
            'message': '{} set, {} deleted'.format(set_count, delete_count),
        }

# ################################################################################################################################
# ################################################################################################################################

def _parse_env_lines(text):
    out = []
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' not in line:
            out.append((None, None, line, 'Missing "=" sign'))
            continue
        key, _, value = line.partition('=')
        key = key.strip()
        value = value.strip()
        if not key:
            out.append((None, None, line, 'Empty key'))
            continue
        out.append((key, value, line, None))
    return out
