# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import subprocess
import tempfile
from logging import getLogger

# Django
from django.http import JsonResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.common.json_internal import loads

if 0:
    from django.http import HttpRequest

logger = getLogger(__name__)

@method_allowed('POST')
def lint_python(req:'HttpRequest') -> 'JsonResponse':
    """ Runs Ruff linter on Python code and returns annotations for ACE editor.
    """
    try:
        body = loads(req.body)
    except Exception as e:
        logger.warning('Invalid request body: %s', e)
        return JsonResponse({'success': False, 'error': 'Invalid request body'}, status=400)

    code = body.get('code', '')
    if not code:
        return JsonResponse({'success': True, 'annotations': []})

    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name

        result = subprocess.run(
            ['ruff', 'check', '--output-format=json', '--no-fix', temp_path],
            capture_output=True,
            text=True,
            timeout=10
        )

        annotations = []
        markers = []
        if result.stdout:
            try:
                ruff_output = json.loads(result.stdout)
                for item in ruff_output:
                    row = item.get('location', {}).get('row', 1) - 1
                    column = item.get('location', {}).get('column', 0)
                    code_str = item.get('code', '')
                    message = item.get('message', '')
                    text = f'{code_str}: {message}' if code_str else message

                    annotations.append({
                        'row': row,
                        'column': column,
                        'text': text,
                        'type': 'error'
                    })

                    if code_str in ('F841', 'F401'):
                        end_location = item.get('end_location', {})
                        end_row = end_location.get('row', row + 1) - 1
                        end_column = end_location.get('column', column)
                        markers.append({
                            'startRow': row,
                            'startCol': column - 1,
                            'endRow': end_row,
                            'endCol': end_column - 1,
                            'type': 'unused'
                        })
            except json.JSONDecodeError:
                pass

        return JsonResponse({'success': True, 'annotations': annotations, 'markers': markers})

    except subprocess.TimeoutExpired:
        logger.warning('Ruff linting timed out')
        return JsonResponse({'success': False, 'error': 'Linting timed out'}, status=500)
    except FileNotFoundError:
        logger.warning('Ruff not found')
        return JsonResponse({'success': False, 'error': 'Ruff linter not installed'}, status=500)
    except Exception as e:
        logger.warning('Ruff linting failed: %s', e)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    finally:
        try:
            import os
            os.unlink(temp_path)
        except Exception:
            pass
