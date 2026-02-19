# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import subprocess
import tempfile
from http.client import BAD_REQUEST, INTERNAL_SERVER_ERROR
from logging import getLogger
from traceback import format_exc

# Django
from django.http import JsonResponse

# Zato
from zato.admin.web.views import method_allowed
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

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name

        file_uri = 'file://' + temp_path

        initialize_request = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'initialize',
            'params': {
                'processId': None,
                'rootUri': None,
                'capabilities': {}
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

        result = subprocess.run(
            ['zuban', 'server'],
            input=lsp_input,
            capture_output=True,
            text=True,
            timeout=10
        )

        logger.info('Zuban stdout: %s', result.stdout[:500] if result.stdout else 'empty')
        logger.info('Zuban stderr: %s', result.stderr[:500] if result.stderr else 'empty')

        completions = []
        if result.stdout:
            responses = parse_lsp_response(result.stdout)
            for resp in responses:
                if resp.get('id') == 2:
                    lsp_result = resp.get('result')
                    if lsp_result:
                        items = []
                        if isinstance(lsp_result, dict):
                            items = lsp_result.get('items', [])
                        elif isinstance(lsp_result, list):
                            items = lsp_result

                        for item in items:
                            label = item.get('label', '')
                            kind = item.get('kind', 1)
                            detail = item.get('detail', '')

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
                            kind_str = kind_map.get(kind, 'text')

                            completions.append({
                                'name': label,
                                'value': label,
                                'type': kind_str,
                                'detail': detail
                            })
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
    finally:
        if temp_path:
            try:
                import os
                os.unlink(temp_path)
            except Exception:
                pass
