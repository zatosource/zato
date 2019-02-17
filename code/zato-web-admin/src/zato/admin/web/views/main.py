# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django.contrib.auth import logout as _logout
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed

@method_allowed('GET')
def index_redirect(req):
    return HttpResponseRedirect('/zato')

@method_allowed('GET')
def index(req):
    return TemplateResponse(req, 'zato/index.html')

@method_allowed('GET')
def logout(req):
    _logout(req)
    return index_redirect(req)

@method_allowed('GET')
def my_account(req):
    pass
