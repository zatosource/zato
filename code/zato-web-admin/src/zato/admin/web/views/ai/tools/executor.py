# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import re
import subprocess
import tempfile
import time
from logging import getLogger
from traceback import format_exc

# PyYAML
import yaml

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_tool_to_enmasse_key = {
    'create_security': 'security',
    'create_channel_rest': 'channel_rest',
    'create_outgoing_rest': 'outgoing_rest',
    'create_scheduler': 'scheduler',
    'create_sql': 'sql',
    'create_cache': 'cache',
    'create_groups': 'groups',
    'create_email_smtp': 'email_smtp',
    'create_email_imap': 'email_imap',
    'create_odoo': 'odoo',
    'create_elastic_search': 'elastic_search',
    'create_confluence': 'confluence',
    'create_jira': 'jira',
    'create_ldap': 'ldap',
    'create_microsoft_365': 'microsoft_365',
    'create_outgoing_soap': 'outgoing_soap',
    'create_pubsub_topic': 'pubsub_topic',
    'create_pubsub_subscription': 'pubsub_subscription',
    'create_pubsub_permission': 'pubsub_permission',
    'create_channel_openapi': 'channel_openapi',
}

# ################################################################################################################################
# ################################################################################################################################

def execute_enmasse_batch(tool_calls:'list') -> 'anydict':
    """ Executes multiple enmasse tools in a single CLI call.
    """
    logger.info('Executing batch of %d enmasse tools', len(tool_calls))

    yaml_config = {}

    for tool_name, arguments in tool_calls:
        enmasse_key = _tool_to_enmasse_key.get(tool_name)
        if not enmasse_key:
            return {
                'success': False,
                'error': f'Unknown tool: {tool_name}'
            }

        if enmasse_key not in yaml_config:
            yaml_config[enmasse_key] = []
        yaml_config[enmasse_key].append(arguments)

    try:
        file_content = yaml.dump(yaml_config)

        logger.info('Running enmasse CLI with file_content: %s', file_content)

        server_path = os.path.expanduser('~/env/qs-1/server1')

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        command = f'zato enmasse --import --input {temp_file_path} {server_path} --verbose --missing-wait-time 2'
        logger.info('Running command: %s', command)

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )

        logger.info('Command exit code: %s', result.returncode)
        logger.info('Command stdout: %s', result.stdout)
        logger.info('Command stderr: %s', result.stderr)

        is_ok = 'Enmasse OK' in result.stdout

        if is_ok:
            return {
                'success': True,
                'message': f'Created {len(tool_calls)} objects successfully'
            }
        else:
            error_msg = result.stderr or result.stdout or 'Enmasse import failed'
            return {
                'success': False,
                'error': error_msg
            }

    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Enmasse command timed out after 30 seconds'
        }

    except Exception:
        error_msg = format_exc()
        logger.warning('Tool execution failed: %s', error_msg)
        return {
            'success': False,
            'error': error_msg
        }

# ################################################################################################################################

def is_enmasse_tool(tool_name:'str') -> 'bool':
    """ Returns True if the tool is an enmasse tool.
    """
    return tool_name in _tool_to_enmasse_key

# ################################################################################################################################

def is_service_tool(tool_name:'str') -> 'bool':
    """ Returns True if the tool is a service deployment/deletion tool.
    """
    return tool_name in ('deploy_service', 'delete_service')

# ################################################################################################################################

def _extract_service_names(code:'str') -> 'list':
    """ Extracts service names from Python code by finding 'name = ...' in Service classes.
    """
    out = []
    pattern = re.compile(r"^\s*name\s*=\s*['\"]([^'\"]+)['\"]", re.MULTILINE)
    for match in pattern.finditer(code):
        out.append(match.group(1))
    return out

# ################################################################################################################################

def _wait_for_services_deployed(client:'any_', service_names:'list', timeout:'int'=20) -> 'tuple':
    """ Waits for all services to be deployed by polling zato.service.is-deployed.
    Returns (success, error_message).
    """
    if not client or not service_names:
        return True, None

    time.sleep(0.25)

    start_time = time.time()
    poll_interval = 0.25

    while time.time() - start_time < timeout:
        all_deployed = True
        for service_name in service_names:
            try:
                response = client.invoke('zato.service.is-deployed', {'name': service_name})
                if response.ok:
                    is_deployed = response.data.get('is_deployed', False)
                    if not is_deployed:
                        all_deployed = False
                        break
                else:
                    all_deployed = False
                    break
            except Exception as e:
                logger.warning('Error checking if service %s is deployed: %s', service_name, e)
                all_deployed = False
                break

        if all_deployed:
            logger.info('All services deployed: %s', service_names)
            return True, None

        time.sleep(poll_interval)

    server_log_path = os.path.expanduser('~/env/qs-1/server1/logs/server.log')
    error_lines = []
    try:
        with open(server_log_path, 'r') as f:
            lines = f.readlines()
            for line in lines[-50:]:
                if 'error' in line.lower() or 'exception' in line.lower():
                    error_lines.append(line.strip())
    except Exception as e:
        logger.warning('Could not read server log: %s', e)

    error_msg = f'Timeout waiting for services to deploy: {service_names}'
    if error_lines:
        error_msg += '\n\nRecent errors from server.log:\n' + '\n'.join(error_lines[-10:])

    return False, error_msg

