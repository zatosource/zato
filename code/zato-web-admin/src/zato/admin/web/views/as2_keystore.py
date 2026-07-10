# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from datetime import datetime, timezone
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

def _get_expiry_info(cert_chain:'str') -> 'anydict':
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
    except Exception:
        return out

    not_after = certificates[0].not_valid_after_utc
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
    and the next decryption pair staged for rotation.
    """
    response = req.zato.client.invoke(_service_get)
    data = response.data

    # The expiry of our signing certificate and of the staged next certificate
    # is computed for display only.
    signing_expiry = _get_expiry_info(data['as2_signing_cert_chain'])
    next_cert_expiry = _get_expiry_info(data['as2_next_decryption_cert'])

    return_data = {
        'cluster_id': default_cluster_id,
        'as2_signing_key': data['as2_signing_key'],
        'as2_signing_cert_chain': data['as2_signing_cert_chain'],
        'as2_decryption_key': data['as2_decryption_key'],
        'as2_next_decryption_key': data['as2_next_decryption_key'],
        'as2_next_decryption_cert': data['as2_next_decryption_cert'],
        'signing_expiry': signing_expiry,
        'next_cert_expiry': next_cert_expiry,
        'zato_clusters': True,
        'zato_template_name': 'zato/as2-keystore.html',
    }

    return TemplateResponse(req, 'zato/as2-keystore.html', return_data)

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
    except Exception:
        msg = 'Keystore could not be saved, e:`{}`'.format(format_exc())
        logger.error(msg)
        return JsonResponse({'is_ok': False, 'message': msg}, status=500)

    if not response.ok:
        return JsonResponse({'is_ok': False, 'message': response.details}, status=500)

    return JsonResponse({'is_ok': True, 'message': 'Keystore saved'})

# ################################################################################################################################
# ################################################################################################################################
