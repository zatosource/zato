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
from random import choice, randint
from unittest import TestCase
from uuid import uuid4

# anyjson
from anyjson import loads

# nose
from nose.tools import eq_

# Bunch
from bunch import Bunch

# Zato
from zato.common.odb.model import Service
from zato.common.test import Expected, ServiceTestCase
from zato.server.service.internal.service import GetByName

class GetByNameTestCase(ServiceTestCase):
    
    def test(self):
        request = {'cluster_id': randint(1, 100), 'name': uuid4().hex}
        
        expected_id = randint(1, 100)
        expected_name = uuid4().hex
        expected_is_active = choice((True, False))
        expected_impl_name = uuid4().hex
        expected_is_internal = choice((True, False))
        
        service = Service()
        service.id = expected_id
        service.name = expected_name
        service.is_active = expected_is_active
        service.impl_name = expected_impl_name
        service.is_internal = expected_is_internal
        
        expected = Expected()
        expected.add(service)
        
        instance = self.invoke(GetByName, request, expected)
        response = Bunch(loads(instance.response.payload.getvalue())['response'])
        
        eq_(response.id, expected_id)
        eq_(response.name, expected_name)
        eq_(response.is_active, expected_is_active)
        eq_(response.impl_name, expected_impl_name)
        eq_(response.is_internal, expected_is_internal)
        eq_(response.usage_count, 0)
