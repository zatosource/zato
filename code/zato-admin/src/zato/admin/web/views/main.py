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
from django.contrib.auth import logout as _logout
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import meth_allowed

@meth_allowed('GET')
def index_redirect(req):
    return HttpResponseRedirect('/zato')

@meth_allowed('GET')
def index(req):
    return TemplateResponse(req, 'zato/index.html')

@meth_allowed('GET')
def logout(req):
    _logout(req)
    return index_redirect(req)

@meth_allowed('GET')
def my_account(req):
    pass
