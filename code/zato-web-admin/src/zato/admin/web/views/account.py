# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Django
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.forms.account import BasicSettingsForm
from zato.admin.web.models import ClusterColorMarker
from zato.admin.web.views import method_allowed

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

DEFAULT_PROMPT = 'Click to pick a color'

# ################################################################################################################################

profile_attrs = 'timezone', 'date_format', 'time_format'

# ################################################################################################################################

@method_allowed('GET')
def settings_basic(req):

    # Data for the template
    initial = {}

    # Process explicitly named attributes
    for attr in profile_attrs:
        initial[attr] = getattr(req.zato.user_profile, attr, None)

    return_data = {
        'clusters': req.zato.clusters,
        'default_prompt': DEFAULT_PROMPT,
        'form':BasicSettingsForm(initial),
        'username': req.user.username
    }

    cluster_color_markers = req.zato.user_profile.cluster_color_markers.all()
    cluster_colors = {str(item.cluster_id):item.color for item in cluster_color_markers}
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
