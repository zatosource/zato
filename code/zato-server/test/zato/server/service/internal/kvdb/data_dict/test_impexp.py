# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Bunch
from bunch import Bunch

# Zato
from zato.common import zato_namespace
from zato.common.test import rand_string, ServiceTestCase
from zato.server.service.internal.kvdb.data_dict.impexp import Import

##############################################################################

class ImportTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = Import
        self.sio = self.service_class.SimpleIO
    
    def get_request_data(self):
        return {'data':rand_string()}
    
    def get_response_data(self):
        return Bunch()
    
    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_kvdb_data_dict_impexp_import_request')
        self.assertEquals(self.sio.response_elem, 'zato_kvdb_data_dict_impexp_import_response')
        self.assertEquals(self.sio.input_required, ('data',))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_required')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.kvdb.data-dict.impexp.import')
