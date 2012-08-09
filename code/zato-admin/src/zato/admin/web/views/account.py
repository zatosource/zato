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
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

# Zato
from zato.admin.web.views import meth_allowed
from zato.common.util import TRACE1

logger = logging.getLogger(__name__)

@meth_allowed('GET')
def settings(req):
    return_data = {'clusters':req.zato.clusters}

    if logger.isEnabledFor(TRACE1):
        logger.log(TRACE1, 'Returning render_to_response [{}]'.format(str(return_data)))
    
    return render_to_response('zato/account/settings.html', return_data, context_instance=RequestContext(req))
