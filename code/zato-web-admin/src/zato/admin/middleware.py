# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django.conf import settings
from django.contrib.auth.views import login
from django.core.urlresolvers import resolve
from django.http import HttpResponseRedirect

# Bunch
from bunch import Bunch

# Zato
from zato.admin.settings import ADMIN_INVOKE_NAME, ADMIN_INVOKE_PASSWORD, \
    ADMIN_INVOKE_PATH,SASession
from zato.admin.web.forms import ChooseClusterForm
from zato.admin.web.models import ClusterColorMarker, UserProfile
from zato.client import AnyServiceInvoker
from zato.common.odb.model import Cluster


# Code below is taken from http://djangosnippets.org/snippets/136/
# Slightly modified for Zato's purposes.

###
# Copyright (c) 2006-2007, Jared Kuolt
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the SuperJared.com nor the names of its
#       contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###

class ZatoMiddleware(object):
    """
    Require Login middleware. If enabled, each Django-powered page will
    require authentication.

    If an anonymous user requests a page, he/she is redirected to the login
    page set by REQUIRE_LOGIN_PATH or /accounts/login/ by default.
    """
    def __init__(self):
        self.require_login_path = getattr(settings, 'REQUIRE_LOGIN_PATH', '/accounts/login/')
        self.dont_require_login = settings.DONT_REQUIRE_LOGIN

    def process_request(self, req):
        for dont_require_login in self.dont_require_login:
            if req.path.startswith(dont_require_login):
                return None

        if req.path != self.require_login_path and req.user.is_anonymous():
            if req.POST:
                return login(req)
            else:
                return HttpResponseRedirect('{}?next={}'.format(self.require_login_path, req.path))
            
        # Makes each Django view have an access to a 'zato.odb' attribute of the
        # request object. The attribute is an SQLAlchemy session to the database
        # defined in app's settings.py
        req.zato = Bunch()
        req.zato.odb = SASession()
        req.zato.args = Bunch() # Arguments read from URL

        resolved_kwargs = resolve(req.path).kwargs
        req.zato.id = resolved_kwargs.get('id')
        req.zato.cluster_id = req.GET.get('cluster') or req.POST.get('cluster_id') or \
            resolved_kwargs.get('cluster_id') or resolved_kwargs.get('cluster')
        
        if req.zato.cluster_id:
            req.zato.cluster = req.zato.odb.query(Cluster).filter_by(id=req.zato.cluster_id).one()
            
            url = 'http://{}:{}'.format(req.zato.cluster.lb_host, req.zato.cluster.lb_port)
            auth = (ADMIN_INVOKE_NAME, ADMIN_INVOKE_PASSWORD)
            req.zato.client = AnyServiceInvoker(url, ADMIN_INVOKE_PATH, auth, to_bunch=True)
            
        req.zato.clusters = req.zato.odb.query(Cluster).order_by('name').all()
        req.zato.choose_cluster_form = ChooseClusterForm(req.zato.clusters, req.GET)

        if not req.user.is_anonymous():
            try:
                user_profile = UserProfile.objects.get(user=req.user)
            except UserProfile.DoesNotExist:
                user_profile = UserProfile(user=req.user)
                user_profile.save()
            req.zato.user_profile = user_profile
        else:
            req.zato.user_profile = None

    def process_template_response(self, req, resp):
        try:
            ccm = ClusterColorMarker.objects.get(cluster_id=req.zato.cluster_id, user_profile=req.zato.user_profile)
        except ClusterColorMarker.DoesNotExist:
            pass
        else:
            resp.context_data['cluster_color'] = ccm.color

        resp.render()
        
        return resp
