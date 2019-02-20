# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from json import dumps, loads

# Django
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.template.response import TemplateResponse

# PyOTP
import pyotp

# Zato
from zato.admin import zato_settings
from zato.admin.web.forms.account import BasicSettingsForm
from zato.admin.web.models import ClusterColorMarker
from zato.admin.web.views import method_allowed
from zato.common.crypto import CryptoManager

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

DEFAULT_PROMPT = 'Click to pick a color'

# ################################################################################################################################

profile_attrs = 'timezone', 'date_format', 'time_format'
profile_attrs_opaque = 'totp_key', 'totp_key_label'

# ################################################################################################################################

@method_allowed('GET')
def settings_basic(req):

    # Data for the template
    initial = {}

    # Process explicitly named attributes
    for attr in profile_attrs:
        initial[attr] = getattr(req.zato.user_profile, attr, None)

    # Process attributes from opaque data
    opaque_attrs = req.zato.user_profile.opaque1
    if opaque_attrs:
        opaque_attrs = loads(opaque_attrs)

        for attr in profile_attrs_opaque:
            initial[attr] = opaque_attrs.get(attr) or ''

    # Generate or use the existing TOTP key
    totp_key = initial.get('totp_key')
    if not totp_key:
        totp_key = pyotp.random_base32()
    else:
        cm = CryptoManager(secret_key=zato_settings.zato_secret_key)
        totp_key = cm.decrypt(totp_key)

    # Make sure TOTP key label is not empty
    totp_key_label = initial['totp_key_label']
    totp_key_label = totp_key_label or 'Zato web-admin'
    initial['totp_key_label'] = totp_key_label

    # Build the actual TOTP object for later use
    totp =  pyotp.totp.TOTP(totp_key)

    # Update template data with TOTP information
    initial['totp_key'] = totp.secret
    initial['totp_key_provision_uri'] = totp.provisioning_uri(req.user.username, issuer_name=totp_key_label)

    return_data = {
        'clusters': req.zato.clusters,
        'default_prompt': DEFAULT_PROMPT,
        'form':BasicSettingsForm(initial)
    }

    cluster_color_markers = req.zato.user_profile.cluster_color_markers.all()
    cluster_colors = {str(getattr(item, 'cluster_id')):getattr(item, 'color') for item in cluster_color_markers}
    return_data['cluster_colors'] = cluster_colors

    return TemplateResponse(req, 'zato/account/settings.html', return_data)

# ################################################################################################################################

@method_allowed('POST')
def settings_basic_save(req):

    # Process explicitly named attributes
    for attr in profile_attrs:
        # Use False as default value so as to convert blank checkboxes into a boolean value
        value = req.POST.get(attr, False)
        setattr(req.zato.user_profile, attr, value)

    # Process opaque attributes
    opaque_attrs = {}
    for attr in profile_attrs_opaque:
        value = req.POST.get(attr)
        opaque_attrs[attr] = value

    # Encrypt TOTP before it is saved to the database
    totp_key = opaque_attrs.get('totp_key')
    if totp_key:
        cm = CryptoManager(secret_key=zato_settings.zato_secret_key)
        totp_key = cm.encrypt(totp_key.encode('utf8'))
        opaque_attrs['totp_key'] = totp_key

    # Save all opaque attributes along with the profile
    req.zato.user_profile.opaque1 = dumps(opaque_attrs)

    # Save the profile
    req.zato.user_profile.save()

    # Save preferred cluster colour markers
    for key, value in req.POST.items():
        if key.startswith('color_') and value != DEFAULT_PROMPT:
            cluster_id = key.replace('color_', '')

            if 'checkbox_{}'.format(cluster_id) in req.POST:
                try:
                    ccm = ClusterColorMarker.objects.get(cluster_id=cluster_id, user_profile=req.zato.user_profile)
                except ClusterColorMarker.DoesNotExist:
                    ccm = ClusterColorMarker()
                    ccm.cluster_id = cluster_id
                    ccm.user_profile = req.zato.user_profile
                ccm.color = value
                ccm.save()
            else:
                ClusterColorMarker.objects.filter(cluster_id=cluster_id, user_profile=req.zato.user_profile).delete()

    msg = 'Settings saved'
    messages.add_message(req, messages.INFO, msg, extra_tags='success')
    return redirect(reverse('account-settings-basic'))

# ################################################################################################################################
