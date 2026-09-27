# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http import HTTPStatus
from traceback import format_exc

# Django
from django.http import HttpResponseServerError, JsonResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.common.api import Lets_Encrypt
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_Template_Name = 'zato/ssl-config/index.html'

# ################################################################################################################################
# ################################################################################################################################

def _get_ssl_config(req:'any_') -> 'anydict':
    response = req.zato.client.invoke(Lets_Encrypt.Service.Get, {})
    out = response.data.ssl_config
    return out

# ################################################################################################################################

def _invoke(req:'any_', service_name:'str', request:'anydict', error_message:'str') -> 'any_':
    """ Invokes a service that only starts something and answers with the state of the page right after it did.
    """
    try:
        response = req.zato.client.invoke(service_name, request)
        if response.ok:
            ssl_config = _get_ssl_config(req)
            return JsonResponse({'status': 'ok', 'details': ssl_config})
        else:
            return JsonResponse({'status': 'error', 'message': response.details}, status=HTTPStatus.BAD_REQUEST)
    except Exception:
        exception_details = format_exc()
        msg = f'{error_message}, e:`{exception_details}`'
        logger.error(msg)
        return HttpResponseServerError(msg.encode('utf-8'))

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req:'any_') -> 'TemplateResponse':

    ssl_config = _get_ssl_config(req)

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'ssl_config': ssl_config,
        'ssl_config_json': dumps(ssl_config),
        'zato_template_name': _Template_Name,
    }

    return TemplateResponse(req, _Template_Name, return_data)

# ################################################################################################################################

@method_allowed('POST')
def refresh(req:'any_') -> 'JsonResponse':
    """ Answers the time-ago refresh, which asks about each of the cells on the page by its ID,
    and adds the whole state of the page for the rows that have no timestamps.
    """
    ssl_config = _get_ssl_config(req)
    certificate = ssl_config['certificate']
    status = ssl_config['status']

    if certificate is None:
        not_after_utc = None
    else:
        not_after_utc = certificate['not_after_utc']

    out = {
        'certificate': {'time_utc': not_after_utc},
        'last_check': {'time_utc': status['last_check_utc']},
        'port_check': {'time_utc': status['port_check_utc']},
        'details': ssl_config,
    }

    return JsonResponse(out)

# ################################################################################################################################

@method_allowed('GET')
def public_endpoint(req:'any_') -> 'JsonResponse':
    """ Answers the one request the page makes in the background after it loaded, because checking
    the public IP address and its DNS name means reaching out to the internet.
    """
    response = req.zato.client.invoke(Lets_Encrypt.Service.Get_Public_Endpoint, {})
    public_endpoint = response.data.public_endpoint

    out = {
        'public_ip': public_endpoint['public_ip'],
        'public_dns_name': public_endpoint['public_dns_name'],
    }

    return JsonResponse(out)

# ################################################################################################################################

@method_allowed('POST')
def set_lets_encrypt(req:'any_') -> 'any_':
    is_enabled = req.POST['is_enabled'] == 'true'
    out = _invoke(req, Lets_Encrypt.Service.Set_Lets_Encrypt, {'is_enabled': is_enabled},
        'Let\'s Encrypt could not be enabled or disabled')
    return out

# ################################################################################################################################

@method_allowed('POST')
def check_port(req:'any_') -> 'any_':
    out = _invoke(req, Lets_Encrypt.Service.Check_Port, {}, 'Port could not be checked')
    return out

# ################################################################################################################################
# ################################################################################################################################
