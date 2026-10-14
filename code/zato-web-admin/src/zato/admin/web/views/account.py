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
from zato.admin.web.models import EnvironmentColorMarker
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
        'default_prompt': DEFAULT_PROMPT,
        'form':BasicSettingsForm(initial),
        'username': req.user.username,
        'environment_color': '',
    }

    if marker := req.zato.user_profile.environment_color_markers.first():
        return_data['environment_color'] = marker.color

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

    # Save the preferred environment color marker
    color = req.POST['color_environment']

    if color != DEFAULT_PROMPT:
        if 'checkbox_environment' in req.POST:
            try:
                marker = EnvironmentColorMarker.objects.get(user_profile=req.zato.user_profile)
            except EnvironmentColorMarker.DoesNotExist:
                marker = EnvironmentColorMarker()
                marker.user_profile = req.zato.user_profile
            marker.color = color
            marker.save()
        else:
            EnvironmentColorMarker.objects.filter(user_profile=req.zato.user_profile).delete()

    msg = 'Settings saved'
    messages.add_message(req, messages.INFO, msg, extra_tags='success')
    return redirect(reverse('account-settings-basic'))

# ################################################################################################################################
