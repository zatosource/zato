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
from collections import namedtuple
from cStringIO import StringIO
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.template import RequestContext
from django.shortcuts import render_to_response

# lxml
from lxml import etree
from lxml.objectify import Element

# validate
from validate import is_boolean

# anyjson
from anyjson import dumps, loads

# Zato
from zato.admin.web import invoke_admin_service
from zato.admin.web.forms import ChooseClusterForm
from zato.admin.web.forms.service import CreateForm, EditForm, WSDLUploadForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, meth_allowed
from zato.common import SourceInfo, zato_namespace, zato_path
from zato.common.odb.model import Cluster, Service
from zato.common.util import TRACE1

logger = logging.getLogger(__name__)

class DictItem(object):
    def __init__(self, system, name, value):
        self.system = system
        self.name = name
        self.value = value

class Index(_Index):
    meth_allowed = 'GET'
    url_name = 'kvdb-data-dict-dictionary'
    template = 'zato/kvdb/data_dict/dictionary.html'
    
    soap_action = 'zato:kvdb.data-dict.dictionary.get-list'
    output_class = DictItem
    
    class SimpleIO(_Index.SimpleIO):
        output_required = ('name', 'source_system', 'target_system', 'source_name', 'target_name', 'source_value', 'target_value')
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
        }
