# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import subprocess
import sys
import tempfile
from http.client import BAD_REQUEST, INTERNAL_SERVER_ERROR
from logging import getLogger
from traceback import format_exc

# Django
from django.http import JsonResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.common.api import IDE_Ignore_Modules
from zato.common.json_internal import loads

if 0:
    from django.http import HttpRequest

logger = getLogger(__name__)

def build_lsp_message(content):
    """ Builds an LSP message with Content-Length header.
    """
    body = json.dumps(content)
    return 'Content-Length: {}\r\n\r\n{}'.format(len(body), body)

def parse_lsp_response(output):
    """ Parses LSP response from stdout, extracting JSON bodies.
    """
    results = []
    parts = output.split('Content-Length:')
    for part in parts:
        part = part.strip()
        if not part:
            continue
        header_end = part.find('\r\n\r\n')
        if header_end == -1:
            header_end = part.find('\n\n')
        if header_end == -1:
            continue
        json_body = part[header_end:].strip()
        if json_body:
            try:
                results.append(json.loads(json_body))
            except json.JSONDecodeError:
                continue
    return results

@method_allowed('POST')
def complete_python(req:'HttpRequest') -> 'JsonResponse':
    """ Runs Zuban LSP to get Python autocompletions for ACE editor.
    """
    try:
        body = loads(req.body)
    except Exception:
        logger.warning('Invalid request body: %s', format_exc())
        return JsonResponse({'success': False, 'error': 'Invalid request body'}, status=BAD_REQUEST)

    code = body.get('code', '')
    line = body.get('line', 1)
    column = body.get('column', 0)

    if not code:
        return JsonResponse({'success': True, 'completions': []})

    try:
        # .. find the stubs directory ..
        stubs_path = None
        for path in sys.path:
            if 'zato-server' in path and path.endswith('src'):
                # .. path is like /code/zato-server/src, stubs are in /code/stubs ..
                code_dir = os.path.dirname(os.path.dirname(path))
                stubs_path = os.path.join(code_dir, 'stubs')
                break

        if stubs_path and os.path.exists(stubs_path):
            fake_file_path = os.path.join(stubs_path, 'zato', 'server', '_ide_temp_service.py')
            root_uri = 'file://' + stubs_path
        else:
            fake_file_path = '/tmp/_ide_temp_service.py'
            root_uri = None

        file_uri = 'file://' + fake_file_path

        initialize_request = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'initialize',
            'params': {
                'processId': os.getpid(),
                'rootUri': root_uri,
                'capabilities': {
                    'textDocument': {
                        'completion': {
                            'completionItem': {
                                'snippetSupport': False
                            }
                        }
                    }
                },
                'initializationOptions': {
                    'mypy_path': [p for p in sys.path if 'zato' in p.lower()]
                }
            }
        }

        initialized_notification = {
            'jsonrpc': '2.0',
            'method': 'initialized',
            'params': {}
        }

        did_open_notification = {
            'jsonrpc': '2.0',
            'method': 'textDocument/didOpen',
            'params': {
                'textDocument': {
                    'uri': file_uri,
                    'languageId': 'python',
                    'version': 1,
                    'text': code
                }
            }
        }

        completion_request = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'textDocument/completion',
            'params': {
                'textDocument': {'uri': file_uri},
                'position': {'line': line - 1, 'character': column}
            }
        }

        shutdown_request = {
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'shutdown',
            'params': None
        }

        exit_notification = {
            'jsonrpc': '2.0',
            'method': 'exit',
            'params': None
        }

        lsp_input = ''
        lsp_input += build_lsp_message(initialize_request)
        lsp_input += build_lsp_message(initialized_notification)
        lsp_input += build_lsp_message(did_open_notification)
        lsp_input += build_lsp_message(completion_request)
        lsp_input += build_lsp_message(shutdown_request)
        lsp_input += build_lsp_message(exit_notification)

        env = os.environ.copy()
        if stubs_path and os.path.exists(stubs_path):
            env['PYTHONPATH'] = stubs_path
        else:
            zato_paths = []
            for p in sys.path:
                if 'zato' not in p.lower():
                    continue
                should_skip = False
                for ignore_module in IDE_Ignore_Modules:
                    if ignore_module in p.lower():
                        should_skip = True
                        break
                if not should_skip:
                    zato_paths.append(p)
            env['PYTHONPATH'] = ':'.join(zato_paths)
        env['ZUBAN_CRASH_ON_ERROR'] = '1'

        proc = subprocess.Popen(
            ['zuban', 'server'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )

        stdout, stderr = proc.communicate(input=lsp_input, timeout=10)

        logger.info('Zuban file_uri: %s', file_uri)
        logger.info('Zuban rootUri: %s', root_uri)
        logger.info('Zuban PYTHONPATH: %s', env.get('PYTHONPATH', ''))
        logger.info('Zuban stdout length: %s', len(stdout) if stdout else 0)
        logger.info('Zuban stderr: %s', stderr if stderr else 'empty')

        completions = []
        if stdout:
            responses = parse_lsp_response(stdout)
            for resp in responses:
                if resp.get('id') == 2:
                    lsp_result = resp.get('result')
                    logger.info('Zuban completion result for line %s col %s: %s', line, column, lsp_result)
                    if lsp_result:
                        items = []
                        if isinstance(lsp_result, dict):
                            items = lsp_result.get('items', [])
                        elif isinstance(lsp_result, list):
                            items = lsp_result

                        # .. allowed dunder methods for zato types ..
                        allowed_dunders = {'__getattr__', '__getitem__', '__dict__'}

                        kind_map = {
                            1: 'text',
                            2: 'method',
                            3: 'function',
                            4: 'constructor',
                            5: 'field',
                            6: 'variable',
                            7: 'class',
                            8: 'interface',
                            9: 'module',
                            10: 'property',
                            11: 'unit',
                            12: 'value',
                            13: 'enum',
                            14: 'keyword',
                            15: 'snippet',
                            16: 'color',
                            17: 'file',
                            18: 'reference',
                            19: 'folder',
                            20: 'enum_member',
                            21: 'constant',
                            22: 'struct',
                            23: 'event',
                            24: 'operator',
                            25: 'type_parameter'
                        }

                        regular_items = []
                        dunder_items = []

                        for item in items:
                            label = item.get('label', '')
                            kind = item.get('kind', 1)
                            detail = item.get('detail', '')
                            kind_str = kind_map.get(kind, 'text')

                            # .. filter dunders for zato types ..
                            is_dunder = label.startswith('__') and label.endswith('__')
                            if is_dunder:
                                if label in allowed_dunders:
                                    dunder_items.append({
                                        'name': label,
                                        'value': label,
                                        'type': kind_str,
                                        'detail': detail
                                    })
                            else:
                                regular_items.append({
                                    'name': label,
                                    'value': label,
                                    'type': kind_str,
                                    'detail': detail
                                })

                        # .. regular items first, then allowed dunders at the end ..
                        completions = regular_items + dunder_items
                    break

        return JsonResponse({'success': True, 'completions': completions})

    except subprocess.TimeoutExpired:
        logger.warning('Zuban completion timed out')
        return JsonResponse({'success': False, 'error': 'Completion timed out'}, status=INTERNAL_SERVER_ERROR)
    except FileNotFoundError:
        logger.warning('Zuban not found')
        return JsonResponse({'success': False, 'error': 'Zuban not installed'}, status=INTERNAL_SERVER_ERROR)
    except Exception:
        logger.warning('Zuban completion failed: %s', format_exc())
        return JsonResponse({'success': False, 'error': 'Completion failed'}, status=INTERNAL_SERVER_ERROR)
