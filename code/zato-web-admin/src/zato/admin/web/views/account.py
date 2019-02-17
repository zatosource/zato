# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Django
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.forms.account import BasicSettingsForm
from zato.admin.web.models import ClusterColorMarker
from zato.admin.web.views import method_allowed

logger = logging.getLogger(__name__)

DEFAULT_PROMPT = 'Click to pick a color'

profile_attrs = ('timezone', 'date_format', 'time_format')

@method_allowed('GET')
def settings_basic(req):
    initial = {}
    for attr in profile_attrs:
        initial[attr] = getattr(req.zato.user_profile, attr)

    return_data = {'clusters':req.zato.clusters, 'default_prompt':DEFAULT_PROMPT, 'form':BasicSettingsForm(initial)}

    cluster_colors = {str(getattr(item, 'cluster_id')):getattr(item, 'color') for item in req.zato.user_profile.cluster_color_markers.all()}
    return_data['cluster_colors'] = cluster_colors

    return TemplateResponse(req, 'zato/account/settings.html', return_data)

@method_allowed('POST')
def settings_basic_save(req):

    for attr in profile_attrs:
        # Use False as default value so as to convert blank checkboxes into a boolean value
        value = req.POST.get(attr, False)
        setattr(req.zato.user_profile, attr, value)
    req.zato.user_profile.save()

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