# ################################################################################################################################

def _apply_edits(content:'str', edits:'list') -> 'tuple':
    """ Applies a list of search/replace edits to content.
    Returns (new_content, error_message). Error is None on success.
    """
    for edit in edits:
        old_text = edit.get('old', '')
        new_text = edit.get('new', '')
        if not old_text:
            return None, 'Edit has empty old text'
        if old_text not in content:
            return None, f'Text not found in file: {old_text[:100]}...'
        content = content.replace(old_text, new_text, 1)
    return content, None

# ################################################################################################################################

def execute_deploy_service(arguments:'anydict', client:'any_'=None) -> 'anydict':
    """ Deploys service files by writing them to the services directory.
    Supports both full code (for new files) and edits (for existing files).
    """
    files = arguments.get('files', [])
    if not files:
        return {'success': False, 'error': 'No files provided'}

    services_root = os.path.expanduser('~/env/qs-1/server1/pickup/code/impl/src/api')
    deployed_files = []
    deployed_details = []
    all_service_names = []

    try:
        for file_info in files:
            file_path = file_info.get('file_path', '')
            code = file_info.get('code', '')
            edits = file_info.get('edits', [])

            if not file_path:
                continue

            if not code and not edits:
                return {'success': False, 'error': f'File {file_path} has neither code nor edits'}

            full_path = os.path.join(services_root, file_path)
            full_path = os.path.normpath(full_path)

            if not full_path.startswith(services_root):
                return {'success': False, 'error': f'Invalid file path: {file_path}'}

            old_content = ''
            is_new = True
            if os.path.exists(full_path):
                is_new = False
                with open(full_path, 'r') as f:
                    old_content = f.read()

            if edits:
                if is_new:
                    return {'success': False, 'error': f'Cannot apply edits to non-existent file: {file_path}'}
                new_content, error = _apply_edits(old_content, edits)
                if error:
                    return {'success': False, 'error': f'Edit failed for {file_path}: {error}'}
            else:
                new_content = code

            dir_path = os.path.dirname(full_path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path)

            with open(full_path, 'w') as f:
                f.write(new_content)

            deployed_files.append(file_path)
            deployed_details.append({
                'file_path': file_path,
                'old_content': old_content,
                'new_content': new_content,
                'is_new': is_new
            })
            logger.info('Deployed service file: %s (is_new=%s, edits=%d)', full_path, is_new, len(edits))

            service_names = _extract_service_names(new_content)
            all_service_names.extend(service_names)
            logger.info('Extracted service names from %s: %s', file_path, service_names)

        if all_service_names:
            success, error = _wait_for_services_deployed(client, all_service_names)
            if not success:
                return {'success': False, 'error': error}

        len_deployed = len(deployed_files)
        file_word = 'file' if len_deployed == 1 else 'files'
        return {
            'success': True,
            'message': f'Deployed {len_deployed} {file_word}',
            'files': deployed_files,
            'details': deployed_details
        }

    except Exception:
        error_msg = format_exc()
        logger.warning('Service deployment failed: %s', error_msg)
        return {'success': False, 'error': error_msg}

# ################################################################################################################################

def execute_delete_service(arguments:'anydict') -> 'anydict':
    """ Deletes service files from the services directory.
    """
    file_paths = arguments.get('file_paths', [])
    if not file_paths:
        return {'success': False, 'error': 'No file paths provided'}

    services_root = os.path.expanduser('~/env/qs-1/server1/pickup/code/impl/src/api')
    deleted_files = []

    try:
        for file_path in file_paths:
            if not file_path:
                continue

            full_path = os.path.join(services_root, file_path)
            full_path = os.path.normpath(full_path)

            if not full_path.startswith(services_root):
                return {'success': False, 'error': f'Invalid file path: {file_path}'}

            if os.path.exists(full_path):
                os.remove(full_path)
                deleted_files.append(file_path)
                logger.info('Deleted service file: %s', full_path)

        len_deleted = len(deleted_files)
        file_word = 'file' if len_deleted == 1 else 'files'
        return {
            'success': True,
            'message': f'Deleted {len_deleted} {file_word}',
            'files': deleted_files
        }

    except Exception:
        error_msg = format_exc()
        logger.warning('Service deletion failed: %s', error_msg)
        return {'success': False, 'error': error_msg}

# ################################################################################################################################

def execute_service_tool(tool_name:'str', arguments:'anydict', client:'any_'=None) -> 'anydict':
    """ Executes a service deployment or deletion tool.
    """
    if tool_name == 'deploy_service':
        return execute_deploy_service(arguments, client)
    elif tool_name == 'delete_service':
        return execute_delete_service(arguments)
    else:
        return {'success': False, 'error': f'Unknown service tool: {tool_name}'}

# ################################################################################################################################
# ################################################################################################################################
