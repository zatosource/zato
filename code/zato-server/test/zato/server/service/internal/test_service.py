# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# anyjson
from anyjson import loads

# nose
from nose.tools import eq_

# Bunch
from bunch import Bunch

# Zato
from zato.common.odb.model import Service
from zato.common.test import Expected, rand_bool, rand_int, rand_string, ServiceTestCase
from zato.server.service.internal.service import GetList, GetByName

def get_data():
    return Bunch({'id':rand_int(), 'name':rand_string(), 'is_active':rand_bool(), 
        'impl_name':rand_string(), 'is_internal':rand_bool()})

class GetListTestCase(ServiceTestCase):
    def test_response(self):
        request = {'cluster_id': rand_int()}
        
        expected_keys = get_data().keys()
        expected_data = tuple(get_data() for x in range(rand_int(10)))
        expected = Expected()
        
        for datum in expected_data:
            item = Service()
            for key in expected_keys:
                value = getattr(datum, key)
                setattr(item, key, value)
            expected.add(item)
            
        instance = self.invoke(GetList, request, expected)
        response = loads(instance.response.payload.getvalue())[GetList.SimpleIO.response_elem]
        
        for idx, item in enumerate(response):
            expected = expected_data[idx]
            given = Bunch(item)
            
            for key in expected_keys:
                given_value = getattr(given, key)
                expected_value = getattr(expected, key)
                eq_(given_value, expected_value)

class GetByNameTestCase(ServiceTestCase):
    def test_response(self):
        request = {'cluster_id':rand_int(), 'name':rand_string()}
        
        expected_id = rand_int()
        expected_name = rand_string()
        expected_is_active = rand_bool()
        expected_impl_name = rand_string()
        expected_is_internal = rand_bool()
        
        service = Service()
        service.id = expected_id
        service.name = expected_name
        service.is_active = expected_is_active
        service.impl_name = expected_impl_name
        service.is_internal = expected_is_internal
        
        expected = Expected()
        expected.add(service)
        
        instance = self.invoke(GetByName, request, expected)
        response = Bunch(loads(instance.response.payload.getvalue())['zato_service_get_by_name_response'])
        
        eq_(response.id, expected_id)
        eq_(response.name, expected_name)
        eq_(response.is_active, expected_is_active)
        eq_(response.impl_name, expected_impl_name)
        eq_(response.is_internal, expected_is_internal)
        eq_(response.usage, 0)
