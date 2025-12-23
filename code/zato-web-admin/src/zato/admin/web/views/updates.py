# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
from logging import getLogger
from traceback import format_exc

# Django
from django.http import HttpResponse
from django.http.response import HttpResponseServerError

# Zato
from zato.admin.web.views import method_allowed
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def run_command(req, command, cwd=None, timeout=30, log_prefix='command'):
    """
    Reusable function to run shell commands and return result.
    Only returns output if command fails.
    """

    logger.info('{}: called from client: {}'.format(log_prefix, req.META.get('REMOTE_ADDR')))
    logger.info('{}: command: {}'.format(log_prefix, command))
    logger.info('{}: cwd: {}'.format(log_prefix, cwd))

    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode != 0:
            logger.error('{}: command failed with exit code {}'.format(log_prefix, result.returncode))
            error_output = result.stdout + result.stderr
            logger.error('{}: error output: {}'.format(log_prefix, error_output))

            response_data = {
                'success': False,
                'error': error_output,
                'exit_code': result.returncode
            }

            response_json = dumps(response_data)
            response = HttpResponseServerError(response_json, content_type='application/json')
            return response

        logger.info('{}: command succeeded'.format(log_prefix))

        success_data = {'success': True}
        success_json = dumps(success_data)
        response = HttpResponse(success_json, content_type='application/json')
        return response

    except subprocess.TimeoutExpired:
        logger.error('{}: command timed out after {} seconds'.format(log_prefix, timeout))

        timeout_msg = 'Command timed out after {} seconds'.format(timeout)
        response_data = {
            'success': False,
            'error': timeout_msg
        }

        response_json = dumps(response_data)
        response = HttpResponseServerError(response_json, content_type='application/json')
        return response

    except Exception:
        logger.error('{}: exception: {}'.format(log_prefix, format_exc()))

        response_data = {
            'success': False,
            'error': 'Internal error occurred'
        }

        response_json = dumps(response_data)
        response = HttpResponseServerError(response_json, content_type='application/json')
        return response

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def download_updates(req):
    """
    Downloads updates and returns result. Only returns output if download fails.
    """

    current_dir = os.path.dirname(os.path.abspath(__file__))

    return run_command(
        req,
        command=['git', 'pull'],
        cwd=current_dir,
        timeout=999_999,
        log_prefix='download_updates'
    )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def install_updates(req):
    """
    Installs updates. Dummy command for now.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    return run_command(
        req,
        command=['git', 'pull'],
        cwd=current_dir,
        timeout=999_999,
        log_prefix='install_updates'
    )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def restart_scheduler(req):
    """
    Restarts scheduler. Dummy command for now.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    return run_command(
        req,
        command=['git', 'pull'],
        cwd=current_dir,
        timeout=999_999,
        log_prefix='restart_scheduler'
    )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def restart_server(req):
    """
    Restarts server. Dummy command for now.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    return run_command(
        req,
        command=['git', 'pull'],
        cwd=current_dir,
        timeout=999_999,
        log_prefix='restart_server'
    )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def restart_proxy(req):
    """
    Restarts proxy. Dummy command for now.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    return run_command(
        req,
        command=['git', 'pull'],
        cwd=current_dir,
        timeout=999_999,
        log_prefix='restart_proxy'
    )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def restart_dashboard(req):
    """
    Restarts dashboard. Dummy command for now.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    return run_command(
        req,
        command=['git', 'pull'],
        cwd=current_dir,
        timeout=999_999,
        log_prefix='restart_dashboard'
    )

# ################################################################################################################################
# ################################################################################################################################
