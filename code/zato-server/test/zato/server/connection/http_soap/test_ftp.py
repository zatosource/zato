# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from unittest import TestCase

# Bunch
from bunch import Bunch

# mock
from mock import patch

# Zato
from zato.common.test import rand_float, rand_string
from zato.server.connection.ftp import FTPStore

class TestFTP(TestCase):
    def test_timeout_is_float(self):
        """ GH #188 - Parameter 'timeout' should be a float.
        """
        class FTPFacade(object):
            def __init__(self, host, user, password, acct, timeout, port, dircache):
                self.timeout = timeout

        with patch('zato.server.connection.ftp.FTPFacade', FTPFacade):
            store = FTPStore()
    
            conn_name = 'test'
            timeout = '20' # String at that point
            params = Bunch({'name':conn_name, 'is_active':True, 'port':21, 'dircache':True, 'timeout':timeout})
    
            for name in 'host', 'user', 'password', 'acct':
                params[name] = rand_string()
    
            store.add_params([params])
            conn = store.get(conn_name)
            self.assertIsInstance(conn.timeout, float)