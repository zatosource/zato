# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
import sys
import tempfile
from logging import getLogger
from traceback import format_exc
from uuid import uuid4

# PyYAML
import yaml

# requests
import requests as requests_lib

# Django
from django.http import HttpResponse
from django.http.response import HttpResponseServerError

# Zato
from zato.admin.web.views import method_allowed
from zato.common.json_internal import dumps, loads
from zato.common.util import openapi_ as openapi_module

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def json_response(data, success=True):
    response_json = dumps(data)
    response_class = HttpResponse if success else HttpResponseServerError
    return response_class(response_json, content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def parse(req):

    response_data = {}
    response_data['success'] = False

    try:
        openapi_data = req.body.decode('utf-8')

        openapi_dir = os.path.dirname(os.path.abspath(openapi_module.__file__))
        parser_path = os.path.join(openapi_dir, 'parser.py')

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            _ = f.write(openapi_data)
            temp_file_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, parser_path, '--from-file', temp_file_path],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                error_msg = result.stderr or 'Parser returned non-zero exit code'
                response_data['error'] = error_msg
                return json_response(response_data, success=False)

            response_data['success'] = True
            response_data['result'] = result.stdout

            return json_response(response_data)

        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        logger.exception('parse exception')
        response_data['error'] = str(e)
        return json_response(response_data, success=False)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def fetch_url(req):

    response_data = {}
    response_data['success'] = False

    try:
        request_data = loads(req.body.decode('utf-8'))
        url = request_data['url']

        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url

        resp = requests_lib.get(url, timeout=30)
        resp.raise_for_status()

        response_data['success'] = True
        response_data['content'] = resp.text

        return json_response(response_data)

    except requests_lib.exceptions.RequestException as e:
        response_data['error'] = f'Failed to fetch URL: {e}'
        return json_response(response_data, success=False)

    except Exception as e:
        logger.exception('fetch_url exception')
        response_data['error'] = str(e)
        return json_response(response_data, success=False)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def import_objects(req):

    response_data = {}
    response_data['success'] = False

    try:
        import_data = req.body.decode('utf-8')
        parsed_data = loads(import_data)

        logger.info('import_objects: received data:\n%s', dumps(parsed_data, indent=2))

        enmasse_config = build_enmasse_config(parsed_data)
        enmasse_yaml = yaml.dump(enmasse_config, default_flow_style=False, sort_keys=False)

        logger.info('import_objects: enmasse YAML:\n%s', enmasse_yaml)

        server_path = os.path.expanduser('~/env/qs-1/server1')

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            _ = f.write(enmasse_yaml)
            enmasse_file_path = f.name

        try:
            cmd = ['zato', 'enmasse', server_path, '--import', '--input', enmasse_file_path, '--verbose']
            logger.info('enmasse command: %s', ' '.join(cmd))

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )

            logger.info('enmasse returncode: %s', result.returncode)
            logger.info('enmasse stdout:\n%s', result.stdout)
            logger.info('enmasse stderr:\n%s', result.stderr)

            if result.returncode != 0:
                error_msg = result.stderr or 'Enmasse returned non-zero exit code'
                response_data['error'] = error_msg
                return json_response(response_data, success=False)

        except Exception:
            logger.error('enmasse exception:\n%s', format_exc())
            response_data['error'] = format_exc()
            return json_response(response_data, success=False)

        finally:
            if os.path.exists(enmasse_file_path):
                os.unlink(enmasse_file_path)

        response_data['success'] = True
        response_data['message'] = 'Import completed'

        return json_response(response_data)

    except Exception as e:
        logger.exception('import_objects exception')
        response_data['error'] = str(e)
        return json_response(response_data, success=False)

# ################################################################################################################################
# ################################################################################################################################

def build_enmasse_config(items):

    enmasse_config = {
        'security': [],
        'outgoing_rest': []
    }

    security_defs = {}

    for item in items:
        server = item['server']
        name = item['name']
        path = item['path']
        auth = item['auth']
        auth_server_url = item.get('auth_server_url', '')
        content_type = item.get('content_type', 'application/json')

        data_format = 'json'
        if 'xml' in content_type.lower():
            data_format = 'xml'

        outgoing_rest_item = {
            'name': name,
            'host': server,
            'url_path': path,
            'data_format': data_format,
            'timeout': 600
        }

        if auth:
            sec_name = f'openapi.{auth}.{name}'
            outgoing_rest_item['security'] = sec_name

            if sec_name not in security_defs:
                sec_type = map_auth_to_security_type(auth)
                sec_def = {
                    'name': sec_name,
                    'type': sec_type,
                    'username': f'{sec_type}_user_{name.replace(" ", "_").lower()}',
                    'password': uuid4().hex
                }
                if sec_type == 'basic_auth':
                    sec_def['realm'] = 'OpenAPI'
                elif sec_type == 'bearer_token' and auth_server_url:
                    sec_def['auth_server_url'] = auth_server_url
                security_defs[sec_name] = sec_def

        enmasse_config['outgoing_rest'].append(outgoing_rest_item)

    for sec_def in security_defs.values():
        enmasse_config['security'].append(sec_def)

    if not enmasse_config['security']:
        del enmasse_config['security']

    return enmasse_config

# ################################################################################################################################
# ################################################################################################################################

def map_auth_to_security_type(auth):
    auth_lower = auth.lower()
    if 'basic' in auth_lower:
        return 'basic_auth'
    elif 'bearer' in auth_lower or 'oauth' in auth_lower:
        return 'bearer_token'
    elif 'api' in auth_lower and 'key' in auth_lower:
        return 'apikey'
    elif 'ntlm' in auth_lower:
        return 'ntlm'
    else:
        return 'basic_auth'

# ################################################################################################################################
# ################################################################################################################################
