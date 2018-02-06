# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from httplib import OK
from json import loads

# Bunch
from bunch import Bunch

# Django
from django.core.urlresolvers import resolve

# Zato
from zato.admin.settings import ADMIN_INVOKE_NAME, ADMIN_INVOKE_PASSWORD, ADMIN_INVOKE_PATH, SASession, settings_db
from zato.admin.web.forms import SearchForm
from zato.admin.web.models import ClusterColorMarker, UserProfile
from zato.client import AnyServiceInvoker
from zato.common import version
from zato.common.odb.model import Cluster

# New in 2.0.8 thus optional
try:
    from zato.admin.settings import lb_use_tls, lb_tls_verify
except ImportError:
    lb_use_tls = False
    lb_tls_verify = True

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

class Client(AnyServiceInvoker):
    def __init__(self, req, *args, **kwargs):
        kwargs['tls_verify'] = lb_tls_verify
        self.forwarded_for = req.META.get('HTTP_X_FORWARDED_FOR') or req.META.get('REMOTE_ADDR')
        super(Client, self).__init__(*args, **kwargs)

    def invoke(self, *args, **kwargs):
        response = super(Client, self).invoke(*args, headers={'X-Zato-Forwarded-For': self.forwarded_for}, **kwargs)
        if response.inner.status_code != OK:
            zato_env = loads(response.inner.text).get('zato_env', {})
            raise Exception('CID: {}\nDetails: {}'.format(zato_env.get('cid'), zato_env.get('details')))
        return response

    def invoke_async(self, *args, **kwargs):
        response = super(Client, self).invoke_async(*args, headers={'X-Zato-Forwarded-For': self.forwarded_for}, **kwargs)
        return response

class ZatoMiddleware(object):

    def process_request(self, req):

        # Makes each Django view have an access to 'zato.odb' and 'zato.setttings_db' attributes
        # of the request object. The attributes are SQLAlchemy sessions tied databases defined in app's settings.py
        req.zato = Bunch()
        req.zato.odb = SASession()
        req.zato.settings_db = settings_db
        req.zato.args = Bunch() # Arguments read from URL

        # Whether this request to web-admin was served over TLS
        req.zato.is_tls = req.META.get('HTTP_X_FORWARDED_PROTO', '').lower() == 'https'

        # Whether communication with load-balancer should go over TLS
        req.zato.lb_use_tls = lb_use_tls
        req.zato.lb_tls_verify = lb_tls_verify

        try:
            resolved_kwargs = resolve(req.path).kwargs
            req.zato.id = resolved_kwargs.get('id')
            req.zato.cluster_id = req.GET.get('cluster') or req.POST.get('cluster_id') or \
                resolved_kwargs.get('cluster_id') or resolved_kwargs.get('cluster')

            if req.zato.cluster_id:
                req.zato.cluster = req.zato.odb.query(Cluster).filter_by(id=req.zato.cluster_id).one()

                url = 'http{}://{}:{}'.format(
                    's' if req.zato.lb_use_tls else '', req.zato.cluster.lb_host, req.zato.cluster.lb_port)
                auth = (ADMIN_INVOKE_NAME, ADMIN_INVOKE_PASSWORD)
                req.zato.client = Client(req, url, ADMIN_INVOKE_PATH, auth, to_bunch=True)

            req.zato.clusters = req.zato.odb.query(Cluster).order_by('name').all()
            req.zato.search_form = SearchForm(req.zato.clusters, req.GET)

            if not req.user.is_anonymous():
                try:
                    user_profile = UserProfile.objects.get(user=req.user)
                except UserProfile.DoesNotExist:
                    user_profile = UserProfile(user=req.user)
                    user_profile.save()
                req.zato.user_profile = user_profile
            else:
                req.zato.user_profile = None
        except Exception:
            req.zato.odb.rollback()
            raise

    def process_template_response(self, req, resp):
        if resp.context_data:
            resp.context_data['zato_version'] = version
        else:
            resp.context_data = {'zato_version':version}

        try:
            ccm = ClusterColorMarker.objects.get(cluster_id=req.zato.cluster_id, user_profile=req.zato.user_profile)
        except ClusterColorMarker.DoesNotExist:
            pass
        else:
            resp.context_data['cluster_color'] = ccm.color

        resp.render()

        return resp
