# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from datetime import datetime, timezone
from http.client import INTERNAL_SERVER_ERROR
from traceback import format_exc

# Django
from django.http import JsonResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.common.api import AS2
from zato.common.defaults import default_cluster_id
from zato.common.util.xml_.keystore import load_certificates_pem

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# A certificate expiring within this many days is highlighted in red.
_expiry_warning_days = 30

# The services the page talks to
_service_get  = 'zato.channel.as2.keystore.get'
_service_edit = 'zato.channel.as2.keystore.edit'

# ################################################################################################################################
# ################################################################################################################################

def get_expiry_info(cert_chain:'str') -> 'anydict':
    """ Returns the not-after date of the first certificate in a pasted PEM chain,
    the number of days left until then and whether that is close enough to warn about.
    """

    # Our response to produce
    out:'anydict' = {
        'date': '',
        'days_left': None,
        'is_warning': False,
    }

    if not cert_chain:
        return out

    try:
        certificates = load_certificates_pem(cert_chain.encode('utf8'))

    # The chain is user-pasted text - anything that is not PEM is simply not displayed.
    except ValueError:
        return out

    first_certificate = certificates[0]
    not_after = first_certificate.not_valid_after_utc
    now = datetime.now(timezone.utc)

    days_left = (not_after - now).days

    out['date'] = not_after.strftime('%Y-%m-%d')
    out['days_left'] = days_left
    out['is_warning'] = days_left < _expiry_warning_days

    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req:'any_') -> 'TemplateResponse':
    """ Our own AS2 keystore - the signing pair, the current decryption key
    and the next decryption pair staged for rotation. The private keys never
    reach the page - only flags saying whether one is stored.
    """
    response = req.zato.client.invoke(_service_get)
    data = response.data

    # The expiry of our signing certificate and of the staged next certificate
    # is computed for display only.
    signing_expiry = get_expiry_info(data['as2_signing_cert_chain'])
    next_cert_expiry = get_expiry_info(data['as2_next_decryption_cert'])

    return_data = {
        'cluster_id': default_cluster_id,
        'as2_signing_cert_chain': data['as2_signing_cert_chain'],
        'as2_next_decryption_cert': data['as2_next_decryption_cert'],
        'has_as2_signing_key': data['has_as2_signing_key'],
        'has_as2_decryption_key': data['has_as2_decryption_key'],
        'has_as2_next_decryption_key': data['has_as2_next_decryption_key'],
        'signing_expiry': signing_expiry,
        'next_cert_expiry': next_cert_expiry,
        'zato_clusters': True,
        'zato_template_name': 'zato/as2-keystore.html',
    }

    out = TemplateResponse(req, 'zato/as2-keystore.html', return_data)

    return out

# ################################################################################################################################

@method_allowed('POST')
def save(req:'any_') -> 'JsonResponse':
    """ Persists the keystore fields on the inbound AS2 channel - an empty field clears
    the stored value, which is how the next decryption pair is removed after a rotation.
    """
    request = {}

    for name in AS2.Keystore_Fields:
        request[name] = req.POST[name]

    try:
        response = req.zato.client.invoke(_service_edit, request)

    # A genuinely broad boundary - whatever went wrong with the invocation,
    # the page must get a response it can display.
    except Exception:
        exception_info = format_exc()
        msg = f'Keystore could not be saved, e:`{exception_info}`'
        logger.error(msg)

        out = JsonResponse({'is_ok': False, 'message': msg}, status=INTERNAL_SERVER_ERROR)
        return out

    if not response.ok:
        out = JsonResponse({'is_ok': False, 'message': response.details}, status=INTERNAL_SERVER_ERROR)
        return out

    out = JsonResponse({'is_ok': True, 'message': 'Keystore saved'})

    return out

# ################################################################################################################################
# ################################################################################################################################
