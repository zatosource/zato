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
from unittest import TestCase

# anyjson
from anyjson import loads

# nose
from nose.tools import eq_

# Bunch
from bunch import Bunch

# Zato
from zato.common.odb.model import ChannelAMQP
from zato.common.test import Expected, rand_bool, rand_int, rand_string, ServiceTestCase
from zato.server.service.internal.channel.amqp import GetList

def get_data():
    return Bunch(
        {'id':rand_int(), 'name':rand_string(), 'is_active':rand_bool(), 'queue':rand_string(), 
         'consumer_tag_prefix':rand_string(), 'def_name':rand_string(), 'def_id':rand_int(), 
         'service_name':rand_string(), 'data_format':rand_string()}
    )

class GetListTestCase(ServiceTestCase):
    def test_response(self):
        request = {'cluster_id': rand_int()}
        
        expected_data = tuple(get_data() for x in range(rand_int(10)))
        expected = Expected()
        
        for datum in expected_data:
            item = ChannelAMQP()
            item.id = datum.id
            item.name = datum.name
            item.is_active = datum.is_active
            item.queue = datum.queue
            item.consumer_tag_prefix = datum.consumer_tag_prefix
            item.def_name = datum.def_name
            item.def_id = datum.def_id
            item.service_name = datum.service_name
            item.data_format = datum.data_format
            expected.add(item)
            
        instance = self.invoke(GetList, request, expected)
        response = loads(instance.response.payload.getvalue())['response']
        
        for idx, item in enumerate(response):
            expected = expected_data[idx]
            given = Bunch(item)
            
            eq_(given.id, expected.id)
            eq_(given.name, expected.name)
            eq_(given.is_active, expected.is_active)
            eq_(given.queue, expected.queue)
            eq_(given.consumer_tag_prefix, expected.consumer_tag_prefix)
            eq_(given.def_name, expected.def_name)
            eq_(given.def_id, expected.def_id)
            eq_(given.service_name, expected.service_name)
            eq_(given.data_format, expected.data_format)
