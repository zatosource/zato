# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

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

# Django
from django.conf import settings
from django.contrib.auth.views import login
from django.http import HttpResponseRedirect

# Bunch
from bunch import Bunch

# Zato
from zato.admin.settings import SASession
from zato.admin.web.forms import ChooseClusterForm
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
            
        # Makes each Django view have an access to an 'odb' attribute of the
        # request object. The attribute is an SQLAlchemy session to the database
        # defined in app's settings.py
        req.zato = Bunch()
        req.zato.odb = SASession()
        
        req.zato.cluster_id = req.GET.get('cluster') or req.POST.get('cluster_id')
        if req.zato.cluster_id:
            req.zato.cluster = req.zato.odb.query(Cluster).filter_by(id=req.zato.cluster_id).one()
            req.zato.clusters = req.zato.odb.query(Cluster).order_by('name').all()
            req.zato.choose_cluster_form = ChooseClusterForm(req.zato.clusters, req.GET)