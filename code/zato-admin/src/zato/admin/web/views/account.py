# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Django
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.models import ClusterColorMarker
from zato.admin.web.views import meth_allowed
from zato.common.util import TRACE1

logger = logging.getLogger(__name__)

DEFAULT_PROMPT = 'Click to pick a color'

@meth_allowed('GET')
def settings_basic(req):
    return_data = {'clusters':req.zato.clusters, 'default_prompt':DEFAULT_PROMPT}
    
    cluster_colors = {str(getattr(item, 'cluster_id')):getattr(item, 'color') for item in req.zato.user_profile.cluster_color_markers.all()}
    return_data['cluster_colors'] = cluster_colors
    
    if logger.isEnabledFor(TRACE1):
        logger.log(TRACE1, 'Returning render_to_response [{}]'.format(str(return_data)))

    return TemplateResponse(req, 'zato/account/settings.html', return_data)

@meth_allowed('POST')
def settings_basic_save(req):

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
